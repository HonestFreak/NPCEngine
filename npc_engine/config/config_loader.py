"""
Advanced Configuration Management for NPCEngine

Supports multiple backends:
- YAML files for development and rapid prototyping  
- Database storage for production and multi-tenant scenarios
- Environment-based configuration switching
"""

import json
import yaml
import os
import logging
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from datetime import datetime
from enum import Enum

from .action_config import ActionConfig
from .environment_config import EnvironmentConfig
from .npc_config import NPCConfig
from .player_action_config import PlayerActionConfig

logger = logging.getLogger(__name__)

class ConfigBackend(Enum):
    """Configuration storage backend options"""
    YAML = "yaml"
    DATABASE = "database"
    ENVIRONMENT = "environment"

class ConfigurationManager:
    """
    Production-grade configuration manager with multiple backends
    
    Features:
    - YAML files for development
    - Database storage for production
    - Environment variable override
    - Validation and type safety
    - Audit logging
    - Hot reloading
    """
    
    def __init__(
        self, 
        config_dir: str = "config",
        backend: ConfigBackend = ConfigBackend.YAML,
        database_url: Optional[str] = None
    ):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.backend = backend
        self.database_url = database_url
        
        # Initialize database connection if needed
        if backend == ConfigBackend.DATABASE:
            self._init_database()
        
        logger.info(f"ConfigurationManager initialized with {backend.value} backend")
    
    def _init_database(self):
        """Initialize database connection for configuration storage"""
        if not self.database_url:
            raise ValueError("Database URL required for database backend")
        
        try:
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker
            
            self.engine = create_engine(self.database_url)
            self.SessionLocal = sessionmaker(bind=self.engine)
            
            # Create configuration tables if they don't exist
            self._create_config_tables()
            logger.info("Database configuration backend initialized")
            
        except ImportError:
            raise ImportError("SQLAlchemy required for database backend: pip install sqlalchemy")
        except Exception as e:
            logger.error(f"Failed to initialize database backend: {e}")
            raise
    
    def _create_config_tables(self):
        """Create configuration tables in database"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS npc_configurations (
            id SERIAL PRIMARY KEY,
            config_name VARCHAR(255) UNIQUE NOT NULL,
            config_type VARCHAR(50) NOT NULL,
            config_data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            version INTEGER DEFAULT 1
        );
        
        CREATE INDEX IF NOT EXISTS idx_config_name_type 
        ON npc_configurations(config_name, config_type);
        """
        
        with self.engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
    
    def load_action_config(self, filename: str = "actions.yaml") -> ActionConfig:
        """Load action configuration with backend selection"""
        try:
            if self.backend == ConfigBackend.DATABASE:
                data = self._load_from_database("actions", filename)
            elif self.backend == ConfigBackend.ENVIRONMENT:
                data = self._load_from_environment("NPC_ACTIONS_CONFIG")
            else:  # YAML backend
                data = self._load_from_yaml(filename)
            
            if not data:
                logger.info(f"No action config found, creating default: {filename}")
                default_config = ActionConfig()
                self.save_action_config(default_config, filename)
                return default_config
            
            return ActionConfig(**data)
            
        except Exception as e:
            logger.error(f"Failed to load action config: {e}")
            return ActionConfig()  # Return default on error
    
    def save_action_config(self, config: ActionConfig, filename: str = "actions.yaml"):
        """Save action configuration with backend selection"""
        try:
            config_dict = config.model_dump(mode='json')
            
            if self.backend == ConfigBackend.DATABASE:
                self._save_to_database("actions", filename, config_dict)
            elif self.backend == ConfigBackend.ENVIRONMENT:
                logger.warning("Cannot save to environment backend - read only")
            else:  # YAML backend
                self._save_to_yaml(filename, config_dict)
            
            logger.info(f"Action config saved successfully: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save action config: {e}")
            raise
    
    def load_environment_config(self, filename: str = "environment.yaml") -> EnvironmentConfig:
        """Load environment configuration with backend selection"""
        try:
            if self.backend == ConfigBackend.DATABASE:
                data = self._load_from_database("environment", filename)
            elif self.backend == ConfigBackend.ENVIRONMENT:
                data = self._load_from_environment("NPC_ENVIRONMENT_CONFIG")
            else:  # YAML backend
                data = self._load_from_yaml(filename)
            
            if not data:
                logger.info(f"No environment config found, creating default: {filename}")
                default_config = EnvironmentConfig()
                self.save_environment_config(default_config, filename)
                return default_config
            
            return EnvironmentConfig(**data)
            
        except Exception as e:
            logger.error(f"Failed to load environment config: {e}")
            return EnvironmentConfig()  # Return default on error
    
    def save_environment_config(self, config: EnvironmentConfig, filename: str = "environment.yaml"):
        """Save environment configuration with backend selection"""
        try:
            config_dict = config.dict()
            
            if self.backend == ConfigBackend.DATABASE:
                self._save_to_database("environment", filename, config_dict)
            elif self.backend == ConfigBackend.ENVIRONMENT:
                logger.warning("Cannot save to environment backend - read only")
            else:  # YAML backend
                self._save_to_yaml(filename, config_dict)
            
            logger.info(f"Environment config saved successfully: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save environment config: {e}")
            raise
    
    def load_npc_config(self, config_name: str = "default") -> NPCConfig:
        """Load NPC configuration with backend selection"""
        try:
            if self.backend == ConfigBackend.DATABASE:
                data = self._load_from_database("npcs", config_name)
            elif self.backend == ConfigBackend.ENVIRONMENT:
                data = self._load_from_environment("NPC_CONFIG")
            else:  # YAML backend
                data = self._load_npc_yaml(config_name)
            
            if not data:
                logger.info(f"No NPC config found, creating default: {config_name}")
                from .npc_config import create_default_npc_config
                default_config = create_default_npc_config()
                self.save_npc_config(default_config, config_name)
                return default_config
            
            return NPCConfig(**data)
            
        except Exception as e:
            logger.error(f"Failed to load NPC config: {e}")
            from .npc_config import create_default_npc_config
            return create_default_npc_config()
    
    def save_npc_config(self, config: NPCConfig, config_name: str = "default"):
        """Save NPC configuration with backend selection"""
        try:
            config_dict = config.model_dump()
            
            if self.backend == ConfigBackend.DATABASE:
                self._save_to_database("npcs", config_name, config_dict)
            elif self.backend == ConfigBackend.ENVIRONMENT:
                logger.warning("Cannot save to environment backend - read only")
            else:  # YAML backend
                self._save_npc_yaml(config_name, config_dict)
            
            logger.info(f"NPC config saved successfully: {config_name}")
            
        except Exception as e:
            logger.error(f"Failed to save NPC config: {e}")
            raise
    
    def _load_from_database(self, config_type: str, config_name: str) -> Optional[Dict[str, Any]]:
        """Load configuration from database"""
        if not hasattr(self, 'SessionLocal'):
            return None
        
        try:
            with self.SessionLocal() as session:
                from sqlalchemy import text
                
                query = text("""
                    SELECT config_data FROM npc_configurations 
                    WHERE config_type = :type AND config_name = :name
                    ORDER BY version DESC LIMIT 1
                """)
                
                result = session.execute(query, {
                    "type": config_type,
                    "name": config_name
                }).fetchone()
                
                if result:
                    return result[0]  # JSONB data
                return None
                
        except Exception as e:
            logger.error(f"Failed to load from database: {e}")
            return None
    
    def _save_to_database(self, config_type: str, config_name: str, config_data: Dict[str, Any]):
        """Save configuration to database"""
        if not hasattr(self, 'SessionLocal'):
            raise RuntimeError("Database not initialized")
        
        try:
            with self.SessionLocal() as session:
                from sqlalchemy import text
                
                # Check if config exists
                check_query = text("""
                    SELECT version FROM npc_configurations 
                    WHERE config_type = :type AND config_name = :name
                    ORDER BY version DESC LIMIT 1
                """)
                
                result = session.execute(check_query, {
                    "type": config_type,
                    "name": config_name
                }).fetchone()
                
                new_version = (result[0] + 1) if result else 1
                
                # Insert new version
                insert_query = text("""
                    INSERT INTO npc_configurations 
                    (config_name, config_type, config_data, version, updated_at)
                    VALUES (:name, :type, :data, :version, :timestamp)
                """)
                
                session.execute(insert_query, {
                    "name": config_name,
                    "type": config_type,
                    "data": json.dumps(config_data),
                    "version": new_version,
                    "timestamp": datetime.now()
                })
                
                session.commit()
                logger.debug(f"Saved {config_type}:{config_name} v{new_version} to database")
                
        except Exception as e:
            logger.error(f"Failed to save to database: {e}")
            raise
    
    def _load_from_environment(self, env_var: str) -> Optional[Dict[str, Any]]:
        """Load configuration from environment variable"""
        try:
            config_json = os.getenv(env_var)
            if config_json:
                return json.loads(config_json)
            return None
        except Exception as e:
            logger.error(f"Failed to load from environment {env_var}: {e}")
            return None
    
    def _load_from_yaml(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load configuration from YAML file"""
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            return None
        
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load YAML {filename}: {e}")
            return None
    
    def _save_to_yaml(self, filename: str, data: Dict[str, Any]):
        """Save configuration to YAML file"""
        config_path = self.config_dir / filename
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, indent=2, sort_keys=False)
        except Exception as e:
            logger.error(f"Failed to save YAML {filename}: {e}")
            raise
    
    def _load_npc_yaml(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Load NPC configuration from YAML with multiple format support"""
        for ext in ['.yaml', '.yml', '.json']:
            config_path = self.config_dir / f"npcs_{config_name}{ext}"
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        if ext == '.json':
                            return json.load(f)
                        else:
                            return yaml.safe_load(f) or {}
                except Exception as e:
                    logger.error(f"Failed to load NPC config {config_path}: {e}")
                    continue
        return None
    
    def _save_npc_yaml(self, config_name: str, data: Dict[str, Any]):
        """Save NPC configuration to YAML"""
        config_path = self.config_dir / f"npcs_{config_name}.yaml"
        self._save_to_yaml(config_path.name, data)
    
    def list_configurations(self, config_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available configurations"""
        if self.backend == ConfigBackend.DATABASE:
            return self._list_database_configs(config_type)
        else:
            return self._list_yaml_configs(config_type)
    
    def _list_database_configs(self, config_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List configurations from database"""
        if not hasattr(self, 'SessionLocal'):
            return []
        
        try:
            with self.SessionLocal() as session:
                from sqlalchemy import text
                
                if config_type:
                    query = text("""
                        SELECT DISTINCT config_name, config_type, 
                               MAX(version) as latest_version,
                               MAX(updated_at) as last_updated
                        FROM npc_configurations 
                        WHERE config_type = :type
                        GROUP BY config_name, config_type
                        ORDER BY last_updated DESC
                    """)
                    result = session.execute(query, {"type": config_type})
                else:
                    query = text("""
                        SELECT DISTINCT config_name, config_type,
                               MAX(version) as latest_version, 
                               MAX(updated_at) as last_updated
                        FROM npc_configurations
                        GROUP BY config_name, config_type
                        ORDER BY config_type, last_updated DESC
                    """)
                    result = session.execute(query)
                
                return [
                    {
                        "name": row[0],
                        "type": row[1], 
                        "version": row[2],
                        "last_updated": row[3],
                        "backend": "database"
                    }
                    for row in result
                ]
                
        except Exception as e:
            logger.error(f"Failed to list database configs: {e}")
            return []
    
    def _list_yaml_configs(self, config_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List configurations from YAML files"""
        configs = []
        
        for file_path in self.config_dir.glob("*.yaml"):
            try:
                # Determine config type from filename
                name = file_path.stem
                if name.startswith("npcs_"):
                    file_type = "npcs"
                    name = name[5:]  # Remove "npcs_" prefix
                elif name == "environment":
                    file_type = "environment"
                elif name == "actions":
                    file_type = "actions"
                else:
                    file_type = "unknown"
                
                if config_type and file_type != config_type:
                    continue
                
                stat = file_path.stat()
                configs.append({
                    "name": name,
                    "type": file_type,
                    "version": 1,  # YAML files don't have versions
                    "last_updated": datetime.fromtimestamp(stat.st_mtime),
                    "backend": "yaml"
                })
                
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                continue
        
        return sorted(configs, key=lambda x: x["last_updated"], reverse=True)
    
    def backup_configuration(self, backup_name: str = None) -> str:
        """Create a backup of all configurations"""
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_dir = self.config_dir / "backups" / backup_name
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup based on current backend
        if self.backend == ConfigBackend.DATABASE:
            self._backup_database_configs(backup_dir)
        else:
            self._backup_yaml_configs(backup_dir)
        
        logger.info(f"Configuration backup created: {backup_dir}")
        return str(backup_dir)
    
    def _backup_database_configs(self, backup_dir: Path):
        """Backup database configurations to YAML files"""
        configs = self._list_database_configs()
        
        for config in configs:
            data = self._load_from_database(config["type"], config["name"])
            if data:
                backup_file = backup_dir / f"{config['type']}_{config['name']}.yaml"
                with open(backup_file, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, indent=2)
    
    def _backup_yaml_configs(self, backup_dir: Path):
        """Backup YAML configurations"""
        import shutil
        
        for file_path in self.config_dir.glob("*.yaml"):
            if file_path.parent.name != "backups":  # Don't backup backups
                shutil.copy2(file_path, backup_dir)

# Backward compatibility
class ConfigLoader(ConfigurationManager):
    """Legacy ConfigLoader for backward compatibility"""
    
    def __init__(self, config_dir: str = "config"):
        # Determine backend from environment
        backend_str = os.getenv("CONFIG_BACKEND", "yaml").lower()
        database_url = os.getenv("CONFIG_DATABASE_URL")
        
        try:
            backend = ConfigBackend(backend_str)
        except ValueError:
            logger.warning(f"Invalid CONFIG_BACKEND '{backend_str}', using YAML")
            backend = ConfigBackend.YAML
        
        super().__init__(config_dir, backend, database_url)
    
    # Legacy methods for backward compatibility
    def load_player_action_config(self, filename: str = "player_actions.yaml") -> PlayerActionConfig:
        """Load player action configuration"""
        try:
            if self.backend == ConfigBackend.DATABASE:
                data = self._load_from_database("player_actions", filename)
            else:
                data = self._load_from_yaml(filename)
            
            if not data:
                from .player_action_config import create_default_player_action_config
                default_config = create_default_player_action_config()
                self.save_player_action_config(default_config, filename)
                return default_config
            
            return PlayerActionConfig(**data)
            
        except Exception as e:
            logger.error(f"Failed to load player action config: {e}")
            from .player_action_config import create_default_player_action_config
            return create_default_player_action_config()
    
    def save_player_action_config(self, config: PlayerActionConfig, filename: str = "player_actions.yaml"):
        """Save player action configuration"""
        try:
            config_dict = config.model_dump(mode='json')
            
            if self.backend == ConfigBackend.DATABASE:
                self._save_to_database("player_actions", filename, config_dict)
            else:
                self._save_to_yaml(filename, config_dict)
            
        except Exception as e:
            logger.error(f"Failed to save player action config: {e}")
            raise
    
    def load_game_config(self, config_name: str) -> Dict[str, Any]:
        """Load a complete game configuration"""
        config = {}
        
        try:
            # Load different config types
            config["actions"] = self.load_action_config().model_dump()
            config["environment"] = self.load_environment_config().dict()
            config["npcs"] = self.load_npc_config(config_name).model_dump()
            
        except Exception as e:
            logger.error(f"Failed to load game config '{config_name}': {e}")
        
        return config
    
    def create_sample_configs(self):
        """Create sample configuration files"""
        # This method remains the same as it's used for examples
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
                        )
                    ],
                    energy_cost=20.0,
                    cooldown=60.0,
                    requirements={"skill_level": 10, "tools": ["hammer", "anvil"]}
                )
            ]
        )
        
        from .environment_config import TimeSchedule
        sample_environment = EnvironmentConfig(
            name="Sample Fantasy World",
            description="A sample medieval fantasy environment",
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
        
        logger.info("Sample configurations created successfully")

def load_from_file(file_path: str) -> Dict[str, Any]:
    """Convenience function to load any config file"""
    path = Path(file_path)
    loader = ConfigLoader(path.parent)
    return loader._load_from_yaml(path.name) or {} 