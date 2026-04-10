#!/usr/bin/env python3
"""Simple Agent Example - Basic NEXUS framework usage."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nexus.container import DIContainer
from nexus.core import Message, MessageRole, MemoryManager, AgentContext

def main():
    print("=== Simple Agent Example ===")
    print()

    # 1. Create a DI Container
    container = DIContainer()
    print("1. DI Container created")

    # 2. Create an agent context
    context = AgentContext(agent_id="simple_agent")
    print(f"2. Agent context: {context.agent_id}")

    # 3. Create a message
    msg = Message(
        role=MessageRole.USER,
        content="What is the capital of France?"
    )
    context.add_message(msg)
    print(f"3. Added message: {msg.content[:30]}...")

    # 4. Create memory
    memory = MemoryManager(db_path=":memory:")
    memory.save("agent_name", {"value": "SimpleAgent"})
    print(f"4. Memory saved: {memory.load("agent_name")}")

    # 5. Create a checkpoint
    checkpoint = context.create_checkpoint()
    print(f"5. Checkpoint: {checkpoint.checkpoint_id[:8]}...")

    print()
    print("=== Example Complete ===")

if __name__ == "__main__":
    main()