# NEXUS Framework - Unit Tests for Core Modules

import pytest
import sys
sys.path.insert(0, "/a0/usr/projects/meta_agentic_framework")

from nexus.core.messages import Message, MessageRole
from nexus.core.memory import Memory
from nexus.core.context import Context


class TestMessage:
    def test_create_user_message():
 msg = Message(role=MessageRole.USER, content="Hello")
 assert msg.role == MessageRole.USER
 assert msg.content == "Hello"

    def test_create_assistant_message():
 msg = Message(role=MessageRole.ASSISTANT, content="Hi there")
 assert msg.role == MessageRole.ASSISTANT
 assert msg.content == "Hi there"

    def test_message_to_dict():
 msg = Message(role=MessageRole.USER, content="Test")
        d = msg.to_dict()
        assert "role" in d
        assert "content" in d


class TestMemory:
    def test_memory_store():
        mem = Memory()
        mem.store("key1", "value1")
        result = mem.retrieve("key1")
        assert result == "value1"

    def test_memory_missing_key():
        mem = Memory()
        result = mem.retrieve("nonexistent")
        assert result is None

    def test_memory_clear():
        mem = Memory()
        mem.store("key1", "value1")
        mem.clear()
        assert mem.retrieve("key1") is None


class TestContext:
    def test_context_create():
        ctx = Context()
        assert ctx is not None

    def test_context_set_get():
        ctx = Context()
        ctx.set("test_key", "test_value")
        assert ctx.get("test_key") == "test_value"