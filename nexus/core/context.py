"""
NEXUS Framework - Agent Context

Conversation context management with checkpointing.
"""

from __future__ import annotations

import time
import threading
from dataclasses import dataclass, field
from typing import Any, Optional
from pathlib import Path

from .messages import Message, MessageRole, ConversationTurn
from .memory import MemoryManager


@dataclass
class Checkpoint:
    """Agent state checkpoint."""
    checkpoint_id: str
    timestamp: float
    messages: list[Message]
    metadata: dict = field(default_factory=dict)


class AgentContext:
    """
    Agent conversation context with checkpointing.
    Supports save/restore for long-running tasks.
    """

    def __init__(self, agent_id: str, memory: Optional[MemoryManager] = None) -> None:
        self.agent_id = agent_id
        self._messages: list[Message] = []
        self._turns: list[ConversationTurn] = []
        self._memory = memory
        self._lock = threading.Lock()
        self._metadata: dict[str, Any] = {}
        self._created_at = time.monotonic()

    def add_message(self, message: Message) -> None:
        """Add a message to the context."""
        with self._lock:
            self._messages.append(message)

    def get_messages(self, limit: Optional[int] = None) -> list[Message]:
        """Get messages from context."""
        with self._lock:
            if limit:
                return self._messages[-limit:]
            return list(self._messages)

    def clear(self) -> None:
        """Clear the context."""
        with self._lock:
            self._messages.clear()
            self._turns.clear()

    def create_checkpoint(self) -> Checkpoint:
        """Create a checkpoint of current state."""
        import uuid
        with self._lock:
            return Checkpoint(
                checkpoint_id=str(uuid.uuid4()),
                timestamp=time.monotonic(),
                messages=list(self._messages),
                metadata=dict(self._metadata)
            )

    def restore_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Restore from a checkpoint."""
        with self._lock:
            self._messages = list(checkpoint.messages)
            self._metadata = dict(checkpoint.metadata)

    def save_checkpoint(self, name: str) -> bool:
        """Save checkpoint to memory."""
        if not self._memory:
            return False
        checkpoint = self.create_checkpoint()
        self._memory.save(f"checkpoint:{name}", {
            "checkpoint_id": checkpoint.checkpoint_id,
            "timestamp": checkpoint.timestamp,
            "messages": [m.to_api_format() for m in checkpoint.messages],
            "metadata": checkpoint.metadata
        }, area="checkpoints")
        return True

    def load_checkpoint(self, name: str) -> Optional[Checkpoint]:
        """Load checkpoint from memory."""
        if not self._memory:
            return None
        data = self._memory.load(f"checkpoint:{name}")
        if not data:
            return None
        return Checkpoint(
            checkpoint_id=data["checkpoint_id"],
            timestamp=data["timestamp"],
            messages=[Message.from_api_format(m) for m in data["messages"]],
            metadata=data["metadata"]
        )

    def get_token_count(self) -> int:
        """Estimate token count for all messages."""
        total = 0
        for msg in self._messages:
            total += len(msg.content.split()) # Rough estimate
        return total


__all__ = ["Checkpoint", "AgentContext"]
