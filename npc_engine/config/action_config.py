"""
Action configuration system for NPC Engine
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum

class ActionTargetType(str, Enum):
    """Types of action targets"""
    NONE = "none"
    NPC = "npc"
    PLAYER = "player"
    OBJECT = "object"
    LOCATION = "location"
    ANY = "any"

class PropertyType(str, Enum):
    """Types of action properties"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"

class ActionProperty(BaseModel):
    """Configuration for an action property"""
    name: str = Field(..., description="Property name")
    type: PropertyType = Field(..., description="Property data type")
    required: bool = Field(True, description="Whether this property is required")
    default: Any = Field(None, description="Default value if not provided")
    description: str = Field("", description="Description of this property")
    validation: Dict[str, Any] = Field(default_factory=dict, description="Validation rules")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "message",
                "type": "string",
                "required": True,
                "description": "The message to speak",
                "validation": {"min_length": 1, "max_length": 500}
            }
        }

class CustomAction(BaseModel):
    """Configuration for a custom action"""
    action_id: str = Field(..., description="Unique identifier for the action")
    name: str = Field(..., description="Display name of the action")
    description: str = Field("", description="Description of what this action does")
    
    # Target configuration
    target_type: ActionTargetType = Field(ActionTargetType.NONE, description="What this action can target")
    requires_target: bool = Field(False, description="Whether this action requires a target")
    
    # Properties configuration
    properties: List[ActionProperty] = Field(default_factory=list, description="Configurable properties for this action")
    
    # Behavioral configuration
    affects_mood: bool = Field(False, description="Whether this action can affect NPC mood")
    creates_memory: bool = Field(True, description="Whether this action creates a memory")
    visibility: str = Field("public", description="Who can see this action (public, private, nearby)")
    
    # Conditions
    requirements: Dict[str, Any] = Field(default_factory=dict, description="Requirements to use this action")
    
    class Config:
        schema_extra = {
            "example": {
                "action_id": "craft_item",
                "name": "Craft Item",
                "description": "Craft an item using available materials",
                "target_type": "object",
                "requires_target": True,
                "properties": [
                    {
                        "name": "item_type",
                        "type": "string",
                        "required": True,
                        "description": "Type of item to craft",
                        "validation": {"choices": ["sword", "shield", "potion"]}
                    },
                    {
                        "name": "quality",
                        "type": "string",
                        "required": False,
                        "default": "normal",
                        "description": "Quality level of the crafted item"
                    }
                ],
                "requirements": {
                    "min_skill_level": 5,
                    "required_tools": ["hammer", "anvil"]
                }
            }
        }

class ActionConfig(BaseModel):
    """Configuration for all actions in the game"""
    version: str = Field("1.0", description="Configuration version")
    custom_actions: List[CustomAction] = Field(default_factory=list, description="Custom actions defined by the user")
    enabled_default_actions: List[str] = Field(
        default_factory=lambda: ["speak", "move", "emote", "interact", "remember"],
        description="Default actions to enable"
    )
    action_categories: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Categorization of actions"
    )
    global_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Global action system settings"
    )
    
    def get_action_by_id(self, action_id: str) -> Optional[CustomAction]:
        """Get a custom action by its ID"""
        for action in self.custom_actions:
            if action.action_id == action_id:
                return action
        return None
    
    def add_action(self, action: CustomAction) -> bool:
        """Add a new custom action"""
        if self.get_action_by_id(action.action_id):
            return False  # Action already exists
        self.custom_actions.append(action)
        return True
    
    def remove_action(self, action_id: str) -> bool:
        """Remove a custom action"""
        action = self.get_action_by_id(action_id)
        if action:
            self.custom_actions.remove(action)
            return True
        return False
    
    class Config:
        schema_extra = {
            "example": {
                "version": "1.0",
                "enabled_default_actions": ["speak", "move", "emote"],
                "custom_actions": [],
                "action_categories": {
                    "combat": ["attack", "defend", "cast_spell"],
                    "social": ["speak", "emote", "trade"],
                    "utility": ["move", "interact", "craft"]
                },
                "global_settings": {
                    "max_energy_cost": 100.0,
                    "default_cooldown": 1.0,
                    "enable_action_queue": True
                }
            }
        }

