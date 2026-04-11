#!/usr/bin/env python3
"""NEXUS Framework - Plugin System

Dynamic skill loading and plugin management.
"""

from __future__ import annotations

import json
import importlib
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PluginMetadata:
    name: str
    version: str
    description: str
    author: str = "unknown"
    dependencies: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    path: Path = field(default_factory=lambda: Path("."))
    enabled: bool = True


@dataclass
class PluginConfig:
    plugin_dir: str = "plugins"
    auto_enable: bool = True
    check_dependencies: bool = True


class PluginManager:
    """Dynamic plugin and skill manager."""

    def __init__(self, config: Optional[PluginConfig] = None):
        self._config = config or PluginConfig()
        self._plugins: Dict[str, PluginMetadata] = {}
        self._loaded: Dict[str, Any] = {}
        self._skills: Dict[str, Callable] = {}

    def discover(self) -> List[PluginMetadata]:
        """Discover all plugins in the plugin directory."""
        plugin_dir = Path(self._config.plugin_dir)
        if not plugin_dir.exists():
            return []
        plugins = []
        for path in plugin_dir.iterdir():
            if path.is_dir():
                skill_file = path / "SKILL.md"
                if skill_file.exists():
                    meta = self._parse_skill_md(skill_file)
                    if meta:
                        meta.path = path
                        plugins.append(meta)
            elif path.suffix == ".py":
                meta = self._parse_python_plugin(path)
                if meta:
                    plugins.append(meta)
        return plugins

    def _parse_skill_md(self, path: Path) -> Optional[PluginMetadata]:
        try:
            content = path.read_text()
            lines_list = content.split(chr(10))
            if lines_list and lines_list[0].strip() == "---":
                yaml_end = 1
                for i, line in enumerate(lines_list[1:], 1):
                    if line.strip() == "---":
                        yaml_end = i
                        break
                yaml_content = chr(10).join(lines_list[1:yaml_end])
                import yaml
                meta_dict = yaml.safe_load(yaml_content) or {}
                return PluginMetadata(
                    name=meta_dict.get("name", path.parent.name),
                    version=meta_dict.get("version", "0.0.1"),
                    description=meta_dict.get("description", ""),
                    author=meta_dict.get("author", "unknown")
                )
        except Exception:
            pass
        return None

    def _parse_python_plugin(self, path: Path) -> Optional[PluginMetadata]:
        try:
            content = path.read_text()
            name = path.stem
            version = "0.0.1"
            description = ""
            for line in content.split(chr(10)):
                if line.startswith("__version__"):
                    version = line.split("=")[1].strip().strip(chr(34))
                elif line.startswith(chr(34)) and not description:
                    description = line.strip(chr(34))
            return PluginMetadata(name=name, version=version, description=description, path=path.parent)
        except Exception:
            return None

    def load(self, name: str) -> Optional[Any]:
        """Load a plugin by name."""
        if name in self._loaded:
            return self._loaded[name]
        if name not in self._plugins:
            plugins = self.discover()
            for p in plugins:
                self._plugins[p.name] = p
        if name not in self._plugins:
            return None
        plugin = self._plugins[name]
        try:
            module_path = plugin.path / "__init__.py"
            if module_path.exists():
                spec = importlib.util.spec_from_file_location(name, module_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self._loaded[name] = module
                    return module
        except Exception:
            pass
        return None

    def unload(self, name: str) -> bool:
        """Unload a plugin."""
        if name in self._loaded:
            del self._loaded[name]
            return True
        return False

    def reload(self, name: str) -> Optional[Any]:
        """Reload a plugin."""
        self.unload(name)
        return self.load(name)

    def load_from_github(self, repo: str) -> Optional[PluginMetadata]:
        """Install a plugin from GitHub."""
        try:
            plugin_dir = Path(self._config.plugin_dir)
            plugin_dir.mkdir(parents=True, exist_ok=True)
            parts = repo.split("/")
            plugin_name = parts[-1].replace(".git", "")
            target = plugin_dir / plugin_name
            if target.exists():
                subprocess.run(["git", "-C", str(target), "pull"], check=True)
            else:
                subprocess.run(["git", "clone", repo, str(target)], check=True)
            skill_file = target / "SKILL.md"
            if skill_file.exists():
                meta = self._parse_skill_md(skill_file)
                if meta:
                    meta.path = target
                    self._plugins[meta.name] = meta
                    return meta
        except Exception:
            return None

    def register_skill(self, name: str, handler: Callable) -> None:
        """Register a skill handler."""
        self._skills[name] = handler

    def get_skill(self, name: str) -> Optional[Callable]:
        """Get a skill handler."""
        return self._skills.get(name)

    def list_skills(self) -> List[str]:
        """List all registered skills."""
        return list(self._skills.keys())


# Default instance
plugin_manager = PluginManager()


__all__ = ["PluginMetadata", "PluginConfig", "PluginManager", "plugin_manager"]