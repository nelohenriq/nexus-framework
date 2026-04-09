"""
NEXUS Framework - OpenAI-Compatible Adapter

Works with vLLM, LM Studio, LocalAI, and other OpenAI-compatible APIs.
"""

from __future__ import annotations

from nexus.adapters.llm.openai import OpenAIAdapter


class OpenAICompatibleAdapter(OpenAIAdapter):
    """Adapter for OpenAI-compatible endpoints (vLLM, LM Studio, etc.)."""

    def __init__(self, model: str, base_url: str, api_key: str = "sk-dummy") -> None:
        super().__init__(model=model, api_key=api_key, base_url=base_url)

    async def _fetch_model_info(self):
        from nexus.ports import ModelInfo
        return ModelInfo(
            id=self.model,
            name=self.model,
            context_window=4096,
            supports_vision=False,
            supports_tools=True,
            supports_streaming=True,
        )


__all__ = ["OpenAICompatibleAdapter"]
