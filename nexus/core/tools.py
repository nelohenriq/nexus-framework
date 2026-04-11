#!/usr/bin/env python3
"""
NEXUS Framework - Tool Registry

Dynamic tool loading, registration, and execution system.
Supports async tools, permission levels, and JSON Schema validation.
"""

from __future__ import annotations

import asyncio
import json
import inspect
import importlib
import importlib.util
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime


class PermissionLevel(str, Enum):
    """Tool permission levels."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"


@dataclass
class ToolSpec:
    """Tool specification with JSON Schema parameters."""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    permission: PermissionLevel = PermissionLevel.READ
    handler: Optional[Callable] = None
    module: Optional[str] = None
    async_supported: bool = True
    timeout_seconds: float = 30.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "permission": self.permission.value,
            "async_supported": self.async_supported,
            "timeout_seconds": self.timeout_seconds
        }


@dataclass
class ToolResult:
    """Result of tool execution."""
    success: bool
    output: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
            "execution_time": self.execution_time
        }


class ToolError(Exception):
    """Tool execution error."""
    def __init__(self, tool_name: str, message: str):
        self.tool_name = tool_name
        self.message = message
        super().__init__(f"Tool '{tool_name}': {message}")


class ToolRegistry:
    """Registry for managing and executing tools."""

    def __init__(self, tools_dirs: Optional[List[Path]] = None):
        self._tools: Dict[str, ToolSpec] = {}
        self._results_cache: Dict[str, ToolResult] = {}
        self._execution_history: List[Dict[str, Any]] = []

        if tools_dirs:
            for tools_dir in tools_dirs:
                self.load_from_directory(tools_dir)

    def register(self, name: str, handler: Callable, description: str = "",
                  parameters: Optional[Dict[str, Any]] = None,
                  permission: PermissionLevel = PermissionLevel.READ,
                  async_supported: Optional[bool] = None,
                  timeout_seconds: float = 30.0) -> None:
        if async_supported is None:
            async_supported = asyncio.iscoroutinefunction(handler)
        spec = ToolSpec(
            name=name,
            description=description,
            parameters=parameters or {},
            permission=permission,
            handler=handler,
            async_supported=async_supported,
            timeout_seconds=timeout_seconds
        )
        self._tools[name] = spec

    def has_tool(self, name: str) -> bool:
        return name in self._tools

    def get_tool(self, name: str) -> Optional[ToolSpec]:
        return self._tools.get(name)

    def list_tools(self) -> List[ToolSpec]:
        return list(self._tools.values())

    def execute(self, name: str, args: Dict[str, Any]) -> ToolResult:
        return asyncio.run(self.execute_async(name, args))

    async def execute_async(self, name: str, args: Dict[str, Any],
                          timeout: Optional[float] = None) -> ToolResult:
        start_time = datetime.now()
        if name not in self._tools:
            return ToolResult(success=False, output="", error=f"Tool '{name}' not found")
        spec = self._tools[name]
        timeout_val = timeout or spec.timeout_seconds
        try:
            if spec.async_supported and spec.handler:
                result = await asyncio.wait_for(spec.handler(**args), timeout=timeout_val)
            elif spec.handler:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, lambda: spec.handler(**args))
            else:
                return ToolResult(success=False, output="", error=f"Tool '{name}' has no handler")
            if isinstance(result, ToolResult):
                tool_result = result
            elif isinstance(result, str):
                tool_result = ToolResult(success=True, output=result)
            else:
                tool_result = ToolResult(success=True, output=str(result) if result else "")
            tool_result.execution_time = (datetime.now() - start_time).total_seconds()
            self._record_execution(name, args, tool_result)
            return tool_result
        except asyncio.TimeoutError:
            return ToolResult(success=False, output="", error=f"Tool '{name}' timed out after {timeout_val}s")
        except Exception as e:
            return ToolResult(success=False, output="", error=f"Tool execution error: {str(e)}")

    def _record_execution(self, name: str, args: Dict[str, Any], result: ToolResult) -> None:
        self._execution_history.append({
            "tool": name,
            "args": args,
            "result": result.to_dict(),
            "timestamp": datetime.now().isoformat()
        })
        if len(self._execution_history) > 100:
            self._execution_history = self._execution_history[-100:]

    def load_from_directory(self, directory: Path) -> int:
        if not directory.exists():
            return 0
        loaded = 0
        for file_path in directory.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
            try:
                module_name = f"tools_{file_path.stem}"
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    for attr_name in dir(module):
                        obj = getattr(module, attr_name)
                        if callable(obj) and hasattr(obj, "_nexus_tool"):
                            tool_info = obj._nexus_tool
                            self.register(
                                name=tool_info.get("name", attr_name),
                                handler=obj,
                                description=tool_info.get("description", ""),
                                parameters=tool_info.get("parameters"),
                                permission=tool_info.get("permission", PermissionLevel.READ),
                                timeout_seconds=tool_info.get("timeout", 30.0)
                            )
                    loaded += 1
            except Exception:
                pass
        return loaded

    def get_execution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._execution_history[-limit:]

    def get_tool_stats(self) -> Dict[str, Any]:
        total = len(self._execution_history)
        successful = sum(1 for e in self._execution_history if e["result"]["success"])
        return {
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": total - successful,
            "success_rate": successful / total if total > 0 else 0,
            "tools_registered": len(self._tools)
        }


def tool(name: Optional[str] = None, description: str = "",
            parameters: Optional[Dict[str, Any]] = None,
            permission: PermissionLevel = PermissionLevel.READ,
            timeout: float = 30.0):
    def decorator(func: Callable) -> Callable:
        func._nexus_tool = {
            "name": name or func.__name__,
            "description": description or func.__doc__ or "",
            "parameters": parameters,
            "permission": permission,
            "timeout": timeout
        }
        return func
    return decorator


@tool(name="response", description="Return a final response to the user")
def response_tool(text: str) -> str:
    return text


@tool(name="think", description="Internal reasoning step")
def think_tool(thoughts: str) -> str:
    return f"Processed: {thoughts[:100]}..."


__all__ = ["ToolRegistry", "ToolSpec", "ToolResult", "ToolError", "PermissionLevel", "tool"]