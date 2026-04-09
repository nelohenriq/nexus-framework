"""
NEXUS Framework - Anthropic Adapter

Native Anthropic Claude API adapter.
"""

from __future__ import annotations

import json
from typing import AsyncIterator

from nexus.ports import Message, StreamChunk, ToolCall, ModelInfo
from nexus.adapters.llm.base import BaseLLMAdapter


class AnthropicAdapter(BaseLLMAdapter):
    """Anthropic Claude API adapter."""

    def __init__(self, model: str = "claude-sonnet-4-20250514", api_key: str | None = None) -> None:
        super().__init__(model, api_key=api_key)
        self.api_key = api_key
        self._client = None

    async def _get_client(self):
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic
                self._client = AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package required: pip install anthropic")
        return self._client

    def _convert_messages(self, messages):
        system = None
        converted = []
        for msg in messages:
            if msg.role == "system":
                system = msg.content if isinstance(msg.content, str) else str(msg.content)
            else:
                converted.append({"role": msg.role, "content": msg.content})
        return system, converted

    async def complete(self, messages, tools=None, temperature=0.7, max_tokens=None, **kwargs) -> Message:
        client = await self._get_client()
        system, converted = self._convert_messages(messages)
        response = await client.messages.create(
            model=self.model,
            system=system,
            messages=converted,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
            tools=tools,
        )
        tool_calls = None
        content_text = None
        for block in response.content:
            if hasattr(block, "text"):
                content_text = block.text
            elif hasattr(block, "name"):
                if not tool_calls:
                    tool_calls = []
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=dict(block.input) if block.input else {},
                ))
        return Message(role="assistant", content=content_text, tool_calls=tool_calls)

    async def stream(self, messages, tools=None, temperature=0.7, max_tokens=None, **kwargs) -> AsyncIterator[StreamChunk]:
        client = await self._get_client()
        system, converted = self._convert_messages(messages)
        async with client.messages.stream(
            model=self.model,
            system=system,
            messages=converted,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
        ) as stream:
            async for text in stream.text_stream:
                yield StreamChunk(content=text)
            yield StreamChunk(is_final=True)

    async def embed(self, text, model=None) -> list[list[float]]:
        raise NotImplementedError("Anthropic does not provide embedding API")

    async def _fetch_model_info(self) -> ModelInfo:
        return ModelInfo(
            id=self.model,
            name=self.model,
            context_window=200000,
            supports_vision="claude-3" in self.model,
            supports_tools=True,
            supports_streaming=True,
        )


__all__ = ["AnthropicAdapter"]
