"""
FastAPI-based REST API for NPC Engine frontend integration
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('npc_engine.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
    import uvicorn

    from ..core.game_session import GameSession
    from ..core.npc_agent import NPCAgent
    from ..core.environment_manager import EnvironmentManager
    from ..core.session_service_factory import session_service_manager
    from ..models.api_models import (
        EventRequest, EventResponse, SessionConfig, SessionInfo,
        SessionStatusResponse, BatchEventRequest, BatchEventResponse,
        HealthCheckResponse, ErrorResponse
    )
    from ..models.npc_models import NPCData, NPCPersonality, NPCState, NPCMemory
    from ..models.environment_models import Location, LocationType, Environment
    from ..models.action_models import DEFAULT_ACTION_DEFINITIONS
    from ..config import ConfigLoader, ActionConfig, EnvironmentConfig, NPCConfig, NPCSchema, NPCInstance

    FASTAPI_AVAILABLE = True
    logger.info("FastAPI dependencies loaded successfully")
except ImportError as e:
    logger.error(f"FastAPI dependencies not available: {e}")
    FASTAPI_AVAILABLE = False
    
    # Create mock classes for development
    class FastAPI:
        def __init__(self, **kwargs): pass
        def add_middleware(self, *args, **kwargs): pass
        def mount(self, *args, **kwargs): pass
        def get(self, *args, **kwargs): return lambda f: f
        def post(self, *args, **kwargs): return lambda f: f
        def put(self, *args, **kwargs): return lambda f: f
        def delete(self, *args, **kwargs): return lambda f: f
    
    class HTTPException(Exception):
        def __init__(self, status_code, detail): 
            self.status_code = status_code
            self.detail = detail
    
    class BaseModel: pass
    class BackgroundTasks: pass
    
    from ..core.game_session import GameSession
    from ..core.npc_agent import NPCAgent
    from ..core.environment_manager import EnvironmentManager
    from ..models.api_models import *
    from ..config import ConfigLoader, ActionConfig, EnvironmentConfig, NPCConfig, NPCSchema, NPCInstance


class NPCEngineAPI:
    """
    REST API for the NPC Engine
    
    Provides endpoints for:
    - Session management
    - Event processing
    - NPC state queries
    - Environment management
    """
    
    def __init__(self):
        self.sessions: Dict[str, GameSession] = {}
        self.start_time = time.time()
        self.config_loader = ConfigLoader()
        self.app = self._create_app()
    
    def _create_app(self) -> FastAPI:
        """Create and configure the FastAPI application"""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            print("NPC Engine API starting up...")
            yield
            # Shutdown
            print("NPC Engine API shutting down...")
            await self._shutdown_all_sessions()
        
        app = FastAPI(
            title="NPC Engine API",
            description="Intelligent NPC backend framework powered by Google ADK",
            version="0.1.0",
            lifespan=lifespan
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        

        # Add routes
        self._add_routes(app)
        
        # Mount static files AFTER API routes to avoid conflicts
        try:
            from pathlib import Path
            static_dir = Path(__file__).parent.parent.parent / "web-gui" / "dist"
            if static_dir.exists():
                app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
                print(f"📁 Serving static files from: {static_dir}")
        except Exception as e:
            print(f"⚠️  Could not mount static files: {e}")
        
        return app
    
    def _add_routes(self, app: FastAPI):
        """Add all API routes"""
        
        @app.get("/health", response_model=HealthCheckResponse)
        async def health_check():
            """Health check endpoint"""
            return HealthCheckResponse(
                status="healthy",
                version="0.1.0",
                uptime=time.time() - self.start_time,
                active_sessions=len(self.sessions),
                total_npcs=sum(len(session.npc_agents) for session in self.sessions.values())
            )
        
        @app.get("/sessions/services")
        async def get_session_services_info():
            """Get information about active session services"""
            services_info = session_service_manager.get_active_services_info()
            session_details = {}
            
            for session_id, session in self.sessions.items():
                session_details[session_id] = {
                    "persistence_type": session.persistence_config.get('type', 'memory'),
                    "service_type": type(session.session_service).__name__,
                    "game_title": session.game_title,
                    "status": session.status
                }
            
            return {
                "services_summary": services_info,
                "sessions": session_details,
                "total_sessions": len(self.sessions)
            }
        
        @app.post("/sessions", response_model=SessionInfo)
        async def create_session(config: SessionConfig):
            """Create a new game session"""
            logger.info(f"Creating new session: {config.session_id}")
            logger.debug(f"Session config: {config.dict()}")
            
            try:
                if config.session_id in self.sessions:
                    logger.warning(f"Session {config.session_id} already exists")
                    raise HTTPException(status_code=400, detail="Session already exists")
                
                # Create and start session
                session = GameSession(config)
                await session.start()
                
                self.sessions[config.session_id] = session
                
                session_info = SessionInfo(
                    session_id=config.session_id,
                    game_title=config.game_title,
                    created_at=session.created_at,
                    last_activity=session.last_activity,
                    npc_count=len(session.npc_agents),
                    total_events=session.total_events_processed,
                    status=session.status
                )
                
                logger.info(f"Session {config.session_id} created successfully with {len(session.npc_agents)} NPCs")
                return session_info
                
            except Exception as e:
                logger.error(f"Failed to create session {config.session_id}: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")
        
        @app.get("/sessions")
        async def list_sessions():
            """Get list of all active sessions"""
            logger.info(f"Listing {len(self.sessions)} active sessions")
            
            sessions_list = []
            for session_id, session in self.sessions.items():
                try:
                    session_data = {
                        "session_id": session_id,
                        "game_title": session.game_title,
                        "created_at": session.created_at.isoformat(),
                        "last_activity": session.last_activity.isoformat(),
                        "npc_count": len(session.npc_agents),
                        "total_events": session.total_events_processed,
                        "status": session.status,
                        "environment": session.environment_manager.world_state.environment.time_of_day if hasattr(session.environment_manager.world_state, 'environment') else "unknown"
                    }
                    sessions_list.append(session_data)
                    logger.debug(f"Added session {session_id} to list")
                except Exception as e:
                    logger.error(f"Error getting data for session {session_id}: {str(e)}")
                    
            logger.info(f"Returning {len(sessions_list)} sessions")
            return sessions_list
        
        @app.delete("/sessions/{session_id}")
        async def delete_session(session_id: str):
            """Delete a game session"""
            if session_id not in self.sessions:
                raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
            
            try:
                session = self.sessions[session_id]
                await session.stop()
                del self.sessions[session_id]
                
                return {"success": True, "message": f"Session {session_id} deleted successfully"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")
        
        @app.post("/sessions/{session_id}/events")
        async def process_event(session_id: str, event_request: EventRequest):
            """Process an event in a session"""
            logger.info(f"🎮 Processing event in session {session_id}")
            logger.info(f"📋 Event request: {event_request}")
            
            try:
                session = self._get_session(session_id)
                
                # Process the event
                result = await session.process_event(event_request)
                
                # Convert EventResponse to a format compatible with the frontend
                response_data = {
                    "success": True,
                    "event_id": result.event_id,
                    "session_id": session_id,
                    "message": f"Event '{event_request.action}' processed successfully",
                    "action_details": [],
                    "processing_complete": result.processing_complete
                }
                
                # Add NPC action details if available
                if result.primary_npc_response:
                    primary_resp = result.primary_npc_response
                    session = self._get_session(session_id)
                    npc_agent = session.get_npc(primary_resp.npc_id)
                    npc_name = npc_agent.npc_data.personality.name if npc_agent else primary_resp.npc_id
                    
                    action_details = {
                        "npc_id": primary_resp.npc_id,
                        "npc_name": npc_name,
                        "action_type": primary_resp.action_result.action.action_type.value if hasattr(primary_resp.action_result.action.action_type, 'value') else str(primary_resp.action_result.action.action_type),
                        "action_properties": primary_resp.action_result.action.properties,
                        "reasoning": primary_resp.reasoning,
                        "success": primary_resp.action_result.success,
                        "message": primary_resp.action_result.message
                    }
                    response_data["action_details"].append(action_details)
                
                logger.info(f"✅ Event processed successfully: {response_data}")
                return response_data
                
            except Exception as e:
                logger.error(f"❌ Error processing event: {str(e)}")
                # Return error response in consistent format
                return {
                    "success": False,
                    "event_id": "error",
                    "session_id": session_id,
                    "message": f"Error processing event: {str(e)}",
                    "action_details": [],
                    "processing_complete": True,
                    "error_message": str(e)
                }
        
        @app.post("/sessions/{session_id}/events/test")
        async def test_event(session_id: str, event_data: dict):
            """Test an event with simplified structure for dashboard testing"""
            logger.info(f"🧪 Testing event in session {session_id}")
            logger.info(f"📋 Event data: {event_data}")
            
            try:
                session = self._get_session(session_id)
                
                # Convert simplified event data to EventRequest format
                event_request = EventRequest(
                    session_id=session_id,
                    action=event_data.get("action", "speak"),
                    initiator=event_data.get("source_id", "player"),
                    target=event_data.get("target_id", ""),
                    location="village_center",  # Default location
                    action_properties=event_data.get("action_data", {}),
                    additional_context={
                        "source": "dashboard_test",
                        "event_type": event_data.get("event_type", "player_to_npc"),
                        "timestamp": datetime.now().isoformat()
                    },
                    priority=5
                )
                
                logger.info(f"📤 Converted to EventRequest: {event_request}")
                
                # Process the event and get full response
                event_response = await session.process_event(event_request)
                logger.info(f"📥 Event processing result: {event_response}")
                
                # Extract NPC actions from the response
                npc_actions = []
                npc_responses_text = []
                
                # Get primary NPC response
                if event_response.primary_npc_response:
                    primary_resp = event_response.primary_npc_response
                    npc_agent = session.get_npc(primary_resp.npc_id)
                    npc_name = npc_agent.npc_data.personality.name if npc_agent else primary_resp.npc_id
                    
                    # Extract the action details
                    action_details = {
                        "npc_id": primary_resp.npc_id,
                        "npc_name": npc_name,
                        "action_type": primary_resp.action_result.action.action_type,
                        "action_properties": primary_resp.action_result.action.properties,
                        "reasoning": primary_resp.reasoning,
                        "success": primary_resp.action_result.success,
                        "message": primary_resp.action_result.message
                    }
                    npc_actions.append(action_details)
                    
                    # Create readable response text
                    action_type = action_details['action_type'].value if hasattr(action_details['action_type'], 'value') else str(action_details['action_type'])
                    action_text = f"{npc_name} performs action: {action_type}"
                    
                    if action_details['action_properties']:
                        props_text = ", ".join([f"{k}={v}" for k, v in action_details['action_properties'].items()])
                        action_text += f" ({props_text})"
                    
                    if primary_resp.reasoning:
                        action_text += f" - Reasoning: {primary_resp.reasoning}"
                    
                    npc_responses_text.append(action_text)
                
                # Get all other NPC responses (if background processing is complete)
                if event_response.all_npc_responses:
                    for npc_resp in event_response.all_npc_responses:
                        # Skip if this is the primary response (already processed)
                        if (event_response.primary_npc_response and 
                            npc_resp.npc_id == event_response.primary_npc_response.npc_id):
                            continue
                        
                        npc_agent = session.get_npc(npc_resp.npc_id)
                        npc_name = npc_agent.npc_data.personality.name if npc_agent else npc_resp.npc_id
                        
                        action_details = {
                            "npc_id": npc_resp.npc_id,
                            "npc_name": npc_name,
                            "action_type": npc_resp.action_result.action.action_type,
                            "action_properties": npc_resp.action_result.action.properties,
                            "reasoning": npc_resp.reasoning,
                            "success": npc_resp.action_result.success,
                            "message": npc_resp.action_result.message
                        }
                        npc_actions.append(action_details)
                        
                        # Create readable response text
                        action_type = action_details['action_type'].value if hasattr(action_details['action_type'], 'value') else str(action_details['action_type'])
                        action_text = f"{npc_name} performs action: {action_type}"
                        
                        if action_details['action_properties']:
                            props_text = ", ".join([f"{k}={v}" for k, v in action_details['action_properties'].items()])
                            action_text += f" ({props_text})"
                        
                        if npc_resp.reasoning:
                            action_text += f" - Reasoning: {npc_resp.reasoning}"
                        
                        npc_responses_text.append(action_text)
                
                # Create comprehensive response
                response = {
                    "success": True,
                    "event_id": event_response.event_id,
                    "response": f"Event '{event_data.get('action')}' processed successfully",
                    "npc_actions": npc_actions,  # Detailed action data
                    "npc_responses": npc_responses_text,  # Human-readable responses
                    "processing_complete": event_response.processing_complete,
                    "immediate_message": event_response.immediate_message,
                    "effects": []
                }
                
                # Add summary text for display
                if npc_responses_text:
                    response["npc_response"] = " | ".join(npc_responses_text)
                else:
                    response["npc_response"] = "No NPC actions triggered"
                
                # Add processing status
                if not event_response.processing_complete:
                    response["status"] = "Background processing in progress - some NPC responses may still be pending"
                
                logger.info(f"✅ Test event completed successfully: {response}")
                return response
                
            except Exception as e:
                logger.error(f"❌ Error testing event: {str(e)}")
                return {
                    "success": False,
                    "error": f"Failed to process event: {str(e)}",
                    "debug": {
                        "session_id": session_id,
                        "event_data": event_data,
                        "error_type": type(e).__name__
                    }
                }
        
        @app.get("/sessions/{session_id}")
        async def get_session_status(session_id: str):
            """Get status of a specific session"""
            logger.info(f"Getting status for session {session_id}")
            session = self._get_session(session_id)
            status = await session.get_session_status()
            logger.debug(f"Session status: {status}")
            return status
        
        @app.get("/sessions/{session_id}/npcs")
        async def get_all_npcs(session_id: str):
            """Get all NPCs in a session"""
            session = self._get_session(session_id)
            return {
                "session_id": session_id,
                "npcs": session.get_npc_states()
            }
        
        @app.get("/sessions/{session_id}/npcs/{npc_id}")
        async def get_npc_status(session_id: str, npc_id: str):
            """Get detailed status of a specific NPC"""
            session = self._get_session(session_id)
            npc_agent = session.get_npc(npc_id)
            
            if not npc_agent:
                raise HTTPException(status_code=404, detail=f"NPC {npc_id} not found")
            
            return {
                "session_id": session_id,
                "npc_id": npc_id,
                "status": npc_agent.get_state_snapshot(),
                "personality": npc_agent.npc_data.personality.dict(),
                "memory_summary": {
                    "short_term_count": len(npc_agent.npc_data.memory.short_term),
                    "long_term_count": len(npc_agent.npc_data.memory.long_term),
                    "recent_memories": npc_agent.npc_data.memory.short_term[-3:] if npc_agent.npc_data.memory.short_term else []
                }
            }
        
        @app.put("/sessions/{session_id}/environment")
        async def update_environment(session_id: str, environment_update: dict):
            """Update environment properties directly"""
            session = self._get_session(session_id)
            
            try:
                # Update time of day
                if "time_of_day" in environment_update:
                    session.environment_manager.world_state.environment.time_of_day = environment_update["time_of_day"]
                
                # Update weather
                if "weather" in environment_update:
                    session.environment_manager.change_weather(environment_update["weather"], 
                                                              environment_update.get("weather_reason", "Manual update"))
                
                # Update world properties
                if "world_properties" in environment_update:
                    session.environment_manager.world_state.environment.world_properties.update(
                        environment_update["world_properties"]
                    )
                
                # Add global events
                if "add_events" in environment_update:
                    for event_name in environment_update["add_events"]:
                        session.environment_manager.trigger_global_event(
                            event_name, 
                            f"Event '{event_name}' triggered via API"
                        )
                
                # Remove global events
                if "remove_events" in environment_update:
                    for event_name in environment_update["remove_events"]:
                        session.environment_manager.end_global_event(event_name)
                
                return {
                    "success": True,
                    "message": "Environment updated successfully",
                    "current_state": session.environment_manager.get_state_snapshot()
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to update environment: {str(e)}")
        
        @app.get("/sessions/{session_id}/environment")
        async def get_environment_status(session_id: str):
            """Get current environment status"""
            session = self._get_session(session_id)
            return session.environment_manager.get_state_snapshot()
        
        @app.get("/templates/session")
        async def get_session_template():
            """Get a template for creating a new session"""
            return {
                "session_config": {
                    "session_id": "example_session",
                    "game_title": "Example Game",
                    "npcs": [
                        {
                            "personality": {
                                "name": "Marcus the Blacksmith",
                                "role": "blacksmith",
                                "personality_traits": ["hardworking", "honest", "gruff"],
                                "background": "A veteran blacksmith who has served the village for 20 years",
                                "goals": ["craft the finest weapons", "train an apprentice"],
                                "relationships": {"player": "neutral"},
                                "dialogue_style": "gruff but helpful"
                            },
                            "state": {
                                "npc_id": "marcus_blacksmith",
                                "current_location": "blacksmith_shop",
                                "current_activity": "working",
                                "mood": "focused",
                                "health": 100.0,
                                "energy": 80.0
                            },
                            "memory": {
                                "short_term": [],
                                "long_term": [],
                                "relationships_memory": {}
                            }
                        }
                    ],
                    "environment": {
                        "session_id": "example_session",
                        "locations": {
                            "blacksmith_shop": {
                                "location_id": "blacksmith_shop",
                                "name": "Marcus's Blacksmith Shop",
                                "location_type": "building",
                                "description": "A busy blacksmith shop filled with the sound of hammering",
                                "connected_locations": ["town_center"],
                                "properties": {"temperature": "hot", "noise_level": "loud"},
                                "npcs_present": ["marcus_blacksmith"],
                                "items_present": []
                            }
                        },
                        "time_of_day": "morning",
                        "weather": "sunny"
                    },
                    "available_actions": [action.dict() for action in DEFAULT_ACTION_DEFINITIONS],
                    "settings": {
                        "difficulty": "normal",
                        "npc_reaction_speed": "fast"
                    }
                }
            }
        
        @app.get("/config/actions")
        async def get_action_config():
            """Get current action configuration"""
            try:
                config = self.config_loader.load_action_config()
                return config.dict()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to load action config: {str(e)}")
        
        @app.get("/config/actions/definitions")
        async def get_action_definitions():
            """Get detailed action definitions with properties for all available actions"""
            try:
                from ..models.action_models import DEFAULT_ACTION_DEFINITIONS
                from ..config.action_config import ActionProperty as ConfigActionProperty, PropertyType
                
                # Load custom actions from config
                config = self.config_loader.load_action_config()
                
                # Convert default actions to the format expected by frontend
                default_actions = []
                for action_def in DEFAULT_ACTION_DEFINITIONS:
                    if action_def.action_type in config.enabled_default_actions:
                        properties = []
                        for prop in action_def.properties:
                            # Convert validation dict to frontend format
                            validation = {}
                            if hasattr(prop, 'validation') and prop.validation:
                                validation = prop.validation
                            
                            properties.append({
                                "name": prop.name,
                                "type": prop.type,
                                "required": prop.required,
                                "description": prop.description,
                                "default": prop.default_value,
                                "validation": validation
                            })
                        
                        default_actions.append({
                            "action_id": action_def.action_type,
                            "name": action_def.action_type.capitalize(),
                            "description": action_def.description,
                            "properties": properties
                        })
                
                # Convert custom actions to frontend format
                custom_actions = []
                for custom_action in config.custom_actions:
                    properties = []
                    for prop in custom_action.properties:
                        validation = {}
                        if hasattr(prop, 'validation') and prop.validation:
                            validation = prop.validation
                        
                        properties.append({
                            "name": prop.name,
                            "type": prop.type,
                            "required": prop.required,
                            "description": prop.description,
                            "default": prop.default,
                            "validation": validation
                        })
                    
                    custom_actions.append({
                        "action_id": custom_action.action_id,
                        "name": custom_action.name,
                        "description": custom_action.description,
                        "properties": properties
                    })
                
                return {
                    "version": config.version,
                    "enabled_default_actions": config.enabled_default_actions,
                    "default_action_definitions": default_actions,
                    "custom_actions": custom_actions,
                    "action_categories": config.action_categories,
                    "global_settings": config.global_settings
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to load action definitions: {str(e)}")
        
        @app.put("/config/actions")
        async def update_action_config(config: ActionConfig):
            """Update NPC action configuration"""
            try:
                self.config_loader.save_action_config(config)
                return {"success": True, "message": "NPC action configuration updated"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to save action config: {str(e)}")
        
        @app.get("/config/player-actions")
        async def get_player_action_config():
            """Get current player action configuration"""
            try:
                config = self.config_loader.load_player_action_config()
                return config.model_dump(mode='json')
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to load player action config: {str(e)}")
        
        @app.put("/config/player-actions")
        async def update_player_action_config(config: dict):
            """Update player action configuration"""
            try:
                from npc_engine.config.player_action_config import PlayerActionConfig
                player_config = PlayerActionConfig(**config)
                self.config_loader.save_player_action_config(player_config)
                return {"success": True, "message": "Player action configuration updated"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to save player action config: {str(e)}")
        
        @app.get("/config/environment")
        async def get_environment_config():
            """Get current environment configuration"""
            try:
                config = self.config_loader.load_environment_config()
                return config.dict()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to load environment config: {str(e)}")
        
        @app.put("/config/environment")
        async def update_environment_config(config: EnvironmentConfig):
            """Update environment configuration"""
            try:
                self.config_loader.save_environment_config(config)
                return {"success": True, "message": "Environment configuration updated"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to save environment config: {str(e)}")
        
        @app.post("/config/generate-samples")
        async def generate_sample_configs():
            """Generate sample configuration files"""
            try:
                self.config_loader.create_sample_configs()
                return {
                    "success": True,
                    "message": "Sample configurations created",
                    "files": ["sample_actions.yaml", "sample_environment.yaml"]
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to create samples: {str(e)}")
        
        @app.get("/config/game/{game_name}")
        async def get_game_config(game_name: str):
            """Get complete game configuration"""
            try:
                config = self.config_loader.load_game_config(game_name)
                return config
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to load game config: {str(e)}")
        
        @app.post("/sessions/from-config/{config_name}")
        async def create_session_from_config(config_name: str, session_id: str = None):
            """Create a session from a configuration file"""
            try:
                if not session_id:
                    session_id = f"session_{int(time.time())}"
                
                if session_id in self.sessions:
                    raise HTTPException(status_code=400, detail="Session already exists")
                
                # Load configurations
                config_loader = ConfigLoader()
                
                # Load NPCs from configuration
                npcs_data = []
                try:
                    npc_config = config_loader.load_npc_config(config_name)
                    
                    # Check if NPCs are in the new instances format or old npcs format
                    npc_instances = []
                    if hasattr(npc_config, 'instances') and npc_config.instances:
                        # New format: NPCs are in instances dict
                        npc_instances = list(npc_config.instances.values())[:5]  # Limit to 5 NPCs for performance
                    elif hasattr(npc_config, 'npcs') and npc_config.npcs:
                        # Old format: NPCs are in npcs list
                        npc_instances = npc_config.npcs[:5]
                    
                    # Convert configured NPCs to NPCData objects
                    for npc_instance in npc_instances:
                        # Handle both new instance format and old npc format
                        if hasattr(npc_instance, 'properties'):
                            # New instance format
                            properties = npc_instance.properties
                            npc_id = npc_instance.id
                            name = npc_instance.name
                            description = npc_instance.description
                            is_active = properties.get("active", True)
                        else:
                            # Old format or dictionary
                            properties = getattr(npc_instance, 'properties', npc_instance)
                            npc_id = getattr(npc_instance, 'npc_id', properties.get('npc_id', f"npc_{len(npcs_data)+1}"))
                            name = getattr(npc_instance, 'name', properties.get('name', f"NPC {len(npcs_data)+1}"))
                            description = getattr(npc_instance, 'description', properties.get('description', "A village NPC"))
                            is_active = getattr(npc_instance, 'enabled', properties.get('enabled', True))
                        
                        if is_active:
                            personality_traits = properties.get("personality_traits", ["friendly", "helpful"])
                            if isinstance(personality_traits, str):
                                personality_traits = personality_traits.split(", ") if ", " in personality_traits else [personality_traits]
                            
                            # Extract skills as goals if available
                            skills = properties.get("skills", {})
                            goals = ["help visitors", "live peacefully"]
                            if "trading" in skills:
                                goals.append("trade goods")
                            if "combat" in skills and skills.get("combat", 0) > 5:
                                goals.append("protect others")
                            if "magic" in skills:
                                goals.append("study magic")
                            
                            npc_data = NPCData(
                                personality=NPCPersonality(
                                    name=name,
                                    role=properties.get("job", "villager"),
                                    personality_traits=personality_traits,
                                    background=description,
                                    goals=goals,
                                    relationships={},
                                    dialogue_style=properties.get("dialogue_style", "friendly")
                                ),
                                state=NPCState(
                                    npc_id=npc_id,
                                    current_location=properties.get("location", "village_center"),
                                    current_activity="standing",
                                    mood=properties.get("base_emotion", "neutral"),
                                    health=float(properties.get("health", 100)),
                                    energy=float(properties.get("energy", 100))
                                ),
                                memory=NPCMemory(
                                    short_term=[],
                                    long_term=[],
                                    relationships_memory={}
                                )
                            )
                            npcs_data.append(npc_data)
                except Exception as e:
                    logger.warning(f"Failed to load NPCs from config: {e}")
                
                # If no NPCs were loaded, create default demo NPC
                if not npcs_data:
                    npcs_data = [
                        NPCData(
                            personality=NPCPersonality(
                                name="Demo NPC",
                                role="villager",
                                personality_traits=["friendly", "helpful"],
                                background="A helpful NPC for testing",
                                goals=["assist players", "provide information"],
                                relationships={},
                                dialogue_style="friendly"
                            ),
                            state=NPCState(
                                npc_id="demo_npc_1",
                                current_location="village_center",
                                current_activity="standing",
                                mood="neutral",
                                health=100.0,
                                energy=100.0
                            ),
                            memory=NPCMemory(
                                short_term=[],
                                long_term=[],
                                relationships_memory={}
                            )
                        )
                    ]
                
                # Load environment from configuration
                locations = {}
                environment_time = "morning"
                environment_weather = "sunny"
                try:
                    # Try to load from sample_environment.yaml which has actual locations
                    try:
                        env_config = config_loader.load_environment_config("sample_environment.yaml")
                    except:
                        env_config = config_loader.load_environment_config()
                    
                    environment_time = env_config.default_time
                    environment_weather = env_config.default_weather
                    
                    # Create locations from environment config
                    for location_config in env_config.locations:
                        # Map location types
                        location_type = LocationType.TOWN
                        if hasattr(location_config, 'location_type'):
                            if location_config.location_type == "building":
                                location_type = LocationType.BUILDING
                            elif location_config.location_type == "outdoor":
                                location_type = LocationType.OUTDOOR
                        
                        # Get location ID and other properties
                        location_id = getattr(location_config, 'location_id', getattr(location_config, 'id', f"location_{len(locations)}"))
                        connected = getattr(location_config, 'connected_locations', [])
                        properties = getattr(location_config, 'properties', {})
                        
                        locations[location_id] = Location(
                            location_id=location_id,
                            name=location_config.name,
                            location_type=location_type,
                            description=location_config.description,
                            connected_locations=connected,
                            properties=properties,
                            npcs_present=[npc.state.npc_id for npc in npcs_data if npc.state.current_location == location_id],
                            items_present=[]
                        )
                except Exception as e:
                    logger.warning(f"Failed to load environment from config: {e}")
                
                # If no locations were loaded, create default village center
                if not locations:
                    locations = {
                        "village_center": Location(
                            location_id="village_center",
                            name="Village Center",
                            location_type=LocationType.TOWN,
                            description="The bustling center of the village",
                            connected_locations=[],
                            properties={},
                            npcs_present=[npc.state.npc_id for npc in npcs_data],
                            items_present=[]
                        )
                    }
                    
                    # Update NPC locations to village_center if they don't have a valid location
                    for npc in npcs_data:
                        if npc.state.current_location not in locations:
                            npc.state.current_location = "village_center"
                
                # Create session configuration
                session_config = SessionConfig(
                    session_id=session_id,
                    game_title=f"NPC Engine - {config_name.title()} World",
                    npcs=npcs_data,
                    environment=Environment(
                        session_id=session_id,
                        locations=locations,
                        time_of_day=environment_time,
                        weather=environment_weather,
                        game_time=0,
                        world_properties={},
                        active_events=[]
                    ),
                    available_actions=DEFAULT_ACTION_DEFINITIONS,
                    settings={}
                )
                
                # Create and start session
                session = GameSession(session_config)
                await session.start()
                
                self.sessions[session_id] = session
                
                return SessionInfo(
                    session_id=session_id,
                    game_title=session_config.game_title,
                    created_at=session.created_at,
                    last_activity=session.last_activity,
                    npc_count=len(session.npc_agents),
                    total_events=session.total_events_processed,
                    status=session.status
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to create session from config: {str(e)}")
        
        @app.get("/config/npcs", response_model=NPCConfig)
        async def get_npc_config():
            """Get current NPC configuration including schemas and instances"""
            try:
                config_loader = ConfigLoader()
                npc_config = config_loader.load_npc_config()
                return npc_config
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to load NPC config: {str(e)}")
        
        @app.put("/config/npcs", response_model=Dict[str, str])
        async def update_npc_config(config: NPCConfig):
            """Update NPC configuration"""
            try:
                config_loader = ConfigLoader()
                config_loader.save_npc_config(config)
                return {"message": "NPC configuration updated successfully"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to update NPC config: {str(e)}")
        
        @app.get("/config/npcs/schemas", response_model=List[NPCSchema])
        async def get_npc_schemas():
            """Get all available NPC schemas"""
            try:
                config_loader = ConfigLoader()
                npc_config = config_loader.load_npc_config()
                return npc_config.schemas
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to load NPC schemas: {str(e)}")
        
        @app.post("/config/npcs/schemas", response_model=Dict[str, str])
        async def add_npc_schema(schema: NPCSchema):
            """Add a new NPC schema"""
            try:
                config_loader = ConfigLoader()
                npc_config = config_loader.load_npc_config()
                
                # Check if schema already exists
                if any(s.schema_id == schema.schema_id for s in npc_config.schemas):
                    raise HTTPException(status_code=400, detail=f"Schema with ID '{schema.schema_id}' already exists")
                
                npc_config.schemas.append(schema)
                config_loader.save_npc_config(npc_config)
                return {"message": f"NPC schema '{schema.schema_id}' added successfully"}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to add NPC schema: {str(e)}")
        
        @app.put("/config/npcs/schemas/{schema_id}", response_model=Dict[str, str])
        async def update_npc_schema(schema_id: str, schema: NPCSchema):
            """Update an existing NPC schema"""
            try:
                config_loader = ConfigLoader()
                npc_config = config_loader.load_npc_config()
                
                # Find and update schema
                for i, existing_schema in enumerate(npc_config.schemas):
                    if existing_schema.schema_id == schema_id:
                        npc_config.schemas[i] = schema
                        config_loader.save_npc_config(npc_config)
                        return {"message": f"NPC schema '{schema_id}' updated successfully"}
                
                raise HTTPException(status_code=404, detail=f"Schema with ID '{schema_id}' not found")
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to update NPC schema: {str(e)}")
        
        @app.delete("/config/npcs/schemas/{schema_id}", response_model=Dict[str, str])
        async def delete_npc_schema(schema_id: str):
            """Delete an NPC schema"""
            try:
                config_loader = ConfigLoader()
                npc_config = config_loader.load_npc_config()
                
                # Check if any NPCs use this schema
                if any(npc.schema_id == schema_id for npc in npc_config.npcs):
                    raise HTTPException(status_code=400, detail=f"Cannot delete schema '{schema_id}' - NPCs are using it")
                
                # Remove schema
                npc_config.schemas = [s for s in npc_config.schemas if s.schema_id != schema_id]
                config_loader.save_npc_config(npc_config)
                return {"message": f"NPC schema '{schema_id}' deleted successfully"}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to delete NPC schema: {str(e)}")
        
        @app.get("/config/npcs/instances", response_model=List[NPCInstance])
        async def get_npc_instances():
            """Get all NPC instances"""
            try:
                config_loader = ConfigLoader()
                npc_config = config_loader.load_npc_config()
                return npc_config.npcs
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to load NPC instances: {str(e)}")
        
        @app.post("/config/npcs/instances", response_model=Dict[str, str])
        async def add_npc_instance(npc: NPCInstance):
            """Add a new NPC instance"""
            try:
                config_loader = ConfigLoader()
                npc_config = config_loader.load_npc_config()
                
                # Check if NPC ID already exists
                if any(existing_npc.npc_id == npc.npc_id for existing_npc in npc_config.npcs):
                    raise HTTPException(status_code=400, detail=f"NPC with ID '{npc.npc_id}' already exists")
                
                # Validate schema exists
                if not any(s.schema_id == npc.schema_id for s in npc_config.schemas):
                    raise HTTPException(status_code=400, detail=f"Schema '{npc.schema_id}' not found")
                
                npc_config.npcs.append(npc)
                config_loader.save_npc_config(npc_config)
                return {"message": f"NPC '{npc.npc_id}' added successfully"}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to add NPC instance: {str(e)}")
        
        @app.put("/config/npcs/instances/{npc_id}", response_model=Dict[str, str])
        async def update_npc_instance(npc_id: str, npc: NPCInstance):
            """Update an existing NPC instance"""
            try:
                config_loader = ConfigLoader()
                npc_config = config_loader.load_npc_config()
                
                # Find and update NPC
                for i, existing_npc in enumerate(npc_config.npcs):
                    if existing_npc.npc_id == npc_id:
                        # Validate schema exists
                        if not any(s.schema_id == npc.schema_id for s in npc_config.schemas):
                            raise HTTPException(status_code=400, detail=f"Schema '{npc.schema_id}' not found")
                        
                        npc_config.npcs[i] = npc
                        config_loader.save_npc_config(npc_config)
                        return {"message": f"NPC '{npc_id}' updated successfully"}
                
                raise HTTPException(status_code=404, detail=f"NPC with ID '{npc_id}' not found")
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to update NPC instance: {str(e)}")
        
        @app.delete("/config/npcs/instances/{npc_id}", response_model=Dict[str, str])
        async def delete_npc_instance(npc_id: str):
            """Delete an NPC instance"""
            try:
                config_loader = ConfigLoader()
                npc_config = config_loader.load_npc_config()
                
                # Remove NPC
                original_count = len(npc_config.npcs)
                npc_config.npcs = [npc for npc in npc_config.npcs if npc.npc_id != npc_id]
                
                if len(npc_config.npcs) == original_count:
                    raise HTTPException(status_code=404, detail=f"NPC with ID '{npc_id}' not found")
                
                config_loader.save_npc_config(npc_config)
                return {"message": f"NPC '{npc_id}' deleted successfully"}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to delete NPC instance: {str(e)}")
        
        @app.post("/config/npcs/instances/bulk", response_model=Dict[str, Any])
        async def add_bulk_npc_instances(npcs: List[NPCInstance]):
            """Add multiple NPC instances at once"""
            try:
                config_loader = ConfigLoader()
                npc_config = config_loader.load_npc_config()
                
                added_count = 0
                errors = []
                
                for npc in npcs:
                    try:
                        # Check if NPC ID already exists
                        if any(existing_npc.npc_id == npc.npc_id for existing_npc in npc_config.npcs):
                            errors.append(f"NPC with ID '{npc.npc_id}' already exists")
                            continue
                        
                        # Validate schema exists
                        if not any(s.schema_id == npc.schema_id for s in npc_config.schemas):
                            errors.append(f"NPC '{npc.npc_id}': Schema '{npc.schema_id}' not found")
                            continue
                        
                        npc_config.npcs.append(npc)
                        added_count += 1
                    except Exception as e:
                        errors.append(f"NPC '{npc.npc_id}': {str(e)}")
                
                if added_count > 0:
                    config_loader.save_npc_config(npc_config)
                
                return {
                    "message": f"Added {added_count} NPCs successfully",
                    "added_count": added_count,
                    "total_requested": len(npcs),
                    "errors": errors
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to add bulk NPC instances: {str(e)}")
        
        @app.post("/sessions/{session_id}/spawn-npcs", response_model=Dict[str, Any])
        async def spawn_npcs_in_session(session_id: str, npc_ids: Optional[List[str]] = None):
            """Spawn NPCs from configuration into a session"""
            try:
                if session_id not in self.sessions:
                    raise HTTPException(status_code=404, detail="Session not found")
                
                session = self.sessions[session_id]
                config_loader = ConfigLoader()
                npc_config = config_loader.load_npc_config()
                
                # If no specific NPC IDs provided, spawn all enabled NPCs
                npcs_to_spawn = npc_config.npcs
                if npc_ids:
                    npcs_to_spawn = [npc for npc in npc_config.npcs if npc.npc_id in npc_ids]
                
                # Filter only enabled NPCs
                npcs_to_spawn = [npc for npc in npcs_to_spawn if npc.enabled]
                
                spawned_count = 0
                errors = []
                
                for npc_instance in npcs_to_spawn:
                    try:
                        # Find the schema for this NPC
                        schema = next((s for s in npc_config.schemas if s.schema_id == npc_instance.schema_id), None)
                        if not schema:
                            errors.append(f"Schema '{npc_instance.schema_id}' not found for NPC '{npc_instance.npc_id}'")
                            continue
                        
                        # Create NPC agent with properties from configuration
                        npc_agent = NPCAgent(
                            npc_id=npc_instance.npc_id,
                            name=npc_instance.name,
                            personality=npc_instance.personality,
                            background=npc_instance.properties.get("backstory", ""),
                            initial_location=npc_instance.location
                        )
                        
                        # Set additional properties
                        for prop_name, prop_value in npc_instance.properties.items():
                            setattr(npc_agent, prop_name, prop_value)
                        
                        # Set stats
                        for stat_name, stat_value in npc_instance.stats.items():
                            setattr(npc_agent, stat_name, stat_value)
                        
                        # Add to session
                        session.npcs[npc_instance.npc_id] = npc_agent
                        spawned_count += 1
                        
                    except Exception as e:
                        errors.append(f"NPC '{npc_instance.npc_id}': {str(e)}")
                
                return {
                    "message": f"Spawned {spawned_count} NPCs in session '{session_id}'",
                    "spawned_count": spawned_count,
                    "total_requested": len(npcs_to_spawn),
                    "errors": errors
                }
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to spawn NPCs: {str(e)}")
    
    def _get_session(self, session_id: str) -> GameSession:
        """Get a session by ID or raise 404"""
        if session_id not in self.sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        return self.sessions[session_id]
    
    async def _shutdown_all_sessions(self):
        """Shutdown all active sessions"""
        for session in self.sessions.values():
            try:
                await session.stop()
            except Exception as e:
                print(f"Error stopping session: {e}")
        self.sessions.clear()
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, **kwargs):
        """Run the API server"""
        uvicorn.run(self.app, host=host, port=port, **kwargs)


# Create a default instance for easy importing
api = NPCEngineAPI()


# CLI entry point
def main():
    """Main entry point for running the API server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NPC Engine API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print(f"Starting NPC Engine API on {args.host}:{args.port}")
    api.run(host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main() 