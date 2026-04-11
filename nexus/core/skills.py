#!/usr/bin/env python3
"""
NEXUS Framework - SKILL.md Parser

Parses Hermes-style SKILL.md files with YAML frontmatter.
"""

from __future__ import annotations

import re
import json
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime


@dataclass
class SkillSpec:
    """Specification for a skill loaded from SKILL.md."""
    id: str
    name: str
    description: str = ""
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    tools: List[str] = field(default_factory=list)
    content: str = ""
    file_path: Optional[Path] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "description": self.description}


@dataclass
class SkillLoadResult:
    loaded: List[SkillSpec] = field(default_factory=list)
    failed: List[Dict[str, Any]] = field(default_factory=list)
    total_found: int = 0


class SkillParser:
    """Parser for SKILL.md files in Hermes format."""

    def __init__(self, strict: bool = False):
        self.strict = strict

    def parse(self, content: str, file_path: Optional[Path] = None) -> SkillSpec:
        parts = content.split("---")
        if len(parts) >= 3 and parts[0].strip() == "":
            frontmatter_str = parts[1]
            body = "---".join(parts[2:])
            try:
                frontmatter = yaml.safe_load(frontmatter_str) or {}
            except:
                frontmatter = {}
            return SkillSpec(
                id=str(hash(file_path) % 10000) if file_path else "unknown",
                name=file_path.parent.name if file_path else "unknown",
                description=frontmatter.get("description", ""),
                content=body.strip(),
                file_path=file_path
            )
        return SkillSpec(id="raw", name="raw", content=content, file_path=file_path)

    def parse_file(self, file_path: Path) -> SkillSpec:
        content = file_path.read_text(encoding="utf-8")
        return self.parse(content, file_path)

    def load_from_directory(self, directory: Path, recursive: bool = True) -> SkillLoadResult:
        result = SkillLoadResult()
        if not directory.exists():
            return result
        pattern = "**/SKILL.md" if recursive else "SKILL.md"
        for skill_file in directory.glob(pattern):
            try:
                spec = self.parse_file(skill_file)
                result.loaded.append(spec)
            except Exception as e:
                result.failed.append({"file": str(skill_file), "error": str(e)})
        result.total_found = len(result.loaded) + len(result.failed)
        return result


class SkillRegistry:
    """Registry for managing loaded skills."""

    def __init__(self, parser: Optional[SkillParser] = None):
        self.parser = parser or SkillParser()
        self._skills: Dict[str, SkillSpec] = {}

    def load_from_directory(self, directory: Path, recursive: bool = True) -> SkillLoadResult:
        result = self.parser.load_from_directory(directory, recursive)
        for skill in result.loaded:
            self._skills[skill.id] = skill
        return result

    def get(self, skill_id: str) -> Optional[SkillSpec]:
        return self._skills.get(skill_id)

    def list_all(self) -> List[SkillSpec]:
        return list(self._skills.values())


__all__ = ["SkillParser", "SkillSpec", "SkillRegistry", "SkillLoadResult"]