"""Task Queue Lifecycle - Task management."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import queue
import threading


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class Task:
    id: str
    name: str
    payload: Any
    priority: int = 0
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Any = None
    error: Optional[str] = None


class TaskQueue:
    def __init__(self, max_workers: int = 4):
        self.queue = queue.PriorityQueue()
        self.tasks = {}
        self.max_workers = max_workers
        self._running = False
        self._workers = []

    def submit(self, task: Task) -> str:
        self.tasks[task.id] = task
        self.queue.put((-task.priority, task.id, task))
        return task.id

    def get(self, timeout: Optional[float] = None) -> Optional[Task]:
        try:
            _, _, task = self.queue.get(timeout=timeout)
            return task
        except queue.Empty:
            return None

    def update_status(self, task_id: str, status: TaskStatus, result: Any = None, error: Optional[str] = None):
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = status
            if status == TaskStatus.RUNNING:
                task.started_at = datetime.now().isoformat()
            elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                task.completed_at = datetime.now().isoformat()
                task.result = result
                task.error = error

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        tasks = list(self.tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda x: x.created_at, reverse=True)


def create_task_queue(max_workers: int = 4):
    return TaskQueue(max_workers=max_workers)