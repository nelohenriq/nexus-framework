"""
NEXUS Framework - Structured Logging

Provides structured logging using structlog.
"""

from __future__ import annotations

import sys
import logging
from typing import Any, Optional
from datetime import datetime
from pathlib import Path

# Try to import structlog, fall back to standard logging
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False


def configure_logging(
    level: str = "INFO",
    format_type: str = "console",
    output: Optional[str] = None
) -> None:
    """Configure logging for NEXUS framework."""
    log_level = getattr(logging, level.upper(), logging.INFO)

    if STRUCTLOG_AVAILABLE:
        # Configure structlog
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer() if format_type == "console" else structlog.processors.JSONRenderer()
        ]

        structlog.configure(
            processors=processors,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True
        )
    else:
        # Fall back to standard logging
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )


def get_logger(name: str = "nexus") -> Any:
    """Get a logger instance."""
    if STRUCTLOG_AVAILABLE:
        return structlog.get_logger(name)
    return logging.getLogger(name)


class NexusLogger:
    """Wrapper logger for consistent interface."""

    def __init__(self, name: str = "nexus"):
        self._logger = get_logger(name)
        self._name = name

    def debug(self, msg: str, **kwargs: Any) -> None:
        self._log("debug", msg, **kwargs)

    def info(self, msg: str, **kwargs: Any) -> None:
        self._log("info", msg, **kwargs)

    def warning(self, msg: str, **kwargs: Any) -> None:
        self._log("warning", msg, **kwargs)

    def error(self, msg: str, **kwargs: Any) -> None:
        self._log("error", msg, **kwargs)

    def _log(self, level: str, msg: str, **kwargs: Any) -> None:
        logger = getattr(self._logger, level)
        if STRUCTLOG_AVAILABLE:
            logger(msg, **kwargs)
        else:
            logger(msg)


# Module-level logger
logger = NexusLogger()


__all__ = ["configure_logging", "get_logger", "NexusLogger", "logger"]