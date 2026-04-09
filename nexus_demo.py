#!/usr/bin/env python3
"""NEXUS Framework Demo - Showcasing all 6 phases."""

import sys
import os
import time
import uuid

# Add nexus to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("NEXUS Framework Demo - All 6 Phases")
    print("=" * 60)
    print()

    # ========================================
    # PHASE 1: DI Container & Configuration
    # ========================================
    print("[Phase 1] DI Container & Configuration")
    print("-" * 40)
    from nexus.container import DIContainer

    container = DIContainer()
    print(f" DI Container created: {type(container).__name__}")
    print(f" Bindings: {len(container._bindings)}")
    print(f" Singletons: {len(container._singletons)}")
    print()

    # ========================================
    # PHASE 2: Efficiency Layer
    # ========================================
    print("[Phase 2] Efficiency Layer")
    print("-" * 40)
    from nexus.efficiency import PromptCache, RateLimiter, BudgetEnforcer, BudgetConfig

    cache = PromptCache(max_entries=100)
    print(f" PromptCache: max_entries={cache._max_entries}")

    limiter = RateLimiter(max_rpm=60)
    print(f" RateLimiter: max_rpm={limiter._max_rpm}")

    config = BudgetConfig(max_tokens=10000)
    budget = BudgetEnforcer(config)
    print(f" BudgetEnforcer: max_tokens={config.max_tokens}")
    print()

    # ========================================
    # PHASE 3: Core Agent Components
    # ========================================
    print("[Phase 3] Core Agent Components")
    print("-" * 40)
    from nexus.core import Message, MessageRole, MemoryManager, AgentContext

    msg = Message(role=MessageRole.USER, content="Hello, NEXUS!")
    print(f" Message: role={msg.role.value}, content={msg.content[:20]}...")

    memory = MemoryManager(db_path=":memory:")
    memory.save("session_start", {"time": time.time()})
    print(f" MemoryManager: 1 entry saved")

    context = AgentContext(agent_id="demo_agent")
    checkpoint = context.create_checkpoint()
    print(f" AgentContext: checkpoint={checkpoint.checkpoint_id[:8]}...")
    print()

    # ========================================
    # PHASE 4: Security & Multimodal
    # ========================================
    print("[Phase 4] Security & Multimodal")
    print("-" * 40)
    from nexus.security import SecurityManager

    security = SecurityManager()
    print(f" SecurityManager: {len(security.layers)} security layers")

    # Test input validation
    passed, errors = security.check_input({"test": "data"})
    print(f" Input validation: {"passed" if passed else "failed"}")
    print()

    # ========================================
    # PHASE 5: Multi-Agent & Persistence
    # ========================================
    print("[Phase 5] Multi-Agent & Persistence")
    print("-" * 40)
    from nexus.multiagent import AgentRegistry, MessageBus, PersistenceManager, AgentMessage, MessageType, MessagePriority, AgentState

    registry = AgentRegistry()
    agent_id = registry.register("worker1", ["compute", "analyze"])
    print(f" AgentRegistry: registered agent {agent_id[:8]}")

    bus = MessageBus()
    bus.register_agent(agent_id)
    agent_msg = AgentMessage(
        message_id=str(uuid.uuid4()),
        sender_id="demo",
        receiver_id=agent_id,
        message_type=MessageType.TASK,
        priority=MessagePriority.NORMAL,
        content={"task": "test"}
    )
    bus.send(agent_msg)
    received = bus.receive(agent_id)
    print(f" MessageBus: sent and received message")

    persistence = PersistenceManager(db_path=":memory:")
    agent_state = AgentState(
        agent_id=agent_id,
        name="worker1",
        status="active",
        context={"task": "demo"}
    )
    persistence.save_agent_state(agent_state)
    print(f" PersistenceManager: saved agent state")
    print()

    # ========================================
    # PHASE 6: Autonomous Features
    # ========================================
    print("[Phase 6] Autonomous Features")
    print("-" * 40)
    from nexus.autonomous import HealthMonitor, SelfHealingManager, TaskScheduler, LearningEngine

    # Health Monitor
    health = HealthMonitor(check_interval=5.0)
    status = health.get_status()
    print(f" HealthMonitor: {status["overall"]} status")

    # Self-Healing Manager
    healing = SelfHealingManager(max_retries=3)
    print(f" SelfHealingManager: max_retries={healing._max_retries}")

    # Task Scheduler
    scheduler = TaskScheduler(max_workers=2)
    task_id = scheduler.schedule("demo_task", lambda: "Task completed!")
    print(f" TaskScheduler: scheduled task {task_id}")

    # Learning Engine
    learning = LearningEngine()
    learning.record_learning("demo_event", {"test": True}, "success")
    print(f" LearningEngine: recorded 1 learning event")
    print()

    # ========================================
    # Summary
    # ========================================
    print("=" * 60)
    print("NEXUS Framework Demo Complete!")
    print("=" * 60)
    print()
    print("All 6 phases operational:")
    print(" [OK] Phase 1: DI Container & Configuration")
    print(" [OK] Phase 2: Efficiency Layer")
    print(" [OK] Phase 3: Core Agent Components")
    print(" [OK] Phase 4: Security & Multimodal")
    print(" [OK] Phase 5: Multi-Agent & Persistence")
    print(" [OK] Phase 6: Autonomous Features")
    print()

if __name__ == "__main__":
    main()