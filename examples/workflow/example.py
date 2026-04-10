#!/usr/bin/env python3
"""Workflow Example - Multi-step workflow with persistence."""

import sys
import os
import uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nexus.multiagent import WorkflowOrchestrator, AgentRegistry

def main():
    print("=== Workflow Example ===")
    print()

    # 1. Create agent registry and register agents
    registry = AgentRegistry()
    fetcher_agent = registry.register("fetcher", ["fetch"])
    processor_agent = registry.register("processor", ["process"])
    saver_agent = registry.register("saver", ["save"])
    print("1. Registered 3 agents for workflow steps")

    # 2. Create workflow orchestrator
    orchestrator = WorkflowOrchestrator()
    print("2. Workflow orchestrator created")

    # 3. Define workflow steps with agent assignments
    steps = [
        {"name": "fetch_data", "agent_id": fetcher_agent, "task": "Fetch data from source"},
        {"name": "process_data", "agent_id": processor_agent, "task": "Process the fetched data"},
        {"name": "save_result", "agent_id": saver_agent, "task": "Save processed results"}
    ]
    print("3. Defined 3 workflow steps:")
    for step in steps:
        print(f" - {step["name"]}: {step["task"]}")

    # 4. Create workflow
    workflow = orchestrator.create_workflow("data_pipeline", steps)
    print(f"4. Workflow created: {workflow.workflow_id[:8]}")

    # 5. Get workflow status
    print(f"5. Workflow status: {workflow.status.value}")
    print(f" Steps: {len(workflow.steps)}")

    print()
    print("=== Example Complete ===")

if __name__ == "__main__":
    main()