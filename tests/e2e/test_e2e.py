# NEXUS Framework - End-to-End Tests

import pytest
import sys
import os
sys.path.insert(0, "/a0/usr/projects/meta_agentic_framework")


class TestNexusE2E:
    def test_import_framework(self):
        import nexus
        assert nexus is not None

    def test_efficiency_layer(self):
        from nexus.efficiency.tokenizer import Tokenizer
        from nexus.efficiency.rate_limiter import RateLimiter
        from nexus.efficiency.budget_enforcer import BudgetEnforcer, BudgetConfig
        from nexus.efficiency.prompt_cache import PromptCache

        t = Tokenizer()
        assert t.count_tokens("Hello world") > 0

        limiter = RateLimiter(max_rpm=60)
        assert limiter.acquire() == True

        config = BudgetConfig(max_tokens=1000)
        enforcer = BudgetEnforcer(config)
        status = enforcer.track(100)
        assert status.tokens_used == 100

        cache = PromptCache(max_size=100)
        cache.put("key1", "value1")
        assert cache.get_cached("key1") == "value1"

    def test_security_layer(self):
        from nexus.security.sanitizer import Sanitizer

        s = Sanitizer()
        result = s.sanitize_input("<script>alert(1)</script>Hello")
        assert "<script>" not in result