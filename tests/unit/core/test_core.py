# NEXUS Framework - Unit Tests for Core Modules

import pytest
import sys
sys.path.insert(0, "/a0/usr/projects/meta_agentic_framework")

from nexus.core.messages import Message, MessageRole


class TestMessage:
    def test_create_user_message(self):
        msg = Message(role=MessageRole.USER, content="Hello")
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello"

    def test_create_assistant_message(self):
        msg = Message(role=MessageRole.ASSISTANT, content="Hi there")
        assert msg.role == MessageRole.ASSISTANT
        assert msg.content == "Hi there"

    def test_message_to_api_format(self):
        msg = Message(role=MessageRole.USER, content="Test")
        d = msg.to_api_format()
        assert "role" in d
        assert "content" in d