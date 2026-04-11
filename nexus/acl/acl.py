#!/usr/bin/env python3
"""
NEXUS Framework - Anti-Corruption Layer (ACL)

Translates external framework patterns to NEXUS native format.
Supports: Hermes, Agent Zero, OpenClaw, OpenFang
"""

from __future__ import annotations

import json
import re
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypeVar, Generic
from abc import ABC, abstractmethod
from datetime import datetime

# Import NEXUS types
try:
    from nexus.core.tools import ToolSpec, PermissionLevel
    from nexus.core.skills import SkillSpec
    from nexus.core.messages import Message
    from nexus.core.memory import MemoryEvent
except ImportError:
    # Fallback definitions for standalone use
    pass


# ============================================================================
# Core ACL Types
# ============================================================================

T = TypeVar("T")


@dataclass
class TranslationResult(Generic[T]):
    """Result of ACL translation."""
    success: bool
    data: Optional[T] = None
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    source_format: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "warnings": self.warnings,
            "errors": self.errors,
            "source_format": self.source_format
        }


class AntiCorruptionLayer(ABC, Generic[T]):
    """Base class for anti-corruption layer translators."""

    def __init__(self, source_format: str):
        self.source_format = source_format
        self._warnings: List[str] = []

    def _add_warning(self, msg: str) -> None:
        self._warnings.append(msg)

    def _reset_warnings(self) -> None:
        self._warnings = []

    @abstractmethod
    def translate_skill(self, source: Dict[str, Any]) -> TranslationResult:
        """Translate a skill definition."""
        pass

    @abstractmethod
    def translate_tool(self, source: Dict[str, Any]) -> TranslationResult:
        """Translate a tool definition."""
        pass

    @abstractmethod
    def translate_memory(self, source: Dict[str, Any]) -> TranslationResult:
        """Translate a memory entry."""
        pass


# ============================================================================
# Hermes ACL
# ============================================================================

