# NEXUS Framework - Unit Tests for Efficiency Layer

import pytest
import time
import sys
sys.path.insert(0, "/a0/usr/projects/meta_agentic_framework")

from nexus.efficiency.tokenizer import Tokenizer
from nexus.efficiency.rate_limiter import RateLimiter
from nexus.efficiency.budget_enforcer import BudgetEnforcer, BudgetConfig
from nexus.efficiency.prompt_cache import PromptCache


class TestTokenizer:
    def test_count_tokens_basic():
        t = Tokenizer()
        count = t.count_tokens("Hello world")
        assert count > 0
        assert isinstance(count, int)

    def test_count_tokens_empty():
        t = Tokenizer()
        assert t.count_tokens("") == 0

    def test_estimate_fallback():
        t = Tokenizer()
        count = t.estimate("Hello world")
        assert count > 0


class TestRateLimiter:
    def test_acquire_immediate():
        limiter = RateLimiter(max_rpm=60)
        assert limiter.acquire() == True

    def test_get_status():
        limiter = RateLimiter(max_rpm=60)
        status = limiter.get_status()
        assert "remaining" in status
        assert "max_rpm" in status


class TestBudgetEnforcer:
    def test_track_tokens():
        config = BudgetConfig(max_tokens=1000)
        enforcer = BudgetEnforcer(config)
        status = enforcer.track(100)
        assert status.tokens_used == 100

    def test_can_proceed():
        config = BudgetConfig(max_tokens=100)
        enforcer = BudgetEnforcer(config)
        assert enforcer.can_proceed() == True
        enforcer.track(100)
        assert enforcer.can_proceed() == False

    def test_budget_reset():
        config = BudgetConfig(max_tokens=100)
        enforcer = BudgetEnforcer(config)
        enforcer.track(50)
        enforcer.reset()
        status = enforcer.get_status()
        assert status.tokens_used == 0


class TestPromptCache:
    def test_put_and_get():
        cache = PromptCache(max_size=100)
        cache.put("key1", "value1")
        result = cache.get_cached("key1")
        assert result == "value1"

    def test_cache_miss():
        cache = PromptCache(max_size=100)
        result = cache.get_cached("nonexistent")
        assert result is None

    def test_cache_stats():
        cache = PromptCache(max_size=100)
        cache.put("key1", "value1")
        cache.get_cached("key1")
        stats = cache.get_stats()
        assert stats["hits"] >= 1