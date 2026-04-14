# NEXUS Framework - End-to-End Tests

import pytest
import sys
import os
sys.path.insert(0, "/a0/usr/projects/meta_agentic_framework")

# E2E test for complete framework flow


class TestNexusE2E:
    def test_import_framework():
        """Test that framework can be imported."""
        import nexus
        assert nexus is not None

    def test_efficiency_layer():
        """Test efficiency layer components."""
        from nexus.efficiency.tokenizer import Tokenizer
        from nexus.efficiency.rate_limiter import RateLimiter
        from nexus.efficiency.budget_enforcer import BudgetEnforcer, BudgetConfig
        from nexus.efficiency.prompt_cache import PromptCache

        # Test tokenizer
        t = Tokenizer()
        assert t.count_tokens("Hello world") > 0

        # Test rate limiter
        limiter = RateLimiter(max_rpm=60)
        assert limiter.acquire() == True

        # Test budget enforcer
        config = BudgetConfig(max_tokens=1000)
        enforcer = BudgetEnforcer(config)
        status = enforcer.track(100)
        assert status.tokens_used == 100

        # Test prompt cache
        cache = PromptCache(max_size=100)
        cache.put("key1", "value1")
        assert cache.get_cached("key1") == "value1"

    def test_security_layer():
        """Test security layer components."""
        from nexus.security.sanitizer import Sanitizer

        s = Sanitizer()
        result = s.sanitize_input("<script>alert(1)</script>Hello")
        assert "<script>" not in result

    def test_memory_modules():
        """Test memory modules."""
        from nexus.memory.stack import MemoryStack
        from nexus.memory.palace import Palace

        stack = MemoryStack()
        assert stack is not None

        palace = Palace()
        assert palace is not None

    def test_orchestration():
        """Test orchestration modules."""
        from nexus.orchestration.templates import AgentTemplates
        from nexus.orchestration.heartbeat import HeartbeatMonitor

        templates = AgentTemplates()
        assert templates is not None

    def test_utils_lazy_loader():
        """Test lazy loader utility."""
        from nexus.utils.lazy_loader import LazyLoader, get_lazy_module

        loader = LazyLoader()
        assert loader is not None
        assert loader.is_loaded("nonexistent") == False