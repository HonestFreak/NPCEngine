"""
Environment configuration system for NPC Engine
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class LocationConfig(BaseModel):
    """Configuration for a location"""
    location_id: str = Field(..., description="Unique identifier for the location")
    name: str = Field(..., description="Display name of the location")
    location_type: str = Field("building", description="Type of location")
    description: str = Field("", description="Description of the location")
    
    # Connections
    connected_locations: List[str] = Field(default_factory=list, description="Adjacent locations")
    
    # Properties
    properties: Dict[str, Any] = Field(default_factory=dict, description="Location-specific properties")
    
    # Available actions
    available_actions: List[str] = Field(default_factory=list, description="Actions available at this location")
    
    # Objects and NPCs
    default_objects: List[Dict[str, Any]] = Field(default_factory=list, description="Objects present by default")
    default_npcs: List[str] = Field(default_factory=list, description="NPCs that start at this location")
    
    # Environmental conditions
    lighting: str = Field("normal", description="Lighting conditions")
    temperature: str = Field("normal", description="Temperature conditions")
    noise_level: str = Field("quiet", description="Ambient noise level")
    
    class Config:
        schema_extra = {
            "example": {
                "location_id": "magic_shop",
                "name": "Mystical Artifacts Shop",
                "location_type": "building",
                "description": "A dimly lit shop filled with magical artifacts and mysterious potions",
                "connected_locations": ["town_square", "back_alley"],
                "properties": {
                    "shop_type": "magic",
                    "security_level": "high",
                    "magical_aura": "strong"
                },
                "available_actions": ["browse", "buy", "examine", "speak", "cast_spell"],
                "default_objects": [
                    {"id": "crystal_ball", "name": "Crystal Ball", "interactable": True},
                    {"id": "spell_books", "name": "Ancient Spell Books", "interactable": True}
                ],
                "default_npcs": ["wizard_shopkeeper"],
                "lighting": "dim",
                "temperature": "cool",
                "noise_level": "mystical_whispers"
            }
        }

class WeatherPattern(BaseModel):
    """Configuration for weather patterns"""
    weather_id: str = Field(..., description="Unique identifier for weather type")
    name: str = Field(..., description="Display name of weather")
    description: str = Field("", description="Description of this weather")
    
    # Effects
    visibility_modifier: float = Field(1.0, description="Visibility multiplier (0.0 - 2.0)")
    movement_modifier: float = Field(1.0, description="Movement speed multiplier")
    mood_effects: Dict[str, float] = Field(default_factory=dict, description="Mood effects on NPCs")
    
    # Transition rules
    can_transition_to: List[str] = Field(default_factory=list, description="Weather types this can change to")
    transition_probability: Dict[str, float] = Field(default_factory=dict, description="Probability of transitioning")
    
    class Config:
        schema_extra = {
            "example": {
                "weather_id": "thunderstorm",
                "name": "Thunderstorm",
                "description": "Heavy rain with lightning and thunder",
                "visibility_modifier": 0.3,
                "movement_modifier": 0.7,
                "mood_effects": {
                    "fear": 0.2,
                    "anxiety": 0.3,
                    "cozy": -0.1
                },
                "can_transition_to": ["rainy", "cloudy"],
                "transition_probability": {
                    "rainy": 0.6,
                    "cloudy": 0.3
                }
            }
        }

class TimeSchedule(BaseModel):
    """Configuration for time-based events"""
    event_name: str = Field(..., description="Name of the scheduled event")
    description: str = Field("", description="Description of the event")
    
    # Timing
    time_of_day: str = Field(..., description="When this event occurs")
    frequency: str = Field("daily", description="How often this event occurs")
    
    # Effects
    world_effects: Dict[str, Any] = Field(default_factory=dict, description="Effects on the world")
    npc_effects: Dict[str, Any] = Field(default_factory=dict, description="Effects on NPCs")
    
    class Config:
        schema_extra = {
            "example": {
                "event_name": "market_opening",
                "description": "The daily opening of the marketplace",
                "time_of_day": "morning",
                "frequency": "daily",
                "world_effects": {
                    "market_active": True,
                    "crowd_level": "busy"
                },
                "npc_effects": {
                    "merchants": {"activity": "trading", "mood_boost": 0.1},
                    "guards": {"alertness": "high"}
                }
            }
        }

class EnvironmentConfig(BaseModel):
    """Complete environment configuration"""
    version: str = Field("1.0", description="Configuration version")
    
    # Basic settings
    name: str = Field("Custom Game World", description="Name of the game world")
    description: str = Field("", description="Description of the game world")
    
    # Locations
    locations: List[LocationConfig] = Field(default_factory=list, description="All locations in the world")
    
    # Weather system
    weather_patterns: List[WeatherPattern] = Field(default_factory=list, description="Available weather patterns")
    default_weather: str = Field("sunny", description="Default weather condition")
    weather_change_frequency: float = Field(0.1, description="Probability of weather change per hour")
    
    # Time system
    time_progression_rate: float = Field(1.0, description="How fast time progresses (1.0 = real time)")
    default_time: str = Field("morning", description="Starting time of day")
    scheduled_events: List[TimeSchedule] = Field(default_factory=list, description="Time-based events")
    
    # Global properties
    world_properties: Dict[str, Any] = Field(default_factory=dict, description="Global world properties")
    
    # Rules and systems
    environmental_rules: Dict[str, Any] = Field(default_factory=dict, description="Environmental behavior rules")
    
    def get_location_by_id(self, location_id: str) -> Optional[LocationConfig]:
        """Get a location configuration by ID"""
        for location in self.locations:
            if location.location_id == location_id:
                return location
        return None
    
    def add_location(self, location: LocationConfig) -> bool:
        """Add a new location"""
        if self.get_location_by_id(location.location_id):
            return False  # Location already exists
        self.locations.append(location)
        return True
    
    def get_weather_by_id(self, weather_id: str) -> Optional[WeatherPattern]:
        """Get a weather pattern by ID"""
        for weather in self.weather_patterns:
            if weather.weather_id == weather_id:
                return weather
        return None
    
    class Config:
        schema_extra = {
            "example": {
                "version": "1.0",
                "name": "Medieval Fantasy Town",
                "description": "A bustling medieval town with magic and mystery",
                "locations": [],
                "weather_patterns": [],
                "default_weather": "sunny",
                "weather_change_frequency": 0.2,
                "time_progression_rate": 60.0,
                "default_time": "morning",
                "world_properties": {
                    "magic_level": "high",
                    "technology_level": "medieval",
                    "danger_level": "low"
                },
                "environmental_rules": {
                    "night_effects": {
                        "visibility_reduced": True,
                        "npc_energy_drain": 1.5
                    },
                    "weather_effects": {
                        "rain_mood_penalty": 0.1,
                        "sunny_mood_bonus": 0.05
                    }
                }
            }
        }

# Alias for backward compatibility
Location = LocationConfig

def create_default_environment_config() -> EnvironmentConfig:
    """Create a default environment configuration with sample locations and settings"""
    
    # Sample locations
    sample_locations = [
        LocationConfig(
            location_id="village_center",
            name="Village Center",
            location_type="outdoor",
            description="A bustling town square with a magical fountain at its center, surrounded by cobblestone paths",
            connected_locations=["blacksmith_shop", "magic_tower", "tavern", "market_square", "forest_path"],
            properties={
                "crowd_level": "moderate",
                "safety_level": "very_safe",
                "magical_aura": "mild"
            },
            available_actions=["speak", "move", "emote", "examine", "gather_information"],
            default_objects=[
                {"id": "magical_fountain", "name": "Fountain of Eternal Spring", "interactable": True},
                {"id": "notice_board", "name": "Village Notice Board", "interactable": True}
            ],
            default_npcs=["town_guard", "village_elder"],
            lighting="bright",
            temperature="pleasant",
            noise_level="moderate"
        ),
        
        LocationConfig(
            location_id="blacksmith_shop",
            name="Thorin's Smithy",
            location_type="building",
            description="A hot and noisy smithy where the master blacksmith Thorin forges legendary weapons",
            connected_locations=["village_center"],
            properties={
                "shop_type": "blacksmith",
                "skill_level": "master",
                "reputation": "excellent"
            },
            available_actions=["craft_sword", "speak", "examine", "trade_item", "repair_item"],
            default_objects=[
                {"id": "master_anvil", "name": "Ancient Dwarven Anvil", "interactable": True},
                {"id": "magical_forge", "name": "Enchanted Forge", "interactable": True},
                {"id": "weapon_rack", "name": "Display Weapon Rack", "interactable": True}
            ],
            default_npcs=["thorin_blacksmith"],
            lighting="fire_lit",
            temperature="hot",
            noise_level="loud"
        ),
        
        LocationConfig(
            location_id="magic_tower",
            name="Arcanum Spire",
            location_type="building",
            description="A tall crystalline tower humming with magical energy, home to the village's archmage",
            connected_locations=["village_center"],
            properties={
                "magical_aura": "very_strong",
                "knowledge_level": "extensive",
                "protective_wards": "active"
            },
            available_actions=["cast_fireball", "study_magic", "speak", "examine", "research_spell"],
            default_objects=[
                {"id": "crystal_orb", "name": "Scrying Crystal", "interactable": True},
                {"id": "spell_library", "name": "Ancient Tome Collection", "interactable": True},
                {"id": "alchemy_station", "name": "Alchemical Laboratory", "interactable": True}
            ],
            default_npcs=["eldara_archmage"],
            lighting="magical_glow",
            temperature="cool",
            noise_level="mystical_whispers"
        ),
        
        LocationConfig(
            location_id="tavern",
            name="The Prancing Pony",
            location_type="building",
            description="A cozy tavern filled with laughter, music, and the aroma of hearty meals",
            connected_locations=["village_center"],
            properties={
                "atmosphere": "jovial",
                "food_quality": "excellent",
                "information_hub": True
            },
            available_actions=["speak", "drink", "eat", "listen_for_rumors", "play_music"],
            default_objects=[
                {"id": "bar_counter", "name": "Polished Oak Bar", "interactable": True},
                {"id": "fireplace", "name": "Crackling Fireplace", "interactable": True},
                {"id": "bulletin_board", "name": "Quest Board", "interactable": True}
            ],
            default_npcs=["barkeep_finn", "traveling_bard"],
            lighting="warm",
            temperature="cozy",
            noise_level="cheerful_chatter"
        )
    ]
    
    # Sample weather patterns
    sample_weather = [
        WeatherPattern(
            weather_id="magical_storm",
            name="Arcane Tempest",
            description="A storm crackling with wild magical energy and rainbow lightning",
            visibility_modifier=0.4,
            movement_modifier=0.6,
            mood_effects={
                "excitement": 0.3,
                "anxiety": 0.2,
                "wonder": 0.4
            },
            can_transition_to=["partly_cloudy", "light_rain"],
            transition_probability={
                "partly_cloudy": 0.6,
                "light_rain": 0.3
            }
        ),
        
        WeatherPattern(
            weather_id="fairy_mist",
            name="Enchanted Mist",
            description="A gentle mist that sparkles with fairy dust and soft magical lights",
            visibility_modifier=0.7,
            movement_modifier=0.9,
            mood_effects={
                "serenity": 0.3,
                "mystique": 0.2,
                "calm": 0.2
            },
            can_transition_to=["sunny", "partly_cloudy"],
            transition_probability={
                "sunny": 0.5,
                "partly_cloudy": 0.4
            }
        )
    ]
    
    # Sample scheduled events
    sample_events = [
        TimeSchedule(
            event_name="morning_market",
            description="The village market comes alive with merchants and traders",
            time_of_day="morning",
            frequency="daily",
            world_effects={
                "market_active": True,
                "trade_prices": "standard",
                "crowd_level": "busy"
            },
            npc_effects={
                "merchants": {"mood_boost": 0.2, "activity": "trading"},
                "guards": {"alertness": "high"}
            }
        ),
        
        TimeSchedule(
            event_name="evening_celebration",
            description="The village gathers for evening festivities and storytelling",
            time_of_day="evening",
            frequency="daily",
            world_effects={
                "celebration_active": True,
                "tavern_busy": True
            },
            npc_effects={
                "all": {"mood_boost": 0.15, "sociability": "increased"}
            }
        )
    ]
    
    return EnvironmentConfig(
        version="1.0",
        name="Elderwood Village",
        description="A mystical village nestled in an ancient forest, where magic and nature coexist in harmony",
        locations=sample_locations,
        weather_patterns=sample_weather,
        default_weather="partly_cloudy",
        weather_change_frequency=0.15,
        time_progression_rate=60.0,
        default_time="morning",
        scheduled_events=sample_events,
        world_properties={
            "magic_level": "high",
            "technology_level": "medieval_fantasy",
            "danger_level": "low",
            "political_system": "village_council",
            "economy_type": "barter_and_coin",
            "dominant_religion": "nature_worship",
            "main_language": "Common",
            "literacy_rate": "moderate"
        },
        environmental_rules={
            "night_effects": {
                "visibility_reduced": True,
                "npc_energy_drain": 1.2,
                "magical_activity": "increased",
                "creature_spawns": "nocturnal_only"
            },
            "weather_effects": {
                "rain_mood_penalty": 0.1,
                "sunny_mood_bonus": 0.05,
                "storm_fear_factor": 0.2,
                "snow_movement_penalty": 0.3
            },
            "seasonal_changes": {
                "spring": {"growth_rate": "increased", "mood_modifier": 0.1},
                "summer": {"energy_bonus": 0.1, "heat_effects": True},
                "autumn": {"harvest_season": True, "preparation_mood": 0.05},
                "winter": {"cold_effects": True, "indoor_preference": 0.3}
            }
        }
    ) 