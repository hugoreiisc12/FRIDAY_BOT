"""Backward-compatible shim: re-export ConversationManager and symbols
from the canonical implementation in `ai.conversation_manager`.
"""

from ai.conversation_manager import (
    ConversationManager,
    EstadoBot,
    ModoAcao,
    ContextoConversa,
    PROMPTS,
)

__all__ = ["ConversationManager", "EstadoBot", "ModoAcao", "ContextoConversa", "PROMPTS"]
