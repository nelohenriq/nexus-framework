#!/usr/bin/env python3
"""NEXUS Framework - REST API Module."""

from __future__ import annotations

try:
    from .rest import create_app, run_server, app
    __all__ = ["create_app", "run_server", "app"]
except ImportError:
    __all__ = []