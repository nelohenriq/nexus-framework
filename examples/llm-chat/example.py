#!/usr/bin/env python3
"""LLM Chat Example - Integration with LLM providers."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nexus.container import DIContainer
from nexus.efficiency import PromptCache, RateLimiter, BudgetEnforcer, BudgetConfig
from nexus.core import Message, MessageRole, MemoryManager, AgentContext

def main():
    print("=== LLM Chat Example ===")
    print()

    # 1. Set up DI Container with LLM configuration
    container = DIContainer()
    print("1. DI Container created for LLM integration")

    # 2. Configure efficiency layer
    cache = PromptCache(max_entries=100)
    limiter = RateLimiter(max_rpm=60)
    budget = BudgetEnforcer(BudgetConfig(max_tokens=10000))
    print("2. Efficiency layer configured:")
    print(f" - PromptCache: {cache._max_entries} entries")
    print(f" - RateLimiter: {limiter._max_rpm} RPM")
    print(f" - BudgetEnforcer: {budget._config.max_tokens} tokens")

    # 3. Create conversation context
    context = AgentContext(agent_id="llm_chat_agent")
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
        Message(role=MessageRole.USER, content="What is machine learning?")
    ]
    for msg in messages:
        context.add_message(msg)
    print(f"3. Conversation context: {len(context.get_messages())} messages")

    # 4. Set up memory for conversation history
    memory = MemoryManager(db_path=":memory:")
    memory.save("conversation_1", {"topic": "machine learning", "messages": 2})
    print(f"4. Memory initialized: {memory.load("conversation_1")}")

    # 5. Demonstrate prompt caching
    cache.put("You are a helpful assistant.", 10)
    entry = cache.get_cached("You are a helpful assistant.")
    if entry:
        print(f"5. Prompt cached: {entry.prefix_hash}...")
    else:
        print("5. Prompt not found in cache")

    # 6. Check rate limit status
    status = limiter.get_status()
    print(f"6. Rate limit status: {status.requests_remaining} requests remaining")

    print()
    print("=== Example Complete ===")

if __name__ == "__main__":
    main()