from __future__ import annotations
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
import uuid


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(slots=True)
class WorkflowStep:
    step_id: str
    name: str
    agent_id: str
    task: str
    dependencies: list[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: Optional[dict] = None
    error: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retries: int = 0
    max_retries: int = 3

    def to_dict(self) -> dict[str, Any]:
        return {"step_id": self.step_id, "name": self.name, "agent_id": self.agent_id, "task": self.task, "dependencies": self.dependencies, "status": self.status.value, "result": self.result, "error": self.error}


@dataclass(slots=True)
class Workflow:
    workflow_id: str
    name: str
    steps: list[WorkflowStep] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    context: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.monotonic)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        return {"workflow_id": self.workflow_id, "name": self.name, "steps": [s.to_dict() for s in self.steps], "status": self.status.value, "context": self.context}


class WorkflowOrchestrator:
    def __init__(self) -> None:
        self._workflows: dict[str, Workflow] = {}
        self._step_callbacks: dict[str, Callable] = {}
        self._lock = threading.RLock()

    def create_workflow(self, name: str, steps: list[dict], context: Optional[dict] = None) -> Workflow:
        workflow_id = str(uuid.uuid4())
        workflow_steps = []
        for step_def in steps:
            step = WorkflowStep(step_id=str(uuid.uuid4()), name=step_def.get("name", "Step"), agent_id=step_def["agent_id"], task=step_def["task"], dependencies=step_def.get("dependencies", []))
            workflow_steps.append(step)
        workflow = Workflow(workflow_id=workflow_id, name=name, steps=workflow_steps, context=context or {})
        with self._lock:
            self._workflows[workflow_id] = workflow
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return self._workflows.get(workflow_id)

    def get_ready_steps(self, workflow_id: str) -> list[WorkflowStep]:
        workflow = self._workflows.get(workflow_id)
        if not workflow: return []
        ready = []
        completed_ids = {s.step_id for s in workflow.steps if s.status == StepStatus.COMPLETED}
        for step in workflow.steps:
            if step.status != StepStatus.PENDING: continue
            if all(dep in completed_ids for dep in step.dependencies):
                ready.append(step)
        return ready

    def start_step(self, workflow_id: str, step_id: str) -> bool:
        with self._lock:
            workflow = self._workflows.get(workflow_id)
            if not workflow: return False
            for step in workflow.steps:
                if step.step_id == step_id:
                    step.status = StepStatus.RUNNING
                    step.started_at = time.monotonic()
                    if workflow.status == WorkflowStatus.PENDING:
                        workflow.status = WorkflowStatus.RUNNING
                        workflow.started_at = time.monotonic()
                    return True
            return False

    def complete_step(self, workflow_id: str, step_id: str, result: dict) -> bool:
        with self._lock:
            workflow = self._workflows.get(workflow_id)
            if not workflow: return False
            for step in workflow.steps:
                if step.step_id == step_id:
                    step.status = StepStatus.COMPLETED
                    step.result = result
                    step.completed_at = time.monotonic()
                    self._check_completion(workflow)
                    return True
            return False

    def fail_step(self, workflow_id: str, step_id: str, error: str) -> bool:
        with self._lock:
            workflow = self._workflows.get(workflow_id)
            if not workflow: return False
            for step in workflow.steps:
                if step.step_id == step_id:
                    step.retries += 1
                    if step.retries >= step.max_retries:
                        step.status = StepStatus.FAILED
                        step.error = error
                        workflow.status = WorkflowStatus.FAILED
                    else:
                        step.status = StepStatus.PENDING
                    return True
            return False

    def _check_completion(self, workflow: Workflow) -> None:
        all_done = all(s.status in (StepStatus.COMPLETED, StepStatus.SKIPPED) for s in workflow.steps)
        if all_done:
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = time.monotonic()

    def cancel_workflow(self, workflow_id: str) -> bool:
        with self._lock:
            workflow = self._workflows.get(workflow_id)
            if not workflow: return False
            workflow.status = WorkflowStatus.CANCELLED
            for step in workflow.steps:
                if step.status == StepStatus.PENDING:
                    step.status = StepStatus.SKIPPED
            return True

    def get_workflow_status(self, workflow_id: str) -> dict:
        workflow = self._workflows.get(workflow_id)
        if not workflow: return {"error": "Workflow not found"}
        completed = sum(1 for s in workflow.steps if s.status == StepStatus.COMPLETED)
        total = len(workflow.steps)
        return {"workflow_id": workflow_id, "name": workflow.name, "status": workflow.status.value, "progress": f"{completed}/{total}", "progress_percent": (completed / total * 100) if total > 0 else 0}

    def list_workflows(self, status: Optional[WorkflowStatus] = None) -> list[Workflow]:
        if status:
            return [w for w in self._workflows.values() if w.status == status]
        return list(self._workflows.values())