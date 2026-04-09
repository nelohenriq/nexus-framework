"""
NEXUS Framework - Rate Limiting

Built-in rate limiting for LLM API protection.
Uses sliding window algorithm for accurate RPM limiting.
"""

from __future__ import annotations

import time
import threading
from collections import deque
from dataclasses import dataclass
from typing import Optional


@dataclass
class RateLimitStatus:
    """Status of rate limiter."""
    requests_made: int
    requests_remaining: int
    reset_in_seconds: float
    is_limited: bool


class RateLimiter:
    """
    Rate limiter using sliding window algorithm.
    Protects against API rate limit errors.
    """

    def __init__(self, max_rpm: int = 60, name: str = "default") -> None:
        self._max_rpm = max_rpm
        self._name = name
        self._requests: deque[float] = deque()
        self._lock = threading.Lock()
        self._total_requests = 0
        self._total_limited = 0

    def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        Acquire permission to make a request.
        Blocks if rate limited until slot available.
        Returns True if acquired, False if timeout.
        """
        start_time = time.time()
        while True:
            with self._lock:
                now = time.time()
                window_start = now - 60.0
                while self._requests and self._requests[0] < window_start:
                    self._requests.popleft()
                if len(self._requests) < self._max_rpm:
                    self._requests.append(now)
                    self._total_requests += 1
                    return True
                self._total_limited += 1
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    return False
            time.sleep(0.1)

    def try_acquire(self) -> bool:
        """Non-blocking attempt to acquire."""
        with self._lock:
            now = time.time()
            window_start = now - 60.0
            while self._requests and self._requests[0] < window_start:
                self._requests.popleft()
            if len(self._requests) < self._max_rpm:
                self._requests.append(now)
                self._total_requests += 1
                return True
            return False

    def get_status(self) -> RateLimitStatus:
        """Get current rate limit status."""
        with self._lock:
            now = time.time()
            window_start = now - 60.0
            while self._requests and self._requests[0] < window_start:
                self._requests.popleft()
            requests_made = len(self._requests)
            requests_remaining = self._max_rpm - requests_made
            reset_in = 60.0 - (now - self._requests[0]) if self._requests else 0
            return RateLimitStatus(
                requests_made=requests_made,
                requests_remaining=requests_remaining,
                reset_in_seconds=reset_in,
                is_limited=requests_remaining <= 0
            )

    def get_stats(self) -> dict:
        """Get rate limiter statistics."""
        with self._lock:
            return {
                "name": self._name,
                "max_rpm": self._max_rpm,
                "total_requests": self._total_requests,
                "total_limited": self._total_limited,
                "current_usage": len(self._requests)
            }


__all__ = ["RateLimitStatus", "RateLimiter"]
