#!/usr/bin/env python3
"""
NEXUS Framework - Lazy Loader for Cold Start Optimization

Reduces cold start time by deferring module imports.
Memory efficient with lazy loading and caching.
"""

from __future__ import annotations

import importlib
import sys
import threading
from typing import Any, Callable, Optional, Dict
from dataclasses import dataclass, field
from functools import lru_cache


@dataclass(slots=True)
class LazyModule:
    """Lazy-loaded module wrapper."""
    module_name: str
    _module: Optional[Any] = field(default=None, init=False, repr=False)
    _loader: Optional[Callable] = field(default=None, init=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def load(self) -> Any:
        """Load the module on first access."""
        if self._module is None:
            with self._lock:
                if self._module is None:
                    self._module = importlib.import_module(self.module_name)
        return self._module

    def __getattr__(self, name: str) -> Any:
        return getattr(self.load(), name)


class LazyLoader:
    """
    Lazy loader for reducing cold start time.
    Defers imports until first use.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._modules: Dict[str, LazyModule] = {}
        return cls._instance

    def get(self, module_name: str) -> LazyModule:
        """Get or create a lazy module wrapper."""
        if module_name not in self._modules:
            self._modules[module_name] = LazyModule(module_name=module_name)
        return self._modules[module_name]

    def preload(self, module_names: list[str]) -> None:
        """Preload multiple modules in parallel."""
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.get(name).load) for name in module_names]
            concurrent.futures.wait(futures)

    def is_loaded(self, module_name: str) -> bool:
        """Check if module is loaded."""
        return module_name in sys.modules

    def get_loaded_count(self) -> int:
        """Count actually loaded modules."""
        return sum(1 for m in self._modules.values() if m._module is not None)


# Heavy modules to lazy load
LAZY_MODULES = {
    "tiktoken": "tiktoken",
    "bleach": "bleach",
    "anthropic": "anthropic",
    "yaml": "yaml",
    "aiohttp": "aiohttp",
}


def get_lazy_module(name: str) -> LazyModule:
    """Convenience function to get lazy module."""
    return LazyLoader().get(name)


__all__ = ["LazyLoader", "LazyModule", "get_lazy_module", "LAZY_MODULES"]