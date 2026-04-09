"""
NEXUS Framework - Unified Agentic Framework

Integrating the best features from Hermes, OpenClaw, Agent Zero, and OpenFang
into a single, standalone, production-ready framework.

Features:
- Zero-glitch provider switching
- Built-in efficiency (prompt caching, rate limiting, TOON compression)
- 16 security layers
- Multimodal native support
- Hexagonal architecture with dependency injection

Usage:
 >>> import nexus
 >>> from nexus.container import DIContainer
 >>> from nexus.ports import LLMPort, MemoryPort
 >>> container = DIContainer()
 >>> llm = container.resolve(LLMPort)
"""

__version__ = "0.1.0"
__author__ = "nelohenriq"
__license__ = "MIT"

# Core components (will be available after Phase 3)
# from nexus.container import DIContainer, AdapterRegistry
# from nexus.ports import (
# LLMPort,
# MemoryPort,
# ChannelPort,
# StoragePort,
# MultimodalPort,
# SchedulePort,
# KnowledgePort,
# )

# Placeholder imports - Phase 1 provides foundation only
from nexus.container import DIContainer, AdapterRegistry
from nexus.ports import (
 LLMPort,
 MemoryPort,
 ChannelPort,
 StoragePort,
 MultimodalPort,
 SchedulePort,
 KnowledgePort,
)

# Core components - implemented in Phase 3
# from nexus.core.agent import Agent
# from nexus.core.memory import MemoryManager
# from nexus.core.tools import ToolRegistry
__all__ = [
 # Version
 "__version__",
 "__author__",
 "__license__",
 # Container
 "DIContainer",
 "AdapterRegistry",
 # Ports
 "LLMPort",
 "MemoryPort",
 "ChannelPort",
 "StoragePort",
 "MultimodalPort",
 "SchedulePort",
 "KnowledgePort",
 # Core - Phase 3
 # "Agent",
 # "MemoryManager",
 # "ToolRegistry",
]
