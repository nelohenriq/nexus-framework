"""NEXUS Memory Module.

This module provides comprehensive memory management for AI agents:

Phase 11 - Memory Revolution:
- L0-L3 Memory Stack: Efficient tiered memory (~170 tokens for session start)
- Palace Architecture: Wings/Rooms/Halls/Tunnels organization
- Temporal Knowledge Graph: Facts with validity windows
- Entity Detection: Automatic entity capture from messages
- Three-File Memory: Human-readable, git-trackable memory files
"""

# L0-L3 Memory Stack
from .stack import (
 MemoryStack,
 L0IdentityLayer,
 L1CriticalFactsLayer,
 L2RoomRecallLayer,
 L3DeepSearchLayer,
 create_memory_stack
)

# Palace Architecture
from .palace import (
 Palace,
 Wing,
 Room,
 Hall,
 Memory as PalaceMemory,
 MemoryType,
 Tunnel,
 create_palace,
 generate_memory_id
)

# Temporal Knowledge Graph
from .temporal_kg import (
 TemporalKnowledgeGraph,
 TemporalFact,
 Entity as KGEntity,
 FactStatus,
 RelationType,
 create_temporal_kg
)

# Entity Detection
from .entity_detection import (
 EntityDetector,
 Entity,
 EntityType,
 EntityDetectionResult,
 EntityTracker,
 create_entity_detector,
 detect_entities
)

# Three-File Memory
from .three_file import (
 ThreeFileMemory,
 ContextEntry,
 DecisionEntry,
 LearningEntry,
 create_three_file_memory
)

__all__ = [
 # Memory Stack
 "MemoryStack",
 "L0IdentityLayer",
 "L1CriticalFactsLayer",
 "L2RoomRecallLayer",
 "L3DeepSearchLayer",
 "create_memory_stack",
 # Palace
 "Palace",
 "Wing",
 "Room",
 "Hall",
 "PalaceMemory",
 "MemoryType",
 "Tunnel",
 "create_palace",
 "generate_memory_id",
 # Temporal KG
 "TemporalKnowledgeGraph",
 "TemporalFact",
 "KGEntity",
 "FactStatus",
 "RelationType",
 "create_temporal_kg",
 # Entity Detection
 "EntityDetector",
 "Entity",
 "EntityType",
 "EntityDetectionResult",
 "EntityTracker",
 "create_entity_detector",
 "detect_entities",
 # Three-File Memory
 "ThreeFileMemory",
 "ContextEntry",
 "DecisionEntry",
 "LearningEntry",
 "create_three_file_memory"
]
