#"""Configuration loaders for meta-agentic SDK."""

from pathlib import Path
from typing import List
import yaml
from meta_agents.config.meta_config import MetaConfig
from meta_agents.models.agents import AgentDescriptor
from meta_agents.models.skills import SkillSpec
from meta_agents.models.projects import ProjectConfig


def load_meta_config(path: Path) -> MetaConfig:
    """Load meta.yaml and expand ~, validate presence of backends.hermes."""
    if not path.exists():
        raise FileNotFoundError(f'meta.yaml not found at {path}')
    return MetaConfig.from_yaml(path)


def discover_agents(root: Path) -> List[AgentDescriptor]:
    """Discover and load all agent configurations from agents/*.yaml."""
    agents_dir = root / "agents"
    if not agents_dir.exists():
        return []
    agents = []
    for yaml_file in agents_dir.glob("*.yaml"):
        content = yaml_file.read_text()
        data = yaml.safe_load(content)
        if data:
            agents.append(AgentDescriptor(**data))
    return agents


def discover_skills(root: Path) -> List[SkillSpec]:
    """Walk skills/ directory recursively and discover all SKILM.md files."""
    skills_dir = root / "skills"
    if not skills_dir.exists():
        return []
    skills = []
    for skill_md in skills_dir.rglob("SKILM.md"):
        rel_path = skill_md.relative_to(skills_dir)
        skill_id = str(rel_path.parent)
        skills.append(SkillSpec.from_skill_md(skill_md, skill_id))
    return skills


def discover_projects(root: Path) -> List[ProjectConfig]:
    """Discover and load all project configurations from projects*/config.yaml."""
    projects_dir = root / "projects"
    if not projects_dir.exists():
        return []
    projects = []
    for config_file in projects_dir.glob("*/config.yaml"):
        content = config_file.read_text()
        data = yaml.safe_load(content)
        if data:
            data["path"] = config_file.parent
            projects.append(ProjectConfig(**data))
    return projects
