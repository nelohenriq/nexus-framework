"""
NEXUS Framework - Port Protocols

This module defines the protocol interfaces (Ports) for the hexagonal architecture.
Each Port defines a contract that Adapters must implement, enabling:
- Clean separation of concerns
- Easy testing with mock adapters
- Provider-agnostic implementation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import AsyncIterator, Callable, Protocol, TypeVar, runtime_checkable

# ============================================================================
# Data Classes (Normalized Structures)
# ============================================================================


@dataclass(frozen=True)
class ToolCall:
 """Normalized tool call - works identically across all providers."""
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


# ============================================================================
# Port Protocols
# ============================================================================


@runtime_checkable
class LLMPort(Protocol):
 """LLM abstraction for model-agnostic integration."""

 async def complete(
 self,
 messages: list[Message],
 tools: list[dict] | None = None,
 temperature: float = 0.7,
 max_tokens: int | None = None,
 **kwargs,
 ) -> Message:
 """Generate a completion."""
 ...

 async def stream(
 self,
 messages: list[Message],
 tools: list[dict] | None = None,
 temperature: float = 0.7,
 max_tokens: int | None = None,
 **kwargs,
 ) -> AsyncIterator[StreamChunk]:
 """Generate a streaming completion."""
 ...

 async def embed(
 self,
 text: str | list[str],
 model: str | None = None,
 ) -> list[list[float]]:
 """Generate embeddings."""
 ...

 async def get_model_info(self) -> ModelInfo:
 """Get model capabilities."""
 ...

 async def count_tokens(self, messages: list[Message]) -> int:
 """Count tokens in messages."""
 ...


@runtime_checkable
class MemoryPort(Protocol):
 """Memory abstraction for persistent storage."""

 async def remember(self, fact: str, metadata: dict | None = None) -> str: ...
 async def recall(self, query: str, limit: int = 10) -> list[MemoryHit]: ...
 async def forget(self, fact_id: str) -> bool: ...
 async def search_semantic(
 self, query: str, threshold: float = 0.7, limit: int = 10
 ) -> list[MemoryHit]: ...


@runtime_checkable
class ChannelPort(Protocol):
 """Channel abstraction for multi-platform support."""

 async def send(self, message: Message) -> None: ...
 async def receive(self) -> AsyncIterator[Message]: ...
 async def get_history(self, limit: int = 100) -> list[Message]: ...


@runtime_checkable
class StoragePort(Protocol):
 """Storage abstraction for files and blobs."""

 async def read(self, path: str) -> bytes: ...
 async def write(self, path: str, data: bytes) -> None: ...
 async def delete(self, path: str) -> bool: ...
 async def list_files(self, prefix: str) -> list[str]: ...


@runtime_checkable
class MultimodalPort(Protocol):
 """Multimodal input/output abstraction."""

 async def process_image(self, image: bytes | str, format: str = "auto") -> dict: ...
 async def process_pdf(
 self, pdf: bytes | str, extract_images: bool = True
 ) -> dict: ...
 async def transcribe_audio(
 self, audio: bytes | str, language: str = "en"
 ) -> dict: ...


@runtime_checkable
class SchedulePort(Protocol):
 """Scheduler abstraction for autonomous tasks."""

 async def schedule(
 self, task_id: str, cron: str, handler: Callable[[], None]
 ) -> None: ...
 async def schedule_once(
 self, task_id: str, delay_seconds: float, handler: Callable[[], None]
 ) -> None: ...
 async def cancel(self, task_id: str) -> bool: ...
 async def get_scheduled(self) -> list[dict]: ...


@runtime_checkable
class KnowledgePort(Protocol):
 """Knowledge graph abstraction."""

 async def add_entity(
 self, entity_type: str, entity_id: str, properties: dict
 ) -> None: ...
 async def add_relation(
 self,
 from_entity: tuple[str, str],
 relation: str,
 to_entity: tuple[str, str],
 properties: dict | None = None,
 ) -> None: ...
 async def query(self, query: str, params: dict | None = None) -> list[dict]: ...


T = TypeVar("T")


@runtime_checkable
class Port(Protocol[T]):
 """Base Port protocol for type-safe dependency injection."""

 pass


__all__ = [
 "ToolCall",
 "ToolResult",
 "StreamChunk",
 "Message",
 "MemoryHit",
 "ModelInfo",
 "UsageStats",
 "Provider",
 "LLMPort",
 "MemoryPort",
 "ChannelPort",
 "StoragePort",
 "MultimodalPort",
 "SchedulePort",
 "KnowledgePort",
 "Port",
]
