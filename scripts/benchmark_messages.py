#!/usr/bin/env python3
"""Benchmark script for messages.py optimization."""

import sys
import time
sys.path.insert(0, "/a0/usr/projects/meta_agentic_framework")

from nexus.core.messages import Message, MessageRole, ConversationTurn

def benchmark_messages():
    """Run message operations benchmark."""
    start = time.perf_counter()
    
    # Create 1000 messages
    messages = []
    for i in range(1000):
        msg = Message(
            role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
            content=f"Test message {i}",
            metadata={"index": i}
        )
        messages.append(msg)
    
    # Convert to API format 1000 times
    api_formats = [msg.to_api_format() for msg in messages]
    
    # Convert from API format 100 times
    reconstructed = [Message.from_api_format(data) for data in api_formats[:100]]
    
    # Create 100 conversation turns
    turns = []
    for i in range(100):
        turn = ConversationTurn(
            messages=[messages[i], messages[i+1]],
            response=messages[i+2] if i+2 < len(messages) else None,
            tokens_used=100 + i,
            latency_ms=50.0 + i
        )
        turns.append(turn)
    
    elapsed = time.perf_counter() - start
    return elapsed

if __name__ == "__main__":
    elapsed = benchmark_messages()
    print(f"{elapsed:.6f}")
