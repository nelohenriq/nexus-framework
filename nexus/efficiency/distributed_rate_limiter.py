#!/usr/bin/env python3
"""
NEXUS Framework - Distributed Rate Limiter

Redis-backed distributed rate limiting for multi-instance deployments.
Provides atomic rate limiting across multiple processes/machines.
"""

from __future__ import annotations

import time
import asyncio
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from abc import ABC, abstractmethod


@dataclass
class RateLimitConfig:
    """Configuration for distributed rate limiting."""
    max_rpm: int = 60
    max_rph: int = 3600
    max_concurrent: int = 10
    retry_after: float = 1.0
    key_prefix: str = "nexus:rate_limit"
    redis_url: str = "redis://localhost:6379/0"


class RateLimitBackend(ABC):
    """Abstract base class for rate limit backends."""

    @abstractmethod
    async def acquire(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Try to acquire a rate limit slot."""
        pass

    @abstractmethod
    async def get_status(self, key: str) -> Dict[str, Any]:
        """Get current rate limit status."""
        pass

    @abstractmethod
    async def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        pass


class InMemoryRateLimitBackend(RateLimitBackend):
    """In-memory rate limit backend (single process)."""

    def __init__(self):
        self._windows: Dict[str, List[float]] = {}
        self._lock = asyncio.Lock()

    async def acquire(self, key: str, max_requests: int, window_seconds: int) -> bool:
        async with self._lock:
            now = time.time()
            cutoff = now - window_seconds
            if key not in self._windows:
                self._windows[key] = []
            self._windows[key] = [t for t in self._windows[key] if t > cutoff]
            if len(self._windows[key]) >= max_requests:
                return False
            self._windows[key].append(now)
            return True

    async def get_status(self, key: str) -> Dict[str, Any]:
        async with self._lock:
            window = self._windows.get(key, [])
            return {
                "requests": len(window),
                "remaining": max(0, 60 - len(window)),
                "reset_at": max(window) if window else time.time()
            }

    async def reset(self, key: str) -> None:
        async with self._lock:
            self._windows.pop(key, None)


class RedisRateLimitBackend(RateLimitBackend):
    """Redis-backed rate limit backend (distributed)."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self._redis: Optional[Any] = None

    async def _get_redis(self) -> Any:
        if self._redis is None:
            try:
                import redis.asyncio as aioredis
                self._redis = await aioredis.from_url(self.redis_url)
            except ImportError:
                raise RuntimeError("redis package required for distributed rate limiting")
        return self._redis

    async def acquire(self, key: str, max_requests: int, window_seconds: int) -> bool:
        redis = await self._get_redis()
        now = time.time()
        window_key = f"{key}:{int(now // window_seconds)}"
        count = await redis.incr(window_key)
        if count == 1:
            await redis.expire(window_key, window_seconds)
        return count <= max_requests

    async def get_status(self, key: str) -> Dict[str, Any]:
        redis = await self._get_redis()
        now = time.time()
        window_key = f"{key}:{int(now // 60)}"
        count = int(await redis.get(window_key) or 0)
        return {
            "requests": count,
            "remaining": max(0, 60 - count),
            "reset_at": now + 60 - (now % 60)
        }

    async def reset(self, key: str) -> None:
        redis = await self._get_redis()
        pattern = f"{key}:*"
        keys = await redis.keys(pattern)
        if keys:
            await redis.delete(*keys)


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""
    allowed: bool
    remaining: int
    reset_at: float
    retry_after: Optional[float] = None


class DistributedRateLimiter:
    """Distributed rate limiter with multiple backend support."""

    def __init__(
        self,
        config: Optional[RateLimitConfig] = None,
        backend: Optional[RateLimitBackend] = None
    ):
        self.config = config or RateLimitConfig()
        self._backend = backend
        self._local_fallback = InMemoryRateLimitBackend()

    async def _get_backend(self) -> RateLimitBackend:
        if self._backend:
            return self._backend
        try:
            backend = RedisRateLimitBackend(self.config.redis_url)
            import redis.asyncio as aioredis
            await aioredis.from_url(self.config.redis_url).ping()
            self._backend = backend
            return backend
        except Exception:
            self._backend = self._local_fallback
            return self._local_fallback

    async def acquire(self, key: str = "default") -> RateLimitResult:
        backend = await self._get_backend()
        full_key = f"{self.config.key_prefix}:{key}"
        allowed = await backend.acquire(full_key, self.config.max_rpm, 60)
        status = await backend.get_status(full_key)
        return RateLimitResult(
            allowed=allowed,
            remaining=status.get("remaining", 0),
            reset_at=status.get("reset_at", time.time() + 60),
            retry_after=None if allowed else self.config.retry_after
        )

    async def wait_and_acquire(self, key: str = "default", timeout: float = 30.0) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            result = await self.acquire(key)
            if result.allowed:
                return True
            if result.retry_after:
                await asyncio.sleep(min(result.retry_after, timeout - (time.time() - start)))
        return False

    async def get_status(self, key: str = "default") -> Dict[str, Any]:
        backend = await self._get_backend()
        full_key = f"{self.config.key_prefix}:{key}"
        return await backend.get_status(full_key)

    async def reset(self, key: str = "default") -> None:
        backend = await self._get_backend()
        full_key = f"{self.config.key_prefix}:{key}"
        await backend.reset(full_key)

    async def get_backend_type(self) -> str:
        backend = await self._get_backend()
        if isinstance(backend, RedisRateLimitBackend):
            return "redis"
        return "memory"


def create_rate_limiter(
    redis_url: Optional[str] = None,
    max_rpm: int = 60
) -> DistributedRateLimiter:
    config = RateLimitConfig(max_rpm=max_rpm)
    if redis_url:
        config.redis_url = redis_url
        backend = RedisRateLimitBackend(redis_url)
        return DistributedRateLimiter(config, backend)
    return DistributedRateLimiter(config)


__all__ = [
    "DistributedRateLimiter",
    "RateLimitConfig",
    "RateLimitResult",
    "RateLimitBackend",
    "InMemoryRateLimitBackend",
    "RedisRateLimitBackend",
    "create_rate_limiter"
]