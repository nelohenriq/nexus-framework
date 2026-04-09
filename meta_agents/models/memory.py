#"""Memory provider interface for meta-agentic SDK."""

from dataclasses import dataclass
from typing import Protocol, List, Dict, Any, Optional


@dataclass
class MemoryEvent:
    """Represents a memory event to be stored."""
    id: str
    project_id: str
    agent_id: str
    session_id: str
    timestamp: float
    content: str
    metadata: Dict[str, Any]


@dataclass
class MemoryHit:
    """Represents a search result from memory."""
    event: MemoryEvent
    score: float


@dataclass
class ForgetCriteria:
    """Criteria for forgetting memories."""
    project_id: Optional[str] = None
    before_timestamp: Optional[float] = None
    tag: Optional[str] = None


class MemoryProvider(Protocol):
    """Protocol defining the memory provider interface."""
    def store(self, event: MemoryEvent) -> None:
        """Store a memory event."""
        ...

    def search(self, query: str, *, filters: Dict[str, Any] | None = None) -> List[MemoryHit]:
        """Search memories by query with optional filters."""
        ...

    def summarize_session(self, session_id: str) -> str:
        """Summarize a session's memories."""
        ...

    def forget(self, criteria: ForgetCriteria) -> int:
        """Forget memories matching criteria. Returns count of forgotten items."""
        ...
