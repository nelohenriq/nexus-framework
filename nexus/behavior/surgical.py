"""Surgical Change Detection - Minimal diff detection."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import difflib


@dataclass(slots=True)
class Change:
    file_path: str
    old_content: str
    new_content: str
    line_start: int = 0
    line_end: int = 0
    change_type: str = "modification"

@dataclass(slots=True)
class DiffResult:
    changes: List[Change]
    lines_added: int = 0
    lines_removed: int = 0
    lines_modified: int = 0
    is_surgical: bool = True


class SurgicalDetector:
    MAX_CHANGE_RATIO = 0.3

    def detect_changes(self, old_content: str, new_content: str, file_path: str = "") -> DiffResult:
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))
        changes = []
        added = sum(1 for line in diff if line.startswith("+"))
        removed = sum(1 for line in diff if line.startswith("-"))
        total_old = len(old_lines)
        is_surgical = total_old == 0 or (added + removed) / total_old < self.MAX_CHANGE_RATIO
        return DiffResult(changes=changes, lines_added=added, lines_removed=removed, is_surgical=is_surgical)

    def is_surgical_change(self, old_content: str, new_content: str) -> bool:
        result = self.detect_changes(old_content, new_content)
        return result.is_surgical


def detect_surgical_change(old_content: str, new_content: str) -> DiffResult:
    return SurgicalDetector().detect_changes(old_content, new_content)