"""
Action System for managing available actions and their execution
"""

from typing import Dict, List, Any, Optional
from ..models.action_models import ActionDefinition, Action, ActionResult, ActionType, DEFAULT_ACTION_DEFINITIONS




class ActionSystem:
    """
    Manages the available actions that NPCs can perform
    
    Responsibilities:
    - Validate action definitions
    - Check if actions can be performed
    - Process action results
    """
    
    def __init__(self, available_actions: List[ActionDefinition] = None):
        self.available_actions: Dict[str, ActionDefinition] = {}
        
        # Load default or custom actions
        actions_to_load = available_actions or DEFAULT_ACTION_DEFINITIONS
        for action_def in actions_to_load:
            self.add_action_definition(action_def)
    
    def add_action_definition(self, action_def: ActionDefinition) -> bool:
        """Add a new action definition"""
        try:
            self.available_actions[action_def.action_type] = action_def
            return True
        except Exception:
            return False
    
    def get_action_definition(self, action_type: str) -> Optional[ActionDefinition]:
        """Get action definition by type"""
        return self.available_actions.get(action_type)
    
    def get_all_actions(self) -> Dict[str, ActionDefinition]:
        """Get all available action definitions"""
        return self.available_actions.copy()
    
    def validate_action(self, action: Action) -> tuple[bool, str]:
        """Validate if an action can be performed"""
        action_def = self.get_action_definition(action.action_type)
        
        if not action_def:
            return False, f"Unknown action type: {action.action_type}"
        
        # Check required properties
        for prop in action_def.properties:
            if prop.required and prop.name not in action.properties:
                return False, f"Missing required property: {prop.name}"
        
        # Validate property types and values
        for prop_name, prop_value in action.properties.items():
            prop_def = next((p for p in action_def.properties if p.name == prop_name), None)
            if prop_def:
                if not self._validate_property(prop_value, prop_def):
                    return False, f"Invalid value for property {prop_name}"
        
        return True, "Valid"
    
    def _validate_property(self, value: Any, prop_def) -> bool:
        """Validate property value against definition"""
        # Type validation
        type_mapping = {
            "string": str,
            "int": int,
            "integer": int,
            "float": float,
            "bool": bool,
            "boolean": bool,
            "list": list,
            "dict": dict
        }
        
        expected_type = type_mapping.get(prop_def.type)
        if expected_type and not isinstance(value, expected_type):
            return False
        
        # Validation rules
        if prop_def.validation:
            # Check choices/options
            if "options" in prop_def.validation:
                if value not in prop_def.validation["options"]:
                    return False
            
            # Check numeric ranges
            if "min" in prop_def.validation and value < prop_def.validation["min"]:
                return False
            if "max" in prop_def.validation and value > prop_def.validation["max"]:
                return False
            
            # Check string length
            if "max_length" in prop_def.validation and isinstance(value, str):
                if len(value) > prop_def.validation["max_length"]:
                    return False
        
        return True
    
    def can_perform_action(self, action: Action) -> tuple[bool, str]:
        """Check if an action can be performed (simplified)"""
        return self.validate_action(action)
    
    def get_actions_for_category(self, category: str) -> List[ActionDefinition]:
        """Get actions by category (e.g., 'social', 'movement', 'utility')"""
        category_mapping = {
            "social": ["speak", "emote"],
            "movement": ["move"],
            "utility": ["wait", "interact"],
            "all": list(self.available_actions.keys())
        }
        
        action_types = category_mapping.get(category, [])
        return [self.available_actions[action_type] for action_type in action_types 
                if action_type in self.available_actions]
 