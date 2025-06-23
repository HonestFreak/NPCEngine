"""
Configuration loader for NPC Engine
"""

import json
import yaml
import os
from typing import Dict, Any, Optional, Union
from pathlib import Path

from .action_config import ActionConfig
from .environment_config import EnvironmentConfig
from .npc_config import NPCConfig
from .player_action_config import PlayerActionConfig

class ConfigLoader:
    """Loader for NPC Engine configuration files"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
    
    def load_action_config(self, filename: str = "actions.yaml") -> ActionConfig:
        """Load action configuration from file"""
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            # Create default config
            default_config = ActionConfig()
            self.save_action_config(default_config, filename)
            return default_config
        
        data = self._load_file(config_path)
        return ActionConfig(**data)
    
    def save_action_config(self, config: ActionConfig, filename: str = "actions.yaml"):
        """Save action configuration to file"""
        config_path = self.config_dir / filename
        # Convert enums to strings to avoid YAML serialization issues
        config_dict = config.model_dump(mode='json')
        self._save_file(config_path, config_dict)
    
    def load_environment_config(self, filename: str = "environment.yaml") -> EnvironmentConfig:
        """Load environment configuration from file"""
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            # Create default config
            default_config = EnvironmentConfig()
            self.save_environment_config(default_config, filename)
            return default_config
        
        data = self._load_file(config_path)
        return EnvironmentConfig(**data)
    
    def save_environment_config(self, config: EnvironmentConfig, filename: str = "environment.yaml"):
        """Save environment configuration to file"""
        config_path = self.config_dir / filename
        self._save_file(config_path, config.dict())
    
    def load_player_action_config(self, filename: str = "player_actions.yaml") -> PlayerActionConfig:
        """Load player action configuration from file"""
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            # Create default config
            from .player_action_config import create_default_player_action_config
            default_config = create_default_player_action_config()
            self.save_player_action_config(default_config, filename)
            return default_config
        
        data = self._load_file(config_path)
        return PlayerActionConfig(**data)
    
    def save_player_action_config(self, config: PlayerActionConfig, filename: str = "player_actions.yaml"):
        """Save player action configuration to file"""
        config_path = self.config_dir / filename
        # Convert enums to strings to avoid YAML serialization issues
        config_dict = config.model_dump(mode='json')
        self._save_file(config_path, config_dict)
    
    def load_game_config(self, config_name: str) -> Dict[str, Any]:
        """Load a complete game configuration"""
        game_dir = self.config_dir / "games" / config_name
        game_dir.mkdir(parents=True, exist_ok=True)
        
        config = {}
        
        # Load actions
        actions_file = game_dir / "actions.yaml"
        if actions_file.exists():
            config["actions"] = self.load_action_config(str(actions_file))
        
        # Load environment
        env_file = game_dir / "environment.yaml"
        if env_file.exists():
            config["environment"] = self.load_environment_config(str(env_file))
        
        # Load NPCs
        npcs_file = game_dir / "npcs.yaml"
        if npcs_file.exists():
            config["npcs"] = self._load_file(npcs_file)
        
        # Load game settings
        settings_file = game_dir / "settings.yaml"
        if settings_file.exists():
            config["settings"] = self._load_file(settings_file)
        
        return config
    
    def create_sample_configs(self):
        """Create sample configuration files"""
        # Sample action config
        from .action_config import CustomAction, ActionProperty, PropertyType, ActionTargetType
        
        sample_actions = ActionConfig(
            custom_actions=[
                CustomAction(
                    action_id="craft_sword",
                    name="Craft Sword",
                    description="Craft a sword using materials",
                    target_type=ActionTargetType.OBJECT,
                    requires_target=True,
                    properties=[
                        ActionProperty(
                            name="material",
                            type=PropertyType.STRING,
                            required=True,
                            description="Material to use for crafting",
                            validation={"choices": ["iron", "steel", "mithril"]}
                        ),
                        ActionProperty(
                            name="enchantment",
                            type=PropertyType.STRING,
                            required=False,
                            default="none",
                            description="Enchantment to apply"
                        )
                    ],
                    energy_cost=20.0,
                    cooldown=60.0,
                    requirements={"skill_level": 10, "tools": ["hammer", "anvil"]}
                ),
                CustomAction(
                    action_id="cast_fireball",
                    name="Cast Fireball",
                    description="Cast a fireball spell",
                    target_type=ActionTargetType.ANY,
                    requires_target=True,
                    properties=[
                        ActionProperty(
                            name="power",
                            type=PropertyType.INTEGER,
                            required=False,
                            default=5,
                            description="Power level of the spell",
                            validation={"min": 1, "max": 10}
                        )
                    ],
                    energy_cost=15.0,
                    cooldown=10.0,
                    requirements={"mana": 30, "spell_components": ["sulfur"]}
                )
            ],
            action_categories={
                "crafting": ["craft_sword", "craft_armor", "craft_potion"],
                "magic": ["cast_fireball", "cast_heal", "cast_teleport"],
                "social": ["speak", "emote", "trade"]
            }
        )
        
        # Sample environment config
        from .environment_config import LocationConfig, WeatherPattern, TimeSchedule
        
        sample_environment = EnvironmentConfig(
            name="Fantasy Village",
            description="A peaceful village with magical elements",
            locations=[
                LocationConfig(
                    location_id="blacksmith_shop",
                    name="Thorin's Blacksmith",
                    location_type="building",
                    description="A busy blacksmith shop with the sound of hammering",
                    connected_locations=["village_center"],
                    properties={"temperature": "hot", "noise_level": "loud"},
                    available_actions=["craft_sword", "speak", "examine"],
                    default_objects=[
                        {"id": "anvil", "name": "Heavy Anvil", "interactable": True},
                        {"id": "forge", "name": "Blazing Forge", "interactable": True}
                    ],
                    default_npcs=["thorin_blacksmith"]
                ),
                LocationConfig(
                    location_id="magic_tower",
                    name="Wizard's Tower",
                    location_type="building",
                    description="A tall tower filled with magical energy",
                    connected_locations=["village_center"],
                    properties={"magical_aura": "strong", "lighting": "mystical"},
                    available_actions=["cast_fireball", "study_magic", "speak"],
                    default_npcs=["gandalf_wizard"]
                )
            ],
            weather_patterns=[
                WeatherPattern(
                    weather_id="magical_storm",
                    name="Magical Storm",
                    description="A storm crackling with magical energy",
                    visibility_modifier=0.5,
                    movement_modifier=0.8,
                    mood_effects={"excitement": 0.2, "fear": 0.1},
                    can_transition_to=["sunny", "cloudy"]
                )
            ],
            scheduled_events=[
                TimeSchedule(
                    event_name="daily_market",
                    description="The village market opens for the day",
                    time_of_day="morning",
                    frequency="daily",
                    world_effects={"market_active": True},
                    npc_effects={"merchants": {"mood_boost": 0.1}}
                )
            ]
        )
        
        # Save sample configs
        self.save_action_config(sample_actions, "sample_actions.yaml")
        self.save_environment_config(sample_environment, "sample_environment.yaml")
    
    def load_npc_config(self, config_name: str = "default") -> NPCConfig:
        """Load NPC configuration from file"""
        try:
            config_path = self.config_dir / f"npcs_{config_name}.yaml"
            if not config_path.exists():
                # Try JSON format
                config_path = self.config_dir / f"npcs_{config_name}.json"
                if not config_path.exists():
                    # Create default config
                    from .npc_config import create_default_npc_config
                    default_config = create_default_npc_config()
                    self.save_npc_config(default_config, config_name)
                    return default_config
            
            with open(config_path, 'r') as f:
                if config_path.suffix == '.yaml':
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            return NPCConfig(**data)
        except Exception as e:
            print(f"Error loading NPC config: {e}")
            from .npc_config import create_default_npc_config
            return create_default_npc_config()
    
    def save_npc_config(self, config: NPCConfig, config_name: str = "default") -> None:
        """Save NPC configuration to file"""
        try:
            config_path = self.config_dir / f"npcs_{config_name}.yaml"
            with open(config_path, 'w') as f:
                yaml.dump(config.model_dump(), f, default_flow_style=False, sort_keys=False)
            print(f"NPC configuration saved to {config_path}")
        except Exception as e:
            print(f"Error saving NPC config: {e}")
            raise
    
    def _load_file(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from JSON or YAML file"""
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            with open(file_path, 'r') as f:
                return yaml.safe_load(f) or {}
        elif file_path.suffix.lower() == '.json':
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def _save_file(self, file_path: Path, data: Dict[str, Any]):
        """Save configuration to JSON or YAML file"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)
        elif file_path.suffix.lower() == '.json':
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

def load_from_file(file_path: str) -> Dict[str, Any]:
    """Convenience function to load any config file"""
    path = Path(file_path)
    loader = ConfigLoader(path.parent)
    return loader._load_file(path) 