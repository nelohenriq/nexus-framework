#!/usr/bin/env python3
"""
NEXUS Framework - Docker Sandbox

Secure execution environment for tool execution.
Provides containerized isolation with resource limits.
"""

from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class SandboxConfig:
    """Configuration for Docker sandbox."""
    image: str = "python:3.11-slim"
    memory_limit: str = "512m"
    cpu_limit: float = 1.0
    timeout_seconds: float = 60.0
    network_enabled: bool = False
    read_only_fs: bool = True
    allowed_paths: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)


@dataclass
class SandboxResult:
    """Result of sandbox execution."""
    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    execution_time: float = 0.0
    container_id: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "execution_time": self.execution_time
        }


class DockerSandbox:
    """Docker-based sandbox for secure code execution."""

    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()
        self._docker_available: Optional[bool] = None

    async def is_available(self) -> bool:
        """Check if Docker is available."""
        if self._docker_available is not None:
            return self._docker_available
        try:
            proc = await asyncio.create_subprocess_exec(
                "docker", "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            self._docker_available = proc.returncode == 0
        except Exception:
            self._docker_available = False
        return self._docker_available

    async def execute(
        self,
        code: str,
        language: str = "python",
        files: Optional[Dict[str, str]] = None
    ) -> SandboxResult:
        """Execute code in sandbox."""
        if not await self.is_available():
            return SandboxResult(success=False, error="Docker not available")
        with tempfile.TemporaryDirectory() as tmpdir:
            if language == "python":
                code_file = Path(tmpdir) / "main.py"
                code_file.write_text(code)
            elif language == "javascript":
                code_file = Path(tmpdir) / "main.js"
                code_file.write_text(code)
            else:
                return SandboxResult(success=False, error=f"Unsupported language: {language}")
            if files:
                for name, content in files.items():
                    (Path(tmpdir) / name).write_text(content)
            cmd = ["docker", "run", "--rm"]
            cmd.extend(["--memory", self.config.memory_limit])
            cmd.extend(["--cpus", str(self.config.cpu_limit)])
            if not self.config.network_enabled:
                cmd.append("--network=none")
            if self.config.read_only_fs:
                cmd.append("--read-only")
            cmd.extend(["-v", f"{tmpdir}:/workspace:ro"])
            cmd.extend(["-w", "/workspace"])
            for key, value in self.config.environment.items():
                cmd.extend(["-e", f"{key}={value}"])
            cmd.append(self.config.image)
            if language == "python":
                cmd.extend(["python", "main.py"])
            elif language == "javascript":
                cmd.extend(["node", "main.js"])
            start_time = datetime.now()
            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                try:
                    stdout, stderr = await asyncio.wait_for(
                        proc.communicate(),
                        timeout=self.config.timeout_seconds
                    )
                except asyncio.TimeoutError:
                    proc.kill()
                    return SandboxResult(success=False, error="Execution timed out")
                execution_time = (datetime.now() - start_time).total_seconds()
                return SandboxResult(
                    success=proc.returncode == 0,
                    stdout=stdout.decode("utf-8", errors="replace"),
                    stderr=stderr.decode("utf-8", errors="replace"),
                    exit_code=proc.returncode or 0,
                    execution_time=execution_time
                )
            except Exception as e:
                return SandboxResult(success=False, error=f"Execution error: {str(e)}")

    async def execute_python(self, code: str, files: Optional[Dict[str, str]] = None) -> SandboxResult:
        return await self.execute(code, "python", files)

    async def execute_javascript(self, code: str, files: Optional[Dict[str, str]] = None) -> SandboxResult:
        return await self.execute(code, "javascript", files)


__all__ = ["DockerSandbox", "SandboxConfig", "SandboxResult"]