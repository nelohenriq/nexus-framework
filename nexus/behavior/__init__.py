"""Behavior Module - Goal-driven execution and quality."""

from .goals import (
    GoalStatus, SuccessCriteria, Goal, GoalParser,
    create_goal
)
from .surgical import (
    Change, DiffResult, SurgicalDetector,
    detect_surgical_change
)
from .ambiguity import (
    AmbiguityIssue, AmbiguityResult, AmbiguityDetector,
    detect_ambiguity
)
from .diff_gates import (
    GateResult, QualityGate, GateCheckResult, DiffQualityGates,
    create_quality_gates
)

__all__ = [
    "GoalStatus", "SuccessCriteria", "Goal", "GoalParser", "create_goal",
    "Change", "DiffResult", "SurgicalDetector", "detect_surgical_change",
    "AmbiguityIssue", "AmbiguityResult", "AmbiguityDetector", "detect_ambiguity",
    "GateResult", "QualityGate", "GateCheckResult", "DiffQualityGates", "create_quality_gates"
]