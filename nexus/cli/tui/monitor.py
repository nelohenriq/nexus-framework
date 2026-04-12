"""Real-time Monitoring for TUI."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import threading
import time


@dataclass(slots=True)
class MonitorEvent:
    event_type: str
    source: str
    data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class RealtimeMonitor:
    def __init__(self, max_events: int = 1000):
        self.events = []
        self.max_events = max_events
        self.subscribers = {}
        self._running = False
        self._thread = None

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def emit(self, event: MonitorEvent):
        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        callbacks = self.subscribers.get(event.event_type, [])
        for cb in callbacks:
            try:
                cb(event)
            except Exception:
                pass

    def get_recent(self, count: int = 50) -> List[MonitorEvent]:
        return self.events[-count:]

    def start(self, poll_interval: float = 0.1):
        self._running = True

    def stop(self):
        self._running = False


def create_monitor(max_events: int = 1000) -> RealtimeMonitor:
    return RealtimeMonitor(max_events=max_events)