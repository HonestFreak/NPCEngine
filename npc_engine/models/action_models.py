"""
Action system data models
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class ActionType(str, Enum):
    """Predefined action types for NPCs"""
    SPEAK = "speak"
    MOVE = "move"
    INTERACT = "interact"
    ATTACK = "attack"
    USE_ITEM = "use_item"
    GIVE_ITEM = "give_item"
    TAKE_ITEM = "take_item"
    EMOTE = "emote"
    WAIT = "wait"
    FOLLOW = "follow"
    TRADE = "trade"
    FLEE = "flee"
    INVESTIGATE = "investigate"
    WORK = "work"
    REST = "rest"
    REMEMBER_EVENT = "remember_event"
    CUSTOM = "custom"  # For game-specific actions


class ActionProperty(BaseModel):
    """Defines properties for actions"""
    name: str = Field(..., description="Property name")
    type: str = Field(..., description="Property type (string, int, float, bool, list, dict)")
    required: bool = Field(True, description="Whether this property is required")
    description: str = Field("", description="Description of what this property does")
    default_value: Any = Field(None, description="Default value if not provided")
    validation: Optional[Dict[str, Any]] = Field(None, description="Validation rules (min, max, options, etc.)")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "message",
                "type": "string",
                "required": True,
                "description": "The message to speak",
                "validation": {"max_length": 500}
            }
        }


class ActionDefinition(BaseModel):
    """Defines what actions are available and their properties"""
    action_type: ActionType = Field(..., description="Type of action")
    properties: List[ActionProperty] = Field(default_factory=list, description="Properties this action requires")
    description: str = Field("", description="Description of what this action does")
    preconditions: List[str] = Field(default_factory=list, description="Conditions that must be met to perform action")
    examples: List[str] = Field(default_factory=list, description="Example usage of this action")
    
    class Config:
        schema_extra = {
            "example": {
                "action_type": "speak",
                "properties": [
                    {
                        "name": "message",
                        "type": "string",
                        "required": True,
                        "description": "What to say"
                    },
                    {
                        "name": "tone",
                        "type": "string", 
                        "required": False,
                        "description": "Tone of voice",
                        "default_value": "neutral"
                    }
                ],
                "description": "Makes the NPC speak a message",
                "cooldown": 1.0,
                "energy_cost": 1.0
            }
        }


class TargetType(str, Enum):
    """Types of targets for actions"""
    PLAYER = "player"
    NPC = "npc"
    LOCATION = "location"
    ITEM = "item"
    OBJECT = "object"
    SELF = "self"
    AREA = "area"
    NONE = "none"


class Action(BaseModel):
    """Represents an action to be performed by an NPC"""
    action_type: ActionType = Field(..., description="Type of action to perform")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Action-specific properties")
    target: Optional[str] = Field(None, description="Target of the action (NPC ID, location, item, etc.)")
    target_type: Optional[TargetType] = Field(None, description="Type of target this action affects")
    priority: int = Field(1, description="Priority level (1=low, 10=high)")
    sequence_number: int = Field(1, description="Sequence number for parallel/sequential execution (same number = parallel)")
    reasoning: str = Field("", description="Why the NPC chose this action")


class ActionSequence(BaseModel):
    """Represents a sequence of actions to be performed with parallel/sequential execution"""
    actions: List[Action] = Field(..., description="List of actions to perform (sequence_number determines order)")
    sequence_name: str = Field("", description="Name/description of this action sequence")
    reasoning: str = Field("", description="Why this sequence of actions was chosen")
    
    class Config:
        schema_extra = {
            "example": {
                "actions": [
                    {
                        "action_type": "move",
                        "properties": {"destination": "kitchen"},
                        "target": "kitchen",
                        "target_type": "location",
                        "sequence_number": 1,
                        "reasoning": "Need to go to kitchen first"
                    },
                    {
                        "action_type": "speak",
                        "properties": {"message": "I'll cook you something special!"},
                        "sequence_number": 2,
                        "reasoning": "Tell customer about cooking"
                    },
                    {
                        "action_type": "interact",
                        "properties": {"interaction_type": "cook", "item": "soup"},
                        "target": "stove",
                        "target_type": "object",
                        "sequence_number": 2,
                        "reasoning": "Cook while speaking (parallel action)"
                    }
                ],
                "sequence_name": "Cook soup for customer",
                "reasoning": "Player asked for soup, move first then cook and speak simultaneously"
            }
        }
    
    class Config:
        schema_extra = {
            "example": {
                "action_type": "speak",
                "properties": {
                    "message": "Welcome to my shop, traveler!",
                    "tone": "friendly"
                },
                "target_type": "player",
                "priority": 5,
                "sequence_number": 1,
                "reasoning": "Player just entered my shop, should greet them"
            }
        }


class ActionResult(BaseModel):
    """Result of an action execution"""
    success: bool = Field(..., description="Whether the action was successful")
    action: Action = Field(..., description="The action that was performed")
    npc_id: str = Field(..., description="ID of NPC that performed the action")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the action was performed")
    
    # Results
    message: Optional[str] = Field(None, description="Message to display to players/frontend")
    state_changes: Dict[str, Any] = Field(default_factory=dict, description="Changes to NPC state")
    environment_changes: Dict[str, Any] = Field(default_factory=dict, description="Changes to environment")
    side_effects: List[Dict[str, Any]] = Field(default_factory=list, description="Additional effects triggered")
    
    # Error handling
    error_message: Optional[str] = Field(None, description="Error message if action failed")
    retry_allowed: bool = Field(True, description="Whether this action can be retried")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "action": {
                    "action_type": "speak",
                    "properties": {"message": "Welcome to my shop!"},

                },
                "npc_id": "marcus_blacksmith",
                "message": "Marcus says: 'Welcome to my shop!'",
                "state_changes": {"mood": "friendly"},
                "environment_changes": {},
                "side_effects": []
            }
        }


class ActionQueue(BaseModel):
    """Queue of actions for an NPC to perform"""
    npc_id: str = Field(..., description="NPC this queue belongs to")
    actions: List[Action] = Field(default_factory=list, description="Queued actions")
    current_action: Optional[Action] = Field(None, description="Currently executing action")
    max_queue_size: int = Field(10, description="Maximum number of queued actions")
    
    def add_action(self, action: Action) -> bool:
        """Add an action to the queue"""
        if len(self.actions) >= self.max_queue_size:
            return False
        
        # Insert based on priority (higher priority first)
        inserted = False
        for i, queued_action in enumerate(self.actions):
            if action.priority > queued_action.priority:
                self.actions.insert(i, action)
                inserted = True
                break
        
        if not inserted:
            self.actions.append(action)
        
        return True
    
    def get_next_action(self) -> Optional[Action]:
        """Get the next action to execute"""
        if self.actions:
            return self.actions.pop(0)
        return None
    
    def clear_queue(self):
        """Clear all queued actions"""
        self.actions.clear()
        self.current_action = None


# Predefined action definitions for common game actions
DEFAULT_ACTION_DEFINITIONS = [
    ActionDefinition(
        action_type=ActionType.SPEAK,
        properties=[
            ActionProperty(
                name="message", 
                type="string", 
                required=True, 
                description="What to say to the target",
                validation={"max_length": 500}
            ),
            ActionProperty(
                name="tone", 
                type="string", 
                required=False, 
                description="Tone of voice: neutral, friendly, angry, excited, sad, mysterious, formal, casual",
                default_value="neutral",
                validation={"options": ["neutral", "friendly", "angry", "excited", "sad", "mysterious", "formal", "casual"]}
            ),

        ],
        description="Makes the NPC speak a message to someone",
        examples=[
            "Greet a customer: message='Welcome to my shop!', tone='friendly'",
            "Warn someone: message='Be careful out there!', tone='concerned'"
        ]
    ),
    ActionDefinition(
        action_type=ActionType.MOVE,
        properties=[
            ActionProperty(
                name="destination", 
                type="string", 
                required=True, 
                description="Location name to move to"
            ),
            ActionProperty(
                name="movement_type", 
                type="string", 
                required=False, 
                description="How to move: walk, run, sneak, rush",
                default_value="walk",
                validation={"options": ["walk", "run", "sneak", "rush"]}
            ),
            ActionProperty(
                name="reason",
                type="string",
                required=False,
                description="Why you're moving there",
                default_value=""
            )
        ],
        description="Moves the NPC to a different location",
        examples=[
            "Go to kitchen: destination='kitchen', movement_type='walk', reason='to prepare food'",
            "Rush to help: destination='town_square', movement_type='run', reason='emergency'"
        ]
    ),
    ActionDefinition(
        action_type=ActionType.EMOTE,
        properties=[
            ActionProperty(
                name="emotion", 
                type="string", 
                required=True, 
                description="Emotion to express: happy, sad, angry, excited, curious, confused, surprised, worried, relieved, proud",
                validation={"options": ["happy", "sad", "angry", "excited", "curious", "confused", "surprised", "worried", "relieved", "proud"]}
            ),
            ActionProperty(
                name="intensity", 
                type="int", 
                required=False, 
                description="How intense the emotion is (1=subtle, 10=very intense)",
                default_value=5,
                validation={"min": 1, "max": 10}
            )
        ],
        description="Makes the NPC visibly express an emotion",
        examples=[
            "Show happiness: emotion='happy', intensity=7",
            "Look confused: emotion='confused', intensity=4"
        ]
    ),
    ActionDefinition(
        action_type=ActionType.INTERACT,
        properties=[
            ActionProperty(
                name="interaction_type", 
                type="string", 
                required=True, 
                description="How to interact: use, examine, take, give, open, close, activate, repair, clean, craft"
            ),
            ActionProperty(
                name="item",
                type="string",
                required=False,
                description="Item to use in the interaction (if applicable)",
                default_value=""
            )
        ],
        description="Makes the NPC interact with objects, items, or perform actions",
        examples=[
            "Use forge: interaction_type='use', item='iron_ore'",
            "Examine book: interaction_type='examine'"
        ]
    ),
    ActionDefinition(
        action_type=ActionType.WAIT,
        properties=[
            ActionProperty(
                name="duration", 
                type="float", 
                required=False, 
                description="How long to wait in seconds",
                default_value=1.0,
                validation={"min": 0.1, "max": 10.0}
            ),
            ActionProperty(
                name="reason",
                type="string",
                required=False,
                description="Why you're waiting",
                default_value="thinking"
            )
        ],
        description="Makes the NPC pause and wait",
        examples=[
            "Think about response: duration=2.0, reason='considering your request'",
            "Brief pause: duration=0.5, reason='collecting thoughts'"
        ]
    )
] 