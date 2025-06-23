"""
NPC Configuration System
Allows users to define custom NPC schemas and manage NPC instances
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class PropertyType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"


class NPCProperty(BaseModel):
    name: str
    type: PropertyType
    description: str
    default_value: Any = None
    required: bool = False
    choices: Optional[List[Any]] = None  # For string/integer choices
    min_value: Optional[Union[int, float]] = None  # For numeric validation
    max_value: Optional[Union[int, float]] = None  # For numeric validation
    min_length: Optional[int] = None  # For string/list validation
    max_length: Optional[int] = None  # For string/list validation


class NPCRelationship(BaseModel):
    npc_id: str
    relationship_type: str  # "friend", "enemy", "family", "colleague", etc.
    description: str
    strength: float = Field(ge=0.0, le=1.0, description="Relationship strength from 0 to 1")


class NPCSchema(BaseModel):
    schema_id: str
    name: str
    description: str
    
    # Core properties that every NPC must have
    core_properties: Dict[str, Any] = Field(default_factory=lambda: {
        "id": {"type": "string", "required": True, "description": "Unique identifier for the NPC"},
        "name": {"type": "string", "required": True, "description": "Display name of the NPC"},
        "description": {"type": "string", "required": True, "description": "Brief description of the NPC"}
    })
    
    # Customizable properties that users can add/modify
    custom_properties: List[NPCProperty] = Field(default_factory=list)
    
    # Default example properties that users can modify or remove
    example_properties: List[NPCProperty] = Field(default_factory=lambda: [
        NPCProperty(
            name="job",
            type=PropertyType.STRING,
            description="The NPC's profession or role",
            default_value="Villager",
            choices=["Villager", "Merchant", "Guard", "Blacksmith", "Mage", "Healer", "Scholar", "Farmer", "Noble", "Thief"]
        ),
        NPCProperty(
            name="age",
            type=PropertyType.INTEGER,
            description="Age of the NPC in years",
            default_value=30,
            min_value=1,
            max_value=200
        ),
        NPCProperty(
            name="base_emotion",
            type=PropertyType.STRING,
            description="The NPC's default emotional state",
            default_value="neutral",
            choices=["happy", "sad", "angry", "fearful", "surprised", "disgusted", "neutral", "excited", "calm", "anxious"]
        ),
        NPCProperty(
            name="personality_traits",
            type=PropertyType.LIST,
            description="List of personality traits",
            default_value=["friendly", "helpful"],
            choices=["friendly", "hostile", "helpful", "selfish", "brave", "cowardly", "honest", "deceptive", "loyal", "treacherous", "calm", "aggressive", "wise", "foolish", "generous", "greedy"]
        ),
        NPCProperty(
            name="health",
            type=PropertyType.INTEGER,
            description="Current health points",
            default_value=100,
            min_value=0,
            max_value=200
        ),
        NPCProperty(
            name="energy",
            type=PropertyType.INTEGER,
            description="Current energy level",
            default_value=100,
            min_value=0,
            max_value=100
        ),
        NPCProperty(
            name="wealth",
            type=PropertyType.INTEGER,
            description="Amount of gold/currency the NPC has",
            default_value=50,
            min_value=0
        ),
        NPCProperty(
            name="location",
            type=PropertyType.STRING,
            description="Current location of the NPC",
            default_value="Village Square"
        ),
        NPCProperty(
            name="skills",
            type=PropertyType.DICT,
            description="NPC's skills and their levels",
            default_value={"combat": 5, "crafting": 3, "social": 7}
        ),
        NPCProperty(
            name="inventory",
            type=PropertyType.LIST,
            description="Items the NPC is carrying",
            default_value=["Basic Clothes", "Small Pouch"]
        ),
        NPCProperty(
            name="dialogue_style",
            type=PropertyType.STRING,
            description="How the NPC speaks",
            default_value="formal",
            choices=["formal", "casual", "rustic", "scholarly", "poetic", "blunt", "mysterious", "cheerful", "grumpy"]
        ),
        NPCProperty(
            name="active",
            type=PropertyType.BOOLEAN,
            description="Whether the NPC is currently active in the world",
            default_value=True
        )
    ])


class NPCInstance(BaseModel):
    id: str
    name: str
    description: str
    schema_id: str
    
    # Property values for this specific NPC instance
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    # Relationships with other NPCs
    relationships: List[NPCRelationship] = Field(default_factory=list)
    
    # Session-specific data
    session_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())


class NPCConfig(BaseModel):
    schemas: Dict[str, NPCSchema] = Field(default_factory=dict)
    instances: Dict[str, NPCInstance] = Field(default_factory=dict)
    
    def add_schema(self, schema: NPCSchema):
        """Add a new NPC schema"""
        self.schemas[schema.schema_id] = schema
    
    def remove_schema(self, schema_id: str):
        """Remove an NPC schema and all instances using it"""
        if schema_id in self.schemas:
            # Remove all instances using this schema
            instances_to_remove = [
                instance_id for instance_id, instance in self.instances.items()
                if instance.schema_id == schema_id
            ]
            for instance_id in instances_to_remove:
                del self.instances[instance_id]
            
            # Remove the schema
            del self.schemas[schema_id]
    
    def add_instance(self, instance: NPCInstance):
        """Add a new NPC instance"""
        self.instances[instance.id] = instance
    
    def remove_instance(self, instance_id: str):
        """Remove an NPC instance"""
        if instance_id in self.instances:
            del self.instances[instance_id]
    
    def get_instances_by_schema(self, schema_id: str) -> List[NPCInstance]:
        """Get all instances of a specific schema"""
        return [
            instance for instance in self.instances.values()
            if instance.schema_id == schema_id
        ]
    
    def validate_instance_properties(self, instance: NPCInstance) -> List[str]:
        """Validate an instance's properties against its schema"""
        errors = []
        
        if instance.schema_id not in self.schemas:
            errors.append(f"Schema '{instance.schema_id}' not found")
            return errors
        
        schema = self.schemas[instance.schema_id]
        
        # Check core properties
        for prop_name, prop_def in schema.core_properties.items():
            if prop_def.get("required", False) and prop_name not in instance.properties:
                errors.append(f"Required core property '{prop_name}' is missing")
        
        # Check custom and example properties
        all_properties = schema.custom_properties + schema.example_properties
        for prop in all_properties:
            if prop.required and prop.name not in instance.properties:
                errors.append(f"Required property '{prop.name}' is missing")
            
            if prop.name in instance.properties:
                value = instance.properties[prop.name]
                
                # Type validation
                if prop.type == PropertyType.INTEGER and not isinstance(value, int):
                    errors.append(f"Property '{prop.name}' must be an integer")
                elif prop.type == PropertyType.FLOAT and not isinstance(value, (int, float)):
                    errors.append(f"Property '{prop.name}' must be a number")
                elif prop.type == PropertyType.STRING and not isinstance(value, str):
                    errors.append(f"Property '{prop.name}' must be a string")
                elif prop.type == PropertyType.BOOLEAN and not isinstance(value, bool):
                    errors.append(f"Property '{prop.name}' must be a boolean")
                elif prop.type == PropertyType.LIST and not isinstance(value, list):
                    errors.append(f"Property '{prop.name}' must be a list")
                elif prop.type == PropertyType.DICT and not isinstance(value, dict):
                    errors.append(f"Property '{prop.name}' must be a dictionary")
                
                # Value validation
                if prop.choices and value not in prop.choices:
                    errors.append(f"Property '{prop.name}' must be one of {prop.choices}")
                
                if prop.min_value is not None and isinstance(value, (int, float)) and value < prop.min_value:
                    errors.append(f"Property '{prop.name}' must be at least {prop.min_value}")
                
                if prop.max_value is not None and isinstance(value, (int, float)) and value > prop.max_value:
                    errors.append(f"Property '{prop.name}' must be at most {prop.max_value}")
                
                if prop.min_length is not None and hasattr(value, '__len__') and len(value) < prop.min_length:
                    errors.append(f"Property '{prop.name}' must have at least {prop.min_length} items")
                
                if prop.max_length is not None and hasattr(value, '__len__') and len(value) > prop.max_length:
                    errors.append(f"Property '{prop.name}' must have at most {prop.max_length} items")
        
        return errors


