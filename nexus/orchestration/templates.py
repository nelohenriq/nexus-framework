"""Agent Template Library - Pre-built agent configurations."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class AgentRole(Enum):
    RESEARCHER = "researcher"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    TESTER = "tester"
    ANALYST = "analyst"
    WRITER = "writer"
    SECURITY = "security"
    DEVOPS = "devops"
    MANAGER = "manager"
    COORDINATOR = "coordinator"


@dataclass(slots=True)
class AgentTemplate:
    name: str
    role: AgentRole
    description: str
    system_prompt: str
    tools: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    memory_config: Dict[str, Any] = field(default_factory=dict)
    behavior_config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "role": self.role.value, "description": self.description, "system_prompt": self.system_prompt, "tools": self.tools, "skills": self.skills}


class TemplateRegistry:
    TEMPLATES = {
        "researcher": AgentTemplate(name="Researcher", role=AgentRole.RESEARCHER, description="Specialized in information gathering", system_prompt="You are a researcher. Gather information and provide reports.", tools=["search", "document_query"], skills=["research"]),
        "developer": AgentTemplate(name="Developer", role=AgentRole.DEVELOPER, description="Specialized in software development", system_prompt="You are a developer. Write clean, efficient code.", tools=["code_execution", "text_editor"], skills=["coding"]),
        "reviewer": AgentTemplate(name="Reviewer", role=AgentRole.REVIEWER, description="Specialized in code review", system_prompt="You are a reviewer. Analyze code for issues.", tools=["text_editor"], skills=["review"]),
        "tester": AgentTemplate(name="Tester", role=AgentRole.TESTER, description="Specialized in testing", system_prompt="You are a tester. Write tests and validate.", tools=["code_execution"], skills=["testing"]),
        "analyst": AgentTemplate(name="Analyst", role=AgentRole.ANALYST, description="Specialized in data analysis", system_prompt="You are an analyst. Analyze data and generate insights.", tools=["code_execution"], skills=["analysis"]),
        "writer": AgentTemplate(name="Writer", role=AgentRole.WRITER, description="Specialized in documentation", system_prompt="You are a writer. Create clear documentation.", tools=["text_editor"], skills=["writing"]),
        "security": AgentTemplate(name="Security", role=AgentRole.SECURITY, description="Specialized in security", system_prompt="You are a security specialist. Identify vulnerabilities.", tools=["code_execution"], skills=["security"]),
        "devops": AgentTemplate(name="DevOps", role=AgentRole.DEVOPS, description="Specialized in infrastructure", system_prompt="You are a DevOps engineer. Manage deployments.", tools=["code_execution"], skills=["devops"]),
        "manager": AgentTemplate(name="Manager", role=AgentRole.MANAGER, description="Specialized in coordination", system_prompt="You are a project manager. Coordinate tasks.", tools=["scheduler"], skills=["management"]),
        "coordinator": AgentTemplate(name="Coordinator", role=AgentRole.COORDINATOR, description="Specialized in orchestration", system_prompt="You are a coordinator. Orchestrate agents.", tools=["call_subordinate"], skills=["orchestration"])
    }

    @classmethod
    def get(cls, name: str) -> Optional[AgentTemplate]:
        return cls.TEMPLATES.get(name)

    @classmethod
    def list_all(cls) -> List[str]:
        return list(cls.TEMPLATES.keys())


def get_template(name: str) -> Optional[AgentTemplate]:
    return TemplateRegistry.get(name)


def list_templates() -> List[str]:
    return TemplateRegistry.list_all()