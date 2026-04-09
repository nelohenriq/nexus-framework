from __future__ import annotations
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import uuid
import queue


class MessagePriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


class MessageType(Enum):
    TASK = "task"
    RESULT = "result"
    STATUS = "status"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    BROADCAST = "broadcast"


@dataclass(slots=True)
class AgentMessage:
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: MessageType
    priority: MessagePriority
    content: dict[str, Any]
    timestamp: float = field(default_factory=time.monotonic)
    reply_to: Optional[str] = None
    ttl: int = 60

    def to_dict(self) -> dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "content": self.content,
        }


class MessageBus:
    _instance: Optional[MessageBus] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> MessageBus:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._queues = {}
                    cls._instance._subscribers = {}
                    cls._instance._bus_lock = threading.RLock()
        return cls._instance

    def register_agent(self, agent_id: str, max_queue_size: int = 1000) -> None:
        with self._bus_lock:
            if agent_id not in self._queues:
                self._queues[agent_id] = queue.Queue(maxsize=max_queue_size)
                self._subscribers[agent_id] = set()

    def unregister_agent(self, agent_id: str) -> bool:
        with self._bus_lock:
            if agent_id in self._queues:
                del self._queues[agent_id]
                del self._subscribers[agent_id]
            return True
        return False

    def send(self, message: AgentMessage) -> bool:
        with self._bus_lock:
            receiver = message.receiver_id
            if receiver not in self._queues:
                return False
            try:
                self._queues[receiver].put_nowait(message)
                return True
            except queue.Full:
                return False

    def receive(self, agent_id: str, timeout: float = 0.1) -> Optional[AgentMessage]:
        q = self._queues.get(agent_id)
        if not q:
            return None
        try:
            return q.get(timeout=timeout)
        except queue.Empty:
            return None

    def subscribe(self, subscriber_id: str, publisher_id: str) -> bool:
        with self._bus_lock:
            if publisher_id not in self._subscribers:
                self._subscribers[publisher_id] = set()
            self._subscribers[publisher_id].add(subscriber_id)
        return True

    def get_stats(self) -> dict[str, Any]:
        with self._bus_lock:
            return {"agents": len(self._queues), "subs": sum(len(s) for s in self._subscribers.values())}