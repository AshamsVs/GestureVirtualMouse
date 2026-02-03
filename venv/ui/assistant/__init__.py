"""
Ava Assistant Package
Central intelligence system for the AI desktop assistant
"""

from .personality import AvaPersonality, create_personality
from .command_registry import CommandRegistry, Command, CommandCategory, create_registry
from .assistant_core import create_assistant, AvaCore, AssistantState

__all__ = [
    'AvaPersonality',
    'create_personality',
    'CommandRegistry',
    'Command',
    'CommandCategory',
    'create_registry',
    'AvaCore',
    'AssistantState',
    'create_assistant'
]

__version__ = '1.0.0'
__assistant_name__ = 'Ava'