"""
Game Session orchestrator that coordinates NPCs, environment, and events
"""

import asyncio
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from google.adk.models import Gemini

from .npc_agent import NPCAgent
from .environment_manager import EnvironmentManager
from .session_service_factory import session_service_manager
from ..models.npc_models import NPCData
from ..models.environment_models import GameEvent, EventType, Location
from ..models.action_models import ActionDefinition, DEFAULT_ACTION_DEFINITIONS
from ..models.api_models import EventRequest, EventResponse, NPCResponse, SessionConfig


class GameSession:
    """
    Main orchestrator for a game session
    
    Manages:
    - Multiple NPC agents
    - Environment state
    - Event processing and coordination
    - Background updates
    - Session lifecycle
    """
    
    def __init__(self, session_config: SessionConfig):
        self.session_id = session_config.session_id
        self.game_title = session_config.game_title
        self.settings = session_config.settings
        self.persistence_config = session_config.persistence.dict()
        
        # Get or create session service based on persistence configuration
        self.session_service = session_service_manager.get_or_create_session_service(
            self.session_id, 
            self.persistence_config
        )
        
        # Core components
        self.environment_manager = EnvironmentManager(self.session_id)
        self.npc_agents: Dict[str, NPCAgent] = {}
        self.available_actions = session_config.available_actions or DEFAULT_ACTION_DEFINITIONS
        
        # Session state
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.total_events_processed = 0
        self.status = "initializing"
        
        # Background processing
        self._background_tasks: List[asyncio.Task] = []
        self._event_queue = asyncio.Queue()
        self._processing_events = False
        
        # Thread pool for parallel processing
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Initialize from config
        self._initialize_from_config(session_config)
    
    def _initialize_from_config(self, config: SessionConfig):
        """Initialize session from configuration"""
        # Set up environment
        self.environment_manager.world_state.environment = config.environment
        
        # Add locations to environment
        for location in config.environment.locations.values():
            self.environment_manager.add_location(location)
        
        # Create NPC agents
        for npc_data in config.npcs:
            self.add_npc(npc_data)
    
    async def start(self):
        """Start the game session"""
        if self.status != "initializing":
            raise RuntimeError(f"Cannot start session in status: {self.status}")
        
        self.status = "starting"
        
        # Start environment background processing
        await self.environment_manager.start_background_processing()
        
        # Start event processing
        self._processing_events = True
        self._background_tasks.append(
            asyncio.create_task(self._event_processing_loop())
        )
        
        # Start NPC background behaviors
        self._background_tasks.append(
            asyncio.create_task(self._npc_behavior_loop())
        )
        
        self.status = "active"
        print(f"Game session {self.session_id} started with {len(self.npc_agents)} NPCs")
    
    async def stop(self):
        """Stop the game session"""
        self.status = "stopping"
        
        # Stop event processing
        self._processing_events = False
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        self._background_tasks.clear()
        
        # Stop environment processing
        await self.environment_manager.stop_background_processing()
        
        # Shutdown thread pool
        self._thread_pool.shutdown(wait=True)
        
        self.status = "stopped"
        print(f"Game session {self.session_id} stopped")
    
    def add_npc(self, npc_data: NPCData, model_name: str = "gemini-1.5-flash") -> bool:
        """Add a new NPC to the session"""
        try:
            npc_agent = NPCAgent(
                npc_data=npc_data,
                model_name=model_name,
                available_actions=self.available_actions
            )
            
            self.npc_agents[npc_data.state.npc_id] = npc_agent
            
            # Add NPC to environment
            if npc_data.state.current_location:
                location = self.environment_manager.get_location(npc_data.state.current_location)
                if location and npc_data.state.npc_id not in location.npcs_present:
                    location.npcs_present.append(npc_data.state.npc_id)
            
            return True
        except Exception as e:
            print(f"Error adding NPC {npc_data.state.npc_id}: {e}")
            return False
    
    def remove_npc(self, npc_id: str) -> bool:
        """Remove an NPC from the session"""
        if npc_id not in self.npc_agents:
            return False
        
        npc_agent = self.npc_agents[npc_id]
        
        # Remove from environment
        for location in self.environment_manager.get_all_locations().values():
            if npc_id in location.npcs_present:
                location.npcs_present.remove(npc_id)
        
        # Remove from agents
        del self.npc_agents[npc_id]
        
        return True
    
    def get_npc(self, npc_id: str) -> Optional[NPCAgent]:
        """Get an NPC agent by ID"""
        return self.npc_agents.get(npc_id)
    
    def get_all_npcs(self) -> Dict[str, NPCAgent]:
        """Get all NPC agents"""
        return self.npc_agents.copy()
    
    async def process_event(self, event_request: EventRequest) -> EventResponse:
        """Process a game event and coordinate NPC responses"""
        self.last_activity = datetime.now()
        self.total_events_processed += 1
        
        # Generate event ID if not provided
        event_id = event_request.event_id or str(uuid.uuid4())
        
        # Create game event
        game_event = GameEvent(
            event_id=event_id,
            event_type=self._determine_event_type(event_request),
            initiator=event_request.initiator,
            target=event_request.target,
            action=event_request.action,
            location=event_request.location,
            description=f"{event_request.initiator} {event_request.action}",
            properties=event_request.action_properties
        )
        
        # Add to environment
        self.environment_manager.add_event(game_event)
        
        # Create initial response
        response = EventResponse(
            event_id=event_id,
            session_id=self.session_id,
            processing_complete=False
        )
        
        try:
            # Determine which NPCs are affected
            affected_npcs = self._get_affected_npcs(game_event)
            
            if affected_npcs:
                # Get primary NPC response quickly for low latency
                primary_npc_id = self._get_primary_affected_npc(game_event, affected_npcs)
                if primary_npc_id:
                    primary_response = await self._get_npc_response(primary_npc_id, game_event)
                    response.primary_npc_response = primary_response
                    response.immediate_message = primary_response.action_result.message
                
                # Queue background processing for other NPCs
                await self._queue_background_event_processing(game_event, affected_npcs, response)
            
            response.processing_complete = len(affected_npcs) <= 1
            
        except Exception as e:
            response.error_message = f"Error processing event: {str(e)}"
            print(f"Error processing event {event_id}: {e}")
        
        return response
    
    async def get_session_status(self) -> Dict[str, Any]:
        """Get current session status"""
        return {
            "session_id": self.session_id,
            "game_title": self.game_title,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "total_events": self.total_events_processed,
            "npc_count": len(self.npc_agents),
            "environment": self.environment_manager.get_state_snapshot(),
            "active_npcs": list(self.npc_agents.keys()),
            "persistence": {
                "type": self.persistence_config.get('type', 'memory'),
                "service_type": type(self.session_service).__name__,
                "configured": True
            }
        }
    
    def _determine_event_type(self, event_request: EventRequest) -> EventType:
        """Determine the event type based on the request"""
        if event_request.initiator == "player":
            return EventType.PLAYER_ACTION
        elif event_request.initiator in self.npc_agents:
            return EventType.NPC_ACTION
        elif event_request.initiator == "system":
            return EventType.SYSTEM_EVENT
        else:
            return EventType.INTERACTION
    
    def _get_affected_npcs(self, event: GameEvent) -> List[str]:
        """Determine which NPCs are affected by an event"""
        affected = []
        
        # Target NPC is always affected
        if event.target and event.target in self.npc_agents:
            affected.append(event.target)
        
        # NPCs at the same location are affected
        location_npcs = self.environment_manager.get_npcs_at_location(event.location)
        for npc_id in location_npcs:
            if npc_id not in affected and npc_id != event.initiator:
                affected.append(npc_id)
        
        # NPCs in nearby locations might be affected (if it's a loud event)
        if event.action in ["shout", "explosion", "combat"]:
            for location in self.environment_manager.get_all_locations().values():
                if event.location in location.connected_locations:
                    nearby_npcs = location.npcs_present
                    for npc_id in nearby_npcs:
                        if npc_id not in affected and npc_id != event.initiator:
                            affected.append(npc_id)
        
        return affected
    
    def _get_primary_affected_npc(self, event: GameEvent, affected_npcs: List[str]) -> Optional[str]:
        """Get the primary NPC that should respond immediately"""
        # Target NPC has priority
        if event.target and event.target in affected_npcs:
            return event.target
        
        # Otherwise, pick the first affected NPC
        return affected_npcs[0] if affected_npcs else None
    
    async def _get_npc_response(self, npc_id: str, event: GameEvent) -> NPCResponse:
        """Get a response from a specific NPC"""
        npc_agent = self.npc_agents.get(npc_id)
        if not npc_agent:
            raise ValueError(f"NPC {npc_id} not found")
        
        # Get environment context
        context = self.environment_manager.get_environment_context(event.location)
        
        # Process event with NPC
        action_result = await npc_agent.process_event(event, context)
        
        # Create NPC response
        return NPCResponse(
            npc_id=npc_id,
            action_result=action_result,
            reasoning=action_result.action.reasoning,
            emotion=npc_agent.npc_data.state.mood,
            relationship_changes={}  # Could be expanded to track relationship changes
        )
    
    async def _queue_background_event_processing(
        self, 
        event: GameEvent, 
        affected_npcs: List[str], 
        response: EventResponse
    ):
        """Queue background processing for remaining NPCs"""
        # Create background processing task
        task_data = {
            "event": event,
            "affected_npcs": affected_npcs,
            "response": response,
            "timestamp": datetime.now()
        }
        
        await self._event_queue.put(task_data)
    
    async def _event_processing_loop(self):
        """Background loop for processing events"""
        while self._processing_events:
            try:
                # Wait for events with timeout
                task_data = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                
                # Process the event in background
                await self._process_event_background(task_data)
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in event processing loop: {e}")
    
    async def _process_event_background(self, task_data: Dict[str, Any]):
        """Process an event in the background"""
        event = task_data["event"]
        affected_npcs = task_data["affected_npcs"]
        response = task_data["response"]
        
        try:
            # Process all affected NPCs
            all_responses = []
            
            # Use asyncio.gather for parallel processing
            tasks = []
            for npc_id in affected_npcs:
                if npc_id != response.primary_npc_response.npc_id if response.primary_npc_response else None:
                    task = self._get_npc_response(npc_id, event)
                    tasks.append(task)
            
            if tasks:
                npc_responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                for npc_response in npc_responses:
                    if isinstance(npc_response, NPCResponse):
                        all_responses.append(npc_response)
                    else:
                        print(f"Error getting NPC response: {npc_response}")
            
            # Add primary response if it exists
            if response.primary_npc_response:
                all_responses.append(response.primary_npc_response)
            
            # Update response
            response.all_npc_responses = all_responses
            response.processing_complete = True
            
            # Apply any environment updates
            self._apply_environment_updates(event, all_responses)
            
        except Exception as e:
            response.error_message = f"Background processing error: {str(e)}"
            response.processing_complete = True
            print(f"Error in background event processing: {e}")
    
    def _apply_environment_updates(self, event: GameEvent, responses: List[NPCResponse]):
        """Apply environment updates from NPC responses"""
        for response in responses:
            # Apply state changes to NPCs
            npc_agent = self.npc_agents.get(response.npc_id)
            if npc_agent:
                for key, value in response.action_result.state_changes.items():
                    if hasattr(npc_agent.npc_data.state, key):
                        setattr(npc_agent.npc_data.state, key, value)
            
            # Apply environment changes
            for key, value in response.action_result.environment_changes.items():
                self.environment_manager.set_global_variable(key, value)
    
    async def _npc_behavior_loop(self):
        """Background loop for autonomous NPC behaviors"""
        while self._processing_events:
            try:
                # Periodically trigger autonomous NPC behaviors
                await asyncio.sleep(30)  # Check every 30 seconds
                
                for npc_id, npc_agent in self.npc_agents.items():
                    # Check if NPC should do something autonomously
                    if await self._should_npc_act_autonomously(npc_agent):
                        await self._trigger_autonomous_npc_action(npc_agent)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in NPC behavior loop: {e}")
    
    async def _should_npc_act_autonomously(self, npc_agent: NPCAgent) -> bool:
        """Determine if an NPC should act autonomously"""
        # Simple logic: act if energy is high and no recent activity
        if npc_agent.npc_data.state.energy > 80:
            recent_events = self.environment_manager.get_events_involving_npc(
                npc_agent.npc_id, limit=3
            )
            
            # If no recent events involving this NPC, they might act autonomously
            if not recent_events:
                return True
        
        return False
    
    async def _trigger_autonomous_npc_action(self, npc_agent: NPCAgent):
        """Trigger an autonomous action for an NPC using the new ADK-powered thinking"""
        try:
            # Use the NPC's new autonomous thinking capability
            autonomous_action = await npc_agent.think_autonomously()
            
            if autonomous_action:
                # Create an autonomous event based on the action
                autonomous_event = GameEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=EventType.NPC_ACTION,
                    initiator=npc_agent.npc_id,
                    action=autonomous_action.action_type.value,
                    location=npc_agent.npc_data.state.current_location,
                    description=f"{npc_agent.npc_data.personality.name} autonomously decides to {autonomous_action.action_type.value}",
                    properties=autonomous_action.properties
                )
                
                # Add event to environment for other NPCs to potentially react to
                self.environment_manager.add_event(autonomous_event)
                
                # Update NPC state based on the autonomous action
                npc_agent._update_state_after_action(autonomous_action)
                
                print(f"🤖 {npc_agent.npc_data.personality.name} autonomously {autonomous_action.action_type.value}: {autonomous_action.reasoning}")
            
        except Exception as e:
            print(f"Error in autonomous NPC action for {npc_agent.npc_id}: {e}")
    
    def get_npc_states(self) -> Dict[str, Dict[str, Any]]:
        """Get current states of all NPCs"""
        return {
            npc_id: agent.get_state_snapshot()
            for npc_id, agent in self.npc_agents.items()
        } 