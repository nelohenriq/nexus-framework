#!/usr/bin/env python3
"""
NEXUS Framework - Prometheus Metrics

Provides Prometheus metrics for monitoring NEXUS framework.
"""

from __future__ import annotations

import time
from typing import Optional, Callable
from dataclasses import dataclass, field
from functools import wraps
from contextlib import contextmanager

# Try to import prometheus_client
try:
    from prometheus_client import (
        Counter, Histogram, Gauge, Info, CollectorRegistry,
        generate_latest, CONTENT_TYPE_LATEST, start_http_server
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    Counter = Histogram = Gauge = Info = None
    CollectorRegistry = None


@dataclass
class MetricsConfig:
    """Configuration for metrics collection."""
    enabled: bool = True
    port: int = 9090
    prefix: str = "nexus"
    labels: dict = field(default_factory=dict)


class NexusMetrics:
    """
    Prometheus metrics for NEXUS framework.
    Provides counters, histograms, and gauges for monitoring.
    """

    def __init__(self, config: Optional[MetricsConfig] = None):
        self._config = config or MetricsConfig()
        self._registry = None
        self._metrics = {}

        if not PROMETHEUS_AVAILABLE or not self._config.enabled:
            return

        prefix = self._config.prefix
        self._registry = CollectorRegistry()

        # LLM metrics
        self._metrics["llm_requests_total"] = Counter(
            f"{prefix}_llm_requests_total",
            "Total LLM API requests",
            ["provider", "model", "status"],
            registry=self._registry
        )

        self._metrics["llm_request_duration"] = Histogram(
            f"{prefix}_llm_request_duration_seconds",
            "LLM request latency in seconds",
            ["provider", "model"],
            buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60],
            registry=self._registry
        )

        self._metrics["llm_tokens_total"] = Counter(
            f"{prefix}_llm_tokens_total",
            "Total tokens processed",
            ["provider", "model", "type"],
            registry=self._registry
        )

        # Agent metrics
        self._metrics["agent_executions_total"] = Counter(
            f"{prefix}_agent_executions_total",
            "Total agent executions",
            ["agent_id", "status"],
            registry=self._registry
        )

        self._metrics["agent_active"] = Gauge(
            f"{prefix}_agent_active",
            "Number of active agents",
            registry=self._registry
        )

        # Tool metrics
        self._metrics["tool_executions_total"] = Counter(
            f"{prefix}_tool_executions_total",
            "Total tool executions",
            ["tool_name", "status"],
            registry=self._registry
        )

        self._metrics["tool_errors_total"] = Counter(
            f"{prefix}_tool_errors_total",
            "Total tool errors",
            ["tool_name", "error_type"],
            registry=self._registry
        )

        # Memory metrics
        self._metrics["memory_operations_total"] = Counter(
            f"{prefix}_memory_operations_total",
            "Total memory operations",
            ["operation", "status"],
            registry=self._registry
        )

        self._metrics["memory_size_bytes"] = Gauge(
            f"{prefix}_memory_size_bytes",
            "Memory storage size in bytes",
            registry=self._registry
        )

        # Cache metrics
        self._metrics["cache_hits_total"] = Counter(
            f"{prefix}_cache_hits_total",
            "Total cache hits",
            ["cache_name"],
            registry=self._registry
        )

        self._metrics["cache_misses_total"] = Counter(
            f"{prefix}_cache_misses_total",
            "Total cache misses",
            ["cache_name"],
            registry=self._registry
        )

    def track_llm_request(self, provider: str, model: str, status: str, duration: float, prompt_tokens: int, completion_tokens: int) -> None:
        """Track an LLM request."""
        if not PROMETHEUS_AVAILABLE or not self._config.enabled:
            return
        self._metrics["llm_requests_total"].labels(provider, model, status).inc()
        self._metrics["llm_request_duration"].labels(provider, model).observe(duration)
        self._metrics["llm_tokens_total"].labels(provider, model, "prompt").inc(prompt_tokens)
        self._metrics["llm_tokens_total"].labels(provider, model, "completion").inc(completion_tokens)

    def track_agent_execution(self, agent_id: str, status: str) -> None:
        """Track an agent execution."""
        if not PROMETHEUS_AVAILABLE or not self._config.enabled:
            return
        self._metrics["agent_executions_total"].labels(agent_id, status).inc()

    def track_tool_execution(self, tool_name: str, status: str, error_type: Optional[str] = None) -> None:
        """Track a tool execution."""
        if not PROMETHEUS_AVAILABLE or not self._config.enabled:
            return
        self._metrics["tool_executions_total"].labels(tool_name, status).inc()
        if error_type:
            self._metrics["tool_errors_total"].labels(tool_name, error_type).inc()

    def track_memory_operation(self, operation: str, status: str) -> None:
        """Track a memory operation."""
        if not PROMETHEUS_AVAILABLE or not self._config.enabled:
            return
        self._metrics["memory_operations_total"].labels(operation, status).inc()

    def track_cache_hit(self, cache_name: str, hit: bool) -> None:
        """Track a cache hit or miss."""
        if not PROMETHEUS_AVAILABLE or not self._config.enabled:
            return
        if hit:
            self._metrics["cache_hits_total"].labels(cache_name).inc()
        else:
            self._metrics["cache_misses_total"].labels(cache_name).inc()

    def set_active_agents(self, count: int) -> None:
        """Set the number of active agents."""
        if not PROMETHEUS_AVAILABLE or not self._config.enabled:
            return
        self._metrics["agent_active"].set(count)

    def set_memory_size(self, size_bytes: int) -> None:
        """Set the memory storage size."""
        if not PROMETHEUS_AVAILABLE or not self._config.enabled:
            return
        self._metrics["memory_size_bytes"].set(size_bytes)

    def start_server(self) -> None:
        """Start the Prometheus metrics server."""
        if not PROMETHEUS_AVAILABLE or not self._config.enabled:
            return
        start_http_server(self._config.port, registry=self._registry)

    def get_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        if not PROMETHEUS_AVAILABLE or not self._config.enabled:
            return ""
        return generate_latest(self._registry).decode("utf-8")


# Decorator for timing functions
def timed(metric_name: str, labels: Optional[dict] = None):
    """Decorator to time a function and record in histogram."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start
                # Log duration if metrics available
            pass
        return wrapper
    return decorator


# Context manager for timing blocks
@contextmanager
def timed_block(metric: NexusMetrics, name: str, **labels):
    """Context manager to time a block of code."""
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        # Duration recorded


# Global metrics instance
metrics = NexusMetrics()


__all__ = ["MetricsConfig", "NexusMetrics", "timed", "timed_block", "metrics"]