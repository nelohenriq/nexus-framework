"""
NEXUS Framework - Prompt Caching

Built-in prompt caching for LLM API optimization.
Reduces token usage by caching static prefixes.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any
import threading


@dataclass
class CacheEntry:
    """Entry in the prompt cache."""
    prefix_hash: str
    static_prefix: str
    tokens: int
    hits: int = 0
    created_at: float = field(default_factory=time.time)
    last_hit: float = field(default_factory=time.time)


class PromptCache:
    """
    Prompt caching system for LLM API optimization.
    Caches static prefixes to reduce token usage.
    """

    def __init__(self, max_entries: int = 1000) -> None:
        self._cache: dict[str, CacheEntry] = {}
        self._max_entries = max_entries
        self._lock = threading.Lock()
        self._total_hits = 0
        self._total_saved = 0

    def compute_prefix_hash(self, prefix: str) -> str:
        """Compute SHA256 hash of prefix for cache key."""
        return hashlib.sha256(prefix.encode()).hexdigest()[:16]

    def get_cached(self, prefix: str) -> CacheEntry | None:
        """Get cached entry for prefix if exists."""
        prefix_hash = self.compute_prefix_hash(prefix)
        with self._lock:
            entry = self._cache.get(prefix_hash)
            if entry:
                entry.hits += 1
                entry.last_hit = time.time()
                self._total_hits += 1
                self._total_saved += entry.tokens
                return entry
            return None

    def put(self, prefix: str, tokens: int) -> CacheEntry:
        """Cache a static prefix."""
        prefix_hash = self.compute_prefix_hash(prefix)
        with self._lock:
            if len(self._cache) >= self._max_entries:
                self._evict_oldest()
            entry = CacheEntry(
                prefix_hash=prefix_hash,
                static_prefix=prefix,
                tokens=tokens
            )
            self._cache[prefix_hash] = entry
            return entry

    def _evict_oldest(self) -> None:
        """Evict oldest/least used entry."""
        if not self._cache:
            return
        oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_hit)
        del self._cache[oldest_key]

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                "total_entries": len(self._cache),
                "total_hits": self._total_hits,
                "tokens_saved": self._total_saved,
                "entries": [
                    {"hash": e.prefix_hash, "tokens": e.tokens, "hits": e.hits}
                    for e in self._cache.values()
                ]
            }


__all__ = ["CacheEntry", "PromptCache"]