def create_default_npc_schemas() -> Dict[str, NPCSchema]:
    """Create default NPC schemas"""
    schemas = {}
    
    # Generic Villager Schema
    villager = NPCSchema(
        schema_id="generic_villager",
        name="Generic Villager",
        description="A basic villager template suitable for most common NPCs"
    )
    schemas["generic_villager"] = villager
    
    # Merchant Schema
    merchant = NPCSchema(
        schema_id="merchant",
        name="Merchant",
        description="A trader who buys and sells goods",
        custom_properties=[
            NPCProperty(
                name="shop_type",
                type=PropertyType.STRING,
                description="Type of shop the merchant runs",
                default_value="general",
                choices=["general", "weapons", "armor", "potions", "books", "food", "jewelry", "magical"]
            ),
            NPCProperty(
                name="trade_routes",
                type=PropertyType.LIST,
                description="Cities and locations the merchant trades with",
                default_value=["Nearby Town", "Capital City"]
            ),
            NPCProperty(
                name="reputation",
                type=PropertyType.FLOAT,
                description="Trading reputation (0.0 to 1.0)",
                default_value=0.7,
                min_value=0.0,
                max_value=1.0
            )
        ]
    )
    # Override some example properties for merchants
    merchant.example_properties = [prop for prop in merchant.example_properties if prop.name != "job"]
    merchant.example_properties.append(
        NPCProperty(
            name="job",
            type=PropertyType.STRING,
            description="The NPC's profession or role",
            default_value="Merchant",
            required=True
        )
    )
    merchant.example_properties.append(
        NPCProperty(
            name="wealth",
            type=PropertyType.INTEGER,
            description="Amount of gold/currency the NPC has",
            default_value=500,  # Merchants have more money
            min_value=0
        )
    )
    schemas["merchant"] = merchant
    
    # Guard Schema
    guard = NPCSchema(
        schema_id="guard",
        name="Guard",
        description="A protective warrior who maintains order",
        custom_properties=[
            NPCProperty(
                name="patrol_area",
                type=PropertyType.STRING,
                description="Area the guard is responsible for patrolling",
                default_value="Main Gate"
            ),
            NPCProperty(
                name="authority_level",
                type=PropertyType.INTEGER,
                description="Level of authority (1-10)",
                default_value=5,
                min_value=1,
                max_value=10
            ),
            NPCProperty(
                name="equipment",
                type=PropertyType.LIST,
                description="Guard's equipment and weapons",
                default_value=["Iron Sword", "Leather Armor", "Shield", "Whistle"]
            )
        ]
    )
    # Override properties for guards
    guard.example_properties = [prop for prop in guard.example_properties if prop.name not in ["job", "health"]]
    guard.example_properties.extend([
        NPCProperty(
            name="job",
            type=PropertyType.STRING,
            description="The NPC's profession or role",
            default_value="Guard",
            required=True
        ),
        NPCProperty(
            name="health",
            type=PropertyType.INTEGER,
            description="Current health points",
            default_value=150,  # Guards have more health
            min_value=0,
            max_value=200
        )
    ])
    schemas["guard"] = guard
    
    # Mage Schema
    mage = NPCSchema(
        schema_id="mage",
        name="Mage",
        description="A practitioner of magical arts",
        custom_properties=[
            NPCProperty(
                name="magic_school",
                type=PropertyType.STRING,
                description="School of magic the mage specializes in",
                default_value="elemental",
                choices=["elemental", "healing", "illusion", "necromancy", "divination", "transmutation", "enchantment"]
            ),
            NPCProperty(
                name="spell_list",
                type=PropertyType.LIST,
                description="Spells the mage knows",
                default_value=["Fireball", "Heal", "Magic Missile"]
            ),
            NPCProperty(
                name="mana",
                type=PropertyType.INTEGER,
                description="Current mana points",
                default_value=100,
                min_value=0,
                max_value=200
            ),
            NPCProperty(
                name="magical_focus",
                type=PropertyType.STRING,
                description="Magical item used to channel magic",
                default_value="Wooden Staff"
            )
        ]
    )
    # Override properties for mages
    mage.example_properties = [prop for prop in mage.example_properties if prop.name not in ["job", "skills"]]
    mage.example_properties.extend([
        NPCProperty(
            name="job",
            type=PropertyType.STRING,
            description="The NPC's profession or role",
            default_value="Mage",
            required=True
        ),
        NPCProperty(
            name="skills",
            type=PropertyType.DICT,
            description="NPC's skills and their levels",
            default_value={"combat": 3, "magic": 9, "social": 6, "knowledge": 8}
        )
    ])
    schemas["mage"] = mage
    
    return schemas


