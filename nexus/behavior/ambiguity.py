"""Ambiguity Detection - Detect unclear instructions."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import re


@dataclass(slots=True)
class AmbiguityIssue:
    text: str
    issue_type: str
    suggestion: str
    severity: str = "medium"


@dataclass(slots=True)
class AmbiguityResult:
    text: str
    is_ambiguous: bool
    issues: List[AmbiguityIssue] = field(default_factory=list)


class AmbiguityDetector:
    VAGUE_WORDS = ["something", "some", "maybe", "possibly", "somehow", "thing", "stuff", "etc", "and so on", "you know"]
    RELATIVE_WORDS = ["here", "there", "this", "that", "these", "those", "it", "they"]

    def detect(self, text: str) -> AmbiguityResult:
        issues = []
        text_lower = text.lower()
        for word in self.VAGUE_WORDS:
            if word in text_lower:
                issues.append(AmbiguityIssue(text=word, issue_type="vague", suggestion=f"Replace '{word}' with specific details", severity="medium"))
        return AmbiguityResult(text=text, is_ambiguous=len(issues) > 0, issues=issues)

    def suggest_clarification(self, text: str) -> List[str]:
        result = self.detect(text)
        return [i.suggestion for i in result.issues]


def detect_ambiguity(text: str) -> AmbiguityResult:
    return AmbiguityDetector().detect(text)