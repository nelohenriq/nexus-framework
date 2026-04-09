"""Agent descriptor models for meta-agentic SDK."""

from pydantic import BaseModel, Field
from typing import List, Optional


class SecurityPolicyRef(BaseModel):
 """Reference to a security policy."""
 name: str


class AgentDescriptor(BaseModel):
 """Represents an abstract agent configuration that can be mapped onto Hermes (and later other backends)."""
 
 id: str = Field(..., description="Unique ID, used in filenames & references")
 name: str
 role: str
 system_prompt: str
 
 skills: List[str] = Field(
 default_factory=list,
 description="List of skill IDs, e.g., 'core/example-skill'",
 )
 tools: List[str] = Field(
 default_factory=list,
 description="Logical tool names; backend decides concrete mapping",
 )
 
 project: Optional[str] = Field(
 default=None,
 description="Default project ID this agent operates in",
 )
 
 model: Optional[str] = Field(
 default=None,
 description="Logical model name, to be mapped to Hermes config",
 )
 
 security: Optional[SecurityPolicyRef] = None
