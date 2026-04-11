#!/usr/bin/env python3
"""NEXUS Framework - Observability Module."""

from __future__ import annotations

try:
    from .metrics import MetricsConfig, NexusMetrics, metrics
    __all__ = ["MetricsConfig", "NexusMetrics", "metrics"]
except ImportError:
    __all__ = []