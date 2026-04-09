"""Project configuration models for meta-agentic SDK."""

from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional


class ProjectConfig(BaseModel):
 """Represents a project configuration."""
 
 id: str
 name: str
 path: Path
 default_agent: Optional[str] = None


# Note: path is set programmatically to the directory containing config.yaml
