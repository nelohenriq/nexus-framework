#!/usr/bin/env python3
"""
NEXUS Framework - Agent Loop Implementation

Monologue cycle agent execution engine inspired by Agent Zero.
Handles context management, tool execution, error recovery, and memory injection.
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional, Union

from nexus.core.messages import Message, MessageRole
from nexus.core.memory import MemoryManager
from nexus.core.context import AgentContext
from nexus.core.tools import ToolRegistry, ToolResult, ToolError
from nexus.efficiency.rate_limiter import RateLimiter
from nexus.efficiency.budget_enforcer import BudgetEnforcer, BudgetConfig
from nexus.efficiency.tokenizer import Tokenizer


class AgentState(str, Enum):
    """Agent execution state."""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING_TOOL = "executing_tool"
    WAITING_INPUT = "waiting_input"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentResponse:
    """Final response from agent."""
    agent_id: str
    content: str
    success: bool
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    tokens_used: int = 0
    execution_time: float = 0.0


@dataclass
class ToolCallRequest:
    """Request to execute a tool."""
    tool_name: str
    tool_args: dict
    call_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


@dataclass
class AgentConfig:
    """Configuration for an agent instance."""
    agent_id: str = "default_agent"
    max_iterations: int = 100
    context_window_limit: int = 128000
    summarization_threshold: float = 0.8
    enable_memory: bool = True
    enable_checkpoints: bool = True
    checkpoint_interval: int = 10
    temperature: float = 0.7
    max_tokens: int = 4096


class AgentLoop:
    """
    Monologue cycle agent execution engine.
    """

    def __init__(
        self,
        config: AgentConfig,
        llm_adapter: Any,
        tool_registry: ToolRegistry,
        memory_manager: Optional[MemoryManager] = None,
        rate_limiter: Optional[RateLimiter] = None,
        budget_enforcer: Optional[BudgetEnforcer] = None
    ):
        self.config = config
        self.llm = llm_adapter
        self.tools = tool_registry
        self.memory = memory_manager
        self.rate_limiter = rate_limiter
        self.budget = budget_enforcer
        self.state = AgentState.IDLE
        self.iteration = 0
        self._start_time = 0.0
        self._total_tokens = 0
        self._tokenizer = Tokenizer()

    def run(self, context: AgentContext, task: str, system_prompt: Optional[str] = None) -> AgentResponse:
        """Run the agent loop synchronously."""
        return asyncio.run(self.run_async(context, task, system_prompt))

    async def run_async(self, context: AgentContext, task: str, system_prompt: Optional[str] = None) -> AgentResponse:
        self._start_time = time.time()
        self.state = AgentState.THINKING
        self.iteration = 0
        context.add_message(Message(role=MessageRole.USER, content=task))
        try:
            while self.iteration < self.config.max_iterations:
                self.iteration += 1
                if self._needs_summarization(context):
                    await self._summarize_context(context)
                prompt = self._assemble_prompt(context, system_prompt)
                if self.rate_limiter:
                    await self.rate_limiter.acquire_async()
                self.state = AgentState.THINKING
                response = await self._call_llm(prompt)
                self._total_tokens += response.get("tokens", 0)
                parsed = self._parse_response(response)
                if parsed.get("type") == "response":
                    self.state = AgentState.COMPLETED
                    return AgentResponse(
                        agent_id=self.config.agent_id,
                        content=parsed.get("content", ""),
                        success=True,
                        tokens_used=self._total_tokens,
                        execution_time=time.time() - self._start_time
                    )
                if parsed.get("type") == "tool_call":
                    self.state = AgentState.EXECUTING_TOOL
                    tool_result = await self._execute_tool(parsed)
                    context.add_message(Message(
                        role=MessageRole.TOOL,
                        content=json.dumps(tool_result.to_dict()),
                        metadata={"tool_name": parsed.get("tool_name")}
                    ))
            return AgentResponse(
                agent_id=self.config.agent_id,
                content="Max iterations reached",
                success=False,
                error="max_iterations_exceeded",
                tokens_used=self._total_tokens
            )
        except Exception as e:
            self.state = AgentState.ERROR
            return AgentResponse(
                agent_id=self.config.agent_id,
                content="",
                success=False,
                error=str(e),
                tokens_used=self._total_tokens
            )

    def _assemble_prompt(self, context: AgentContext, system_prompt: Optional[str] = None) -> list:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        for msg in context.messages:
            messages.append({"role": msg.role.value, "content": msg.content})
        return messages

    async def _call_llm(self, messages: list) -> dict:
        try:
            response = await self.llm.chat(messages=messages, temperature=self.config.temperature, max_tokens=self.config.max_tokens)
            return response
        except Exception as e:
            return {"error": str(e), "content": ""}

    def _parse_response(self, response: dict) -> dict:
        content = response.get("content", "")
        try:
            if content.strip().startswith("{"):
                parsed = json.loads(content)
                if "tool_name" in parsed:
                    return {"type": "tool_call", "tool_name": parsed.get("tool_name"), "tool_args": parsed.get("tool_args", {})}
                elif parsed.get("type") == "response":
                    return {"type": "response", "content": parsed.get("text", content)}
        except json.JSONDecodeError:
            pass
        return {"type": "response", "content": content}

    async def _execute_tool(self, parsed: dict) -> ToolResult:
        tool_name = parsed.get("tool_name")
        tool_args = parsed.get("tool_args", {})
        if not self.tools.has_tool(tool_name):
            return ToolResult(success=False, output="", error=f"Tool not found: {tool_name}")
        try:
            result = await self.tools.execute_async(tool_name, tool_args)
            return result
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

    def _needs_summarization(self, context: AgentContext) -> bool:
        """Check if context needs summarization using precise token counting."""
        messages = [{"role": m.role.value, "content": m.content} for m in context.messages]
        estimated_tokens = self._tokenizer.count_messages(messages).tokens
        threshold = self.config.context_window_limit * self.config.summarization_threshold
        return estimated_tokens > threshold

    async def _summarize_context(self, context: AgentContext) -> None:
        if len(context.messages) < 10:
            return
        older_messages = context.messages[:-10]
        summary_text = "\n".join([f"{m.role.value}: {m.content[:200]}" for m in older_messages[:5]])
        summary = Message(role=MessageRole.SYSTEM, content=f"[CONTEXT SUMMARY]\n{summary_text}")
        context.messages = [summary] + context.messages[-10:]


__all__ = ["AgentLoop", "AgentConfig", "AgentResponse", "AgentState", "ToolCallRequest"]