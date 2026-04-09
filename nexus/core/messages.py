"""
NEXUS Framework - Message Types

Unified message format for agent communication.
Optimized for performance.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class MessageRole(str, Enum):
    """Role of a message sender."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass(slots=True)
class Message:
    """
    Unified message format.
    Optimized with __slots__ for memory efficiency.
    """
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: list[dict] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    _timestamp: float = field(default_factory=time.monotonic, repr=False)
    _api_format_cache: dict | None = field(default=None, init=False, repr=False, compare=False)

    def to_api_format(self) -> dict:
        """Convert to LLM API format with caching."""
        if self._api_format_cache is not None:
            return self._api_format_cache
        result = {"role": self.role.value, "content": self.content}
        if self.name:
            result["name"] = self.name
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        if self.role == MessageRole.TOOL and self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        self._api_format_cache = result
        return result

    @classmethod
    def from_api_format(cls, data: dict) -> "Message":
        """Create from LLM API format."""
        return cls(
            role=MessageRole(data["role"]),
            content=data.get("content") or "",
            name=data.get("name"),
            tool_call_id=data.get("tool_call_id"),
            tool_calls=data.get("tool_calls", [])[:]
        )

    def clear_cache(self) -> None:
        """Clear API format cache if message is modified."""
        self._api_format_cache = None


@dataclass
class ConversationTurn:
    """A single turn in the conversation."""
    messages: list[Message] = field(default_factory=list)
    response: Optional[Message] = None
    tool_results: list[Message] = field(default_factory=list)
    tokens_used: int = 0
    latency_ms: float = 0.0


__all__ = ["MessageRole", "Message", "ConversationTurn"]
