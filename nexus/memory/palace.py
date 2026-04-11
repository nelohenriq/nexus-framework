"""Palace Architecture Implementation."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
from enum import Enum
import json
import hashlib


class MemoryType(Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"

    @classmethod
    def from_string(cls, value: str):
        try:
            return cls[value.upper()]
        except KeyError:
            return cls.SEMANTIC


@dataclass
class Tunnel:
    source_id: str
    target_id: str
    relationship: str
    strength: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship": self.relationship,
            "strength": self.strength,
            "metadata": self.metadata
        }


@dataclass
class Memory:
    id: str
    content: str
    memory_type: MemoryType
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    importance: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "timestamp": self.timestamp,
            "importance": self.importance,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            content=data["content"],
            memory_type=MemoryType.from_string(data.get("memory_type", "semantic")),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            importance=data.get("importance", 1.0),
            metadata=data.get("metadata", {})
        )


@dataclass
class Hall:
    name: str
    memory_type: MemoryType
    memories: Dict[str, Memory] = field(default_factory=dict)
    tunnels: List[Tunnel] = field(default_factory=list)

    def add_memory(self, memory: Memory):
        self.memories[memory.id] = memory
        return memory.id

    def search(self, query: str, top_k: int = 5):
        results = []
        query_lower = query.lower()
        for memory in self.memories.values():
            if query_lower in memory.content.lower():
                results.append(memory)
        results.sort(key=lambda x: x.importance, reverse=True)
        return results[:top_k]


@dataclass
class Room:
    name: str
    description: str = ""
    halls: Dict[str, Hall] = field(default_factory=dict)

    def __post_init__(self):
        if not self.halls:
            for mt in MemoryType:
                self.halls[mt.value] = Hall(name=mt.value, memory_type=mt)

    def add_memory(self, memory: Memory, hall: str = "semantic"):
        if hall not in self.halls:
            self.halls[hall] = Hall(name=hall, memory_type=MemoryType.from_string(hall))
        return self.halls[hall].add_memory(memory)


@dataclass
class Wing:
    name: str
    description: str = ""
    rooms: Dict[str, Room] = field(default_factory=dict)

    def add_room(self, name: str, description: str = ""):
        if name not in self.rooms:
            self.rooms[name] = Room(name=name, description=description)
        return self.rooms[name]


@dataclass
class Palace:
    wings: Dict[str, Wing] = field(default_factory=dict)
    name: str = "Memory Palace"

    def __post_init__(self):
        if not self.wings:
            self.wings = {
                "People": Wing(name="People"),
                "Projects": Wing(name="Projects"),
                "Concepts": Wing(name="Concepts")
            }

    def add_memory(self, wing: str, room: str, hall: str, memory: Memory):
        if wing not in self.wings:
            self.wings[wing] = Wing(name=wing)
        if room not in self.wings[wing].rooms:
            self.wings[wing].rooms[room] = Room(name=room)
        return self.wings[wing].rooms[room].add_memory(memory, hall)

    def search(self, query: str, top_k: int = 10):
        results = []
        for wing in self.wings.values():
            for room in wing.rooms.values():
                for hall in room.halls.values():
                    results.extend(hall.search(query, top_k))
        results.sort(key=lambda x: x.importance, reverse=True)
        return results[:top_k]


def create_palace(name: str = "Memory Palace"):
    return Palace(name=name)


def generate_memory_id(content: str):
    timestamp = datetime.now().isoformat()
    return hashlib.md5(f"{content}:{timestamp}".encode()).hexdigest()[:12]
