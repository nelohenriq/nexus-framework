"""Meta configuration models for meta-agentic SDK."""

from pydantic import BaseModel, Field
from typing import Dict, Optional, Any
from pathlib import Path


class HermesBackendConfig(BaseModel):
    """Configuration for Hermes backend."""
    home: str = Field(default="~/.hermes", description="Hermes home directory")
    hermes_bin: Optional[str] = Field(default="hermes", description="Optional explicit CLI path")


class BackendConfigs(BaseModel):
    """Container for backend configurations."""
    hermes: Optional[HermesBackendConfig] = None


class MetaConfig(BaseModel):
    """Top-level meta configuration from meta.yaml."""
    version: str = Field(default="0.1", description="Config version")
    default_backend: str = Field(default="hermes", description="Default backend to use")
    backends: BackendConfigs = Field(default_factory=BackendConfigs)

    @classmethod
    def from_yaml(cls, path: Path) -> "MetaConfig":
        """Load MetaConfig from a meta.yaml file."""
        import yaml
        content = path.read_text()
        data = yaml.safe_load(content) or {}
        return cls(**data)
