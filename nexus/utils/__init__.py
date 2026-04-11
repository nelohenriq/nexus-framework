#!/usr/bin/env python3
"""NEXUS Framework - Utils Module."""

from __future__ import annotations

try:
    from .logging import configure_logging, get_logger, NexusLogger, logger
    __all__ = ["configure_logging", "get_logger", "NexusLogger", "logger"]
except ImportError:
    __all__ = []