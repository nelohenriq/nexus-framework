from __future__ import annotations
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import uuid


class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass(slots=True)
class AgentInfo:
    agent_id: str
    name: str
    capabilities: list[str] = field(default_factory=list)
    status: AgentStatus = AgentStatus.IDLE
    last_heartbeat: float = field(default_factory=time.monotonic)
    metadata: dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[str] = None
    children: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "capabilities": self.capabilities,
            "status": self.status.value,
            "last_heartbeat": self.last_heartbeat,
            "metadata": self.metadata,
            "parent_id": self.parent_id,
            "children": self.children,
        }


class AgentRegistry:
    """Thread-safe agent registry with RLock for concurrent access."""
    _instance: Optional[AgentRegistry] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> AgentRegistry:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._agents = {}
                    cls._instance._by_capability = {}
                    cls._instance._registry_lock = threading.RLock()
        return cls._instance

    def register(self, name: str, capabilities: list[str],
        parent_id: Optional[str] = None,
        metadata: Optional[dict] = None) -> str:
        agent_id = str(uuid.uuid4())
        agent_info = AgentInfo(
            agent_id=agent_id, name=name,
            capabilities=capabilities,
            metadata=metadata or {}, parent_id=parent_id)
        with self._registry_lock:
            self._agents[agent_id] = agent_info
            for cap in capabilities:
                if cap not in self._by_capability:
                    self._by_capability[cap] = set()
                self._by_capability[cap].add(agent_id)
            if parent_id and parent_id in self._agents:
                self._agents[parent_id].children.append(agent_id)
        return agent_id

    def unregister(self, agent_id: str) -> bool:
        with self._registry_lock:
            if agent_id not in self._agents:
                return False
            agent = self._agents.pop(agent_id)
            for cap in agent.capabilities:
                self._by_capability.get(cap, set()).discard(agent_id)
            if agent.parent_id and agent.parent_id in self._agents:
                self._agents[agent.parent_id].children.remove(agent_id)
            return True

    def get(self, agent_id: str) -> Optional[AgentInfo]:
        """Thread-safe get by ID."""
        with self._registry_lock:
            return self._agents.get(agent_id)

    def find_by_capability(self, capability: str) -> list[AgentInfo]:
        """Thread-safe find by capability."""
        with self._registry_lock:
            ids = self._by_capability.get(capability, set())
            return [self._agents[i] for i in ids if i in self._agents]

    def find_best_for_task(self, required: list[str]) -> Optional[AgentInfo]:
        """Thread-safe find best agent for task."""
        with self._registry_lock:
            candidates = None
            for cap in required:
                agents = self._by_capability.get(cap, set())
                candidates = agents if candidates is None else candidates & agents
            if not candidates:
                return None
            for aid in candidates:
                agent = self._agents.get(aid)
                if agent and agent.status == AgentStatus.IDLE:
                    return agent
            return None

    def get_all(self) -> list[AgentInfo]:
        """Thread-safe get all agents."""
        with self._registry_lock:
            return list(self._agents.values())

    def count(self) -> int:
        """Thread-safe count of agents."""
        with self._registry_lock:
            return len(self._agents)

    def update_status(self, agent_id: str, status: AgentStatus) -> bool:
        """Thread-safe status update."""
        with self._registry_lock:
            if agent_id in self._agents:
                self._agents[agent_id].status = status
                self._agents[agent_id].last_heartbeat = time.monotonic()
                return True
            return False


__all__ = ["AgentRegistry", "AgentInfo", "AgentStatus"]