def create_sample_npc_instances() -> List[NPCInstance]:
    """Create sample NPC instances"""
    instances = []
    
    # Sample Villager
    villager = NPCInstance(
        id="npc_villager_001",
        name="Martha the Baker",
        description="A kind baker who makes the best bread in the village",
        schema_id="generic_villager",
        properties={
            "job": "Baker",
            "age": 45,
            "base_emotion": "happy",
            "personality_traits": ["friendly", "helpful", "generous"],
            "health": 80,
            "energy": 90,
            "wealth": 120,
            "location": "Bakery",
            "skills": {"combat": 2, "crafting": 8, "social": 9, "cooking": 10},
            "inventory": ["Apron", "Flour", "Fresh Bread", "Rolling Pin"],
            "dialogue_style": "cheerful",
            "active": True
        }
    )
    instances.append(villager)
    
    # Sample Merchant
    merchant = NPCInstance(
        id="npc_merchant_001",
        name="Gareth the Trader",
        description="A well-traveled merchant with exotic goods from distant lands",
        schema_id="merchant",
        properties={
            "job": "Merchant",
            "age": 38,
            "base_emotion": "neutral",
            "personality_traits": ["shrewd", "honest", "worldly"],
            "health": 100,
            "energy": 85,
            "wealth": 750,
            "location": "Market Square",
            "skills": {"combat": 4, "social": 9, "trading": 10, "appraisal": 8},
            "inventory": ["Ledger", "Scales", "Exotic Spices", "Silk Cloth", "Gems"],
            "dialogue_style": "formal",
            "active": True,
            "shop_type": "general",
            "trade_routes": ["Capital City", "Port Town", "Mountain Settlement"],
            "reputation": 0.85
        }
    )
    instances.append(merchant)
    
    # Sample Guard
    guard = NPCInstance(
        id="npc_guard_001",
        name="Captain Roderick",
        description="A veteran guard captain who has protected the village for over a decade",
        schema_id="guard",
        properties={
            "job": "Guard",
            "age": 42,
            "base_emotion": "calm",
            "personality_traits": ["loyal", "brave", "disciplined", "protective"],
            "health": 160,
            "energy": 95,
            "wealth": 200,
            "location": "Village Gate",
            "skills": {"combat": 9, "leadership": 8, "social": 6, "tactics": 7},
            "inventory": ["Steel Sword", "Chain Mail", "Tower Shield", "Horn", "Badge of Office"],
            "dialogue_style": "formal",
            "active": True,
            "patrol_area": "Village Perimeter",
            "authority_level": 8,
            "equipment": ["Steel Sword", "Chain Mail", "Tower Shield", "Horn", "Badge of Office"]
        },
        relationships=[
            NPCRelationship(
                npc_id="npc_villager_001",
                relationship_type="protector",
                description="Protects Martha and other villagers",
                strength=0.7
            )
        ]
    )
    instances.append(guard)
    
    # Sample Mage
    mage = NPCInstance(
        id="npc_mage_001",
        name="Eldara the Wise",
        description="An ancient mage who serves as the village's magical advisor and healer",
        schema_id="mage",
        properties={
            "job": "Mage",
            "age": 127,
            "base_emotion": "calm",
            "personality_traits": ["wise", "patient", "mysterious", "helpful"],
            "health": 90,
            "energy": 70,
            "wealth": 300,
            "location": "Mage Tower",
            "skills": {"combat": 4, "magic": 10, "social": 7, "knowledge": 10, "alchemy": 9},
            "inventory": ["Crystal Staff", "Spell Components", "Ancient Tome", "Healing Potions"],
            "dialogue_style": "scholarly",
            "active": True,
            "magic_school": "healing",
            "spell_list": ["Greater Heal", "Purify", "Light", "Dispel Magic", "Scrying"],
            "mana": 180,
            "magical_focus": "Crystal Staff of Healing"
        },
        relationships=[
            NPCRelationship(
                npc_id="npc_guard_001",
                relationship_type="advisor",
                description="Provides magical counsel to the guard captain",
                strength=0.6
            ),
            NPCRelationship(
                npc_id="npc_villager_001",
                relationship_type="healer",
                description="Provides healing services to the baker when needed",
                strength=0.5
            )
        ]
    )
    instances.append(mage)
    
    return instances


def create_default_npc_config() -> NPCConfig:
    """Create default NPC configuration with sample data"""
    config = NPCConfig()
    
    # Add default schemas
    schemas = create_default_npc_schemas()
    for schema_id, schema in schemas.items():
        config.add_schema(schema)
    
    # Add sample instances
    instances = create_sample_npc_instances()
    for instance in instances:
        config.add_instance(instance)
    
    return config 