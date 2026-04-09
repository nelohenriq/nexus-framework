#"""Runtime backend base protocol for meta-agentic SDK."""

from typing import Protocol, Iterable
from meta_agents.models.agents import AgentDescriptor
from meta_agents.models.skills import SkillSpec
from meta_agents.models.projects import ProjectConfig
from meta_agents.models.memory import MemoryProvider


class RuntimeBackend(Protocol):
    """Protocol defining the runtime backend interface."""
    def sync_agents(self, agents: Iterable[AgentDescriptor]) -> None:
        """Sync agent configurations to the backend."""
        ...

    def sync_skills(self, skills: Iterable[SkillSpec]) -> None:
        """Sync skill specifications to the backend."""
        ...

    def sync_projects(self, projects: Iterable[ProjectConfig]) -> None:
        """Sync project configurations to the backend."""
        ...

    def get_memory_provider(self, project_id: str) -> MemoryProvider:
        """Get a memory provider for a specific project."""
        ...
