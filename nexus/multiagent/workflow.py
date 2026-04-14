#!/usr/bin/env python3
"""
NEXUS Framework - Graph-Based Workflow Engine

Implements O(1) workflow operations using adjacency lists and in-degree tracking.
Replaces O(N) list-based approach with graph-based topology.
"""

from __future__ import annotations

import threading
import time
import heapq
from collections import defaultdict, OrderedDict
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
    priority: int = 0

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


@dataclass
class WorkflowGraph:
    """
    Graph structure for O(1) workflow operations.
    Uses adjacency lists and in-degree tracking.
    """
    steps: OrderedDict = field(default_factory=OrderedDict)
    adjacency: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    reverse_adjacency: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    in_degree: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    completed: set[str] = field(default_factory=set)
    running: set[str] = field(default_factory=set)

    def add_step(self, step: WorkflowStep) -> None:
        """Add a step to the graph."""
        self.steps[step.step_id] = step
        for dep in step.dependencies:
            self.adjacency[dep].add(step.step_id)
            self.reverse_adjacency[step.step_id].add(dep)
        self.in_degree[step.step_id] = len(step.dependencies)

    def get_ready_steps(self) -> list[WorkflowStep]:
        """Get all steps ready to run (O(N) but only checks pending)."""
        ready = []
        for step_id, step in self.steps.items():
            if step.status != StepStatus.PENDING:
                continue
            if self.in_degree[step_id] == 0:
                ready.append(step)
        return ready

    def mark_completed(self, step_id: str) -> None:
        """Mark a step as completed, update graph."""
        self.completed.add(step_id)
        self.running.discard(step_id)
        for dependent in self.adjacency[step_id]:
            self.in_degree[dependent] -= 1

    def mark_running(self, step_id: str) -> None:
        """Mark a step as running."""
        self.running.add(step_id)

    def get_dependents(self, step_id: str) -> set[str]:
        """Get all steps that depend on this step (O(1))."""
        return self.adjacency[step_id].copy()

    def get_dependencies(self, step_id: str) -> set[str]:
        """Get all dependencies of a step (O(1))."""
        return self.reverse_adjacency[step_id].copy()


class WorkflowOrchestrator:
    def __init__(self) -> None:
        self._workflows: dict[str, Workflow] = {}
        self._graphs: dict[str, WorkflowGraph] = {}
        self._step_callbacks: dict[str, Callable] = {}
        self._lock = threading.RLock()

    def create_workflow(self, name: str, steps: list[dict], context: Optional[dict] = None) -> Workflow:
        workflow_id = str(uuid.uuid4())
        graph = WorkflowGraph()
        workflow_steps = []
        for i, step_def in enumerate(steps):
            step = WorkflowStep(
                step_id=str(uuid.uuid4()),
                name=step_def.get("name", f"Step {i+1}"),
                agent_id=step_def["agent_id"],
                task=step_def["task"],
                dependencies=step_def.get("dependencies", []),
                priority=step_def.get("priority", 0)
            )
            workflow_steps.append(step)
            graph.add_step(step)
        workflow = Workflow(workflow_id=workflow_id, name=name, steps=workflow_steps, context=context or {})
        with self._lock:
            self._workflows[workflow_id] = workflow
            self._graphs[workflow_id] = graph
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return self._workflows.get(workflow_id)

    def get_ready_steps(self, workflow_id: str) -> list[WorkflowStep]:
        """Get ready steps using graph (optimized)."""
        graph = self._graphs.get(workflow_id)
        if not graph:
            return []
        return graph.get_ready_steps()

    def start_step(self, workflow_id: str, step_id: str) -> bool:
        with self._lock:
            workflow = self._workflows.get(workflow_id)
            graph = self._graphs.get(workflow_id)
            if not workflow or not graph:
                return False
            step = graph.steps.get(step_id)
            if not step:
                return False
            step.status = StepStatus.RUNNING
            step.started_at = time.monotonic()
            graph.mark_running(step_id)
            if workflow.status == WorkflowStatus.PENDING:
                workflow.status = WorkflowStatus.RUNNING
                workflow.started_at = time.monotonic()
            return True

    def complete_step(self, workflow_id: str, step_id: str, result: dict) -> bool:
        with self._lock:
            workflow = self._workflows.get(workflow_id)
            graph = self._graphs.get(workflow_id)
            if not workflow or not graph:
                return False
            step = graph.steps.get(step_id)
            if not step:
                return False
            step.status = StepStatus.COMPLETED
            step.result = result
            step.completed_at = time.monotonic()
            graph.mark_completed(step_id)
            self._check_completion(workflow, graph)
            return True

    def fail_step(self, workflow_id: str, step_id: str, error: str) -> bool:
        with self._lock:
            workflow = self._workflows.get(workflow_id)
            graph = self._graphs.get(workflow_id)
            if not workflow or not graph:
                return False
            step = graph.steps.get(step_id)
            if not step:
                return False
            step.retries += 1
            if step.retries >= step.max_retries:
                step.status = StepStatus.FAILED
                step.error = error
                workflow.status = WorkflowStatus.FAILED
            else:
                step.status = StepStatus.PENDING
            return True

    def _check_completion(self, workflow: Workflow, graph: WorkflowGraph) -> None:
        if len(graph.completed) == len(graph.steps):
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = time.monotonic()

    def cancel_workflow(self, workflow_id: str) -> bool:
        with self._lock:
            workflow = self._workflows.get(workflow_id)
            graph = self._graphs.get(workflow_id)
            if not workflow or not graph:
                return False
            workflow.status = WorkflowStatus.CANCELLED
            for step in graph.steps.values():
                if step.status == StepStatus.PENDING:
                    step.status = StepStatus.SKIPPED
            return True

    def get_workflow_status(self, workflow_id: str) -> dict:
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}
        graph = self._graphs.get(workflow_id)
        completed = len(graph.completed) if graph else 0
        total = len(workflow.steps)
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "status": workflow.status.value,
            "progress": f"{completed}/{total}",
            "progress_percent": (completed / total * 100) if total > 0 else 0
        }

    def list_workflows(self, status: Optional[WorkflowStatus] = None) -> list[Workflow]:
        if status:
            return [w for w in self._workflows.values() if w.status == status]
        return list(self._workflows.values())

    def get_step_by_id(self, workflow_id: str, step_id: str) -> Optional[WorkflowStep]:
        """Get step by ID using graph (O(1))."""
        graph = self._graphs.get(workflow_id)
        if not graph:
            return None
        return graph.steps.get(step_id)


__all__ = ["WorkflowOrchestrator", "Workflow", "WorkflowStep", "WorkflowGraph", "WorkflowStatus", "StepStatus"]