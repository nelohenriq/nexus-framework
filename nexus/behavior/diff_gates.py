"""Diff Quality Gates - Quality verification."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from enum import Enum


class GateResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"


@dataclass(slots=True)
class QualityGate:
    name: str
    check: Callable[[str], bool]
    description: str = ""
    severity: str = "error"


@dataclass(slots=True)
class GateCheckResult:
    gate_name: str
    result: GateResult
    message: str = ""


class DiffQualityGates:
    def __init__(self):
        self.gates = []
        self._add_default_gates()

    def _add_default_gates(self):
        self.gates.append(QualityGate(name="syntax", check=lambda c: True, description="Valid syntax", severity="error"))
        self.gates.append(QualityGate(name="size", check=lambda c: len(c) < 10000, description="Reasonable size", severity="warn"))

    def add_gate(self, gate: QualityGate):
        self.gates.append(gate)

    def check(self, content: str) -> List[GateCheckResult]:
        results = []
        for gate in self.gates:
            try:
                passed = gate.check(content)
                result = GateResult.PASS if passed else GateResult.FAIL
            except Exception:
                result = GateResult.WARN
            results.append(GateCheckResult(gate_name=gate.name, result=result))
        return results

    def passes_all(self, content: str) -> bool:
        results = self.check(content)
        return all(r.result == GateResult.PASS for r in results)


def create_quality_gates():
    return DiffQualityGates()