"""
NEXUS Framework - OpenAI Adapter

Native OpenAI API adapter with full feature support.
"""

from __future__ import annotations

import json
from typing import AsyncIterator

from nexus.ports import Message, StreamChunk, ToolCall, ModelInfo
from nexus.adapters.llm.base import BaseLLMAdapter


class OpenAIAdapter(BaseLLMAdapter):
    """OpenAI API adapter."""

    def __init__(self, model: str = "gpt-4-turbo", api_key: str | None = None, base_url: str | None = None) -> None:
        super().__init__(model, api_key=api_key, base_url=base_url)
        self.api_key = api_key
        self.base_url = base_url or "https://api.openai.com/v1"
        self._client = None

    async def _get_client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                raise ImportError("openai package required: pip install openai")
        return self._client

    async def complete(self, messages, tools=None, temperature=0.7, max_tokens=None, **kwargs) -> Message:
        client = await self._get_client()
        normalized = self._normalize_messages(messages)
        response = await client.chat.completions.create(
            model=self.model,
            messages=normalized,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice="auto" if tools else None,
        )
        choice = response.choices[0]
        tool_calls = None
        if choice.message.tool_calls:
            tool_calls = [
                ToolCall(id=tc.id, name=tc.function.name, arguments=json.loads(tc.function.arguments))
                for tc in choice.message.tool_calls
            ]
        return Message(role="assistant", content=choice.message.content, tool_calls=tool_calls)

    async def stream(self, messages, tools=None, temperature=0.7, max_tokens=None, **kwargs) -> AsyncIterator[StreamChunk]:
        client = await self._get_client()
        normalized = self._normalize_messages(messages)
        stream = await client.chat.completions.create(
            model=self.model,
            messages=normalized,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta:
                yield StreamChunk(content=delta.content, is_final=bool(chunk.choices[0].finish_reason))

    async def embed(self, text, model=None) -> list[list[float]]:
        client = await self._get_client()
        texts = [text] if isinstance(text, str) else text
        response = await client.embeddings.create(
            model=model or "text-embedding-3-small",
            input=texts,
        )
        return [e.embedding for e in response.data]

    async def _fetch_model_info(self) -> ModelInfo:
        return ModelInfo(
            id=self.model,
            name=self.model,
            context_window=128000 if "gpt-4" in self.model else 16385,
            supports_vision="vision" in self.model or "gpt-4o" in self.model,
            supports_tools=True,
            supports_streaming=True,
        )


__all__ = ["OpenAIAdapter"]
