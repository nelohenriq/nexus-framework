#!/usr/bin/env python3
"""NEXUS Framework - Resilience Module."""

from __future__ import annotations

try:
    from .resilience import (
        CircuitState, CircuitBreakerConfig, CircuitBreaker, CircuitBreakerOpenError,
        RetryConfig, retry_with_backoff, retry_async_with_backoff,
        ResiliencePolicy, default_circuit_breaker, default_retry_config
    )
    __all__ = [
        "CircuitState", "CircuitBreakerConfig", "CircuitBreaker", "CircuitBreakerOpenError",
        "RetryConfig", "retry_with_backoff", "retry_async_with_backoff",
        "ResiliencePolicy", "default_circuit_breaker", "default_retry_config"
    ]
except ImportError:
    __all__ = []