#!/usr/bin/env python3
"""
NEXUS Framework - Resilience Patterns

Provides circuit breaker, retry with backoff, and fault tolerance.
"""

from __future__ import annotations

import time
import random
import threading
from typing import Callable, Optional, Any, TypeVar, List
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import logging

T = TypeVar("T")


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout: float = 60.0
    half_open_max_calls: int = 3


@dataclass
class RetryConfig:
    """Configuration for retry with backoff."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: List[type] = field(default_factory=lambda: [Exception])


class CircuitBreaker:
    """
    Circuit breaker for fault tolerance.
    Prevents cascading failures by stopping calls to failing services.
    """

    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        self._config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._lock = threading.RLock()
        self._logger = logging.getLogger("nexus.circuit_breaker")

    @property
    def state(self) -> CircuitState:
        return self._state

    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        with self._lock:
            if self._state == CircuitState.CLOSED:
                return True
            if self._state == CircuitState.OPEN:
                if time.time() - self._last_failure_time >= self._config.timeout:
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
                    self._logger.info("Circuit breaker entering half-open state")
                    return True
                return False
            if self._state == CircuitState.HALF_OPEN:
                return self._success_count < self._config.half_open_max_calls
            return False

    def record_success(self) -> None:
        """Record a successful execution."""
        with self._lock:
            self._failure_count = 0
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self._config.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._logger.info("Circuit breaker closed after recovery")

    def record_failure(self) -> None:
        """Record a failed execution."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                self._logger.warning("Circuit breaker reopened from half-open")
            elif self._failure_count >= self._config.failure_threshold:
                self._state = CircuitState.OPEN
                self._logger.error(f"Circuit breaker opened after {self._failure_count} failures")

    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute a function with circuit breaker protection."""
        if not self.can_execute():
            raise CircuitBreakerOpenError("Circuit breaker is open")
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


def retry_with_backoff(config: Optional[RetryConfig] = None) -> Callable:
    """Decorator for retry with exponential backoff."""
    cfg = config or RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            for attempt in range(cfg.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except tuple(cfg.retryable_exceptions) as e:
                    last_exception = e
                    if attempt == cfg.max_retries:
                        break
                    delay = min(
                        cfg.base_delay * (cfg.exponential_base ** attempt),
                        cfg.max_delay
                    )
                    if cfg.jitter:
                        delay = delay * (0.5 + random.random())
                    logging.getLogger("nexus.retry").warning(
                        f"Retry {attempt + 1}/{cfg.max_retries} after {delay:.2f}s: {e}"
                    )
                    time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


def retry_async_with_backoff(config: Optional[RetryConfig] = None) -> Callable:
    """Decorator for async retry with exponential backoff."""
    import asyncio
    cfg = config or RetryConfig()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(cfg.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except tuple(cfg.retryable_exceptions) as e:
                    last_exception = e
                    if attempt == cfg.max_retries:
                        break
                    delay = min(
                        cfg.base_delay * (cfg.exponential_base ** attempt),
                        cfg.max_delay
                    )
                    if cfg.jitter:
                        delay = delay * (0.5 + random.random())
                    logging.getLogger("nexus.retry").warning(
                        f"Async retry {attempt + 1}/{cfg.max_retries} after {delay:.2f}s: {e}"
                    )
                    await asyncio.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


class ResiliencePolicy:
    """Combined resilience policy with circuit breaker and retry."""

    def __init__(
        self,
        circuit_config: Optional[CircuitBreakerConfig] = None,
        retry_config: Optional[RetryConfig] = None
    ):
        self._circuit = CircuitBreaker(circuit_config)
        self._retry_config = retry_config or RetryConfig()

    def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute with full resilience protection."""
        @retry_with_backoff(self._retry_config)
        def protected_call():
            return self._circuit.call(func, *args, **kwargs)
        return protected_call()

    @property
    def circuit_state(self) -> CircuitState:
        return self._circuit.state


# Default instances
default_circuit_breaker = CircuitBreaker()
default_retry_config = RetryConfig()


__all__ = [
    "CircuitState", "CircuitBreakerConfig", "CircuitBreaker", "CircuitBreakerOpenError",
    "RetryConfig", "retry_with_backoff", "retry_async_with_backoff",
    "ResiliencePolicy", "default_circuit_breaker", "default_retry_config"
]