"""
NPCEngine - World-class intelligent NPC backend framework powered by Google ADK

A sophisticated multi-agent orchestration system for creating intelligent,
personality-driven NPCs in games and interactive applications.

Features:
- Google ADK integration with Gemini LLM
- Multi-agent orchestration
- Dynamic personality modeling
- Flexible session persistence
- Production-ready REST API
- Real-time React dashboard

Example:
    >>> from npc_engine import NPCEngine, NPCData
    >>> engine = NPCEngine()
    >>> await engine.start()
"""

__version__ = "1.0.0"
__author__ = "NPCEngine Team"
__email__ = "team@npcengine.dev"
__license__ = "MIT"

import logging
import warnings
from typing import Optional

# Configure logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# ADK availability check
_ADK_AVAILABLE = False
_ADK_ERROR: Optional[str] = None

try:
    import google.adk
    _ADK_AVAILABLE = True
except ImportError as e:
    _ADK_ERROR = str(e)
    warnings.warn(
        f"Google ADK not available: {e}. "
        "Install with: pip install google-adk",
        ImportWarning,
        stacklevel=2
    )

# Core imports
from .models import (
    NPCData,
    NPCPersonality, 
    NPCState,
    NPCMemory,
    Environment,
    Location,
    GameEvent,
    Action,
    ActionResult
)

# Conditional imports based on ADK availability
if _ADK_AVAILABLE:
    try:
        from .core import (
            NPCAgent,
            GameSession,
            EnvironmentManager,
            ActionSystem
        )
        from .api import NPCEngineAPI
        
        __all__ = [
            # Core classes
            "NPCAgent",
            "GameSession", 
            "EnvironmentManager",
            "ActionSystem",
            "NPCEngineAPI",
            # Data models
            "NPCData",
            "NPCPersonality",
            "NPCState", 
            "NPCMemory",
            "Environment",
            "Location",
            "GameEvent",
            "Action",
            "ActionResult",
            # Utilities
            "is_adk_available",
            "get_adk_error"
        ]
    except ImportError as core_error:
        warnings.warn(
            f"Failed to import core components: {core_error}. "
            "Only data models are available.",
            ImportWarning,
            stacklevel=2
        )
        
        __all__ = [
            "NPCData", 
            "NPCPersonality",
            "NPCState",
            "NPCMemory", 
            "Environment",
            "Location",
            "GameEvent",
            "Action", 
            "ActionResult",
            "is_adk_available",
            "get_adk_error"
        ]
else:
    __all__ = [
        "NPCData",
        "NPCPersonality", 
        "NPCState",
        "NPCMemory",
        "Environment", 
        "Location",
        "GameEvent",
        "Action",
        "ActionResult",
        "is_adk_available", 
        "get_adk_error"
    ]

def is_adk_available() -> bool:
    """Check if Google ADK is available."""
    return _ADK_AVAILABLE

def get_adk_error() -> Optional[str]:
    """Get the error message if ADK is not available."""
    return _ADK_ERROR 