def create_default_action_config() -> ActionConfig:
    """Create a default action configuration with sample actions"""
    
    # Sample custom actions
    sample_actions = [
        CustomAction(
            action_id="craft_sword",
            name="Craft Sword",
            description="Craft a sword using available materials",
            target_type=ActionTargetType.OBJECT,
            requires_target=True,
            properties=[
                ActionProperty(
                    name="material",
                    type=PropertyType.STRING,
                    required=True,
                    description="Material to use for crafting",
                    validation={"choices": ["iron", "steel", "mithril", "adamantium"]}
                ),
                ActionProperty(
                    name="enchantment",
                    type=PropertyType.STRING,
                    required=False,
                    default="none",
                    description="Enchantment to apply to the sword",
                    validation={"choices": ["none", "fire", "ice", "lightning", "poison"]}
                ),
                ActionProperty(
                    name="quality",
                    type=PropertyType.STRING,
                    required=False,
                    default="standard",
                    description="Quality level of craftsmanship",
                    validation={"choices": ["poor", "standard", "high", "masterwork"]}
                )
            ],
            affects_mood=False,
            creates_memory=True,
            visibility="public",
            requirements={
                "skill_level": 15,
                "required_tools": ["hammer", "anvil", "forge"],
                "required_materials": ["metal_ingot"]
            }
        ),
        
        CustomAction(
            action_id="cast_fireball",
            name="Cast Fireball",
            description="Cast a magical fireball at a target",
            target_type=ActionTargetType.ANY,
            requires_target=True,
            properties=[
                ActionProperty(
                    name="power",
                    type=PropertyType.INTEGER,
                    required=False,
                    default=5,
                    description="Power level of the spell (1-10)",
                    validation={"min": 1, "max": 10}
                ),
                ActionProperty(
                    name="range",
                    type=PropertyType.FLOAT,
                    required=False,
                    default=10.0,
                    description="Range of the spell in meters",
                    validation={"min": 1.0, "max": 50.0}
                )
            ],
            affects_mood=True,
            creates_memory=True,
            visibility="public",
            requirements={
                "mana": 30,
                "spell_components": ["sulfur"],
                "spell_knowledge": ["fire_magic"]
            }
        ),
        
        CustomAction(
            action_id="trade_item",
            name="Trade Item",
            description="Trade an item with another character",
            target_type=ActionTargetType.NPC,
            requires_target=True,
            properties=[
                ActionProperty(
                    name="offered_item",
                    type=PropertyType.STRING,
                    required=True,
                    description="Item being offered for trade"
                ),
                ActionProperty(
                    name="requested_item",
                    type=PropertyType.STRING,
                    required=True,
                    description="Item being requested in return"
                ),
                ActionProperty(
                    name="negotiable",
                    type=PropertyType.BOOLEAN,
                    required=False,
                    default=True,
                    description="Whether the trade terms are negotiable"
                )
            ],
            energy_cost=5.0,
            cooldown=0.0,
            affects_mood=True,
            creates_memory=True,
            visibility="nearby",
            requirements={
                "reputation": 0
            }
        )
    ]
    
    return ActionConfig(
        version="1.0",
        custom_actions=sample_actions,
        enabled_default_actions=["speak", "move", "emote", "interact", "remember"],
        action_categories={
            "crafting": ["craft_sword", "craft_armor", "craft_potion", "repair_item"],
            "combat": ["cast_fireball", "attack", "defend", "cast_heal"],
            "social": ["speak", "emote", "trade_item", "persuade"],
            "utility": ["move", "interact", "examine", "remember"],
            "magic": ["cast_fireball", "cast_heal", "cast_teleport", "enchant_item"]
        },
        global_settings={
            "max_energy_cost": 100.0,
            "default_cooldown": 1.0,
            "enable_action_queue": True,
            "max_concurrent_actions": 1,
            "allow_action_interruption": False
        }
    ) 