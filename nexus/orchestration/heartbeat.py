"""Heartbeat Execution - Periodic health checks."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import threading
import time


@dataclass(slots=True)
class HeartbeatConfig:
    interval_seconds: float = 30.0
    max_missed: int = 3
    timeout_seconds: float = 5.0


@dataclass(slots=True)
class HeartbeatStatus:
    agent_id: str
    last_heartbeat: str
    missed_count: int = 0
    is_alive: bool = True


class HeartbeatMonitor:
    def __init__(self, config: Optional[HeartbeatConfig] = None):
        self.config = config or HeartbeatConfig()
        self.agents = {}
        self._running = False
        self._thread = None

    def register(self, agent_id: str):
        self.agents[agent_id] = HeartbeatStatus(agent_id=agent_id, last_heartbeat=datetime.now().isoformat())

    def heartbeat(self, agent_id: str):
        if agent_id in self.agents:
            self.agents[agent_id].last_heartbeat = datetime.now().isoformat()
            self.agents[agent_id].missed_count = 0
            self.agents[agent_id].is_alive = True

    def check_health(self) -> Dict[str, Any]:
        now = datetime.now()
        unhealthy = []
        for agent_id, status in self.agents.items():
            last = datetime.fromisoformat(status.last_heartbeat)
            elapsed = (now - last).total_seconds()
            if elapsed > self.config.interval_seconds:
                status.missed_count += 1
                if status.missed_count >= self.config.max_missed:
                    status.is_alive = False
                    unhealthy.append(agent_id)
        return {"healthy": len(unhealthy) == 0, "unhealthy_agents": unhealthy, "total_agents": len(self.agents)}

    def start_background(self):
        if self._running:
            return
        self._running = True
        def _monitor():
            while self._running:
                self.check_health()
                time.sleep(self.config.interval_seconds)
        self._thread = threading.Thread(target=_monitor, daemon=True)
        self._thread.start()

    def stop_background(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)


def create_heartbeat_monitor(config: Optional[HeartbeatConfig] = None):
    return HeartbeatMonitor(config=config)