"""
NEXUS Framework - Configuration System

Simple, hierarchical configuration with:
- Zero-config defaults (Ollama if available)
- YAML file loading
- Environment variable expansion
- Provider-specific settings
"""

from __future__ import annotations

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

from nexus.ports import Provider


@dataclass
class LLMConfig:
    """LLM provider configuration."""
    provider: str = "ollama"
    model: str = "llama3.2"
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None


@dataclass
class MemoryConfig:
    """Memory configuration."""
    provider: str = "sqlite"
    path: str = "./nexus.db"
    vector_enabled: bool = True


@dataclass
class SecurityConfig:
    """Security configuration."""
    sandbox_enabled: bool = True
    audit_logging: bool = True
    rate_limit_rpm: int = 60


@dataclass
class NexusConfig:
    """Main NEXUS configuration."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    agent_name: str = "nexus-agent"
    log_level: str = "INFO"


class ConfigLoader:
    """Configuration loader with zero-config support."""

    DEFAULT_CONFIG_NAMES = ["nexus.yaml", "nexus.yml", ".nexus.yaml"]

    def __init__(self, config_path: str | Path | None = None):
        self.config_path = Path(config_path) if config_path else None
        self._config: NexusConfig | None = None

    def load(self) -> NexusConfig:
        if self._config:
            return self._config
        if self.config_path:
            self._config = self._load_from_file(self.config_path)
        else:
            self._config = self._auto_discover()
        return self._config

    def _auto_discover(self) -> NexusConfig:
        for name in self.DEFAULT_CONFIG_NAMES:
            path = Path(name)
            if path.exists():
                return self._load_from_file(path)
        return self._get_zero_config()

    def _load_from_file(self, path: Path) -> NexusConfig:
        with open(path) as f:
            raw = yaml.safe_load(f) or {}
        raw = self._expand_env_vars(raw)
        return self._parse_config(raw)

    def _expand_env_vars(self, data: dict) -> dict:
        result = {}
        for key, value in data.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                var_name = value[2:-1]
                value = os.environ.get(var_name, "")
            elif isinstance(value, dict):
                value = self._expand_env_vars(value)
            result[key] = value
        return result

    def _parse_config(self, raw: dict) -> NexusConfig:
        llm_raw = raw.get("llm", {})
        llm_config = LLMConfig(
            provider=llm_raw.get("provider", "ollama"),
            model=llm_raw.get("model", "llama3.2"),
            api_key=llm_raw.get("api_key"),
            base_url=llm_raw.get("base_url"),
            temperature=llm_raw.get("temperature", 0.7),
            max_tokens=llm_raw.get("max_tokens"),
        )
        memory_raw = raw.get("memory", {})
        memory_config = MemoryConfig(
            provider=memory_raw.get("provider", "sqlite"),
            path=memory_raw.get("path", "./nexus.db"),
            vector_enabled=memory_raw.get("vector_enabled", True),
        )
        security_raw = raw.get("security", {})
        security_config = SecurityConfig(
            sandbox_enabled=security_raw.get("sandbox_enabled", True),
            audit_logging=security_raw.get("audit_logging", True),
            rate_limit_rpm=security_raw.get("rate_limit_rpm", 60),
        )
        return NexusConfig(
            llm=llm_config,
            memory=memory_config,
            security=security_config,
            agent_name=raw.get("agent_name", "nexus-agent"),
            log_level=raw.get("log_level", "INFO"),
        )

    def _get_zero_config(self) -> NexusConfig:
        if self._check_ollama():
            return NexusConfig(llm=LLMConfig(provider="ollama", model="llama3.2"))
        return NexusConfig()

    def _check_ollama(self) -> bool:
        try:
            import aiohttp
            import asyncio
            async def check():
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:11434/api/version", timeout=aiohttp.ClientTimeout(total=2)) as resp:
                        return resp.status == 200
            try:
                return asyncio.get_event_loop().run_until_complete(check())
            except:
                return False
        except:
            return False


def load_config(path: str | Path | None = None) -> NexusConfig:
    """Convenience function to load configuration."""
    return ConfigLoader(path).load()


def create_adapter_from_config(config: NexusConfig):
    """Create LLM adapter from configuration."""
    from nexus.adapters.llm import OpenAIAdapter, OllamaAdapter, AnthropicAdapter, OpenAICompatibleAdapter
    provider = config.llm.provider
    if provider == "openai":
        return OpenAIAdapter(model=config.llm.model, api_key=config.llm.api_key, base_url=config.llm.base_url)
    elif provider == "ollama":
        return OllamaAdapter(model=config.llm.model, base_url=config.llm.base_url or "http://localhost:11434")
    elif provider == "anthropic":
        return AnthropicAdapter(model=config.llm.model, api_key=config.llm.api_key)
    elif provider == "openai-compatible":
        return OpenAICompatibleAdapter(model=config.llm.model, base_url=config.llm.base_url)
    else:
        raise ValueError(f"Unknown provider: {provider}")


__all__ = ["NexusConfig", "LLMConfig", "MemoryConfig", "SecurityConfig", "ConfigLoader", "load_config", "create_adapter_from_config"]
