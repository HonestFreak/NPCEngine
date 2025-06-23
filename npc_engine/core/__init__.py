"""
Core components of the NPC Engine
"""

# Only import if ADK is available
try:
    from .npc_agent import NPCAgent
    from .environment_manager import EnvironmentManager
    from .action_system import ActionSystem
    from .game_session import GameSession

    __all__ = ["NPCAgent", "EnvironmentManager", "ActionSystem", "GameSession"]
except ImportError:
    __all__ = [] 