"""Unified Backend Interface - Single API for all LLM providers."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Iterator
from datetime import datetime
import json


@dataclass(slots=True)
class LLMResponse:
    content: str
    model: str
    provider: str
    tokens_used: int = 0
    latency_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedBackend:
    def __init__(self):
        self.providers = {}
        self.default_provider = None
        self.default_model = None

    def register_provider(self, name: str, client: Any, models: List[str], is_default: bool = False):
        self.providers[name] = {"client": client, "models": models}
        if is_default or not self.default_provider:
            self.default_provider = name
            self.default_model = models[0] if models else None

    def generate(self, prompt: str, model: Optional[str] = None, provider: Optional[str] = None, **kwargs) -> LLMResponse:
        provider = provider or self.default_provider
        if not provider or provider not in self.providers:
            return LLMResponse(content="", model="", provider="error", metadata={"error": "No provider available"})
        model = model or self.default_model
        p = self.providers[provider]
        start = datetime.now()
        try:
            client = p["client"]
            response = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], **kwargs)
            latency = (datetime.now() - start).total_seconds() * 1000
            return LLMResponse(content=response.choices[0].message.content, model=model, provider=provider, tokens_used=response.usage.total_tokens if hasattr(response, "usage") else 0, latency_ms=latency)
        except Exception as e:
            return LLMResponse(content="", model=model or "", provider=provider or "", metadata={"error": str(e)})

    def stream(self, prompt: str, model: Optional[str] = None, provider: Optional[str] = None, **kwargs) -> Iterator[str]:
        provider = provider or self.default_provider
        if not provider or provider not in self.providers:
            return
        model = model or self.default_model
        p = self.providers[provider]
        try:
            client = p["client"]
            response = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], stream=True, **kwargs)
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception:
            return

    def list_providers(self) -> List[str]:
        return list(self.providers.keys())

    def list_models(self, provider: Optional[str] = None) -> List[str]:
        provider = provider or self.default_provider
        if provider and provider in self.providers:
            return self.providers[provider]["models"]
        return []


def create_unified_backend():
    return UnifiedBackend()