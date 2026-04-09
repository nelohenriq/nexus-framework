"""Logging setup for meta-agentic SDK."""

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", format_string: Optional[str] = None) -> logging.Logger:
 """Setup logging for the meta-agentic SDK."""
 if format_string is None:
  format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
 logging.basicConfig(level=getattr(logging, level.upper()),
 format=format_string, stream=sys.stdout)
 return logging.getLogger("meta_agents")


def get_logger(name: str) -> logging.Logger:
 """Get a logger instance for a specific module."""
 return logging.getLogger(f"meta_agents.{name}")
