#"""Skill specification models for meta-agentic SDK."""

from pydantic import BaseModel
from pathlib import Path
from typing import List


class SkillSpec(BaseModel):
    """Represents a skill parsed from a SKILM.d file."""
    id: str
    name: str
    description: str = ""
    tags: List[str] = []
    requirements: List[str] = []
    path: Path

    @classmethod
    def from_skill_md(cls, path: Path, skill_id: str) -> "SkillSpec":
        """Parse a SKILM.d file and create a SkillSpec."""
        content = path.read_text()
        name = skill_id.split("/")[-1] if "/" in skill_id else skill_id
        description = ""
        tags: List[str] = []
        requirements: List[str] = []

        if content.startswith("---"):
            end_idx = content.find("---", 3)
            if end_idx != -1:
                import yaml
                frontmatter = yaml.safe_load(content[3:end_idx].strip()) or {}
                name = frontmatter.get("name", name)
                description = frontmatter.get("description", "")
                tags = frontmatter.get("tags", [])
                requirements = frontmatter.get("requirements", [])
                body = content[end_idx + 3:].strip()
            else:
                body = content

        if name == skill_id.split("/")[-1]:
            for line in body.split("\n"):
                if line.startswith("# "):
                    name = line[2:].strip()
                    break

        return cls(id=skill_id, name=name, description=description,
                             tags=tags, requirements=requirements, path=path)
