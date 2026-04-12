"""Goal-Driven Execution - Structured goal management."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum


class GoalStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass(slots=True)
class SuccessCriteria:
    description: str
    verification_method: str = "manual"
    is_met: bool = False


@dataclass(slots=True)
class Goal:
    id: str
    description: str
    success_criteria: List[SuccessCriteria] = field(default_factory=list)
    status: GoalStatus = GoalStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    sub_goals: List["Goal"] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def is_complete(self) -> bool:
        if self.status != GoalStatus.COMPLETED:
            return False
        return all(c.is_met for c in self.success_criteria)

    def verify_criteria(self) -> int:
        met = sum(1 for c in self.success_criteria if c.is_met)
        return met


class GoalParser:
    def parse(self, description: str) -> Goal:
        import hashlib
        goal_id = hashlib.md5(f"{description}:{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        return Goal(id=goal_id, description=description)

    def parse_with_criteria(self, description: str, criteria: List[str]) -> Goal:
        goal = self.parse(description)
        goal.success_criteria = [SuccessCriteria(description=c) for c in criteria]
        return goal


def create_goal(description: str, criteria: Optional[List[str]] = None) -> Goal:
    parser = GoalParser()
    if criteria:
        return parser.parse_with_criteria(description, criteria)
    return parser.parse(description)