"""
NPC-related data models
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class NPCPersonality(BaseModel):
    """Defines the core personality traits of an NPC"""
    name: str = Field(..., description="Name of the NPC")
    role: str = Field(..., description="Role/profession of the NPC (e.g., 'merchant', 'guard', 'villager')")
    personality_traits: List[str] = Field(default_factory=list, description="Personality traits like 'friendly', 'suspicious', 'greedy'")
    background: str = Field("", description="Backstory and history of the NPC")
    goals: List[str] = Field(default_factory=list, description="Current goals and motivations")
    relationships: Dict[str, str] = Field(default_factory=dict, description="Relationships with other NPCs/players")
    dialogue_style: str = Field("casual", description="How the NPC speaks (formal, casual, aggressive, etc.)")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Marcus the Blacksmith",
                "role": "blacksmith",
                "personality_traits": ["hardworking", "honest", "gruff"],
                "background": "A veteran blacksmith who has been in the village for 20 years",
                "goals": ["craft the finest weapons", "train an apprentice"],
                "relationships": {"player": "neutral", "mayor": "friendly"},
                "dialogue_style": "gruff but helpful"
            }
        }


class NPCMemory(BaseModel):
    """Represents the memory system of an NPC"""
    short_term: List[Dict[str, Any]] = Field(default_factory=list, description="Recent events and interactions")
    long_term: List[Dict[str, Any]] = Field(default_factory=list, description="Important memories that persist")
    relationships_memory: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict, 
        description="Memories specific to relationships with other characters"
    )
    
    def add_memory(self, memory: Dict[str, Any], is_important: bool = False):
        """Add a new memory to the NPC"""
        memory["timestamp"] = datetime.now().isoformat()
        
        if is_important:
            self.long_term.append(memory)
        else:
            self.short_term.append(memory)
            # Keep only last 20 short-term memories
            if len(self.short_term) > 20:
                self.short_term.pop(0)
    
    def get_relevant_memories(self, context: str, character: str = None) -> List[Dict[str, Any]]:
        """Retrieve memories relevant to current context"""
        relevant = []
        
        # Add recent short-term memories
        relevant.extend(self.short_term[-5:])
        
        # Add relevant long-term memories (simplified keyword matching)
        for memory in self.long_term:
            if any(keyword in memory.get("content", "").lower() for keyword in context.lower().split()):
                relevant.append(memory)
        
        # Add character-specific memories
        if character and character in self.relationships_memory:
            relevant.extend(self.relationships_memory[character][-3:])
        
        return relevant


class NPCState(BaseModel):
    """Current state of an NPC"""
    npc_id: str = Field(..., description="Unique identifier for the NPC")
    current_location: str = Field(..., description="Current location of the NPC")
    current_activity: str = Field("idle", description="What the NPC is currently doing")
    mood: str = Field("neutral", description="Current emotional state")
    health: float = Field(100.0, description="Health percentage (0-100)")
    energy: float = Field(100.0, description="Energy level (0-100)")
    inventory: List[Dict[str, Any]] = Field(default_factory=list, description="Items the NPC possesses")
    status_effects: List[str] = Field(default_factory=list, description="Temporary effects affecting the NPC")
    last_updated: datetime = Field(default_factory=datetime.now, description="When state was last modified")
    
    # Dynamic attributes for game-specific data
    custom_attributes: Dict[str, Any] = Field(default_factory=dict, description="Game-specific attributes")
    
    class Config:
        schema_extra = {
            "example": {
                "npc_id": "marcus_blacksmith",
                "current_location": "blacksmith_shop",
                "current_activity": "hammering_sword",
                "mood": "focused",
                "health": 95.0,
                "energy": 80.0,
                "inventory": [{"item": "iron_ingot", "quantity": 5}, {"item": "hammer", "quantity": 1}],
                "status_effects": [],
                "custom_attributes": {"skill_level": 85, "reputation": "respected"}
            }
        }


class NPCData(BaseModel):
    """Complete NPC data structure combining personality, state, and memory"""
    personality: NPCPersonality
    state: NPCState
    memory: NPCMemory
    
    class Config:
        schema_extra = {
            "example": {
                "personality": {
                    "name": "Marcus the Blacksmith",
                    "role": "blacksmith",
                    "personality_traits": ["hardworking", "honest", "gruff"],
                    "background": "A veteran blacksmith",
                    "goals": ["craft fine weapons"],
                    "relationships": {"player": "neutral"},
                    "dialogue_style": "gruff but helpful"
                },
                "state": {
                    "npc_id": "marcus_blacksmith",
                    "current_location": "blacksmith_shop",
                    "current_activity": "working",
                    "mood": "focused"
                },
                "memory": {
                    "short_term": [],
                    "long_term": [],
                    "relationships_memory": {}
                }
            }
        } 