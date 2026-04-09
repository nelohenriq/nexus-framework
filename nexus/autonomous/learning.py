"""Learning Engine - Adaptation and learning from patterns."""

import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Callable
import json


class AdaptationType(str, Enum):
    THRESHOLD = "threshold"
    ROUTING = "routing"
    BEHAVIOR = "behavior"
    CONFIGURATION = "configuration"


@dataclass(slots=True)
class AdaptationRule:
    rule_id: str
    name: str
    adaptation_type: AdaptationType
    condition: Callable[[dict], bool]
    action: Callable[[dict], dict]
    priority: int = 5
    enabled: bool = True
    trigger_count: int = 0
    last_triggered: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LearningRecord:
    timestamp: float
    event_type: str
    context: dict[str, Any]
    outcome: str
    feedback: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)


class LearningEngine:
    def __init__(self, storage_path: Optional[str] = None):
        self._rules: dict[str, AdaptationRule] = {}
        self._history: list[LearningRecord] = []
        self._patterns: dict[str, list[dict]] = {}
        self._storage_path = storage_path
        self._lock = threading.RLock()

    def register_rule(self, name: str, adaptation_type: AdaptationType,
                condition: Callable[[dict], bool],
                action: Callable[[dict], dict],
                priority: int = 5) -> str:
        rule_id = f"rule_{uuid.uuid4().hex[:8]}"
        rule = AdaptationRule(
            rule_id=rule_id,
            name=name,
            adaptation_type=adaptation_type,
            condition=condition,
            action=action,
            priority=priority
        )
        with self._lock:
            self._rules[rule_id] = rule
        return rule_id

    def evaluate(self, context: dict[str, Any]) -> list[dict]:
        results = []
        with self._lock:
            sorted_rules = sorted(self._rules.values(), key=lambda r: r.priority)
            for rule in sorted_rules:
                if not rule.enabled:
                    continue
                try:
                    if rule.condition(context):
                        action_result = rule.action(context)
                        rule.trigger_count += 1
                        rule.last_triggered = time.monotonic()
                        results.append({
                            "rule_id": rule.rule_id,
                            "name": rule.name,
                            "type": rule.adaptation_type.value,
                            "result": action_result
                        })
                except Exception as e:
                    results.append({
                        "rule_id": rule.rule_id,
                        "name": rule.name,
                        "error": str(e)
                    })
        return results

    def record_learning(self, event_type: str, context: dict[str, Any],
                outcome: str, feedback: Optional[float] = None):
        record = LearningRecord(
            timestamp=time.monotonic(),
            event_type=event_type,
            context=context,
            outcome=outcome,
            feedback=feedback
        )
        with self._lock:
            self._history.append(record)
            if event_type not in self._patterns:
                self._patterns[event_type] = []
            self._patterns[event_type].append(context)