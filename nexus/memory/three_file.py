"""Three-File Memory Structure Implementation."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class ContextEntry:
    timestamp: str
    agent_id: str
    role: str
    current_task: str
    goals: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [f"# Context - {self.timestamp}", "", f"Agent: {self.agent_id}", f"Role: {self.role}", "", f"Task: {self.current_task}"]
        if self.goals:
            lines.append("\nGoals:")
            for g in self.goals:
                lines.append(f"- {g}")
        return "\n".join(lines)


@dataclass(slots=True)
class DecisionEntry:
    timestamp: str
    decision: str
    reasoning: str
    outcome: str = "pending"

    def to_markdown(self) -> str:
        return f"## Decision: {self.timestamp}\n\nDecision: {self.decision}\nReasoning: {self.reasoning}\nOutcome: {self.outcome}\n"


@dataclass(slots=True)
class LearningEntry:
    timestamp: str
    category: str
    title: str
    description: str
    confidence: float = 1.0

    def to_markdown(self) -> str:
        return f"## {self.category}: {self.title}\n\n{self.description}\nConfidence: {self.confidence:.0%}\n"


class ThreeFileMemory:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.context: Optional[ContextEntry] = None
        self.decisions: List[DecisionEntry] = []
        self.learnings: List[LearningEntry] = []

    def initialize(self, agent_id: str, role: str, current_task: str = ""):
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.context = ContextEntry(
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id, role=role, current_task=current_task
        )

    def save(self):
        self.base_path.mkdir(parents=True, exist_ok=True)
        if self.context:
            (self.base_path / "context.md").write_text(self.context.to_markdown())
        decisions_content = "# Decisions\n\n" + "\n".join([d.to_markdown() for d in self.decisions])
        (self.base_path / "decisions.md").write_text(decisions_content)
        learnings_content = "# Learnings\n\n" + "\n".join([l.to_markdown() for l in self.learnings])
        (self.base_path / "learnings.md").write_text(learnings_content)

    def add_decision(self, decision: str, reasoning: str, outcome: str = "pending"):
        self.decisions.append(DecisionEntry(
            timestamp=datetime.now().isoformat(),
            decision=decision, reasoning=reasoning, outcome=outcome
        ))

    def add_learning(self, category: str, title: str, description: str, confidence: float = 1.0):
        self.learnings.append(LearningEntry(
            timestamp=datetime.now().isoformat(),
            category=category, title=title, description=description, confidence=confidence
        ))


def create_three_file_memory(base_path: str, agent_id: str = "", role: str = "") -> ThreeFileMemory:
    memory = ThreeFileMemory(base_path)
    if agent_id or role:
        memory.initialize(agent_id=agent_id, role=role)
    return memory