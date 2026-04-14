"""Self-Healing Manager - Auto-recovery from errors (Async-compatible)."""

import asyncio
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
    """Async-compatible self-healing manager with non-blocking retries."""

    def __init__(self, max_retries: int = 3, backoff_base: float = 1.0):
        self._handlers: dict[str, Callable] = {}
        self._async_handlers: dict[str, Callable] = {}
        self._strategies: dict[str, RecoveryStrategy] = {}
        self._fallbacks: dict[str, Callable] = {}
        self._async_fallbacks: dict[str, Callable] = {}
        self._max_retries = max_retries
        self._backoff_base = backoff_base
        self._error_history: list[ErrorContext] = []
        self._lock = threading.RLock()

    def register_handler(self, error_type: str, handler: Callable, is_async: bool = False) -> str:
        """Register a sync or async error handler."""
        handler_id = f"handler_{error_type}_{len(self._handlers)}"
        if is_async:
            self._async_handlers[error_type] = handler
        else:
            self._handlers[error_type] = handler
        return handler_id

    async def handle_error(self, error: Exception, component: str, **metadata) -> bool:
        """Handle an error asynchronously with non-blocking retries."""
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
            return await self._retry(ctx, error)
        elif strategy == RecoveryStrategy.FALLBACK:
            return await self._fallback(ctx, component)
        elif strategy == RecoveryStrategy.ESCALATE:
            return False
        return False

    async def _retry(self, ctx: ErrorContext, error: Exception) -> bool:
        """Retry with exponential backoff (async, non-blocking)."""
        handler = self._async_handlers.get(ctx.error_type)
        is_async = True
        if not handler:
            handler = self._handlers.get(ctx.error_type)
            is_async = False
        if not handler:
            return False
        while ctx.retry_count < self._max_retries:
            ctx.retry_count += 1
            backoff = self._backoff_base * (2 ** (ctx.retry_count - 1))
            await asyncio.sleep(backoff)
            try:
                if is_async:
                    result = await handler(ctx)
                else:
                    result = handler(ctx)
                if result:
                    return True
            except Exception:
                pass
        return False

    async def _fallback(self, ctx: ErrorContext, component: str) -> bool:
        """Execute fallback handler (async-compatible)."""
        fallback = self._async_fallbacks.get(component)
        is_async = True
        if not fallback:
            fallback = self._fallbacks.get(component)
            is_async = False
        if not fallback:
            return False
        try:
            if is_async:
                await fallback(ctx)
            else:
                fallback(ctx)
        except Exception:
            return False
        return True

    def get_error_history(self, limit: int = 100) -> list[dict]:
        """Get error history (thread-safe read)."""
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


async def handle_error_async(manager: SelfHealingManager, error: Exception, component: str, **metadata) -> bool:
    """Convenience wrapper for async error handling."""
    return await manager.handle_error(error, component, **metadata)