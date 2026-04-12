"""Dream Cycle Implementation - Nightly Autonomous Maintenance."""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, time
import threading
import time as time_module


@dataclass(slots=True)
class DreamTask:
    name: str
    func: Callable
    interval_hours: float = 24.0
    last_run: Optional[datetime] = None
    enabled: bool = True


@dataclass(slots=True)
class DreamResult:
    task_name: str
    success: bool
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class DreamCycle:
    """Nightly autonomous maintenance inspired by GBrain."""

    def __init__(self):
        self.tasks: Dict[str, DreamTask] = {}
        self.results: List[DreamResult] = []
        self.running = False
        self._thread: Optional[threading.Thread] = None

    def register_task(self, name: str, func: Callable, interval_hours: float = 24.0):
        self.tasks[name] = DreamTask(name=name, func=func, interval_hours=interval_hours)

    def run_task(self, task_name: str) -> DreamResult:
        if task_name not in self.tasks:
            return DreamResult(task_name=task_name, success=False, message="Task not found")
        task = self.tasks[task_name]
        if not task.enabled:
            return DreamResult(task_name=task_name, success=False, message="Task disabled")
        try:
            result = task.func()
            task.last_run = datetime.now()
            return DreamResult(task_name=task_name, success=True, message="Completed", data=result or {})
        except Exception as e:
            return DreamResult(task_name=task_name, success=False, message=str(e))

    def run_all_tasks(self) -> List[DreamResult]:
        results = []
        for task_name in self.tasks:
            result = self.run_task(task_name)
            results.append(result)
            self.results.append(result)
        return results

    def start_background(self, check_interval: int = 3600):
        self.running = True
        def _run_cycle():
            while self.running:
                self.run_all_tasks()
                time_module.sleep(check_interval)
        self._thread = threading.Thread(target=_run_cycle, daemon=True)
        self._thread.start()

    def stop_background(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)


def create_dream_cycle() -> DreamCycle:
    return DreamCycle()