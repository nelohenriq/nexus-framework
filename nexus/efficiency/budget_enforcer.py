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


@dataclass(slots=True)
class BudgetConfig:
 """Budget configuration."""
 max_tokens: Optional[int] = None
 max_cost_usd: Optional[float] = None
 warn_threshold: float = 0.8
 cost_per_1k_tokens: float = 0.01


@dataclass(slots=True)
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
 self._cost_usd = 0.0
 self._lock = threading.Lock()

 def track(self, tokens: int) -> BudgetStatus:
 """Track token usage."""
 with self._lock:
 self._tokens_used += tokens
 self._cost_usd += (tokens / 1000) * self._config.cost_per_1k_tokens
 return self.get_status()

 def get_status(self) -> BudgetStatus:
 """Get current budget status."""
 with self._lock:
 tokens_remaining = None
 cost_remaining = None
 percent_used = 0.0
 action = BudgetAction.WARN
 message = "OK"

 if self._config.max_tokens:
 tokens_remaining = max(0, self._config.max_tokens - self._tokens_used)
 percent_used = self._tokens_used / self._config.max_tokens
 if percent_used >= 1.0:
 action = BudgetAction.STOP
 message = f"Token limit reached: {self._tokens_used}/{self._config.max_tokens}"
 elif percent_used >= self._config.warn_threshold:
 action = BudgetAction.WARN
 message = f"Token usage at {percent_used*100:.1f}%"

 if self._config.max_cost_usd:
 cost_remaining = max(0.0, self._config.max_cost_usd - self._cost_usd)
 cost_percent = self._cost_usd / self._config.max_cost_usd
 if cost_percent >= 1.0:
 action = BudgetAction.STOP
 message = f"Cost limit reached: ${self._cost_usd:.2f}/${self._config.max_cost_usd:.2f}"
 elif cost_percent >= self._config.warn_threshold and action != BudgetAction.STOP:
 action = BudgetAction.WARN
 message = f"Cost at ${self._cost_usd:.2f}/${self._config.max_cost_usd:.2f}"

 return BudgetStatus(
 tokens_used=self._tokens_used,
 tokens_remaining=tokens_remaining,
 cost_usd=self._cost_usd,
 cost_remaining=cost_remaining,
 percent_used=percent_used,
 action=action,
 message=message
 )

 def can_proceed(self) -> bool:
 """Check if more tokens can be used."""
 status = self.get_status()
 return status.action != BudgetAction.STOP

 def reset(self) -> None:
 """Reset tracking."""
 with self._lock:
 self._tokens_used = 0
 self._cost_usd = 0.0


__all__ = ["BudgetEnforcer", "BudgetConfig", "BudgetStatus", "BudgetAction"]
