#!/usr/bin/env python3
"""Multi-Agent Example - Orchestrating multiple agents."""

import sys
import os
import uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nexus.multiagent import AgentRegistry, MessageBus, AgentMessage, MessageType, MessagePriority

def main():
    print("=== Multi-Agent Example ===")
    print()

    # 1. Create agent registry
    registry = AgentRegistry()
    print("1. Agent registry created")

    # 2. Register multiple agents with different capabilities
    worker1 = registry.register("worker1", ["compute", "math"])
    worker2 = registry.register("worker2", ["translate", "analyze"])
    coordinator = registry.register("coordinator", ["orchestrate", "delegate"])
    print(f"2. Registered 3 agents:")
    print(f" - worker1: {worker1[:8]} (compute, math)")
    print(f" - worker2: {worker2[:8]} (translate, analyze)")
    print(f" - coordinator: {coordinator[:8]} (orchestrate, delegate)")

    # 3. Find agents by capability
    compute_agents = registry.find_by_capability("compute")
    print(f"3. Agents with compute capability: {len(compute_agents)}")

    # 4. Set up message bus
    bus = MessageBus()
    bus.register_agent(worker1)
    bus.register_agent(worker2)
    print("4. Message bus initialized")

    # 5. Send task message from coordinator to worker1
    task_msg = AgentMessage(
        message_id=str(uuid.uuid4()),
        sender_id=coordinator,
        receiver_id=worker1,
        message_type=MessageType.TASK,
        priority=MessagePriority.HIGH,
        content={"task": "calculate", "data": [1, 2, 3]}
    )
    bus.send(task_msg)
    print(f"5. Task sent from coordinator to worker1")

    # 6. Worker1 receives and processes
    received = bus.receive(worker1)
    if received:
        print(f"6. Worker1 received: {received.content}")

    print()
    print("=== Example Complete ===")

if __name__ == "__main__":
    main()