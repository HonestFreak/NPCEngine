"""
Player Action Configuration Module

This module handles the configuration of actions that players can perform in the game.
Player actions are different from NPC actions in that they are typically triggered directly
by player input rather than AI decision-making.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from npc_engine.config.action_config import ActionProperty, PropertyType

class PlayerActionConfig(BaseModel):
    """Configuration for player actions"""
    version: str = Field("1.0", description="Configuration version")
    player_actions: List['PlayerAction'] = Field(default_factory=list, description="Custom player actions")
    enabled_default_player_actions: List[str] = Field(
        default_factory=lambda: ["inspect", "use_item", "attack", "defend", "run"],
        description="List of default player action IDs that are enabled"
    )
    global_settings: Dict[str, Any] = Field(default_factory=dict, description="Global player action settings")
    
    class Config:
        json_encoders = {
            PropertyType: lambda v: v.value
        }
    
    def add_player_action(self, action: 'PlayerAction') -> bool:
        """Add a new player action if it doesn't already exist"""
        if any(a.action_id == action.action_id for a in self.player_actions):
            return False
        self.player_actions.append(action)
        return True
    
    def remove_player_action(self, action_id: str) -> bool:
        """Remove a player action by ID"""
        original_length = len(self.player_actions)
        self.player_actions = [a for a in self.player_actions if a.action_id != action_id]
        return len(self.player_actions) < original_length
    
    def get_player_action(self, action_id: str) -> Optional['PlayerAction']:
        """Get a player action by ID"""
        return next((a for a in self.player_actions if a.action_id == action_id), None)
    
    def update_player_action(self, action_id: str, updated_action: 'PlayerAction') -> bool:
        """Update an existing player action"""
        for i, action in enumerate(self.player_actions):
            if action.action_id == action_id:
                self.player_actions[i] = updated_action
                return True
        return False

class PlayerAction(BaseModel):
    """Represents a single player action"""
    # Basic action information
    action_id: str = Field(..., description="Unique identifier for this action")
    name: str = Field(..., description="Human-readable name for this action")
    description: str = Field("", description="Detailed description of what this action does")
    
    # Targeting and execution
    target_type: str = Field("none", description="Type of target this action requires")
    requires_target: bool = Field(False, description="Whether this action requires a target to execute")
    
    # Properties configuration
    properties: List[ActionProperty] = Field(default_factory=list, description="Configurable properties for this action")
    
    # Behavioral configuration
    affects_mood: bool = Field(False, description="Whether this action affects NPC mood when used")
    creates_memory: bool = Field(True, description="Whether this action creates memories for NPCs")
    visibility: str = Field("public", description="Visibility of this action (public, private, hidden)")
    requirements: Dict[str, Any] = Field(default_factory=dict, description="Requirements to use this action")
    
    # Player-specific fields
    category: str = Field("player", description="Action category (always 'player' for player actions)")
    cooldown: float = Field(0.0, description="Cooldown in seconds before action can be used again")
    cost: Dict[str, float] = Field(default_factory=dict, description="Resource costs (mana, stamina, etc.)")
    
    class Config:
        json_encoders = {
            PropertyType: lambda v: v.value
        }
        
        schema_extra = {
            "example": {
                "action_id": "player_fireball",
                "name": "Cast Fireball",
                "description": "Launch a magical fireball at the target",
                "target_type": "enemy",
                "requires_target": True,
                "properties": [
                    {
                        "name": "damage",
                        "type": "integer",
                        "required": True,
                        "default": 25,
                        "description": "Damage dealt by the fireball",
                        "validation": {
                            "min": 10,
                            "max": 100
                        }
                    },
                    {
                        "name": "element",
                        "type": "string",
                        "required": False,
                        "default": "fire",
                        "description": "Elemental type of the spell",
                        "validation": {
                            "options": ["fire", "ice", "lightning"]
                        }
                    }
                ],
                "affects_mood": True,
                "creates_memory": True,
                "visibility": "public",
                "requirements": {
                    "level": 5,
                    "class": "mage"
                },
                "category": "player",
                "cooldown": 3.0,
                "cost": {
                    "mana": 20
                }
            }
        }

def create_default_player_action_config() -> PlayerActionConfig:
    """Create a default player action configuration with sample actions"""
    
    # Sample player actions
    sample_actions = [
        PlayerAction(
            action_id="player_inspect",
            name="Inspect",
            description="Examine an object or character in detail",
            target_type="any",
            requires_target=True,
            properties=[
                ActionProperty(
                    name="focus_area",
                    type=PropertyType.STRING,
                    required=False,
                    default="general",
                    description="What aspect to focus on when inspecting",
                    validation={
                        "options": ["general", "combat", "magical", "historical"]
                    }
                )
            ],
            affects_mood=False,
            creates_memory=True,
            visibility="public",
            requirements={},
            category="player",
            cooldown=1.0,
            cost={}
        ),
        PlayerAction(
            action_id="player_attack",
            name="Attack",
            description="Perform a basic attack on a target",
            target_type="enemy",
            requires_target=True,
            properties=[
                ActionProperty(
                    name="attack_type",
                    type=PropertyType.STRING,
                    required=False,
                    default="melee",
                    description="Type of attack to perform",
                    validation={
                        "options": ["melee", "ranged", "special"]
                    }
                ),
                ActionProperty(
                    name="power",
                    type=PropertyType.INTEGER,
                    required=False,
                    default=10,
                    description="Power level of the attack",
                    validation={
                        "min": 1,
                        "max": 100
                    }
                )
            ],
            affects_mood=True,
            creates_memory=True,
            visibility="public",
            requirements={},
            category="player",
            cooldown=2.0,
            cost={"stamina": 5}
        )
    ]
    
    return PlayerActionConfig(
        version="1.0",
        player_actions=sample_actions,
        enabled_default_player_actions=["inspect", "use_item", "attack", "defend", "run"],
        global_settings={
            "allow_custom_actions": True,
            "max_actions_per_turn": 3,
            "action_queue_size": 10
        }
    )

# For backwards compatibility
Config = PlayerActionConfig 