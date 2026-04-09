"""Self-Healing Manager - Auto-recovery from errors."""

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Callable


class RecoveryStrategy(str, Enum):
    RETRY = "retry"
    FALLBACK = "fallback"
    RESTART = "restart"
    ESCALATE = "escalate"
    IGNORE = "ignore"


@dataclass(slots=True)
class ErrorContext:
    error_type: str
    error_message: str
    component: str
    timestamp: float = field(default_factory=time.monotonic)
    retry_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class SelfHealingManager:
    def __init__(self, max_retries: int = 3, backoff_base: float = 1.0):
        self._handlers: dict[str, Callable] = {}
        self._strategies: dict[str, RecoveryStrategy] = {}
        self._fallbacks: dict[str, Callable] = {}
        self._max_retries = max_retries
        self._backoff_base = backoff_base
        self._error_history: list[ErrorContext] = []
        self._lock = threading.RLock()

    def register_handler(self, error_type: str, handler: Callable[[ErrorContext], bool]) -> str:
        handler_id = f"handler_{error_type}_{len(self._handlers)}"
        self._handlers[error_type] = handler
        return handler_id

    def handle_error(self, error: Exception, component: str, **metadata) -> bool:
        ctx = ErrorContext(
            error_type=type(error).__name__,
            error_message=str(error),
            component=component,
            metadata=metadata
        )
        with self._lock:
            self._error_history.append(ctx)
            strategy = self._strategies.get(component, RecoveryStrategy.RETRY)
            if strategy == RecoveryStrategy.IGNORE:
                return True
            elif strategy == RecoveryStrategy.RETRY:
                return self._retry(ctx, error)
            elif strategy == RecoveryStrategy.FALLBACK:
                return self._fallback(ctx, component)
            elif strategy == RecoveryStrategy.ESCALATE:
                return False
        return False

    def _retry(self, ctx: ErrorContext, error: Exception) -> bool:
        handler = self._handlers.get(ctx.error_type)
        if not handler:
            return False
        while ctx.retry_count < self._max_retries:
            ctx.retry_count += 1
            backoff = self._backoff_base * (2 ** (ctx.retry_count - 1))
            time.sleep(backoff)
            try:
                if handler(ctx):
                    return True
            except Exception:
                continue
        return False

    def _fallback(self, ctx: ErrorContext, component: str) -> bool:
        fallback = self._fallbacks.get(component)
        if fallback:
            try:
                fallback(ctx)
                return True
            except Exception:
                return False
        return False

    def get_error_history(self, limit: int = 100) -> list[dict]:
        with self._lock:
            return [
                {
                    "error_type": e.error_type,
                    "message": e.error_message,
                    "component": e.component,
                    "timestamp": e.timestamp,
                    "retries": e.retry_count
                }
            for e in self._error_history[-limit:]
        ]