"""
NEXUS Framework - Base LLM Adapter

Abstract base class for all LLM adapters.
Provides common functionality for zero-glitch provider switching.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator

from nexus.ports import LLMPort, Message, StreamChunk, ModelInfo


class BaseLLMAdapter(LLMPort, ABC):
    """Abstract base class for LLM adapters."""

    def __init__(self, model: str, **kwargs) -> None:
        self.model = model
        self._model_info: ModelInfo | None = None
        self._config = kwargs

    @abstractmethod
    async def complete(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> Message:
        pass

    @abstractmethod
    async def stream(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        pass

    @abstractmethod
    async def embed(
        self,
        text: str | list[str],
        model: str | None = None,
    ) -> list[list[float]]:
        pass

    async def get_model_info(self) -> ModelInfo:
        if self._model_info is None:
            self._model_info = await self._fetch_model_info()
        return self._model_info

    @abstractmethod
    async def _fetch_model_info(self) -> ModelInfo:
        pass

    async def count_tokens(self, messages: list[Message]) -> int:
        total = 0
        for msg in messages:
            content = msg.content
            if isinstance(content, str):
                total += len(content.split())
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, str):
                        total += len(part.split())
        return total

    def _normalize_messages(self, messages: list[Message]) -> list[dict]:
        result = []
        for msg in messages:
            entry = {"role": msg.role}
            if msg.content:
                entry["content"] = msg.content
            if msg.tool_calls:
                entry["tool_calls"] = [
                    {"id": tc.id, "type": "function", "function": {"name": tc.name, "arguments": tc.arguments}}
                    for tc in msg.tool_calls
                ]
            if msg.tool_call_id:
                entry["tool_call_id"] = msg.tool_call_id
            result.append(entry)
        return result


__all__ = ["BaseLLMAdapter"]
