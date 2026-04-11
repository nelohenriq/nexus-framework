"""
NEXUS Framework - Budget Enforcement

Built-in budget tracking and enforcement.
Prevents runaway token usage and cost overruns.
"""

from __future__ import annotations

import time
import threading
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class BudgetAction(str, Enum):
    STOP = "stop"
    WARN = "warn"
    THROTTLE = "throttle"


@dataclass
class BudgetConfig:
    """Budget configuration."""
    max_tokens: Optional[int] = None
    max_cost_usd: Optional[float] = None
    warn_threshold: float = 0.8
    cost_per_1k_tokens: float = 0.01


@dataclass
class BudgetStatus:
    """Current budget status."""
    tokens_used: int
    tokens_remaining: Optional[int]
    cost_usd: float
    cost_remaining: Optional[float]
    percent_used: float
    action: BudgetAction
    message: str


class BudgetEnforcer:
    """
    Budget enforcer for token and cost limits.
    Tracks usage and enforces hard limits.
    """

    def __init__(self, config: BudgetConfig) -> None:
        self._config = config
        self._tokens_used = 0
        self._lock = threading.Lock()
        self._start_time = time.time()
        self._warnings_issued = 0

    def track(self, tokens: int) -> BudgetStatus:
        """Track token usage and return status."""
        with self._lock:
            self._tokens_used += tokens
            cost = (self._tokens_used / 1000) * self._config.cost_per_1k_tokens
            percent_used = self._calculate_percent()
            action, message = self._determine_action(percent_used)
            tokens_remaining = None
            if self._config.max_tokens:
                tokens_remaining = max(0, self._config.max_tokens - self._tokens_used)
            cost_remaining = None
            if self._config.max_cost_usd:
                cost_remaining = max(0.0, self._config.max_cost_usd - cost)
            return BudgetStatus(
                tokens_used=self._tokens_used,
                tokens_remaining=tokens_remaining,
                cost_usd=cost,
                cost_remaining=cost_remaining,
                percent_used=percent_used,
                action=action,
                message=message
            )

    def track_usage(self, tokens: int) -> BudgetStatus:
        """Alias for track() method."""
        return self.track(tokens)

    def _calculate_percent(self) -> float:
        if self._config.max_tokens:
            return self._tokens_used / self._config.max_tokens
        if self._config.max_cost_usd:
            cost = (self._tokens_used / 1000) * self._config.cost_per_1k_tokens
            return cost / self._config.max_cost_usd
        return 0.0

    def _determine_action(self, percent: float) -> tuple[BudgetAction, str]:
        if percent >= 1.0:
            return BudgetAction.STOP, "Budget exhausted. Operation blocked."
        if percent >= self._config.warn_threshold:
            self._warnings_issued += 1
            return BudgetAction.WARN, f"Budget at {percent*100:.1f}%. Consider wrapping up."
        return BudgetAction.THROTTLE, "Within budget."

    def can_proceed(self) -> bool:
        """Check if operation can proceed."""
        with self._lock:
            percent = self._calculate_percent()
            return percent < 1.0

    def get_stats(self) -> dict:
        """Get budget statistics."""
        with self._lock:
            cost = (self._tokens_used / 1000) * self._config.cost_per_1k_tokens
            return {
                "tokens_used": self._tokens_used,
                "cost_usd": round(cost, 4),
                "warnings_issued": self._warnings_issued,
                "uptime_seconds": time.time() - self._start_time
            }


__all__ = ["BudgetAction", "BudgetConfig", "BudgetStatus", "BudgetEnforcer"]