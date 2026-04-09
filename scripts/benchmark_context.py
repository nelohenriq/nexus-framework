#!/usr/bin/env python3
"""Benchmark script for context.py optimization."""

import sys
import time
import tempfile
import os
sys.path.insert(0, "/a0/usr/projects/meta_agentic_framework")

from nexus.core.messages import Message, MessageRole
from nexus.core.context import AgentContext, Checkpoint
from nexus.core.memory import MemoryManager

def benchmark_context():
    """Run context operations benchmark."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    try:
        memory = MemoryManager(db_path)
        context = AgentContext("test-agent", memory=memory)
        
        start = time.perf_counter()
        
        # Add 500 messages
        for i in range(500):
            msg = Message(
                role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                content=f"Test message {i}"
            )
            context.add_message(msg)
        
        # Get messages with limit 100 times
        for limit in [10, 50, 100, 200]:
            msgs = context.get_messages(limit=limit)
        
        # Create 50 checkpoints
        checkpoints = []
        for i in range(50):
            cp = context.create_checkpoint()
            checkpoints.append(cp)
        
        # Restore from checkpoints 20 times
        for cp in checkpoints[:20]:
            context.restore_checkpoint(cp)
        
        # Save and load checkpoints
        for name in ["cp1", "cp2", "cp3"]:
            context.save_checkpoint(name)
            loaded = context.load_checkpoint(name)
        
        # Get token count 100 times
        for _ in range(100):
            count = context.get_token_count()
        
        elapsed = time.perf_counter() - start
        memory.close()
        return elapsed
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

if __name__ == "__main__":
    elapsed = benchmark_context()
    print(f"{elapsed:.6f}")
