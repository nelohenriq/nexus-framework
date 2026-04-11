"""
NEXUS Framework - Core Agent

Core agent loop, memory, context, tools, and skills management.
"""

from __future__ import annotations

from .messages import Message, MessageRole, ConversationTurn
from .memory import MemoryManager, MemoryEntry
from .context import AgentContext, Checkpoint
from .tools import (
 ToolRegistry,
 ToolSpec,
 ToolResult,
 ToolError,
 PermissionLevel,
 tool as tool_decorator
)
from .agent import (
 AgentLoop,
 AgentConfig,
 AgentResponse,
 AgentState,
 ToolCallRequest
)

__all__ = [
 # Messages
 "Message", "MessageRole", "ConversationTurn",
 # Memory
 "MemoryManager", "MemoryEntry",
 # Context
 "AgentContext", "Checkpoint",
 # Tools
 "ToolRegistry", "ToolSpec", "ToolResult", "ToolError", "PermissionLevel",
 "tool_decorator",
 # Agent
 "AgentLoop", "AgentConfig", "AgentResponse", "AgentState", "ToolCallRequest",
]
