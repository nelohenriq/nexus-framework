#!/usr/bin/env python3
"""
NEXUS Framework - Dispatcher Module

Message routing, session management, and context building for multi-channel support.
"""

from __future__ import annotations

import time
import asyncio
import hashlib
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
from collections import OrderedDict
import logging


@dataclass
class AgentSession:
    """Session state for a user conversation."""
    session_id: str
    user_id: str
    channel: str
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    context_data: Dict[str, Any] = field(default_factory=dict)
    message_history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def touch(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now()

    def add_message(self, role: str, content: str) -> None:
        """Add message to history."""
        self.message_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_context_hash(self) -> str:
        """Get hash of current context for caching."""
        data = str(self.context_data) + str(self.message_history[-5:] if len(self.message_history) > 5 else self.message_history)
        return hashlib.md5(data.encode()).hexdigest()[:12]


class LRUCache(OrderedDict):
    """LRU cache with max size limit."""

    def __init__(self, max_size: int = 1000):
        super().__init__()
        self._max_size = max_size

    def __setitem__(self, key, value):
        if key in self:
            self.move_to_end(key)
        super().__setitem__(key, value)
        if len(self) > self._max_size:
            self.popitem(last=False)


class SessionManager:
    """Manages user sessions across channels."""

    def __init__(self, max_sessions: int = 1000, session_ttl: int = 3600):
        self._sessions: LRUCache = LRUCache(max_sessions)
        self._session_ttl = session_ttl
        self._lock = asyncio.Lock()
        self._logger = logging.getLogger("nexus.session")

    def _make_session_id(self, channel: str, user_id: str) -> str:
        """Create unique session ID."""
        return f"{channel}:{user_id}"

    async def get_or_create(self, channel: str, user_id: str) -> AgentSession:
        """Get existing session or create new one."""
        session_id = self._make_session_id(channel, user_id)
        async with self._lock:
            if session_id in self._sessions:
                session = self._sessions[session_id]
                session.touch()
                return session
            session = AgentSession(
                session_id=session_id,
                user_id=user_id,
                channel=channel
            )
            self._sessions[session_id] = session
            self._logger.info(f"Created session: {session_id}")
            return session

    async def get(self, session_id: str) -> Optional[AgentSession]:
        """Get session by ID."""
        return self._sessions.get(session_id)

    async def delete(self, session_id: str) -> bool:
        """Delete a session."""
        async with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    async def cleanup_expired(self) -> int:
        """Remove expired sessions."""
        now = datetime.now()
        expired = []
        for session_id, session in self._sessions.items():
            age = (now - session.last_activity).total_seconds()
            if age > self._session_ttl:
                expired.append(session_id)
        for session_id in expired:
            del self._sessions[session_id]
        if expired:
            self._logger.info(f"Cleaned up {len(expired)} expired sessions")
        return len(expired)


@dataclass
class RouteConfig:
    """Configuration for message routing."""
    handler: Callable
    channel_filter: Optional[List[str]] = None
    priority: int = 0


class MessageRouter:
    """Routes messages to appropriate handlers."""

    def __init__(self, session_manager: Optional[SessionManager] = None):
        self._routes: Dict[str, RouteConfig] = {}
        self._default_handler: Optional[Callable] = None
        self._session_manager = session_manager or SessionManager()
        self._logger = logging.getLogger("nexus.router")

    def register(self, channel: str, handler: Callable, priority: int = 0) -> None:
        """Register a handler for a channel."""
        self._routes[channel] = RouteConfig(handler=handler, priority=priority)

    def set_default(self, handler: Callable) -> None:
        """Set default handler for unregistered channels."""
        self._default_handler = handler

    async def route(self, message: Any) -> Any:
        """Route a message to the appropriate handler."""
        # Get or create session
        session = await self._session_manager.get_or_create(
            getattr(message, "channel", "unknown"),
            getattr(message, "sender", "unknown")
        )

        # Find handler
        channel_value = getattr(message, "channel", "unknown")
        channel_name = channel_value.value if hasattr(channel_value, "value") else str(channel_value)
        handler_config = self._routes.get(channel_name)

        if handler_config:
            handler = handler_config.handler
            try:
                if asyncio.iscoroutinefunction(handler):
                    return await handler(message, session)
                else:
                    return handler(message, session)
            except Exception as e:
                self._logger.error(f"Handler error: {e}")
                raise

        if self._default_handler:
            try:
                if asyncio.iscoroutinefunction(self._default_handler):
                    return await self._default_handler(message, session)
                else:
                    return self._default_handler(message, session)
            except Exception as e:
                self._logger.error(f"Default handler error: {e}")
                raise

        self._logger.warning(f"No handler for channel: {channel_name}")
        return None


class ContextBuilder:
    """Builds agent context from session and message."""

    def __init__(
        self,
        max_history: int = 10,
        system_prompt: str = ""
    ):
        self._max_history = max_history
        self._system_prompt = system_prompt

    def build(self, session: AgentSession, message: Any) -> Dict[str, Any]:
        """Build context for agent execution."""
        # Get recent message history
        history = session.message_history[-self._max_history:] if session.message_history else []

        # Build context
        context = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "channel": session.channel,
            "system_prompt": self._system_prompt,
            "message_history": history,
            "current_message": {
                "role": "user",
                "content": getattr(message, "content", "")
            },
            "metadata": session.metadata
        }

        return context

    def set_system_prompt(self, prompt: str) -> None:
        """Set system prompt."""
        self._system_prompt = prompt


class Dispatcher:
    """Main dispatcher coordinating channels, routing, and context."""

    def __init__(self, session_manager: Optional[SessionManager] = None):
        self._session_manager = session_manager or SessionManager()
        self._router = MessageRouter(self._session_manager)
        self._context_builder = ContextBuilder()
        self._channels: Dict[str, Any] = {}
        self._running = False
        self._logger = logging.getLogger("nexus.dispatcher")

    def register_channel(self, channel: Any) -> None:
        """Register a channel."""
        channel_type = getattr(channel, "_channel_type", "unknown")
        self._channels[channel_type] = channel

    def register_handler(self, channel_type: str, handler: Callable) -> None:
        """Register a handler for a channel type."""
        self._router.register(channel_type, handler)

    async def start(self) -> None:
        """Start the dispatcher."""
        self._running = True
        self._logger.info("Dispatcher started")

    async def stop(self) -> None:
        """Stop the dispatcher."""
        self._running = False
        self._logger.info("Dispatcher stopped")

    async def process(self, message: Any) -> Any:
        """Process a message through the dispatcher."""
        return await self._router.route(message)


__all__ = [
    "AgentSession", "SessionManager", "LRUCache",
    "RouteConfig", "MessageRouter", "ContextBuilder", "Dispatcher"
]