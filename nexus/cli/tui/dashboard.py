"""Dashboard Component for TUI."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass(slots=True)
class AgentStatus:
    agent_id: str
    name: str
    status: str
    current_task: str = ""
    progress: float = 0.0


@dataclass(slots=True)
class MetricCard:
    title: str
    value: str
    unit: str = ""
    trend: str = "stable"
    color: str = "primary"


class DashboardData:
    def __init__(self):
        self.agents = []
        self.metrics = []
        self.logs = []
        self.tasks = []

    def add_agent(self, agent: AgentStatus):
        self.agents.append(agent)

    def add_metric(self, metric: MetricCard):
        self.metrics.append(metric)

    def add_log(self, level: str, message: str):
        self.logs.append({"level": level, "message": message, "timestamp": datetime.now().isoformat()})

    def to_dict(self) -> Dict[str, Any]:
        return {"agents": [{"id": a.agent_id, "name": a.name, "status": a.status, "task": a.current_task, "progress": a.progress} for a in self.agents], "metrics": [{"title": m.title, "value": m.value, "unit": m.unit, "trend": m.trend, "color": m.color} for m in self.metrics], "logs": self.logs[-100:]}


def create_dashboard() -> DashboardData:
    return DashboardData()