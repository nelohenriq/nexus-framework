"""Daemon Polling - Background polling."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import threading
import time


@dataclass(slots=True)
class PollJob:
    name: str
    func: Callable[[], Any]
    interval_seconds: float = 60.0
    enabled: bool = True
    last_run: Optional[str] = None
    last_result: Any = None


class DaemonPoller:
    def __init__(self):
        self.jobs = {}
        self._running = False
        self._thread = None

    def register(self, name: str, func: Callable, interval_seconds: float = 60.0):
        self.jobs[name] = PollJob(name=name, func=func, interval_seconds=interval_seconds)

    def unregister(self, name: str):
        if name in self.jobs:
            del self.jobs[name]

    def run_job(self, name: str) -> Any:
        job = self.jobs.get(name)
        if not job or not job.enabled:
            return None
        try:
            result = job.func()
            job.last_run = datetime.now().isoformat()
            job.last_result = result
            return result
        except Exception as e:
            job.last_result = {"error": str(e)}
            return None

    def start(self, check_interval: float = 1.0):
        if self._running:
            return
        self._running = True
        def _poll():
            while self._running:
                now = datetime.now()
                for job in self.jobs.values():
                    if not job.enabled:
                        continue
                    if job.last_run:
                        last = datetime.fromisoformat(job.last_run)
                        elapsed = (now - last).total_seconds()
                        if elapsed < job.interval_seconds:
                            continue
                    self.run_job(job.name)
                time.sleep(check_interval)
        self._thread = threading.Thread(target=_poll, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)


def create_daemon_poller():
    return DaemonPoller()