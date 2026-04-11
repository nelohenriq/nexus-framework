"""L0-L3 Memory Stack Implementation.

Implements the MemPalace-inspired tiered memory architecture for efficient
context management. Achieves ~170 tokens for session start instead of
thousands of tokens.

Memory Tiers:
- L0: Identity (~50 tokens, always loaded) - Agent identity, current task
- L1: Critical Facts (~120 tokens, always loaded) - Key information
- L2: Room Recall (on-demand) - Recent conversations, context
- L3: Deep Search (on-demand) - Historical data, semantic search
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import json
import hashlib


@dataclass
class MemoryLayer:
    """Base class for memory layers."""
    name: str
    token_budget: int
    always_loaded: bool = False
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "token_budget": self.token_budget,
            "always_loaded": self.always_loaded,
            "data": self.data
        }

    def estimate_tokens(self) -> int:
        """Estimate token count for this layer."""
        content = json.dumps(self.data, default=str)
        # Approximate: ~4 chars per token
        return len(content) // 4


@dataclass
class L0IdentityLayer(MemoryLayer):
    """L0: Identity - Who am I, current task (~50 tokens, always loaded).

    Contains:
    - Agent ID and role
    - Current task description
    - Session context
    """
    agent_id: str = ""
    role: str = ""
    current_task: str = ""
    session_start: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        self.name = "L0_Identity"
        self.token_budget = 50
        self.always_loaded = True
        self.data = {
            "agent_id": self.agent_id,
            "role": self.role,
            "current_task": self.current_task
        }

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update({
            "agent_id": self.agent_id,
            "role": self.role,
            "current_task": self.current_task,
            "session_start": self.session_start
        })
        return d


@dataclass
class L1CriticalFactsLayer(MemoryLayer):
    """L1: Critical Facts - Key information (~120 tokens, always loaded).

    Contains:
    - User preferences
    - Project context
    - Critical constraints
    - Active goals
    """
    facts: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.name = "L1_CriticalFacts"
        self.token_budget = 120
        self.always_loaded = True
        self.data = self.facts

    def add_fact(self, key: str, value: Any):
        """Add a critical fact."""
        self.facts[key] = value
        self.data[key] = value

    def get_fact(self, key: str) -> Optional[Any]:
        """Get a critical fact."""
        return self.facts.get(key)


@dataclass
class L2RoomRecallLayer(MemoryLayer):
    """L2: Room Recall - Recent conversations (on-demand).

    Contains:
    - Recent messages
    - Working memory
    - Current session data
    """
    messages: List[Dict[str, Any]] = field(default_factory=list)
    max_messages: int = 100

    def __post_init__(self):
        self.name = "L2_RoomRecall"
        self.token_budget = 500
        self.always_loaded = False
        self.data = {"messages": self.messages}

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to working memory."""
        msg = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        if metadata:
            msg.update(metadata)
        self.messages.append(msg)
        # Keep within limits
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        self.data["messages"] = self.messages

    def get_recent(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get N most recent messages."""
        return self.messages[-n:]


@dataclass
class L3DeepSearchLayer(MemoryLayer):
    """L3: Deep Search - Historical data (on-demand).

    Contains:
    - Historical conversations
    - Knowledge base
    - Semantic search index
    """
    index_path: Optional[str] = None
    knowledge_base: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.name = "L3_DeepSearch"
        self.token_budget = 2000
        self.always_loaded = False
        self.data = {"knowledge_base": self.knowledge_base}

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search knowledge base (placeholder for vector search)."""
        # Simple keyword search for now
        results = []
        query_lower = query.lower()
        for key, value in self.knowledge_base.items():
            if query_lower in key.lower() or query_lower in str(value).lower():
                results.append({"key": key, "value": value})
        return results[:top_k]

    def add_knowledge(self, key: str, value: Any):
        """Add knowledge to the base."""
        self.knowledge_base[key] = value
        self.data["knowledge_base"] = self.knowledge_base


@dataclass
class MemoryStack:
    """Complete L0-L3 Memory Stack.

    Implements efficient tiered memory that reduces context from thousands
    of tokens to ~170 tokens for session start.

    Usage:
        stack = MemoryStack()
        stack.l0 = L0IdentityLayer(agent_id="agent_001", role="developer")
        stack.l1.add_fact("user_preference", "concise responses")
        stack.l2.add_message("user", "Hello!")

        # Get minimal context for session start
        context = stack.get_session_context()  # ~170 tokens
    """
    l0: Optional[L0IdentityLayer] = None
    l1: Optional[L1CriticalFactsLayer] = None
    l2: Optional[L2RoomRecallLayer] = None
    l3: Optional[L3DeepSearchLayer] = None

    def __post_init__(self):
        if self.l0 is None:
            self.l0 = L0IdentityLayer()
        if self.l1 is None:
            self.l1 = L1CriticalFactsLayer()
        if self.l2 is None:
            self.l2 = L2RoomRecallLayer()
        if self.l3 is None:
            self.l3 = L3DeepSearchLayer()

    def get_session_context(self) -> Dict[str, Any]:
        """Get minimal context for session start (~170 tokens).

        Returns only L0 and L1 layers which are always loaded.
        L2 and L3 are loaded on-demand.
        """
        return {
            "l0": self.l0.to_dict() if self.l0 else {},
            "l1": self.l1.to_dict() if self.l1 else {}
        }

    def get_full_context(self) -> Dict[str, Any]:
        """Get full context including all layers."""
        return {
            "l0": self.l0.to_dict() if self.l0 else {},
            "l1": self.l1.to_dict() if self.l1 else {},
            "l2": self.l2.to_dict() if self.l2 else {},
            "l3": self.l3.to_dict() if self.l3 else {}
        }

    def estimate_total_tokens(self) -> int:
        """Estimate total token count across all layers."""
        total = 0
        for layer in [self.l0, self.l1, self.l2, self.l3]:
            if layer:
                total += layer.estimate_tokens()
        return total

    def to_dict(self) -> Dict[str, Any]:
        return {
            "l0": self.l0.to_dict() if self.l0 else None,
            "l1": self.l1.to_dict() if self.l1 else None,
            "l2": self.l2.to_dict() if self.l2 else None,
            "l3": self.l3.to_dict() if self.l3 else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryStack":
        stack = cls()
        if "l0" in data and data["l0"]:
            stack.l0 = L0IdentityLayer(
                agent_id=data["l0"].get("agent_id", ""),
                role=data["l0"].get("role", ""),
                current_task=data["l0"].get("current_task", "")
            )
        if "l1" in data and data["l1"]:
            stack.l1 = L1CriticalFactsLayer(facts=data["l1"].get("data", {}))
        if "l2" in data and data["l2"]:
            stack.l2 = L2RoomRecallLayer(messages=data["l2"].get("messages", []))
        if "l3" in data and data["l3"]:
            stack.l3 = L3DeepSearchLayer(knowledge_base=data["l3"].get("knowledge_base", {}))
        return stack


def create_memory_stack(agent_id: str = "", role: str = "") -> MemoryStack:
    """Create a new memory stack with optional identity."""
    stack = MemoryStack()
    if agent_id or role:
        stack.l0 = L0IdentityLayer(agent_id=agent_id, role=role)
    return stack
