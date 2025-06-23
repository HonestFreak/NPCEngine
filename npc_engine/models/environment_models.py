"""
Environment and game event data models
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class LocationType(str, Enum):
    """Types of locations in the game world"""
    TOWN = "town"
    BUILDING = "building"
    ROOM = "room"
    OUTDOOR = "outdoor"
    DUNGEON = "dungeon"
    SPECIAL = "special"


class Location(BaseModel):
    """Represents a location in the game world"""
    location_id: str = Field(..., description="Unique identifier for the location")
    name: str = Field(..., description="Display name of the location")
    location_type: LocationType = Field(..., description="Type of location")
    description: str = Field("", description="Description of the location")
    connected_locations: List[str] = Field(default_factory=list, description="Adjacent locations")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Location-specific properties")
    npcs_present: List[str] = Field(default_factory=list, description="NPCs currently at this location")
    items_present: List[Dict[str, Any]] = Field(default_factory=list, description="Items at this location")
    
    class Config:
        schema_extra = {
            "example": {
                "location_id": "blacksmith_shop",
                "name": "Marcus's Blacksmith Shop",
                "location_type": "building",
                "description": "A busy blacksmith shop with the sound of hammering metal",
                "connected_locations": ["town_center", "storage_room"],
                "properties": {"temperature": "hot", "noise_level": "loud"},
                "npcs_present": ["marcus_blacksmith"],
                "items_present": [{"item": "anvil", "interactable": True}]
            }
        }


class WeatherCondition(str, Enum):
    """Weather conditions that can affect the game world"""
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    STORMY = "stormy"
    FOGGY = "foggy"
    SNOWY = "snowy"


class TimeOfDay(str, Enum):
    """Time periods in the game"""
    DAWN = "dawn"
    MORNING = "morning"
    NOON = "noon"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"
    MIDNIGHT = "midnight"


class Environment(BaseModel):
    """Represents the overall game environment state"""
    session_id: str = Field(..., description="Session this environment belongs to")
    locations: Dict[str, Location] = Field(default_factory=dict, description="All locations in the game world")
    
    # Global game state
    time_of_day: TimeOfDay = Field(TimeOfDay.MORNING, description="Current time of day")
    weather: WeatherCondition = Field(WeatherCondition.SUNNY, description="Current weather")
    game_time: int = Field(0, description="Game time in minutes since start")
    
    # World properties
    world_properties: Dict[str, Any] = Field(default_factory=dict, description="Global world properties")
    active_events: List[str] = Field(default_factory=list, description="Currently active world events")
    
    # Dynamic state
    last_updated: datetime = Field(default_factory=datetime.now, description="When environment was last updated")
    
    def add_location(self, location: Location):
        """Add a new location to the environment"""
        self.locations[location.location_id] = location
    
    def get_location(self, location_id: str) -> Optional[Location]:
        """Get a location by ID"""
        return self.locations.get(location_id)
    
    def move_npc(self, npc_id: str, from_location: str, to_location: str) -> bool:
        """Move an NPC from one location to another"""
        if from_location in self.locations and to_location in self.locations:
            # Remove from old location
            if npc_id in self.locations[from_location].npcs_present:
                self.locations[from_location].npcs_present.remove(npc_id)
            
            # Add to new location
            if npc_id not in self.locations[to_location].npcs_present:
                self.locations[to_location].npcs_present.append(npc_id)
            
            return True
        return False
    
    def get_npcs_at_location(self, location_id: str) -> List[str]:
        """Get all NPCs at a specific location"""
        location = self.get_location(location_id)
        return location.npcs_present if location else []
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "game_session_123",
                "time_of_day": "morning",
                "weather": "sunny",
                "game_time": 120,
                "world_properties": {
                    "economy_state": "prosperous",
                    "conflict_level": "peaceful"
                },
                "active_events": ["festival_preparation"]
            }
        }


class EventType(str, Enum):
    """Types of events that can occur in the game"""
    PLAYER_ACTION = "player_action"
    NPC_ACTION = "npc_action"
    ENVIRONMENT_CHANGE = "environment_change"
    SYSTEM_EVENT = "system_event"
    INTERACTION = "interaction"
    COMBAT = "combat"
    DIALOGUE = "dialogue"
    QUEST_EVENT = "quest_event"


class GameEvent(BaseModel):
    """Represents an event that occurred in the game"""
    event_id: str = Field(..., description="Unique identifier for the event")
    event_type: EventType = Field(..., description="Type of event")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the event occurred")
    
    # Event participants
    initiator: str = Field(..., description="Who/what initiated the event (player, NPC ID, system)")
    target: Optional[str] = Field(None, description="Target of the event (NPC ID, location, item)")
    witnesses: List[str] = Field(default_factory=list, description="NPCs that witnessed this event")
    
    # Event details
    action: str = Field(..., description="What action occurred")
    location: str = Field(..., description="Where the event took place")
    description: str = Field("", description="Detailed description of the event")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Event-specific properties")
    
    # Effects
    environment_changes: Dict[str, Any] = Field(default_factory=dict, description="Changes to environment")
    affects_npcs: List[str] = Field(default_factory=list, description="NPCs affected by this event")
    
    class Config:
        schema_extra = {
            "example": {
                "event_id": "event_12345",
                "event_type": "player_action",
                "initiator": "player",
                "target": "marcus_blacksmith",
                "action": "speak",
                "location": "blacksmith_shop",
                "description": "Player greeted the blacksmith",
                "properties": {"message": "Hello there!"},
                "witnesses": ["apprentice_npc"],
                "affects_npcs": ["marcus_blacksmith"]
            }
        }


class WorldState(BaseModel):
    """Complete snapshot of the world state at a point in time"""
    session_id: str = Field(..., description="Session this state belongs to")
    environment: Environment = Field(..., description="Environment state")
    recent_events: List[GameEvent] = Field(default_factory=list, description="Recent events affecting the world")
    global_flags: Dict[str, bool] = Field(default_factory=dict, description="Global boolean flags")
    global_variables: Dict[str, Any] = Field(default_factory=dict, description="Global variables")
    
    def add_event(self, event: GameEvent):
        """Add a new event to the world state"""
        self.recent_events.append(event)
        # Keep only last 50 events to prevent memory bloat
        if len(self.recent_events) > 50:
            self.recent_events.pop(0)
    
    def get_events_at_location(self, location_id: str, limit: int = 10) -> List[GameEvent]:
        """Get recent events that occurred at a specific location"""
        location_events = [event for event in self.recent_events if event.location == location_id]
        return location_events[-limit:]
    
    def get_events_involving_npc(self, npc_id: str, limit: int = 10) -> List[GameEvent]:
        """Get recent events involving a specific NPC"""
        npc_events = [
            event for event in self.recent_events 
            if event.initiator == npc_id or event.target == npc_id or npc_id in event.affects_npcs
        ]
        return npc_events[-limit:] 