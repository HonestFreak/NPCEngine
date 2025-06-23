"""
API models for frontend communication
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from .npc_models import NPCData
from .environment_models import Environment
from .action_models import ActionDefinition, ActionResult


class EventRequest(BaseModel):
    """Request structure for game events from frontend"""
    session_id: str = Field(..., description="Game session identifier")
    event_id: Optional[str] = Field(None, description="Unique event ID (generated if not provided)")
    
    # Event details
    action: str = Field(..., description="Action that occurred")
    initiator: str = Field(..., description="Who initiated the action (player ID or NPC ID)")
    target: Optional[str] = Field(None, description="Target of the action (NPC ID, location, item)")
    location: str = Field(..., description="Where the event took place")
    
    # Action properties
    action_properties: Dict[str, Any] = Field(default_factory=dict, description="Properties specific to the action")
    
    # Context
    additional_context: Dict[str, Any] = Field(default_factory=dict, description="Additional context for the event")
    priority: int = Field(5, description="Event priority (1=low, 10=high)")
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "game_session_123",
                "action": "speak",
                "initiator": "player",
                "target": "marcus_blacksmith",
                "location": "blacksmith_shop",
                "action_properties": {
                    "message": "Hello, can you repair my sword?",
                    "tone": "polite"
                },
                "priority": 7
            }
        }


class NPCResponse(BaseModel):
    """Response from an NPC to an event"""
    npc_id: str = Field(..., description="ID of the responding NPC")
    action_result: ActionResult = Field(..., description="The action the NPC decided to take")
    reasoning: str = Field("", description="Why the NPC chose this action")
    emotion: str = Field("neutral", description="NPC's emotional state after the event")
    relationship_changes: Dict[str, str] = Field(default_factory=dict, description="Changes in relationships")


class EventResponse(BaseModel):
    """Complete response to a game event"""
    event_id: str = Field(..., description="ID of the processed event")
    session_id: str = Field(..., description="Game session identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the response was generated")
    
    # Immediate response (low latency)
    primary_npc_response: Optional[NPCResponse] = Field(None, description="Response from the primary affected NPC")
    immediate_message: Optional[str] = Field(None, description="Immediate message to display")
    
    # Full processing results
    all_npc_responses: List[NPCResponse] = Field(default_factory=list, description="Responses from all affected NPCs")
    environment_updates: Dict[str, Any] = Field(default_factory=dict, description="Updates to environment state")
    side_effects: List[Dict[str, Any]] = Field(default_factory=list, description="Additional triggered effects")
    
    # Status
    processing_complete: bool = Field(False, description="Whether background processing is complete")
    error_message: Optional[str] = Field(None, description="Error message if something went wrong")
    
    class Config:
        schema_extra = {
            "example": {
                "event_id": "event_12345",
                "session_id": "game_session_123",
                "primary_npc_response": {
                    "npc_id": "marcus_blacksmith",
                    "action_result": {
                        "success": True,
                        "action": {
                            "action_type": "speak",
                            "properties": {"message": "Of course! Let me take a look at it."},

                        },
                        "npc_id": "marcus_blacksmith",
                        "message": "Marcus examines your sword and nods."
                    },
                    "reasoning": "Player politely asked for help, which aligns with my helpful nature",
                    "emotion": "helpful"
                },
                "immediate_message": "Marcus looks up from his work and smiles.",
                "processing_complete": True
            }
        }


class SessionPersistenceConfig(BaseModel):
    """Configuration for session persistence"""
    type: str = Field(..., description="Persistence type: 'memory', 'database', or 'vertexai'")
    database_url: Optional[str] = Field(None, description="Database URL for database persistence")
    vertexai_project: Optional[str] = Field(None, description="GCP Project ID for Vertex AI persistence")
    vertexai_location: Optional[str] = Field(default="us-central1", description="GCP location for Vertex AI")
    vertexai_corpus: Optional[str] = Field(None, description="RAG Corpus ID for enhanced memory (optional)")


class SessionConfig(BaseModel):
    """Configuration for a new game session"""
    session_id: str = Field(..., description="Unique session identifier")
    game_title: str = Field(..., description="Title/name of the game")
    
    # Session persistence configuration
    persistence: SessionPersistenceConfig = Field(default_factory=lambda: SessionPersistenceConfig(type="memory"), 
                                                  description="Session persistence configuration")
    
    # NPCs to initialize
    npcs: List[NPCData] = Field(..., description="NPCs to create in this session")
    
    # Environment setup
    environment: Environment = Field(..., description="Initial environment state")
    
    # Available actions
    available_actions: List[ActionDefinition] = Field(..., description="Actions that NPCs can perform")
    
    # Game-specific settings
    settings: Dict[str, Any] = Field(default_factory=dict, description="Game-specific configuration")
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "game_session_123",
                "game_title": "Medieval Adventure",
                "npcs": [
                    {
                        "personality": {
                            "name": "Marcus the Blacksmith",
                            "role": "blacksmith",
                            "personality_traits": ["helpful", "hardworking"],
                            "background": "Village blacksmith for 20 years"
                        },
                        "state": {
                            "npc_id": "marcus_blacksmith",
                            "current_location": "blacksmith_shop",
                            "current_activity": "working"
                        },
                        "memory": {
                            "short_term": [],
                            "long_term": []
                        }
                    }
                ],
                "environment": {
                    "session_id": "game_session_123",
                    "time_of_day": "morning",
                    "weather": "sunny"
                },
                "settings": {
                    "difficulty": "normal",
                    "npc_reaction_speed": "fast"
                }
            }
        }


class SessionInfo(BaseModel):
    """Information about a game session"""
    session_id: str = Field(..., description="Session identifier")
    game_title: str = Field(..., description="Game title")
    created_at: datetime = Field(..., description="When session was created")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    npc_count: int = Field(..., description="Number of NPCs in session")
    total_events: int = Field(..., description="Total events processed")
    status: str = Field(..., description="Session status (active, paused, ended)")


class SessionStatusResponse(BaseModel):
    """Response for session status requests"""
    session_info: SessionInfo = Field(..., description="Basic session information")
    active_npcs: List[str] = Field(..., description="Currently active NPC IDs")
    current_environment: Dict[str, Any] = Field(..., description="Current environment snapshot")
    recent_events: List[Dict[str, Any]] = Field(..., description="Recent events in the session")


class BatchEventRequest(BaseModel):
    """Request for processing multiple events at once"""
    session_id: str = Field(..., description="Game session identifier")
    events: List[EventRequest] = Field(..., description="List of events to process")
    process_sequentially: bool = Field(False, description="Whether to process events in order")


class BatchEventResponse(BaseModel):
    """Response for batch event processing"""
    session_id: str = Field(..., description="Game session identifier")
    responses: List[EventResponse] = Field(..., description="Responses for each event")
    errors: List[Dict[str, str]] = Field(default_factory=list, description="Any errors that occurred")
    processing_time: float = Field(..., description="Total processing time in seconds")


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    uptime: float = Field(..., description="Uptime in seconds")
    active_sessions: int = Field(..., description="Number of active sessions")
    total_npcs: int = Field(..., description="Total NPCs across all sessions")


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="When error occurred")
    request_id: Optional[str] = Field(None, description="Request ID for tracking") 