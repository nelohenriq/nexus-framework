"""
NEXUS Framework - Port Protocols

Protocol interfaces for hexagonal architecture.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import AsyncIterator, Callable, Protocol, TypeVar, runtime_checkable

@dataclass(frozen=True)
class ToolCall:
    """Normalized tool call."""
    id: str
    name: str
    arguments: dict
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class ToolResult:
    """Result of a tool execution."""
    tool_call_id: str
    result: str
    is_error: bool = False
    metadata: dict = field(default_factory=dict)

@dataclass
class StreamChunk:
    """Normalized streaming chunk."""
    content: str | None = None
    tool_calls: list[ToolCall] | None = None
    is_final: bool = False
    finish_reason: str | None = None
    metadata: dict = field(default_factory=dict)

@dataclass
class Message:
    """Chat message with normalized structure."""
    role: str
    content: str | list | None = None
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None
    name: str | None = None
    metadata: dict = field(default_factory=dict)

@dataclass
class MemoryHit:
    """Result from memory search."""
    id: str
    content: str
    score: float
    metadata: dict = field(default_factory=dict)
    created_at: datetime | None = None

@dataclass
class ModelInfo:
    """Model capability information."""
    id: str
    name: str
    context_window: int
    supports_vision: bool = False
    supports_tools: bool = True
    supports_streaming: bool = True
    max_output_tokens: int | None = None

@dataclass
class UsageStats:
    """Token usage statistics."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cached_tokens: int = 0
    cost: float | None = None

class Provider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    OPENAI_COMPATIBLE = "openai-compatible"
    NVIDIA = "nvidia"

@runtime_checkable
class LLMPort(Protocol):
    """LLM abstraction for model-agnostic integration."""
    async def complete(self, messages, tools=None, temperature=0.7, max_tokens=None, **kwargs): pass
    async def stream(self, messages, tools=None, temperature=0.7, max_tokens=None, **kwargs): pass
    async def embed(self, text, model=None): pass
    async def get_model_info(self): pass
    async def count_tokens(self, messages): pass

@runtime_checkable
class MemoryPort(Protocol):
    """Memory abstraction for persistent storage."""
    async def remember(self, fact, metadata=None): pass
    async def recall(self, query, limit=10): pass
    async def forget(self, fact_id): pass
    async def search_semantic(self, query, threshold=0.7, limit=10): pass

@runtime_checkable
class ChannelPort(Protocol):
    """Channel abstraction for multi-platform support."""
    async def send(self, message): pass
    async def receive(self): pass
    async def get_history(self, limit=100): pass

@runtime_checkable
class StoragePort(Protocol):
    """Storage abstraction for files and blobs."""
    async def read(self, path): pass
    async def write(self, path, data): pass
    async def delete(self, path): pass
    async def list_files(self, prefix): pass

@runtime_checkable
class MultimodalPort(Protocol):
    """Multimodal input/output abstraction."""
    async def process_image(self, image, format="auto"): pass
    async def process_pdf(self, pdf, extract_images=True): pass
    async def transcribe_audio(self, audio, language="en"): pass

@runtime_checkable
class SchedulePort(Protocol):
    """Scheduler abstraction for autonomous tasks."""
    async def schedule(self, task_id, cron, handler): pass
    async def schedule_once(self, task_id, delay_seconds, handler): pass
    async def cancel(self, task_id): pass
    async def get_scheduled(self): pass

@runtime_checkable
class KnowledgePort(Protocol):
    """Knowledge graph abstraction."""
    async def add_entity(self, entity_type, entity_id, properties): pass
    async def add_relation(self, from_entity, relation, to_entity, properties=None): pass
    async def query(self, query, params=None): pass

T = TypeVar("T")

@runtime_checkable
class Port(Protocol[T]):
    """Base Port protocol."""
    pass

__all__ = ["ToolCall", "ToolResult", "StreamChunk", "Message", "MemoryHit", "ModelInfo", "UsageStats", "Provider", "LLMPort", "MemoryPort", "ChannelPort", "StoragePort", "MultimodalPort", "SchedulePort", "KnowledgePort", "Port"]
