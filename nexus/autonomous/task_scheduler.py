"""Task Scheduler - Autonomous task scheduling."""

import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Callable
import heapq


class TaskPriority(int, Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class ScheduledTask:
    task_id: str
    name: str
    func: Callable[[], Any]
    priority: int = TaskPriority.NORMAL
    scheduled_time: float = 0.0
    interval: Optional[float] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.monotonic)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other):
        return (self.priority, self.scheduled_time) < (other.priority, other.scheduled_time)


class TaskScheduler:
    def __init__(self, max_workers: int = 4):
        self._tasks: dict[str, ScheduledTask] = {}
        self._queue: list[ScheduledTask] = []
        self._max_workers = max_workers
        self._running = False
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)

    def schedule(self, name: str, func: Callable[[], Any],
                priority: int = TaskPriority.NORMAL,
                delay: float = 0.0,
                interval: Optional[float] = None) -> str:
        task_id = str(uuid.uuid4())[:8]
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            func=func,
            priority=priority,
            scheduled_time=time.monotonic() + delay,
            interval=interval
        )
        with self._lock:
            self._tasks[task_id] = task
            heapq.heappush(self._queue, task)
            self._condition.notify()
        return task_id

    def cancel(self, task_id: str) -> bool:
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id].status = TaskStatus.CANCELLED
                return True
        return False

    def get_status(self, task_id: str) -> Optional[dict]:
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                return {
                    "task_id": task.task_id,
                    "name": task.name,
                    "status": task.status.value,
                    "result": task.result,
                    "error": task.error
                }
            return None

    def start(self):
        with self._lock:
            if self._running:
                return
            self._running = True
            for i in range(self._max_workers):
                t = threading.Thread(target=self._worker, daemon=True)
                t.start()