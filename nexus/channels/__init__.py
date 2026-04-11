#!/usr/bin/env python3
"""
NEXUS Framework - Channels Module

Multi-platform channel gateway supporting Telegram, Discord, CLI, and Web UI.
"""

from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ChannelType(str, Enum):
    CLI = "cli"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    WEB = "web"
    MQTT = "mqtt"
    REST = "rest"


@dataclass
class ChannelMessage:
    """Message from a channel."""
    channel: ChannelType
    sender: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    reply_to: Optional[str] = None
    attachments: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "channel": self.channel.value,
            "sender": self.sender,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "reply_to": self.reply_to,
            "attachments": self.attachments
        }


@dataclass
class ChannelResponse:
    """Response to send to a channel."""
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    reply_to: Optional[str] = None
    attachments: List[str] = field(default_factory=list)


class ChannelPort(ABC):
    """Abstract base class for channel implementations."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the channel."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the channel."""
        pass

    @abstractmethod
    async def listen(self) -> AsyncIterator[ChannelMessage]:
        """Listen for incoming messages."""
        pass

    @abstractmethod
    async def send(self, response: ChannelResponse) -> None:
        """Send a response to the channel."""
        pass

    @abstractmethod
    async def is_connected(self) -> bool:
        """Check if channel is connected."""
        pass


class CLIChannel(ChannelPort):
    """Command-line interface channel."""

    def __init__(self):
        self._connected = False
        self._message_queue: asyncio.Queue = asyncio.Queue()

    async def connect(self) -> None:
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False

    async def listen(self) -> AsyncIterator[ChannelMessage]:
        while self._connected:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
                if line.strip():
                    yield ChannelMessage(
                        channel=ChannelType.CLI,
                        sender="user",
                        content=line.strip()
                    )
            except (EOFError, KeyboardInterrupt):
                break

    async def send(self, response: ChannelResponse) -> None:
        print(response.content)

    async def is_connected(self) -> bool:
        return self._connected

    async def send_message(self, content: str) -> None:
        """Convenience method to send a message."""
        await self.send(ChannelResponse(content=content))


class TelegramChannel(ChannelPort):
    """Telegram bot channel."""

    def __init__(self, token: str, allowed_chat_ids: Optional[List[int]] = None):
        self._token = token
        self._allowed_chat_ids = allowed_chat_ids or []
        self._connected = False
        self._bot = None

    async def connect(self) -> None:
        try:
            from telegram import Bot
            from telegram.ext import Application
            self._bot = Bot(self._token)
            self._connected = True
        except ImportError:
            raise ImportError("python-telegram-bot not installed. Run: pip install python-telegram-bot")

    async def disconnect(self) -> None:
        self._connected = False

    async def listen(self) -> AsyncIterator[ChannelMessage]:
        if not self._connected:
            return
        # Placeholder - actual implementation would use telegram.ext Application
        while self._connected:
            await asyncio.sleep(1)
            pass

    async def send(self, response: ChannelResponse) -> None:
        if not self._connected or not self._bot:
            return
        if response.reply_to:
            chat_id = int(response.reply_to)
            await self._bot.send_message(chat_id=chat_id, text=response.content)

    async def is_connected(self) -> bool:
        return self._connected

    async def send_to_chat(self, chat_id: int, content: str) -> None:
        """Send message to specific chat."""
        await self.send(ChannelResponse(content=content, reply_to=str(chat_id)))


class DiscordChannel(ChannelPort):
    """Discord bot channel."""

    def __init__(self, token: str, allowed_guild_ids: Optional[List[int]] = None):
        self._token = token
        self._allowed_guild_ids = allowed_guild_ids or []
        self._connected = False
        self._client = None

    async def connect(self) -> None:
        try:
            import discord
            intents = discord.Intents.default()
            intents.message_content = True
            self._client = discord.Client(intents=intents)
            self._connected = True
        except ImportError:
            raise ImportError("discord.py not installed. Run: pip install discord.py")

    async def disconnect(self) -> None:
        self._connected = False
        if self._client:
            await self._client.close()

    async def listen(self) -> AsyncIterator[ChannelMessage]:
        if not self._connected:
            return
        # Placeholder - actual implementation would use discord.py event loop
        while self._connected:
            await asyncio.sleep(1)
            pass

    async def send(self, response: ChannelResponse) -> None:
        # Implementation would send via discord.py
        pass

    async def is_connected(self) -> bool:
        return self._connected


class ChannelRegistry:
    """Registry for managing multiple channels."""

    def __init__(self):
        self._channels: Dict[ChannelType, ChannelPort] = {}

    def register(self, channel_type: ChannelType, channel: ChannelPort) -> None:
        self._channels[channel_type] = channel

    def get(self, channel_type: ChannelType) -> Optional[ChannelPort]:
        return self._channels.get(channel_type)

    async def connect_all(self) -> None:
        for channel in self._channels.values():
            await channel.connect()

    async def disconnect_all(self) -> None:
        for channel in self._channels.values():
            await channel.disconnect()


__all__ = [
    "ChannelType", "ChannelMessage", "ChannelResponse", "ChannelPort",
    "CLIChannel", "TelegramChannel", "DiscordChannel", "ChannelRegistry"
]