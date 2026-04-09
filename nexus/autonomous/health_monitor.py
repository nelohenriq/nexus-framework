"""Health Monitor - System health monitoring and alerting."""

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Callable


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass(slots=True)
class HealthCheck:
    name: str
    status: HealthStatus = HealthStatus.HEALTHY
    message: str = ""
    last_check: float = 0.0
    latency_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class HealthMonitor:
    def __init__(self, check_interval: float = 30.0):
        self._checks: dict[str, HealthCheck] = {}
        self._callbacks: dict[str, list[Callable]] = {}
        self._interval = check_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()

    def register_check(self, name: str, check_func: Callable[[], HealthCheck]) -> str:
        with self._lock:
            check_id = f"check_{len(self._checks)}_{name}"
            self._checks[check_id] = HealthCheck(name=name)
            self._callbacks[check_id] = [check_func]
            return check_id

    def run_check(self, check_id: str) -> Optional[HealthCheck]:
        with self._lock:
            if check_id not in self._checks:
                return None
            callbacks = self._callbacks.get(check_id, [])
            if not callbacks:
                return None
            start = time.monotonic()
            try:
                result = callbacks[0]()
                result.latency_ms = (time.monotonic() - start) * 1000
                result.last_check = time.monotonic()
                self._checks[check_id] = result
                return result
            except Exception as e:
                check = self._checks[check_id]
                check.status = HealthStatus.UNHEALTHY
                check.message = str(e)
                check.latency_ms = (time.monotonic() - start) * 1000
                check.last_check = time.monotonic()
                return check

    def get_status(self) -> dict[str, Any]:
        with self._lock:
            statuses = {cid: c.status.value for cid, c in self._checks.items()}
            overall = HealthStatus.HEALTHY
            for c in self._checks.values():
                if c.status == HealthStatus.CRITICAL:
                    overall = HealthStatus.CRITICAL
                    break
                elif c.status == HealthStatus.UNHEALTHY:
                    overall = HealthStatus.UNHEALTHY
                elif c.status == HealthStatus.DEGRADED and overall == HealthStatus.HEALTHY:
                    overall = HealthStatus.DEGRADED
            return {"overall": overall.value, "checks": statuses, "count": len(self._checks), "timestamp": time.monotonic()}