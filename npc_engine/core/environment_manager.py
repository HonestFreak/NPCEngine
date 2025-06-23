"""
Environment Manager for handling game world state
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import uuid

from ..models.environment_models import Environment, Location, GameEvent, WorldState, EventType
from ..models.npc_models import NPCData


class EnvironmentManager:
    """
    Manages the game world environment, locations, and global state
    
    Responsibilities:
    - Track all locations and their properties
    - Manage NPCs positions within the world
    - Handle environment changes (weather, time, events)
    - Coordinate global game state
    - Process environment-level events
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.world_state = WorldState(
            session_id=session_id,
            environment=Environment(session_id=session_id),
            recent_events=[],
            global_flags={},
            global_variables={}
        )
        
        # Track time progression
        self.last_time_update = datetime.now()
        self.time_progression_rate = 60  # 1 real minute = 60 game minutes
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        self._running = False
    
    async def start_background_processing(self):
        """Start background tasks for environment management"""
        if self._running:
            return
        
        self._running = True
        
        # Start time progression
        self._background_tasks.append(
            asyncio.create_task(self._time_progression_loop())
        )
        
        # Start environment updates
        self._background_tasks.append(
            asyncio.create_task(self._environment_update_loop())
        )
    
    async def stop_background_processing(self):
        """Stop all background processing"""
        self._running = False
        
        for task in self._background_tasks:
            task.cancel()
        
        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        self._background_tasks.clear()
    
    def add_location(self, location: Location) -> bool:
        """Add a new location to the environment"""
        try:
            self.world_state.environment.add_location(location)
            return True
        except Exception:
            return False
    
    def get_location(self, location_id: str) -> Optional[Location]:
        """Get a location by ID"""
        return self.world_state.environment.get_location(location_id)
    
    def get_all_locations(self) -> Dict[str, Location]:
        """Get all locations in the environment"""
        return self.world_state.environment.locations
    
    def move_npc(self, npc_id: str, from_location: str, to_location: str) -> bool:
        """Move an NPC from one location to another"""
        success = self.world_state.environment.move_npc(npc_id, from_location, to_location)
        
        if success:
            # Create movement event
            event = GameEvent(
                event_id=str(uuid.uuid4()),
                event_type=EventType.NPC_ACTION,
                initiator=npc_id,
                action="move",
                location=to_location,
                description=f"{npc_id} moved from {from_location} to {to_location}",
                properties={"from": from_location, "to": to_location}
            )
            self.add_event(event)
        
        return success
    
    def get_npcs_at_location(self, location_id: str) -> List[str]:
        """Get all NPCs at a specific location"""
        return self.world_state.environment.get_npcs_at_location(location_id)
    
    def get_nearby_npcs(self, npc_id: str, max_distance: int = 1) -> List[str]:
        """Get NPCs near the specified NPC within max_distance"""
        # Find the NPC's current location
        npc_location = None
        for location_id, location in self.world_state.environment.locations.items():
            if npc_id in location.npcs_present:
                npc_location = location_id
                break
        
        if not npc_location:
            return []
        
        nearby_npcs = []
        
        # Check current location
        current_location = self.get_location(npc_location)
        if current_location:
            nearby_npcs.extend([n for n in current_location.npcs_present if n != npc_id])
            
            # Check connected locations if max_distance > 0
            if max_distance > 0:
                for connected_id in current_location.connected_locations:
                    connected_location = self.get_location(connected_id)
                    if connected_location:
                        nearby_npcs.extend(connected_location.npcs_present)
        
        return list(set(nearby_npcs))  # Remove duplicates
    
    def add_event(self, event: GameEvent):
        """Add a new event to the world state"""
        self.world_state.add_event(event)
        
        # Check if this event triggers any environment changes
        self._process_event_effects(event)
    
    def get_recent_events(self, limit: int = 20) -> List[GameEvent]:
        """Get recent events from the world"""
        return self.world_state.recent_events[-limit:]
    
    def get_events_at_location(self, location_id: str, limit: int = 10) -> List[GameEvent]:
        """Get recent events at a specific location"""
        return self.world_state.get_events_at_location(location_id, limit)
    
    def get_events_involving_npc(self, npc_id: str, limit: int = 10) -> List[GameEvent]:
        """Get recent events involving a specific NPC"""
        return self.world_state.get_events_involving_npc(npc_id, limit)
    
    def set_global_flag(self, flag_name: str, value: bool):
        """Set a global boolean flag"""
        self.world_state.global_flags[flag_name] = value
    
    def get_global_flag(self, flag_name: str, default: bool = False) -> bool:
        """Get a global boolean flag"""
        return self.world_state.global_flags.get(flag_name, default)
    
    def set_global_variable(self, var_name: str, value: Any):
        """Set a global variable"""
        self.world_state.global_variables[var_name] = value
    
    def get_global_variable(self, var_name: str, default: Any = None) -> Any:
        """Get a global variable"""
        return self.world_state.global_variables.get(var_name, default)
    
    def update_time_of_day(self):
        """Update the time of day based on elapsed time"""
        now = datetime.now()
        elapsed_real_time = (now - self.last_time_update).total_seconds()
        elapsed_game_time = elapsed_real_time * self.time_progression_rate
        
        # Update game time in minutes
        self.world_state.environment.game_time += int(elapsed_game_time / 60)
        
        # Update time of day based on game time
        hours_in_day = 24
        minutes_per_hour = 60
        total_minutes_in_day = hours_in_day * minutes_per_hour
        
        current_minute = self.world_state.environment.game_time % total_minutes_in_day
        current_hour = current_minute // minutes_per_hour
        
        # Map hours to time periods
        if 5 <= current_hour < 7:
            new_time = "dawn"
        elif 7 <= current_hour < 12:
            new_time = "morning"
        elif 12 <= current_hour < 13:
            new_time = "noon"
        elif 13 <= current_hour < 18:
            new_time = "afternoon"
        elif 18 <= current_hour < 21:
            new_time = "evening"
        elif 21 <= current_hour < 24:
            new_time = "night"
        else:  # 0 <= current_hour < 5
            new_time = "midnight"
        
        old_time = self.world_state.environment.time_of_day
        if old_time != new_time:
            self.world_state.environment.time_of_day = new_time
            
            # Create time change event
            event = GameEvent(
                event_id=str(uuid.uuid4()),
                event_type=EventType.ENVIRONMENT_CHANGE,
                initiator="system",
                action="time_change",
                location="global",
                description=f"Time changed from {old_time} to {new_time}",
                properties={"from": old_time, "to": new_time, "game_time": self.world_state.environment.game_time}
            )
            self.add_event(event)
        
        self.last_time_update = now
    
    def change_weather(self, new_weather: str, reason: str = ""):
        """Change the weather conditions"""
        old_weather = self.world_state.environment.weather
        if old_weather != new_weather:
            self.world_state.environment.weather = new_weather
            
            # Create weather change event
            event = GameEvent(
                event_id=str(uuid.uuid4()),
                event_type=EventType.ENVIRONMENT_CHANGE,
                initiator="system",
                action="weather_change",
                location="global",
                description=f"Weather changed from {old_weather} to {new_weather}. {reason}",
                properties={"from": old_weather, "to": new_weather, "reason": reason}
            )
            self.add_event(event)
    
    def trigger_global_event(self, event_name: str, description: str, properties: Dict[str, Any] = None):
        """Trigger a global event that affects the entire world"""
        self.world_state.environment.active_events.append(event_name)
        
        event = GameEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.SYSTEM_EVENT,
            initiator="system",
            action="global_event",
            location="global",
            description=description,
            properties=properties or {}
        )
        self.add_event(event)
    
    def end_global_event(self, event_name: str):
        """End a global event"""
        if event_name in self.world_state.environment.active_events:
            self.world_state.environment.active_events.remove(event_name)
            
            event = GameEvent(
                event_id=str(uuid.uuid4()),
                event_type=EventType.SYSTEM_EVENT,
                initiator="system",
                action="global_event_end",
                location="global",
                description=f"Global event '{event_name}' has ended",
                properties={"event_name": event_name}
            )
            self.add_event(event)
    
    def get_environment_context(self, location_id: str = None) -> Dict[str, Any]:
        """Get contextual information about the environment"""
        context = {
            "time_of_day": self.world_state.environment.time_of_day,
            "weather": self.world_state.environment.weather,
            "game_time": self.world_state.environment.game_time,
            "active_events": self.world_state.environment.active_events.copy(),
            "world_properties": self.world_state.environment.world_properties.copy()
        }
        
        if location_id:
            location = self.get_location(location_id)
            if location:
                context["location"] = {
                    "name": location.name,
                    "type": location.location_type,
                    "description": location.description,
                    "properties": location.properties.copy(),
                    "npcs_present": location.npcs_present.copy(),
                    "connected_locations": location.connected_locations.copy()
                }
        
        return context
    
    def _process_event_effects(self, event: GameEvent):
        """Process any environmental effects from an event"""
        # Apply environment changes from the event
        for key, value in event.environment_changes.items():
            if hasattr(self.world_state.environment, key):
                setattr(self.world_state.environment, key, value)
            else:
                # Store in world properties
                self.world_state.environment.world_properties[key] = value
    
    async def _time_progression_loop(self):
        """Background task for time progression"""
        while self._running:
            try:
                self.update_time_of_day()
                await asyncio.sleep(60)  # Update every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in time progression: {e}")
                await asyncio.sleep(60)
    
    async def _environment_update_loop(self):
        """Background task for environment updates"""
        while self._running:
            try:
                # Perform periodic environment maintenance
                await self._perform_environment_maintenance()
                await asyncio.sleep(300)  # Update every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in environment updates: {e}")
                await asyncio.sleep(300)
    
    async def _perform_environment_maintenance(self):
        """Perform periodic environment maintenance tasks"""
        # Clean up old events (keep only last 100)
        if len(self.world_state.recent_events) > 100:
            self.world_state.recent_events = self.world_state.recent_events[-100:]
        
        # Update environment timestamp
        self.world_state.environment.last_updated = datetime.now()
        
        # Check for automatic weather changes (simple example)
        if len(self.world_state.recent_events) > 0:
            recent_weather_events = [
                e for e in self.world_state.recent_events[-10:] 
                if e.action == "weather_change"
            ]
            
            # If no weather change in recent events, occasionally change weather
            if not recent_weather_events and len(self.world_state.recent_events) % 20 == 0:
                import random
                weather_options = ["sunny", "cloudy", "rainy"]
                current_weather = self.world_state.environment.weather
                new_weather = random.choice([w for w in weather_options if w != current_weather])
                self.change_weather(new_weather, "Natural weather change")
    
    def get_state_snapshot(self) -> Dict[str, Any]:
        """Get a complete snapshot of the environment state"""
        return {
            "session_id": self.session_id,
            "environment": {
                "time_of_day": self.world_state.environment.time_of_day,
                "weather": self.world_state.environment.weather,
                "game_time": self.world_state.environment.game_time,
                "active_events": self.world_state.environment.active_events,
                "world_properties": self.world_state.environment.world_properties,
                "location_count": len(self.world_state.environment.locations)
            },
            "recent_events_count": len(self.world_state.recent_events),
            "global_flags": self.world_state.global_flags,
            "global_variables": self.world_state.global_variables,
            "last_updated": self.world_state.environment.last_updated.isoformat()
        } 