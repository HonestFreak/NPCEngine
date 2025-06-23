"""
NPC Engine - Intelligent NPC backend framework powered by Google ADK
"""

__version__ = "0.1.0"
__author__ = "NPC Engine Team"

# Only import core classes if ADK is available
try:
    from .core.npc_agent import NPCAgent
    from .core.environment_manager import EnvironmentManager  
    from .core.action_system import ActionSystem
    from .core.game_session import GameSession
    from .api.npc_api import NPCEngineAPI
    
    __all__ = [
        "NPCAgent",
        "EnvironmentManager", 
        "ActionSystem",
        "GameSession",
        "NPCEngineAPI"
    ]
except ImportError as e:
    # ADK not available, only expose models
    print(f"Warning: Google ADK not available ({e}). Only data models will be accessible.")
    __all__ = [] 