class HermesACL(AntiCorruptionLayer):
    """Anti-corruption layer for Hermes framework."""

    def __init__(self):
        super().__init__("hermes")

    def translate_skill(self, source: Dict[str, Any]) -> TranslationResult:
        """Translate Hermes skill to NEXUS SkillSpec."""
        self._reset_warnings()
        try:
            # Hermes skills have YAML frontmatter
            name = source.get("name", "unnamed")
            description = source.get("description", "")
            parameters = source.get("parameters", {})
            content = source.get("content", "")

            # Convert Hermes parameter format to JSON Schema
            nexus_params = self._convert_hermes_params(parameters)

            skill_spec = {
                "name": name,
                "description": description,
                "parameters": nexus_params,
                "content": content,
                "tools": source.get("tools", []),
                "tags": source.get("tags", [])
            }

            return TranslationResult(
                success=True,
                data=skill_spec,
                warnings=self._warnings,
                source_format="hermes"
            )
        except Exception as e:
            return TranslationResult(
                success=False,
                errors=[str(e)],
                source_format="hermes"
            )

    def _convert_hermes_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Hermes parameter format to JSON Schema."""
        schema = {"type": "object", "properties": {}, "required": []}
        for name, spec in params.items():
            prop_spec = {"type": spec.get("type", "string")}
            if "description" in spec:
                prop_spec["description"] = spec["description"]
            if "default" in spec:
                prop_spec["default"] = spec["default"]
            if spec.get("required", False):
                schema["required"].append(name)
            schema["properties"][name] = prop_spec
        return schema

    def translate_tool(self, source: Dict[str, Any]) -> TranslationResult:
        """Translate Hermes tool to NEXUS ToolSpec."""
        self._reset_warnings()
        # Hermes tools are similar to NEXUS
        tool_spec = {
            "name": source.get("name", "unknown"),
            "description": source.get("description", ""),
            "parameters": source.get("input_schema", {}),
            "permission": "read"
        }
        return TranslationResult(
            success=True,
            data=tool_spec,
            warnings=self._warnings,
            source_format="hermes"
        )

    def translate_memory(self, source: Dict[str, Any]) -> TranslationResult:
        """Translate Hermes memory to NEXUS format."""
        memory_entry = {
            "key": source.get("key", ""),
            "value": source.get("value"),
            "timestamp": source.get("timestamp", datetime.now().isoformat()),
            "metadata": source.get("metadata", {})
        }
        return TranslationResult(
            success=True,
            data=memory_entry,
            source_format="hermes"
        )


# ============================================================================
# Agent Zero ACL
# ============================================================================

class AgentZeroACL(AntiCorruptionLayer):
    """Anti-corruption layer for Agent Zero framework."""

    def __init__(self):
        super().__init__("agent_zero")

    def translate_skill(self, source: Dict[str, Any]) -> TranslationResult:
        """Agent Zero uses different skill format."""
        self._reset_warnings()
        self._add_warning("Agent Zero uses different skill format, converting...")
        skill_spec = {
            "name": source.get("name", "unnamed"),
            "description": source.get("prompt", ""),
            "parameters": {"type": "object", "properties": {}},
            "content": source.get("prompt", ""),
            "tools": source.get("tools", []),
            "tags": ["agent_zero", "imported"]
        }
        return TranslationResult(
            success=True,
            data=skill_spec,
            warnings=self._warnings,
            source_format="agent_zero"
        )

    def translate_tool(self, source: Dict[str, Any]) -> TranslationResult:
        """Translate Agent Zero tool to NEXUS format."""
        self._reset_warnings()
        # Agent Zero tools have different structure
        tool_spec = {
            "name": source.get("name", "unknown"),
            "description": source.get("description", ""),
            "parameters": source.get("parameters", {}),
            "permission": self._map_az_permission(source.get("risk", "low"))
        }
        return TranslationResult(
            success=True,
            data=tool_spec,
            source_format="agent_zero"
        )

    def _map_az_permission(self, risk: str) -> str:
        """Map Agent Zero risk level to NEXUS permission."""
        mapping = {"low": "read", "medium": "write", "high": "execute", "critical": "admin"}
        return mapping.get(risk, "read")

    def translate_memory(self, source: Dict[str, Any]) -> TranslationResult:
        """Translate Agent Zero memory to NEXUS format."""
        memory_entry = {
            "key": source.get("key", ""),
            "value": source.get("content"),
            "timestamp": source.get("timestamp", datetime.now().isoformat()),
            "metadata": {
                "source": "agent_zero",
                "importance": source.get("importance", 0.5)
            }
        }
        return TranslationResult(
            success=True,
            data=memory_entry,
            source_format="agent_zero"
        )


# ============================================================================
# OpenClaw ACL
# ============================================================================

class OpenClawACL(AntiCorruptionLayer):
    """Anti-corruption layer for OpenClaw framework."""

    def __init__(self):
        super().__init__("openclaw")

    def translate_skill(self, source: Dict[str, Any]) -> TranslationResult:
        """Translate OpenClaw skill to NEXUS format."""
        skill_spec = {
            "name": source.get("name", "unnamed"),
            "description": source.get("description", ""),
            "parameters": source.get("schema", {"type": "object", "properties": {}}),
            "content": source.get("instructions", ""),
            "tools": source.get("tools", []),
            "tags": source.get("tags", ["openclaw", "imported"])
        }
        return TranslationResult(
            success=True,
            data=skill_spec,
            source_format="openclaw"
        )

    def translate_tool(self, source: Dict[str, Any]) -> TranslationResult:
        """Translate OpenClaw tool to NEXUS format."""
        tool_spec = {
            "name": source.get("name", "unknown"),
            "description": source.get("description", ""),
            "parameters": source.get("input_schema", {}),
            "permission": "read"
        }
        return TranslationResult(
            success=True,
            data=tool_spec,
            source_format="openclaw"
        )

    def translate_memory(self, source: Dict[str, Any]) -> TranslationResult:
        """Translate OpenClaw memory to NEXUS format."""
        memory_entry = {
            "key": source.get("id", ""),
            "value": source.get("data"),
            "timestamp": source.get("created_at", datetime.now().isoformat()),
            "metadata": source.get("metadata", {})
        }
        return TranslationResult(
            success=True,
            data=memory_entry,
            source_format="openclaw"
        )


# ============================================================================
# OpenFang ACL
# ============================================================================

class OpenFangACL(AntiCorruptionLayer):
    """Anti-corruption layer for OpenFang security framework."""

    def __init__(self):
        super().__init__("openfang")

    def translate_skill(self, source: Dict[str, Any]) -> TranslationResult:
        """OpenFang focuses on security skills."""
        skill_spec = {
            "name": source.get("name", "unnamed"),
            "description": source.get("description", ""),
            "parameters": source.get("parameters", {"type": "object", "properties": {}}),
            "content": source.get("instructions", ""),
            "tools": source.get("tools", []),
            "tags": ["openfang", "security", "imported"]
        }
        return TranslationResult(
            success=True,
            data=skill_spec,
            source_format="openfang"
        )

    def translate_tool(self, source: Dict[str, Any]) -> TranslationResult:
        """Translate OpenFang security tool."""
        tool_spec = {
            "name": source.get("name", "unknown"),
            "description": source.get("description", ""),
            "parameters": source.get("parameters", {}),
            "permission": "admin"
        }
        return TranslationResult(
            success=True,
            data=tool_spec,
            source_format="openfang"
        )

    def translate_memory(self, source: Dict[str, Any]) -> TranslationResult:
        """Translate OpenFang memory to NEXUS format."""
        memory_entry = {
            "key": source.get("key", ""),
            "value": source.get("value"),
            "timestamp": source.get("timestamp", datetime.now().isoformat()),
            "metadata": {
                "source": "openfang",
                "security_level": source.get("security_level", "standard")
            }
        }
        return TranslationResult(
            success=True,
            data=memory_entry,
            source_format="openfang"
        )


# ============================================================================
# ACL Registry
# ============================================================================

class ACLRegistry:
    """Registry for anti-corruption layer translators."""

    def __init__(self):
        self._layers: Dict[str, AntiCorruptionLayer] = {
            "hermes": HermesACL(),
            "agent_zero": AgentZeroACL(),
            "openclaw": OpenClawACL(),
            "openfang": OpenFangACL()
        }

    def get_layer(self, source_format: str) -> Optional[AntiCorruptionLayer]:
        """Get ACL for a specific source format."""
        return self._layers.get(source_format.lower())

    def translate_skill(self, source_format: str, source: Dict[str, Any]) -> TranslationResult:
        """Translate a skill from any supported format."""
        layer = self.get_layer(source_format)
        if not layer:
            return TranslationResult(
                success=False,
                errors=[f"Unknown source format: {source_format}"],
                source_format=source_format
            )
        return layer.translate_skill(source)

    def translate_tool(self, source_format: str, source: Dict[str, Any]) -> TranslationResult:
        """Translate a tool from any supported format."""
        layer = self.get_layer(source_format)
        if not layer:
            return TranslationResult(
                success=False,
                errors=[f"Unknown source format: {source_format}"],
                source_format=source_format
            )
        return layer.translate_tool(source)

    def translate_memory(self, source_format: str, source: Dict[str, Any]) -> TranslationResult:
        """Translate a memory entry from any supported format."""
        layer = self.get_layer(source_format)
        if not layer:
            return TranslationResult(
                success=False,
                errors=[f"Unknown source format: {source_format}"],
                source_format=source_format
            )
        return layer.translate_memory(source)

    def list_supported_formats(self) -> List[str]:
        """List all supported source formats."""
        return list(self._layers.keys())


__all__ = [
    "TranslationResult",
    "AntiCorruptionLayer",
    "HermesACL",
    "AgentZeroACL",
    "OpenClawACL",
    "OpenFangACL",
    "ACLRegistry"
]