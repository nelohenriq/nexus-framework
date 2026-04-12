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
from functools import lru_cache
import json
import hashlib


@dataclass(slots=True)
class MemoryLayer:
    """Base class for memory layers."""
    name: str
    token_budget: int
    always_loaded: bool = False
    data: Dict[str, Any] = field(default_factory=dict)
    _token_cache: Optional[int] = field(default=None, init=False, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "token_budget": self.token_budget, "always_loaded": self.always_loaded, "data": self.data}

    def estimate_tokens(self) -> int:
        """Estimate token count with caching."""
        if self._token_cache is None:
            content = json.dumps(self.data, default=str)
            self._token_cache = len(content) // 4
        return self._token_cache


@dataclass(slots=True)
class L0IdentityLayer(MemoryLayer):
    """L0: Identity - Who am I, current task (~50 tokens, always loaded)."""
    agent_id: str = ""
    role: str = ""
    current_task: str = ""
    session_start: str = field(default_factory=lambda: datetime.now().isoformat())
    _dict_cache: Optional[Dict] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        self.name = "L0_Identity"
        self.token_budget = 50
        self.always_loaded = True
        self.data = {"agent_id": self.agent_id, "role": self.role, "current_task": self.current_task}

    def to_dict(self) -> Dict[str, Any]:
        if self._dict_cache is None:
            self._dict_cache = {"name": self.name, "token_budget": self.token_budget, "always_loaded": self.always_loaded, "data": self.data, "agent_id": self.agent_id, "role": self.role, "current_task": self.current_task, "session_start": self.session_start}
        return self._dict_cache


@dataclass(slots=True)
class L1CriticalFactsLayer(MemoryLayer):
    """L1: Critical Facts - Key information (~120 tokens, always loaded)."""
    facts: Dict[str, Any] = field(default_factory=dict)
    _dict_cache: Optional[Dict] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        self.name = "L1_CriticalFacts"
        self.token_budget = 120
        self.always_loaded = True
        self.data = self.facts

    def add_fact(self, key: str, value: Any):
        """Add a critical fact."""
        self.facts[key] = value
        self.data[key] = value
        self._dict_cache = None
        self._token_cache = None

    def get_fact(self, key: str) -> Optional[Any]:
        return self.facts.get(key)


@dataclass(slots=True)
class L2RoomRecallLayer(MemoryLayer):
    """L2: Room Recall - Recent conversations (on-demand)."""
    messages: List[Dict[str, Any]] = field(default_factory=list)
    max_messages: int = 100

    def __post_init__(self):
        self.name = "L2_RoomRecall"
        self.token_budget = 500
        self.always_loaded = False
        self.data = {"messages": self.messages}

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        msg = {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        if metadata:
            msg.update(metadata)
        self.messages.append(msg)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
            self.data["messages"] = self.messages
        self._token_cache = None

    def get_recent(self, n: int = 10) -> List[Dict[str, Any]]:
        return self.messages[-n:]


@dataclass(slots=True)
class L3DeepSearchLayer(MemoryLayer):
    """L3: Deep Search - Historical data (on-demand)."""
    index_path: Optional[str] = None
    knowledge_base: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.name = "L3_DeepSearch"
        self.token_budget = 2000
        self.always_loaded = False
        self.data = {"knowledge_base": self.knowledge_base}

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        results = []
        query_lower = query.lower()
        kb = self.knowledge_base
        for key, value in kb.items():
            if query_lower in key.lower() or query_lower in str(value).lower():
                results.append({"key": key, "value": value})
        return results[:top_k]

    def add_knowledge(self, key: str, value: Any):
        self.knowledge_base[key] = value
        self.data["knowledge_base"] = self.knowledge_base
        self._token_cache = None


@dataclass(slots=True)
class MemoryStack:
    """Complete L0-L3 Memory Stack."""
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
        l0 = self.l0
        l1 = self.l1
        return {"l0": l0.to_dict() if l0 else {}, "l1": l1.to_dict() if l1 else {}}

    def get_full_context(self) -> Dict[str, Any]:
        l0, l1, l2, l3 = self.l0, self.l1, self.l2, self.l3
        return {"l0": l0.to_dict() if l0 else {}, "l1": l1.to_dict() if l1 else {}, "l2": l2.to_dict() if l2 else {}, "l3": l3.to_dict() if l3 else {}}

    def estimate_total_tokens(self) -> int:
        total = 0
        for layer in (self.l0, self.l1, self.l2, self.l3):
            if layer:
                total += layer.estimate_tokens()
        return total

    def to_dict(self) -> Dict[str, Any]:
        l0, l1, l2, l3 = self.l0, self.l1, self.l2, self.l3
        return {"l0": l0.to_dict() if l0 else None, "l1": l1.to_dict() if l1 else None, "l2": l2.to_dict() if l2 else None, "l3": l3.to_dict() if l3 else None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryStack":
        stack = cls()
        if "l0" in data and data["l0"]:
            stack.l0 = L0IdentityLayer(agent_id=data["l0"].get("agent_id", ""), role=data["l0"].get("role", ""), current_task=data["l0"].get("current_task", ""))
        if "l1" in data and data["l1"]:
            stack.l1 = L1CriticalFactsLayer(facts=data["l1"].get("data", {}))
        if "l2" in data and data["l2"]:
            stack.l2 = L2RoomRecallLayer(messages=data["l2"].get("messages", []))
        if "l3" in data and data["l3"]:
            stack.l3 = L3DeepSearchLayer(knowledge_base=data["l3"].get("knowledge_base", {}))
        return stack


def create_memory_stack(agent_id: str = "", role: str = "") -> MemoryStack:
    stack = MemoryStack()
    if agent_id or role:
        stack.l0 = L0IdentityLayer(agent_id=agent_id, role=role)
    return stack