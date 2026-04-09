"""
NEXUS Framework - Ollama Adapter

Local model support via Ollama. No API key required.
"""

from __future__ import annotations

import json
import aiohttp
from typing import AsyncIterator

from nexus.ports import Message, StreamChunk, ToolCall, ModelInfo
from nexus.adapters.llm.base import BaseLLMAdapter


class OllamaAdapter(BaseLLMAdapter):
    """Ollama local model adapter."""

    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434") -> None:
        super().__init__(model, base_url=base_url)
        self.base_url = base_url.rstrip("/")

    async def complete(self, messages, tools=None, temperature=0.7, max_tokens=None, **kwargs) -> Message:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model,
                "messages": self._normalize_messages(messages),
                "options": {"temperature": temperature},
                "stream": False,
            }
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            async with session.post(f"{self.base_url}/api/chat", json=payload) as resp:
                data = await resp.json()
                return Message(role="assistant", content=data.get("message", {}).get("content", ""))

    async def stream(self, messages, tools=None, temperature=0.7, max_tokens=None, **kwargs) -> AsyncIterator[StreamChunk]:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model,
                "messages": self._normalize_messages(messages),
                "options": {"temperature": temperature},
                "stream": True,
            }
            async with session.post(f"{self.base_url}/api/chat", json=payload) as resp:
                async for line in resp.content:
                    if line.strip():
                        data = json.loads(line)
                        if "message" in data:
                            yield StreamChunk(
                                content=data["message"].get("content"),
                                is_final=data.get("done", False),
                            )

    async def embed(self, text, model=None) -> list[list[float]]:
        async with aiohttp.ClientSession() as session:
            texts = [text] if isinstance(text, str) else text
            payload = {"model": model or self.model, "input": texts}
            async with session.post(f"{self.base_url}/api/embeddings", json=payload) as resp:
                data = await resp.json()
                return [e["embedding"] for e in data.get("embeddings", [data.get("embedding")])]

    async def _fetch_model_info(self) -> ModelInfo:
        return ModelInfo(
            id=self.model,
            name=self.model,
            context_window=4096,
            supports_vision="llava" in self.model.lower(),
            supports_tools=False,
            supports_streaming=True,
        )


__all__ = ["OllamaAdapter"]
