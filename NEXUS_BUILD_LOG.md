# NEXUS Framework - Development Frontier Build Log

**Version:** 2.0.0
**Created:** 2026-04-09
**Status:** Development Blueprint
**Timeline:** 12 Weeks (6 Phases)

---

## Executive Summary

This Development Frontier Build Log provides a comprehensive blueprint for implementing the NEXUS Framework v2.0.0. NEXUS is a unified, standalone agentic framework integrating best practices from Hermes, OpenClaw, Agent Zero, and OpenFang while eliminating their identified weaknesses.

### Development Approach

**Architecture Philosophy:** Hexagonal architecture with dependency injection enables loose coupling, testability, and configuration-driven adapter selection. All core features are built-in (not skills) to prevent chicken-and-egg dependency problems.

**Key Principles:**
- **Security-First:** All 16 security layers fully implemented before feature work
- **Zero-Glitch Provider Switching:** Identical behavior across all LLM providers
- **Built-In Efficiency:** Token optimization, rate limiting, budget enforcement in core
- **Multimodal Native:** Image, PDF, audio normalization across all providers
- **Checkpoint-Ready:** State serialization for long-running task recovery

### Critical Path

```
DI Container → Port Protocols → LLM Adapters → Efficiency Layer → Agent Core → Security → Multimodal → Hands
```

### Success Metrics Summary

| Metric | Target | Phase Verified |
|--------|--------|----------------|
| Cold start | <500ms | Phase 3 |
| Provider switch | <100ms | Phase 1 |
| Memory operation | <50ms | Phase 3 |
| Checkpoint restore | <1s | Phase 6 |
| Test coverage | >90% | All phases |
| Security vulnerabilities | 0 critical/high | Phase 4 |

---

## Task Categories

### Priority Definitions

| Priority | Definition | SLA |
|----------|------------|-----|
| **P0-CRITICAL** | Must have, blocks all other work | Complete within sprint |
| **P0-HIGH** | Core MVP features, blocks dependent tasks | Complete within phase |
| **P1-MEDIUM** | Important but not blocking | Complete by MVP release |
| **P2-LOW** | Nice to have, enhancement | Post-MVP or as time permits |

### Category Definitions

| Category | Scope |
|----------|-------|
| **core** | DI container, agent loop, memory, tools |
| **adapter** | LLM adapters, memory adapters, channel adapters |
| **efficiency** | Rate limiting, caching, compression, budget |
| **security** | All 16 security layers, sandboxing, encryption |
| **multimodal** | Vision, PDF, audio processing |
| **scheduler** | Hands scheduler, autonomous tasks |
| **cli** | Command-line interface, setup wizard |
| **docs** | Documentation, ADRs, guides |

---

## Task Cards

### Phase 1: Foundation (Week 1-2)

---

## NEXUS-001: Project Structure Setup

**Category**: core
**Priority**: P0-CRITICAL
**Phase**: 1
**Dependencies**: None
**Effort**: 4 hours
**Risk**: low

### Description
Initialize the NEXUS project structure following the hexagonal architecture pattern defined in the PRD. Create all necessary directories, `__init__.py` files, and base module structure.

### Acceptance Criteria
- [ ] All directories from PRD Section 5 created
- [ ] All `__init__.py` files present with proper exports
- [ ] `pyproject.toml` configured with dependencies
- [ ] Development environment setup documented
- [ ] `pytest` runs successfully (even with no tests)

### Implementation Notes
- Follow exact structure from PRD Section 5
- Use `src/nexus/` layout for proper packaging
- Include type hints stub files (`.pyi`) for protocols

### Files to Create
```
nexus/
├── __init__.py
├── container/
│   ├── __init__.py
│   ├── di_container.py
│   ├── adapter_registry.py
│   └── lifecycle.py
├── core/
│   ├── __init__.py
│   ├── agent.py
│   ├── memory.py
│   ├── tools.py
│   ├── prompt.py
│   ├── knowledge.py
│   └── checkpoint.py
├── acl/
│   ├── __init__.py
│   ├── hermes_acl.py
│   ├── openclaw_acl.py
│   ├── agent_zero_acl.py
│   └── openfang_acl.py
├── adapters/
│   ├── __init__.py
│   ├── llm/
│   ├── memory/
│   ├── secrets/
│   ├── multimodal/
│   ├── channels/
│   └── storage/
├── efficiency/
│   ├── __init__.py
│   ├── prompt_cache.py
│   ├── token_optimizer.py
│   ├── rate_limiter.py
│   ├── distributed_rate_limiter.py
│   ├── budget.py
│   ├── context_compression.py
│   └── statistics.py
├── ports/
│   ├── __init__.py
│   ├── memory_port.py
│   ├── llm_port.py
│   ├── channel_port.py
│   ├── storage_port.py
│   ├── secrets_port.py
│   ├── multimodal_port.py
│   └── schedule_port.py
├── hands/
│   ├── __init__.py
│   ├── scheduler.py
│   ├── hand.py
│   └── executor.py
├── security/
│   ├── __init__.py
│   ├── sandbox.py
│   ├── validation.py
│   ├── rate_limit.py
│   ├── audit.py
│   ├── output_filter.py
│   ├── encryption.py
│   ├── integrity.py
│   └── layers.py
├── channels/
│   ├── __init__.py
│   ├── dispatcher.py
│   ├── session.py
│   └── context.py
├── config/
│   ├── __init__.py
│   ├── loader.py
│   ├── defaults.py
│   ├── validation.py
│   ├── agent_config.py
│   ├── skill_config.py
│   └── system_config.py
├── cli/
│   ├── __init__.py
│   ├── main.py
│   ├── setup.py
│   └── commands/
│       ├── __init__.py
│       ├── agent.py
│       ├── skill.py
│       ├── hand.py
│       ├── config.py
│       └── system.py
└── utils/
    ├── __init__.py
    ├── logging.py
    ├── fs.py
    └── async_helpers.py
```

---

## NEXUS-002: Dependency Injection Container

**Category**: core
**Priority**: P0-CRITICAL
**Phase**: 1
**Dependencies**: NEXUS-001
**Effort**: 2 days
**Risk**: medium

### Description
Implement the core DI container with service registration, lifecycle management, and auto-wiring. This is the foundation for all hexagonal architecture patterns.

### Acceptance Criteria
- [ ] `DIContainer` class with singleton/transient/scoped lifetimes
- [ ] `register_singleton()`, `register_transient()`, `register_factory()` methods
- [ ] `resolve()` with auto-wiring of constructor dependencies
- [ ] `configure_from_yaml()` for configuration-driven setup
- [ ] Thread-safe singleton resolution
- [ ] Circular dependency detection
- [ ] Unit tests >90% coverage

### Implementation Notes
- Use `typing.Protocol` for service type hints
- Implement `inspect.signature()` for auto-wiring
- Store instances in `_instances` dict for singleton lifetime
- Raise `CircularDependencyError` on cycles

### Files to Create
- `nexus/container/di_container.py` - DI container implementation
- `nexus/container/adapter_registry.py` - Dynamic adapter loading
- `nexus/container/lifecycle.py` - Lifetime enums, descriptors
- `tests/unit/container/test_di_container.py` - Unit tests
- `tests/unit/container/test_adapter_registry.py` - Registry tests

### Code Skeleton
```python
# nexus/container/di_container.py
from typing import TypeVar, Type, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import inspect

T = TypeVar('T')

class Lifetime(Enum):
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

@dataclass
class ServiceDescriptor:
    service_type: Type
    implementation: Type | Callable | None
    lifetime: Lifetime
    instance: Any = None
    factory: Callable | None = None

class CircularDependencyError(Exception):
    pass

class DIContainer:
    def __init__(self):
        self._services: dict[Type, ServiceDescriptor] = {}
        self._instances: dict[Type, Any] = {}
        self._resolving: set[Type] = set()
    
    def register_singleton(self, service_type: Type[T], implementation: Type[T] | None = None) -> None: ...
    def register_transient(self, service_type: Type[T], implementation: Type[T] | None = None) -> None: ...
    def register_factory(self, service_type: Type[T], factory: Callable[[], T], lifetime: Lifetime = Lifetime.SINGLETON) -> None: ...
    def resolve(self, service_type: Type[T]) -> T: ...
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any: ...
    def configure_from_yaml(self, config_path: str) -> None: ...
```

---

## NEXUS-003: Port Protocol Definitions

**Category**: core
**Priority**: P0-CRITICAL
**Phase**: 1
**Dependencies**: NEXUS-001
**Effort**: 1 day
**Risk**: low

### Description
Define all Port protocols using `typing.Protocol`. Ports define the contract that adapters must implement, enabling hexagonal architecture.

### Acceptance Criteria
- [ ] `LLMPort` protocol with all required methods
- [ ] `MemoryPort` protocol for memory operations
- [ ] `ChannelPort` protocol for I/O channels
- [ ] `StoragePort` protocol for file/cloud storage
- [ ] `SecretsPort` protocol for secrets management
- [ ] `MultimodalPort` protocol for media processing
- [ ] `SchedulePort` protocol for task scheduling
- [ ] All protocols have async methods where appropriate
- [ ] Type hints complete for all method signatures

### Implementation Notes
- Use `@runtime_checkable` decorator for isinstance() support
- Include both sync and async versions where needed
- Document expected behavior in docstrings

### Files to Create
- `nexus/ports/llm_port.py` - LLM interface
- `nexus/ports/memory_port.py` - Memory interface
- `nexus/ports/channel_port.py` - Channel interface
- `nexus/ports/storage_port.py` - Storage interface
- `nexus/ports/secrets_port.py` - Secrets interface
- `nexus/ports/multimodal_port.py` - Multimodal interface
- `nexus/ports/schedule_port.py` - Scheduler interface
- `tests/unit/ports/test_all_ports.py` - Protocol validation tests

---

## NEXUS-004: OpenAI LLM Adapter

**Category**: adapter
**Priority**: P0-CRITICAL
**Phase**: 1
**Dependencies**: NEXUS-002, NEXUS-003
**Effort**: 2 days
**Risk**: medium

### Description
Implement native OpenAI adapter with full feature support including streaming, function calling, and vision capabilities.

### Acceptance Criteria
- [ ] Implements `LLMPort` protocol completely
- [ ] Async API calls with proper error handling
- [ ] Streaming support with async generator
- [ ] Function/tool calling with JSON Schema validation
- [ ] Vision support (GPT-4V) with image encoding
- [ ] API version negotiation implemented
- [ ] Graceful fallback on API errors
- [ ] Token usage tracking
- [ ] Unit tests with mocked responses
- [ ] Integration tests against OpenAI API (optional, flagged)

### Implementation Notes
- Use `openai` Python SDK v1.x
- Implement exponential backoff for rate limits
- Store API version in adapter for negotiation
- Use `httpx` for async HTTP

### Files to Create
- `nexus/adapters/llm/base.py` - Base adapter class
- `nexus/adapters/llm/openai.py` - OpenAI implementation
- `nexus/adapters/llm/__init__.py` - Exports
- `tests/unit/adapters/llm/test_openai.py` - Unit tests
- `tests/integration/adapters/test_openai_live.py` - Live API tests (optional)

---

## NEXUS-005: OpenAI-Compatible Adapter

**Category**: adapter
**Priority**: P0-CRITICAL
**Phase**: 1
**Dependencies**: NEXUS-004
**Effort**: 1 day
**Risk**: low

### Description
Implement adapter for OpenAI-compatible endpoints (vLLM, LM Studio, custom deployments). Extends OpenAI adapter with configurable base URL.

### Acceptance Criteria
- [ ] Extends OpenAI adapter with configurable `base_url`
- [ ] Works with vLLM, LM Studio, LocalAI tested
- [ ] Custom headers support for authentication
- [ ] Health check endpoint verification
- [ ] Capability detection (some endpoints lack features)
- [ ] Graceful degradation for missing features

### Implementation Notes
- Inherit from `OpenAIAdapter`
- Override `__init__` to accept `base_url`
- Add `verify_endpoint()` method for health checks

### Files to Create
- `nexus/adapters/llm/openai_compatible.py` - Compatible adapter
- `tests/unit/adapters/llm/test_openai_compatible.py` - Tests

---

## NEXUS-006: Ollama LLM Adapter

**Category**: adapter
**Priority**: P0-CRITICAL
**Phase**: 1
**Dependencies**: NEXUS-003
**Effort**: 2 days
**Risk**: medium

### Description
Implement local Ollama adapter for privacy-first, no-API-key-required operation. Critical for zero-config experience.

### Acceptance Criteria
- [ ] Implements `LLMPort` protocol
- [ ] Auto-detection of local Ollama instance
- [ ] Model listing and pulling capabilities
- [ ] Streaming response support
- [ ] Tool calling support (where model supports)
- [ ] Vision support for LLaVA models
- [ ] Connection timeout handling
- [ ] Works offline (no network required)

### Implementation Notes
- Use `ollama` Python library or HTTP API
- Default base URL: `http://localhost:11434`
- Implement `is_available()` static method
- Handle model download progress

### Files to Create
- `nexus/adapters/llm/ollama.py` - Ollama implementation
- `tests/unit/adapters/llm/test_ollama.py` - Unit tests
- `tests/integration/adapters/test_ollama_local.py` - Local tests

---

## NEXUS-007: Anthropic LLM Adapter

**Category**: adapter
**Priority**: P0-HIGH
**Phase**: 1
**Dependencies**: NEXUS-004
**Effort**: 1.5 days
**Risk**: medium

### Description
Implement Anthropic Claude adapter with proper message formatting and tool calling translation.

### Acceptance Criteria
- [ ] Implements `LLMPort` protocol
- [ ] Message format translation (system, user, assistant)
- [ ] Tool calling with proper schema translation
- [ ] Vision support with Claude's format
- [ ] Streaming support
- [ ] Prompt caching support (Claude feature)
- [ ] Proper token counting (Claude tokenizer)

### Implementation Notes
- Use `anthropic` Python SDK
- Translate OpenAI tool schema to Anthropic format
- Handle Claude's unique system message placement
- Implement prompt caching headers

### Files to Create
- `nexus/adapters/llm/anthropic.py` - Anthropic implementation
- `tests/unit/adapters/llm/test_anthropic.py` - Unit tests

---

## NEXUS-008: SQLite Memory Adapter

**Category**: adapter
**Priority**: P0-CRITICAL
**Phase**: 1
**Dependencies**: NEXUS-003
**Effort**: 1.5 days
**Risk**: low

### Description
Implement SQLite memory adapter with WAL mode for concurrent access and connection pooling.

### Acceptance Criteria
- [ ] Implements `MemoryPort` protocol
- [ ] WAL mode enabled by default
- [ ] Connection pooling (configurable pool size)
- [ ] Async operations using `aiosqlite`
- [ ] CRUD operations for memory entries
- [ ] Semantic search integration point
- [ ] Migration system for schema changes
- [ ] Memory cleanup/retention policies

### Implementation Notes
- Use `aiosqlite` for async operations
- Create tables on first run
- Implement connection pool with `contextvars`
- Default path: `~/.nexus/memory.db`

### Files to Create
- `nexus/adapters/memory/sqlite_adapter.py` - SQLite implementation
- `nexus/adapters/memory/base.py` - Base memory adapter
- `nexus/adapters/memory/__init__.py` - Exports
- `tests/unit/adapters/memory/test_sqlite.py` - Unit tests

---

## NEXUS-009: CLI Skeleton and Init Command

**Category**: cli
**Priority**: P0-CRITICAL
**Phase**: 1
**Dependencies**: NEXUS-001
**Effort**: 1 day
**Risk**: low

### Description
Create CLI skeleton with `nexus init` command for one-command setup. This enables non-technical user onboarding.

### Acceptance Criteria
- [ ] `nexus` command available after install
- [ ] `nexus init` creates default configuration
- [ ] Auto-detects available providers (Ollama first)
- [ ] Creates `nexus.yaml` with sensible defaults
- [ ] Creates `~/.nexus/` directory structure
- [ ] Verifies Python version compatibility
- [ ] Clear error messages for missing dependencies

### Implementation Notes
- Use `typer` for CLI framework
- Use `rich` for beautiful output
- Check for Ollama at `localhost:11434`
- Default to SQLite for zero-config

### Files to Create
- `nexus/cli/main.py` - CLI entry point
- `nexus/cli/setup.py` - Init command implementation
- `nexus/cli/commands/` - Subcommand modules
- `tests/unit/cli/test_init.py` - Init tests

---

## NEXUS-010: Docker Sandbox Implementation

**Category**: security
**Priority**: P0-CRITICAL
**Phase**: 1
**Dependencies**: NEXUS-001
**Effort**: 2 days
**Risk**: high

### Description
Implement Docker-based sandboxing for untrusted skill execution. Critical security feature.

### Acceptance Criteria
- [ ] Docker container creation with resource limits
- [ ] Memory limit: 512MB default
- [ ] CPU limit: 1.0 default
- [ ] Timeout: 30 seconds default
- [ ] Network access disabled by default
- [ ] seccomp profile for syscall restriction
- [ ] Volume mount for skill code (read-only)
- [ ] Container cleanup on completion/failure
- [ ] Health check before skill execution

### Implementation Notes
- Use `docker` Python SDK
- Create minimal Python container image
- Implement `SecurityPolicy` dataclass
- Log all sandbox operations for audit

### Files to Create
- `nexus/security/sandbox.py` - Sandbox implementation
- `nexus/security/policy.py` - Security policy definitions
- `tests/unit/security/test_sandbox.py` - Unit tests
- `tests/integration/security/test_sandbox_live.py` - Docker tests

---

### Phase 2: Built-In Efficiency (Week 3-4)

---

## NEXUS-011: Prompt Caching System

**Category**: efficiency
**Priority**: P0-CRITICAL
**Phase**: 2
**Dependencies**: NEXUS-004, NEXUS-006
**Effort**: 2 days
**Risk**: medium

### Description
Implement prompt caching for static prefix optimization. Reduces token usage and API costs.

### Acceptance Criteria
- [ ] Static prefix identification algorithm
- [ ] Prefix hash computation (SHA-256)
- [ ] Cache hit/miss tracking
- [ ] Per-provider cache storage
- [ ] Cache invalidation on prefix change
- [ ] TOON format for cache storage
- [ ] Statistics: tokens saved, hit rate
- [ ] Integration with LLM adapters

### Implementation Notes
- Use `hashlib` for prefix hashing
- Store cache in `~/.nexus/cache/`
- Implement `PrefixCheckpoint` class
- Anti-pattern detection for cache busters

### Files to Create
- `nexus/efficiency/prompt_cache.py` - Cache implementation
- `nexus/efficiency/prefix_checkpoint.py` - Checkpoint manager
- `tests/unit/efficiency/test_prompt_cache.py` - Unit tests

---

## NEXUS-012: Local Rate Limiter

**Category**: efficiency
**Priority**: P0-CRITICAL
**Phase**: 2
**Dependencies**: NEXUS-001
**Effort**: 1 day
**Risk**: low

### Description
Implement in-memory rate limiting with token bucket algorithm. Protects against API rate limits.

### Acceptance Criteria
- [ ] Token bucket algorithm implementation
- [ ] Sliding window for precise limiting
- [ ] Configurable RPM (requests per minute)
- [ ] Per-provider rate limit configs
- [ ] Auto-backoff on 429 responses
- [ ] Rate limit status tracking
- [ ] Thread-safe implementation

### Implementation Notes
- Use `asyncio.Lock` for thread safety
- Implement `RateLimitConfig` dataclass
- Default limits per provider documented

### Files to Create
- `nexus/efficiency/rate_limiter.py` - Rate limiter implementation
- `tests/unit/efficiency/test_rate_limiter.py` - Unit tests

---

## NEXUS-013: Distributed Rate Limiter

**Category**: efficiency
**Priority**: P0-HIGH
**Phase**: 2
**Dependencies**: NEXUS-012
**Effort**: 1.5 days
**Risk**: medium

### Description
Implement Redis-backed distributed rate limiting for multi-instance deployments.

### Acceptance Criteria
- [ ] Redis connection with connection pooling
- [ ] Lua script for atomic operations
- [ ] Sliding window algorithm (not fixed window)
- [ ] Automatic cleanup of expired entries
- [ ] Redis Sentinel support for HA
- [ ] Graceful fallback to local rate limiting
- [ ] Configuration for Redis URL

### Implementation Notes
- Use `redis` or `aioredis` library
- Lua script ensures atomicity
- Configurable key prefix for namespacing

### Files to Create
- `nexus/efficiency/distributed_rate_limiter.py` - Redis implementation
- `tests/unit/efficiency/test_distributed_rate_limiter.py` - Unit tests
- `tests/integration/efficiency/test_redis_rate_limit.py` - Redis tests

---

## NEXUS-014: Budget Enforcement

**Category**: efficiency
**Priority**: P0-CRITICAL
**Phase**: 2
**Dependencies**: NEXUS-004
**Effort**: 1.5 days
**Risk**: medium

### Description
Implement hard stop on token/cost limits. Prevents runaway API costs.

### Acceptance Criteria
- [ ] Pre-flight cost estimation
- [ ] Running total tracking (tokens and cost)
- [ ] Hard stop when budget exceeded
- [ ] Alert thresholds (50%, 75%, 90%, 100%)
- [ ] Webhook callback for alerts
- [ ] Per-provider pricing table
- [ ] `BudgetExceededError` exception
- [ ] Budget reset capability

### Implementation Notes
- Implement `BudgetEnforcer` class
- Pricing table as class constant
- Use decimal for precise cost calculation

### Files to Create
- `nexus/efficiency/budget.py` - Budget implementation
- `nexus/efficiency/pricing.py` - Pricing tables
- `tests/unit/efficiency/test_budget.py` - Unit tests

---

## NEXUS-015: TOON Context Compression

**Category**: efficiency
**Priority**: P0-HIGH
**Phase**: 2
**Dependencies**: NEXUS-001
**Effort**: 2 days
**Risk**: medium

### Description
Implement TOON (Token-Oriented Object Notation) compression for context optimization.

### Acceptance Criteria
- [ ] TOON encoder implementation
- [ ] TOON decoder implementation
- [ ] ~40% token reduction target
- [ ] Lossless conversion
- [ ] Human-readable output
- [ ] JSON-to-TOON converter
- [ ] TOON-to-JSON converter
- [ ] Streaming support for large contexts

### Implementation Notes
- Follow TOON specification
- Use indentation-based nesting
- Implement explicit array lengths

### Files to Create
- `nexus/efficiency/context_compression.py` - TOON implementation
- `nexus/efficiency/toon.py` - TOON codec
- `tests/unit/efficiency/test_toon.py` - Unit tests

---

## NEXUS-016: Token Statistics Tracker

**Category**: efficiency
**Priority**: P0-HIGH
**Phase**: 2
**Dependencies**: NEXUS-011, NEXUS-012, NEXUS-014
**Effort**: 1 day
**Risk**: low

### Description
Implement unified statistics tracking across all efficiency components.

### Acceptance Criteria
- [ ] Unified stats from cache, rate limiter, budget
- [ ] TOON-formatted reports
- [ ] Real-time metrics exposure
- [ ] Historical tracking (daily/weekly)
- [ ] Export to JSON/CSV
- [ ] Dashboard data endpoint

### Implementation Notes
- Aggregate from all efficiency components
- Store in SQLite for historical analysis
- Implement `get_stats()` method

### Files to Create
- `nexus/efficiency/statistics.py` - Statistics implementation
- `tests/unit/efficiency/test_statistics.py` - Unit tests

---

### Phase 3: Core Agent (Week 5-6)

---

## NEXUS-017: Agent Loop Implementation

**Category**: core
**Priority**: P0-CRITICAL
**Phase**: 3
**Dependencies**: NEXUS-002, NEXUS-004, NEXUS-011
**Effort**: 3 days
**Risk**: high

### Description
Implement the core agent execution loop with LLM interaction, tool execution, and response handling.

### Acceptance Criteria
- [ ] Async agent loop with configurable iterations
- [ ] Prompt assembly and sending to LLM
- [ ] Response parsing (text, tool calls)
- [ ] Tool execution with results
- [ ] Error handling and retry logic
- [ ] Iteration limit enforcement
- [ ] Early termination support
- [ ] Integration with DI container

### Implementation Notes
- Implement `AgentLoop` class
- Use `asyncio` for async operations
- Support both streaming and non-streaming
- Log each iteration for debugging

### Files to Create
- `nexus/core/agent.py` - Agent implementation
- `nexus/core/loop.py` - Loop implementation
- `tests/unit/core/test_agent.py` - Unit tests
- `tests/integration/core/test_agent_loop.py` - Integration tests

---

## NEXUS-018: Memory Manager

**Category**: core
**Priority**: P0-CRITICAL
**Phase**: 3
**Dependencies**: NEXUS-008, NEXUS-017
**Effort**: 2 days
**Risk**: medium

### Description
Implement memory manager for agent state, conversation history, and context management.

### Acceptance Criteria
- [ ] Short-term memory (conversation buffer)
- [ ] Long-term memory (persistent storage)
- [ ] Memory retrieval with relevance scoring
- [ ] Memory pruning (token budget management)
- [ ] Memory consolidation algorithms
- [ ] Integration with SQLite adapter

### Implementation Notes
- Implement `MemoryManager` class
- Use `MemoryPort` through DI container
- Implement LRU for short-term memory

### Files to Create
- `nexus/core/memory.py` - Memory manager
- `tests/unit/core/test_memory.py` - Unit tests

---

## NEXUS-019: Tool Registry

**Category**: core
**Priority**: P0-CRITICAL
**Phase**: 3
**Dependencies**: NEXUS-002, NEXUS-010
**Effort**: 2 days
**Risk**: medium

### Description
Implement tool registry for dynamic tool loading, registration, and execution.

### Acceptance Criteria
- [ ] Tool registration with JSON Schema
- [ ] Dynamic tool loading from skills
- [ ] Tool execution in sandbox (configurable)
- [ ] Tool result handling
- [ ] Tool permission levels
- [ ] Built-in tools: code execution, file operations
- [ ] Tool timeout enforcement

### Implementation Notes
- Implement `ToolRegistry` class
- Integrate with `SecuritySandbox`
- Store tool schemas for validation

### Files to Create
- `nexus/core/tools.py` - Tool registry
- `nexus/tools/builtin/` - Built-in tools
- `tests/unit/core/test_tools.py` - Unit tests

---

## NEXUS-020: Prompt Assembly

**Category**: core
**Priority**: P0-CRITICAL
**Phase**: 3
**Dependencies**: NEXUS-017, NEXUS-018
**Effort**: 1.5 days
**Risk**: medium

### Description
Implement dynamic prompt assembly with system prompts, skills, tools, and context.

### Acceptance Criteria
- [ ] System prompt templates
- [ ] Skill prompt injection
- [ ] Tool definition formatting
- [ ] Context window management
- [ ] Token counting integration
- [ ] Prompt caching integration
- [ ] Provider-specific formatting

### Implementation Notes
- Implement `PromptAssembler` class
- Use Jinja2 for templating
- Integrate with `TokenOptimizer`

### Files to Create
- `nexus/core/prompt.py` - Prompt assembly
- `nexus/prompts/` - Prompt templates
- `tests/unit/core/test_prompt.py` - Unit tests

---

## NEXUS-021: SKILL.md Parser

**Category**: core
**Priority**: P0-CRITICAL
**Phase**: 3
**Dependencies**: NEXUS-019
**Effort**: 1.5 days
**Risk**: low

### Description
Implement parser for SKILL.md format (from Hermes). Enables skill definition in Markdown.

### Acceptance Criteria
- [ ] Parse YAML frontmatter
- [ ] Extract skill metadata (name, description, tags)
- [ ] Parse requirements list
- [ ] Extract skill body (instructions)
- [ ] Parse tool bindings
- [ ] Validate skill structure
- [ ] Load skill into registry

### Implementation Notes
- Use `pyyaml` for frontmatter
- Support Hermes SKILL.md format exactly
- Implement `SkillParser` class

### Files to Create
- `nexus/core/skill_parser.py` - Parser implementation
- `tests/fixtures/skills/` - Test skill files
- `tests/unit/core/test_skill_parser.py` - Unit tests

---

## NEXUS-022: Agent Checkpointing

**Category**: core
**Priority**: P0-CRITICAL
**Phase**: 3
**Dependencies**: NEXUS-017, NEXUS-015
**Effort**: 2 days
**Risk**: medium

### Description
Implement agent state checkpointing for long-running task recovery.

### Acceptance Criteria
- [ ] Automatic checkpointing at intervals
- [ ] Manual checkpoint on critical operations
- [ ] Recovery from last checkpoint
- [ ] TOON format for state serialization
- [ ] Checkpoint compression
- [ ] Checkpoint cleanup (max N stored)
- [ ] Recovery verification

### Implementation Notes
- Implement `CheckpointManager` class
- Store in `~/.nexus/checkpoints/`
- Use TOON for efficient serialization

### Files to Create
- `nexus/core/checkpoint.py` - Checkpoint implementation
- `tests/unit/core/test_checkpoint.py` - Unit tests

---

## NEXUS-023: Anti-Corruption Layer

**Category**: core
**Priority**: P0-HIGH
**Phase**: 3
**Dependencies**: NEXUS-001
**Effort**: 2 days
**Risk**: medium

### Description
Implement ACL for framework integration. Translates external patterns to NEXUS patterns.

### Acceptance Criteria
- [ ] `HermesACL` - Hermes skill/memory translation
- [ ] `AgentZeroACL` - Agent Zero tool translation
- [ ] `OpenClawACL` - OpenClaw configuration translation
- [ ] `OpenFangACL` - OpenFang hand translation
- [ ] Bi-directional translation where applicable
- [ ] Validation of translated artifacts

### Implementation Notes
- One ACL class per source framework
- Focus on common migration patterns
- Document translation rules

### Files to Create
- `nexus/acl/hermes_acl.py` - Hermes translation
- `nexus/acl/agent_zero_acl.py` - Agent Zero translation
- `nexus/acl/openclaw_acl.py` - OpenClaw translation
- `nexus/acl/openfang_acl.py` - OpenFang translation
- `tests/unit/acl/` - ACL tests

---

## NEXUS-024: Zero-Glitch Provider Switch Tests

**Category**: core
**Priority**: P0-CRITICAL
**Phase**: 3
**Dependencies**: NEXUS-004, NEXUS-006, NEXUS-007
**Effort**: 1.5 days
**Risk**: medium

### Description
Comprehensive test suite verifying identical behavior across all LLM providers.

### Acceptance Criteria
- [ ] Same prompt produces same behavior
- [ ] Tool calls format correctly for each provider
- [ ] Streaming behavior consistent
- [ ] Error handling consistent
- [ ] Token counting matches actual usage
- [ ] Provider switch time <100ms
- [ ] Zero errors on switch

### Implementation Notes
- Create provider-agnostic test fixtures
- Test all adapters with same inputs
- Measure switch time benchmarks

### Files to Create
- `tests/integration/test_provider_switch.py` - Switch tests
- `tests/fixtures/provider_agnostic/` - Test fixtures

---

### Phase 4: Multimodal & Security (Week 7-8)

---

## NEXUS-025: Multimodal Port Implementation

**Category**: multimodal
**Priority**: P0-HIGH
**Phase**: 4
**Dependencies**: NEXUS-003
**Effort**: 1 day
**Risk**: low

### Description
Implement the `MultimodalPort` protocol with normalized interfaces for images, PDFs, and audio.

### Acceptance Criteria
- [ ] `process_image()` with format detection
- [ ] `process_pdf()` with text extraction
- [ ] `transcribe_audio()` with language support
- [ ] Provider-specific optimization hooks
- [ ] Async processing throughout

### Implementation Notes
- Define `ProcessedImage`, `ProcessedPDF`, `Transcription` dataclasses
- Support multiple input formats (bytes, Path, base64)

### Files to Create
- `nexus/ports/multimodal_port.py` - Port protocol
- `nexus/adapters/multimodal/base.py` - Base adapter
- `tests/unit/ports/test_multimodal_port.py` - Port tests

---

## NEXUS-026: Vision Adapter Implementation

**Category**: multimodal
**Priority**: P0-HIGH
**Phase**: 4
**Dependencies**: NEXUS-025
**Effort**: 2 days
**Risk**: medium

### Description
Implement vision adapter for image normalization across providers.

### Acceptance Criteria
- [ ] Image format conversion (PNG, JPEG, WEBP, GIF)
- [ ] Size limit enforcement per provider
- [ ] Provider-specific format optimization
- [ ] Base64 encoding for API transmission
- [ ] Image resizing with aspect ratio
- [ ] Metadata preservation

### Implementation Notes
- Use `Pillow` for image processing
- Implement `PROVIDER_LIMITS` constant
- Support batch processing

### Files to Create
- `nexus/adapters/multimodal/vision_adapter.py` - Vision implementation
- `tests/unit/adapters/multimodal/test_vision.py` - Unit tests

### Provider Limits Reference
```python
PROVIDER_LIMITS = {
    'openai': {'max_size': 20_000_000, 'formats': ['PNG', 'JPEG', 'WEBP', 'GIF']},
    'anthropic': {'max_size': 5_000_000, 'formats': ['PNG', 'JPEG', 'WEBP', 'GIF']},
    'ollama': {'max_size': 10_000_000, 'formats': ['PNG', 'JPEG']},
}
```

---

## NEXUS-027: PDF Adapter Implementation

**Category**: multimodal
**Priority**: P1-MEDIUM
**Phase**: 4
**Dependencies**: NEXUS-025
**Effort**: 1.5 days
**Risk**: medium

### Description
Implement PDF adapter for text and image extraction.

### Acceptance Criteria
- [ ] Text extraction from PDFs
- [ ] Per-page text extraction
- [ ] Image extraction from PDFs
- [ ] PDF metadata extraction
- [ ] OCR support for scanned PDFs
- [ ] Large PDF handling (streaming)

### Implementation Notes
- Use `pypdf` or `pdfplumber`
- Optional `pytesseract` for OCR
- Handle password-protected PDFs

### Files to Create
- `nexus/adapters/multimodal/pdf_adapter.py` - PDF implementation
- `tests/unit/adapters/multimodal/test_pdf.py` - Unit tests

---

## NEXUS-028: Audio/Whisper Adapter Implementation

**Category**: multimodal
**Priority**: P1-MEDIUM
**Phase**: 4
**Dependencies**: NEXUS-025
**Effort**: 1.5 days
**Risk**: medium

### Description
Implement audio transcription adapter using OpenAI Whisper.

### Acceptance Criteria
- [ ] Audio format support (MP3, WAV, M4A, etc.)
- [ ] Language detection and specification
- [ ] Timestamp segment extraction
- [ ] Confidence scoring
- [ ] Local Whisper model support
- [ ] OpenAI Whisper API support

### Implementation Notes
- Use `openai-whisper` for local
- Use OpenAI API for remote
- Support both sync and async

### Files to Create
- `nexus/adapters/multimodal/whisper_adapter.py` - Whisper implementation
- `tests/unit/adapters/multimodal/test_whisper.py` - Unit tests

---

## NEXUS-029: Security Layer 1 - Input Validation

**Category**: security
**Priority**: P0-CRITICAL
**Phase**: 4
**Dependencies**: NEXUS-001
**Effort**: 1 day
**Risk**: medium

### Description
Implement comprehensive input validation with recursive type checking and DoS protection.

### Acceptance Criteria
- [ ] Recursive type validation
- [ ] Depth limiting (max 100 levels)
- [ ] Pydantic v2 schema validation
- [ ] Regex DoS protection (100ms timeout)
- [ ] Custom validation rules
- [ ] Clear error messages

### Implementation Notes
- Use `pydantic` for schema validation
- Implement `InputValidator` class
- Add `@validated` decorator

### Files to Create
- `nexus/security/validation.py` - Validation implementation
- `tests/unit/security/test_validation.py` - Unit tests

---

## NEXUS-030: Security Layer 2 - Skill Sandboxing

**Category**: security
**Priority**: P0-CRITICAL
**Phase**: 4
**Dependencies**: NEXUS-010
**Effort**: 1 day
**Risk**: high

### Description
Enhance Docker sandbox with seccomp profiles and comprehensive isolation.

### Acceptance Criteria
- [ ] seccomp profile implementation
- [ ] No network access by default
- [ ] Resource limits enforced (memory, CPU)
- [ ] Timeout enforcement
- [ ] Audit trail of sandbox operations
- [ ] Escape detection

### Implementation Notes
- Build on NEXUS-010 foundation
- Add seccomp JSON profile
- Test escape scenarios

### Files to Create
- `nexus/security/sandbox.py` - Enhanced (already created)
- `nexus/security/seccomp_profile.json` - Seccomp profile
- `tests/integration/security/test_sandbox_escape.py` - Escape tests

---

## NEXUS-031: Security Layer 3 - Rate Limiting (Security)

**Category**: security
**Priority**: P0-HIGH
**Phase**: 4
**Dependencies**: NEXUS-012
**Effort**: 0.5 days
**Risk**: low

### Description
Security-focused rate limiting for abuse prevention.

### Acceptance Criteria
- [ ] Integration with efficiency rate limiter
- [ ] Per-user rate limiting
- [ ] Per-IP rate limiting
- [ ] Brute force protection
- [ ] Rate limit audit logging

### Implementation Notes
- Build on NEXUS-012
- Add security-specific rate limit tiers
- Log all rate limit events

### Files to Create
- `nexus/security/rate_limit.py` - Security rate limiting
- `tests/unit/security/test_rate_limit.py` - Tests

---

## NEXUS-032: Security Layer 4 - Audit Logging

**Category**: security
**Priority**: P0-CRITICAL
**Phase**: 4
**Dependencies**: NEXUS-001
**Effort**: 1 day
**Risk**: low

### Description
Implement comprehensive audit logging with integrity verification.

### Acceptance Criteria
- [ ] Structured JSON logs
- [ ] Append-only log files
- [ ] Log rotation (100MB max)
- [ ] HMAC-SHA256 chain for integrity
- [ ] Retention policy (configurable)
- [ ] Log query interface

### Implementation Notes
- Implement `AuditLogger` class
- Store in `~/.nexus/audit/`
- Use HMAC chain for tamper detection

### Files to Create
- `nexus/security/audit.py` - Audit implementation
- `tests/unit/security/test_audit.py` - Unit tests

---

## NEXUS-033: Security Layer 5 - Output Filtering

**Category**: security
**Priority**: P0-CRITICAL
**Phase**: 4
**Dependencies**: NEXUS-001
**Effort**: 1.5 days
**Risk**: medium

### Description
Implement PII detection and sensitive data redaction.

### Acceptance Criteria
- [ ] PII detection using presidio
- [ ] Custom regex patterns for secrets
- [ ] API key/token redaction
- [ ] Audit trail of redactions
- [ ] Configurable redaction rules
- [ ] Performance <10ms overhead

### Implementation Notes
- Use Microsoft presidio
- Implement custom recognizers for secrets
- Pattern library for common secrets

### Files to Create
- `nexus/security/output_filter.py` - Output filtering
- `nexus/security/patterns.py` - Secret patterns
- `tests/unit/security/test_output_filter.py` - Unit tests

---

## NEXUS-034: Security Layers 6-7 - Authentication & Authorization

**Category**: security
**Priority**: P0-HIGH
**Phase**: 4
**Dependencies**: NEXUS-032
**Effort**: 2 days
**Risk**: medium

### Description
Implement JWT authentication and RBAC authorization.

### Acceptance Criteria
- [ ] JWT with RS256 (RSA 2048)
- [ ] Token lifetime: 1hr access, 7 day refresh
- [ ] Refresh token rotation
- [ ] OAuth2 PKCE flow support
- [ ] RBAC with permission inheritance
- [ ] Roles: admin, developer, user, guest
- [ ] Permission model: `resource:action`

### Implementation Notes
- Use `pyjwt` for JWT handling
- Implement `AuthManager` and `AuthzManager`
- Store permissions in SQLite

### Files to Create
- `nexus/security/auth.py` - Authentication
- `nexus/security/authz.py` - Authorization
- `tests/unit/security/test_auth.py` - Auth tests
- `tests/unit/security/test_authz.py` - Authz tests

---

## NEXUS-035: Security Layer 8 - Encryption

**Category**: security
**Priority**: P0-CRITICAL
**Phase**: 4
**Dependencies**: NEXUS-001
**Effort**: 1.5 days
**Risk**: medium

### Description
Implement encryption for data at rest and in transit.

### Acceptance Criteria
- [ ] AES-256-GCM for data at rest
- [ ] TLS 1.3 for transit (enforce)
- [ ] Key derivation: Argon2id
- [ ] Key rotation: 90-day cycle
- [ ] Encrypted storage for secrets
- [ ] Key backup/recovery

### Implementation Notes
- Use `cryptography` library
- Implement `EncryptionManager` class
- Store keys in secure location

### Files to Create
- `nexus/security/encryption.py` - Encryption implementation
- `nexus/security/keys.py` - Key management
- `tests/unit/security/test_encryption.py` - Unit tests

---

## NEXUS-036: Security Layer 9-10 - Integrity & Non-repudiation

**Category**: security
**Priority**: P0-HIGH
**Phase**: 4
**Dependencies**: NEXUS-035
**Effort**: 1.5 days
**Risk**: medium

### Description
Implement integrity verification and non-repudiation mechanisms.

### Acceptance Criteria
- [ ] SHA-256 for data integrity
- [ ] Ed25519 for code signatures
- [ ] Merkle trees for audit logs
- [ ] Signature verification before skill execution
- [ ] Event sourcing with signed events
- [ ] Timestamp authority integration

### Implementation Notes
- Implement `IntegrityManager` class
- Use `nacl` for Ed25519
- Build Merkle tree for audit logs

### Files to Create
- `nexus/security/integrity.py` - Integrity implementation
- `nexus/security/non_repudiation.py` - Non-repudiation
- `tests/unit/security/test_integrity.py` - Unit tests

---

## NEXUS-037: Security Layers 11-16 - Remaining Layers

**Category**: security
**Priority**: P0-HIGH
**Phase**: 4
**Dependencies**: NEXUS-010, NEXUS-032, NEXUS-035
**Effort**: 3 days
**Risk**: medium

### Description
Implement remaining security layers: Fail-safe, Resource Limits, Dependency Verification, Secure Defaults, Incident Response, Compliance.

### Acceptance Criteria
- [ ] Circuit breaker (half-open after 30s)
- [ ] Retry with exponential backoff
- [ ] Memory/CPU limits via cgroups
- [ ] File descriptor limits (1024 max)
- [ ] pip-audit for CVE scanning
- [ ] SLSA Level 3 compliance
- [ ] All features opt-in for risks
- [ ] Incident response runbook
- [ ] GDPR Data subject rights API
- [ ] SOC2 Audit trail retention (7 years)

### Implementation Notes
- Implement `CircuitBreaker` class
- Use `pip-audit` for dependency scanning
- Create runbook in `docs/security/runbook.md`

### Files to Create
- `nexus/security/fail_safe.py` - Circuit breaker
- `nexus/security/resources.py` - Resource limits
- `nexus/security/compliance.py` - Compliance APIs
- `docs/security/runbook.md` - Incident runbook
- `tests/unit/security/test_remaining_layers.py` - Tests

---

## NEXUS-038: HashiCorp Vault Adapter

**Category**: adapter
**Priority**: P1-MEDIUM
**Phase**: 4
**Dependencies**: NEXUS-003, NEXUS-035
**Effort**: 1.5 days
**Risk**: medium

### Description
Implement HashiCorp Vault adapter for enterprise secrets management.

### Acceptance Criteria
- [ ] AppRole authentication
- [ ] Dynamic secrets (database credentials)
- [ ] Automatic lease renewal
- [ ] Audit logging for secret access
- [ ] Encryption as a Service
- [ ] Fallback to env vars

### Implementation Notes
- Use `hvac` library
- Implement `VaultAdapter` class
- Handle connection failures gracefully

### Files to Create
- `nexus/adapters/secrets/vault_adapter.py` - Vault implementation
- `nexus/adapters/secrets/env_adapter.py` - Env fallback
- `tests/unit/adapters/secrets/test_vault.py` - Unit tests

---

## NEXUS-039: Security Integration Tests

**Category**: security
**Priority**: P0-CRITICAL
**Phase**: 4
**Dependencies**: NEXUS-029 through NEXUS-037
**Effort**: 2 days
**Risk**: medium

### Description
Comprehensive security integration tests across all 16 layers.

### Acceptance Criteria
- [ ] All security layers tested together
- [ ] Attack scenario tests
- [ ] Performance overhead tests
- [ ] No security regressions
- [ ] Coverage >95% for security code

### Implementation Notes
- Create attack simulation tests
- Test layer interactions
- Benchmark security overhead

### Files to Create
- `tests/integration/security/test_all_layers.py` - Integration tests
- `tests/security/attack_scenarios/` - Attack simulations

---

### Phase 5: Multi-Agent & Persistence (Week 9-10)

---

## NEXUS-040: Multi-Agent Hierarchy

**Category**: core
**Priority**: P1-MEDIUM
**Phase**: 5
**Dependencies**: NEXUS-017, NEXUS-019
**Effort**: 3 days
**Risk**: high

### Description
Implement multi-agent hierarchy for task delegation.

### Acceptance Criteria
- [ ] Superior/subordinate agent relationships
- [ ] Task delegation protocol
- [ ] Result aggregation from subordinates
- [ ] Inter-agent communication
- [ ] Subordinate lifecycle management
- [ ] Context isolation between agents

### Implementation Notes
- Implement `AgentHierarchy` class
- Use DI container for subordinate creation
- Implement `delegate_to_subordinate()` method

### Files to Create
- `nexus/core/hierarchy.py` - Hierarchy implementation
- `nexus/core/delegation.py` - Delegation protocol
- `tests/unit/core/test_hierarchy.py` - Unit tests

---

## NEXUS-041: State Persistence

**Category**: core
**Priority**: P1-MEDIUM
**Phase**: 5
**Dependencies**: NEXUS-022, NEXUS-040
**Effort**: 2 days
**Risk**: medium

### Description
Enhance state persistence for multi-agent scenarios.

### Acceptance Criteria
- [ ] Agent state serialization
- [ ] Cross-agent state sharing (controlled)
- [ ] State versioning
- [ ] State migration on schema changes
- [ ] State compression (TOON)
- [ ] State recovery verification

### Implementation Notes
- Build on NEXUS-022 checkpointing
- Implement `StateManager` class
- Handle state conflicts

### Files to Create
- `nexus/core/state.py` - State management
- `tests/unit/core/test_state.py` - Unit tests

---

## NEXUS-042: Knowledge Graph Implementation

**Category**: core
**Priority**: P1-MEDIUM
**Phase**: 5
**Dependencies**: NEXUS-018
**Effort**: 2 days
**Risk**: medium

### Description
Implement basic knowledge graph for entity relationship storage.

### Acceptance Criteria
- [ ] Entity storage and retrieval
- [ ] Relationship storage
- [ ] Graph traversal queries
- [ ] Entity linking
- [ ] Knowledge inference
- [ ] Integration with memory manager

### Implementation Notes
- Implement `KnowledgeGraph` class
- Use SQLite for storage (or dedicated graph DB)
- Support common entity types

### Files to Create
- `nexus/core/knowledge.py` - Knowledge graph
- `tests/unit/core/test_knowledge.py` - Unit tests

---

## NEXUS-043: Semantic Search Integration

**Category**: core
**Priority**: P1-MEDIUM
**Phase**: 5
**Dependencies**: NEXUS-018, NEXUS-042
**Effort**: 2 days
**Risk**: medium

### Description
Implement semantic search for memory and knowledge retrieval.

### Acceptance Criteria
- [ ] Embedding generation
- [ ] Vector storage (ChromaDB adapter)
- [ ] Similarity search
- [ ] Hybrid search (keyword + semantic)
- [ ] Relevance scoring
- [ ] Search result ranking

### Implementation Notes
- Implement `SemanticSearch` class
- Use OpenAI embeddings or local model
- Integrate with ChromaDB adapter

### Files to Create
- `nexus/core/semantic_search.py` - Semantic search
- `nexus/adapters/memory/chromadb_adapter.py` - ChromaDB
- `tests/unit/core/test_semantic_search.py` - Unit tests

---

## NEXUS-044: Multi-Agent Integration Tests

**Category**: core
**Priority**: P1-MEDIUM
**Phase**: 5
**Dependencies**: NEXUS-040, NEXUS-041
**Effort**: 1.5 days
**Risk**: medium

### Description
Integration tests for multi-agent scenarios.

### Acceptance Criteria
- [ ] Delegation flow tests
- [ ] State isolation tests
- [ ] Communication tests
- [ ] Failure handling tests
- [ ] Performance tests

### Files to Create
- `tests/integration/core/test_multi_agent.py` - Integration tests

---

### Phase 6: Autonomous Features (Week 11-12)

---

## NEXUS-045: Hand Scheduler Implementation

**Category**: scheduler
**Priority**: P1-MEDIUM
**Phase**: 6
**Dependencies**: NEXUS-017, NEXUS-022
**Effort**: 3 days
**Risk**: high

### Description
Implement Hand scheduler for autonomous scheduled tasks.

### Acceptance Criteria
- [ ] Cron-based scheduling
- [ ] Hand definition in configuration
- [ ] Hand execution with agent
- [ ] Hand result storage
- [ ] Hand status tracking
- [ ] Error handling and retry
- [ ] Manual hand triggering

### Implementation Notes
- Implement `HandScheduler` class
- Use `apscheduler` or custom implementation
- Store hand definitions in SQLite

### Files to Create
- `nexus/hands/scheduler.py` - Scheduler implementation
- `nexus/hands/hand.py` - Hand definition
- `nexus/hands/executor.py` - Hand execution
- `tests/unit/hands/test_scheduler.py` - Unit tests

---

## NEXUS-046: Hand Checkpoint Integration

**Category**: scheduler
**Priority**: P1-MEDIUM
**Phase**: 6
**Dependencies**: NEXUS-022, NEXUS-045
**Effort**: 1.5 days
**Risk**: medium

### Description
Integrate checkpointing with Hands for long-running autonomous tasks.

### Acceptance Criteria
- [ ] Automatic checkpoint before hand execution
- [ ] Recovery from checkpoint on failure
- [ ] Hand state persistence
- [ ] Checkpoint verification on hand start
- [ ] Resume from checkpoint capability

### Implementation Notes
- Build on NEXUS-022 and NEXUS-045
- Implement `HandCheckpointManager` class

### Files to Create
- `nexus/hands/checkpoint_integration.py` - Integration
- `tests/unit/hands/test_checkpoint_integration.py` - Tests

---

## NEXUS-047: REST API Channel

**Category**: adapter
**Priority**: P1-MEDIUM
**Phase**: 6
**Dependencies**: NEXUS-017, NEXUS-034
**Effort**: 2 days
**Risk**: medium

### Description
Implement REST API channel for external integration.

### Acceptance Criteria
- [ ] FastAPI-based REST server
- [ ] Authentication middleware (JWT)
- [ ] Agent execution endpoint
- [ ] Status/query endpoints
- [ ] WebSocket for streaming
- [ ] OpenAPI documentation
- [ ] Rate limiting integration

### Implementation Notes
- Use `fastapi` for REST framework
- Implement `RESTChannelAdapter`
- Add CORS support

### Files to Create
- `nexus/adapters/channels/rest_adapter.py` - REST implementation
- `nexus/adapters/channels/__init__.py` - Exports
- `tests/unit/adapters/channels/test_rest.py` - Unit tests

---

## NEXUS-048: Monitoring Endpoints

**Category**: core
**Priority**: P2-LOW
**Phase**: 6
**Dependencies**: NEXUS-047
**Effort**: 1 day
**Risk**: low

### Description
Implement monitoring and health endpoints.

### Acceptance Criteria
- [ ] Health check endpoint
- [ ] Metrics endpoint (Prometheus format)
- [ ] Statistics endpoint
- [ ] Budget status endpoint
- [ ] Agent status endpoint

### Implementation Notes
- Add to REST API channel
- Use Prometheus metrics format
- Implement `/health`, `/metrics`, `/stats`

### Files to Create
- `nexus/adapters/channels/monitoring.py` - Monitoring endpoints
- `tests/unit/adapters/channels/test_monitoring.py` - Tests

---

## NEXUS-049: Audit Dashboard (Basic)

**Category**: cli
**Priority**: P2-LOW
**Phase**: 6
**Dependencies**: NEXUS-032, NEXUS-047
**Effort**: 1.5 days
**Risk**: low

### Description
Basic audit dashboard for viewing logs and events.

### Acceptance Criteria
- [ ] Audit log viewer
- [ ] Event filtering
- [ ] Export functionality
- [ ] Basic statistics display

### Implementation Notes
- CLI-based dashboard using `rich`
- Optionally add web dashboard endpoint

### Files to Create
- `nexus/cli/commands/audit.py` - Audit CLI command
- `tests/unit/cli/test_audit.py` - Tests

---

## NEXUS-050: End-to-End Testing

**Category**: core
**Priority**: P0-CRITICAL
**Phase**: 6
**Dependencies**: All components
**Effort**: 3 days
**Risk**: high

### Description
Comprehensive end-to-end testing across all components.

### Acceptance Criteria
- [ ] Full agent workflow test
- [ ] Provider switching test
- [ ] Multi-agent delegation test
- [ ] Hand scheduling test
- [ ] Security layer test
- [ ] Recovery from failure test
- [ ] Performance benchmarks met

### Implementation Notes
- Use `pytest` for test framework
- Create test fixtures for each scenario
- Measure against success criteria

### Files to Create
- `tests/e2e/test_full_workflow.py` - E2E tests
- `tests/e2e/test_performance.py` - Performance tests
- `tests/e2e/conftest.py` - E2E fixtures

---

## NEXUS-051: Documentation Completion

**Category**: docs
**Priority**: P0-CRITICAL
**Phase**: 6
**Dependencies**: All components
**Effort**: 3 days
**Risk**: low

### Description
Complete all required documentation.

### Acceptance Criteria
- [ ] README.md complete
- [ ] Quick Start guide
- [ ] Configuration guide
- [ ] Provider setup guide
- [ ] Security guide
- [ ] API reference
- [ ] All ADRs written
- [ ] Examples directory populated

### Implementation Notes
- Use MkDocs or Sphinx for docs
- Generate API docs from docstrings
- Include code examples

### Files to Create
- `README.md` - Main readme
- `docs/quick-start.md` - Quick start
- `docs/config.md` - Configuration
- `docs/providers.md` - Provider setup
- `docs/security/` - Security docs
- `docs/api/` - API reference
- `docs/adr/` - Architecture Decision Records
- `examples/` - Code examples

---

---

## Phase Breakdown (12 Weeks)

### Phase 1: Foundation (Week 1-2)

**Focus:** Core infrastructure and LLM adapters

| Week | Tasks | Deliverables |
|------|-------|-------------|
| 1 | NEXUS-001, NEXUS-002, NEXUS-003, NEXUS-009 | Project structure, DI container, Port protocols, CLI skeleton |
| 2 | NEXUS-004, NEXUS-005, NEXUS-006, NEXUS-007, NEXUS-008, NEXUS-010 | All LLM adapters, SQLite adapter, Docker sandbox |

**Exit Criteria:**
- [ ] DI container functional with auto-wiring
- [ ] All Port protocols defined
- [ ] OpenAI, OpenAI-Compatible, Ollama adapters working
- [ ] SQLite memory adapter functional
- [ ] Docker sandbox executing skills safely
- [ ] `nexus init` creates working configuration

### Phase 2: Built-In Efficiency (Week 3-4)

**Focus:** Token optimization and cost control

| Week | Tasks | Deliverables |
|------|-------|-------------|
| 3 | NEXUS-011, NEXUS-012, NEXUS-013, NEXUS-015 | Prompt caching, rate limiters, TOON compression |
| 4 | NEXUS-014, NEXUS-016 | Budget enforcement, unified statistics |

**Exit Criteria:**
- [ ] Prompt caching reducing tokens by measurable amount
- [ ] Rate limiting preventing API throttling
- [ ] Budget enforcement stopping at limits
- [ ] TOON compression achieving ~40% reduction
- [ ] Unified statistics dashboard available

### Phase 3: Core Agent (Week 5-6)

**Focus:** Agent execution and state management

| Week | Tasks | Deliverables |
|------|-------|-------------|
| 5 | NEXUS-017, NEXUS-018, NEXUS-019 | Agent loop, memory manager, tool registry |
| 6 | NEXUS-020, NEXUS-021, NEXUS-022, NEXUS-023, NEXUS-024 | Prompt assembly, SKILL parser, checkpointing, ACL, provider switch tests |

**Exit Criteria:**
- [ ] Agent loop executing multi-turn conversations
- [ ] Memory persisting across sessions
- [ ] Tools registered and executing
- [ ] SKILL.md files loading correctly
- [ ] Checkpointing saving and restoring state
- [ ] Provider switching zero-glitch verified

### Phase 4: Multimodal & Security (Week 7-8)

**Focus:** Media processing and security layers

| Week | Tasks | Deliverables |
|------|-------|-------------|
| 7 | NEXUS-025, NEXUS-026, NEXUS-027, NEXUS-028, NEXUS-029, NEXUS-030 | Multimodal adapters, input validation, enhanced sandbox |
| 8 | NEXUS-031 through NEXUS-039 | All 16 security layers, Vault adapter, security integration tests |

**Exit Criteria:**
- [ ] Vision adapter normalizing images across providers
- [ ] PDF and audio processing functional
- [ ] All 16 security layers implemented
- [ ] Security integration tests passing
- [ ] No critical/high security vulnerabilities

### Phase 5: Multi-Agent & Persistence (Week 9-10)

**Focus:** Agent hierarchy and advanced persistence

| Week | Tasks | Deliverables |
|------|-------|-------------|
| 9 | NEXUS-040, NEXUS-041 | Multi-agent hierarchy, state persistence |
| 10 | NEXUS-042, NEXUS-043, NEXUS-044 | Knowledge graph, semantic search, integration tests |

**Exit Criteria:**
- [ ] Superior agents delegating to subordinates
- [ ] State persisting correctly across agents
- [ ] Knowledge graph storing entities/relationships
- [ ] Semantic search finding relevant memories
- [ ] Multi-agent integration tests passing

### Phase 6: Autonomous Features (Week 11-12)

**Focus:** Scheduling and production readiness

| Week | Tasks | Deliverables |
|------|-------|-------------|
| 11 | NEXUS-045, NEXUS-046, NEXUS-047 | Hand scheduler, checkpoint integration, REST API |
| 12 | NEXUS-048, NEXUS-049, NEXUS-050, NEXUS-051 | Monitoring, audit dashboard, E2E tests, documentation |

**Exit Criteria:**
- [ ] Hands executing on schedule
- [ ] REST API serving requests
- [ ] Monitoring endpoints functional
- [ ] E2E tests all passing
- [ ] Documentation complete
- [ ] MVP ready for release

---

## Sprint Milestones

### Sprint 1 (Week 1-2): Foundation Complete
**Demoable Features:**
- `nexus init` creates working project
- Basic agent responds via CLI
- OpenAI and Ollama providers working

**Sprint Review Checklist:**
- [ ] DI container passes all tests
- [ ] Port protocols validated
- [ ] At least 2 LLM adapters working
- [ ] CLI init command functional

### Sprint 2 (Week 3-4): Efficiency Operational
**Demoable Features:**
- Prompt caching reducing token usage
- Budget enforcement stopping at $limit
- Rate limiting protecting APIs

**Sprint Review Checklist:**
- [ ] Cache hit rate >30%
- [ ] Budget enforcement verified
- [ ] Rate limiter preventing 429s
- [ ] TOON compression working

### Sprint 3 (Week 5-6): Agent Functional
**Demoable Features:**
- Agent executing multi-turn conversations
- Tools being called correctly
- Memory persisting
- Provider switching seamless

**Sprint Review Checklist:**
- [ ] Agent loop stable
- [ ] Tools executing in sandbox
- [ ] Checkpoint/restore working
- [ ] Zero provider switch errors

### Sprint 4 (Week 7-8): Secure & Multimodal
**Demoable Features:**
- Vision input working across providers
- PDF text extraction
- All security layers active

**Sprint Review Checklist:**
- [ ] Vision adapter normalized
- [ ] Security tests all passing
- [ ] No critical vulnerabilities
- [ ] Vault integration optional

### Sprint 5 (Week 9-10): Multi-Agent Ready
**Demoable Features:**
- Superior delegating to subordinate
- Knowledge graph populated
- Semantic search returning results

**Sprint Review Checklist:**
- [ ] Delegation working
- [ ] State isolated between agents
- [ ] Knowledge graph queryable
- [ ] Semantic search functional

### Sprint 6 (Week 11-12): Production Ready
**Demoable Features:**
- Scheduled Hands executing
- REST API serving requests
- Full E2E workflow
- Complete documentation

**Sprint Review Checklist:**
- [ ] Hands running on schedule
- [ ] REST API documented
- [ ] E2E tests passing
- [ ] Docs published
- [ ] MVP release ready

---

## Risk Register

### Technical Risks

| ID | Risk | Probability | Impact | Mitigation | Owner |
|----|------|-------------|--------|------------|-------|
| TR-001 | Provider API breaking changes | High | Critical | API version negotiation, pin versions, fallback adapters | LLM Lead |
| TR-002 | Docker sandbox escape | Low | Critical | seccomp profiles, regular audits, minimal container | Security Lead |
| TR-003 | SQLite write contention under load | Medium | High | WAL mode, connection pooling, consider Postgres for scale | Backend Lead |
| TR-004 | Ollama version incompatibility | Medium | High | Version detection, compatibility matrix, graceful errors | Integration Lead |
| TR-005 | TOON parsing edge cases | Medium | Low | Comprehensive test suite, spec validation | Core Lead |
| TR-006 | DI container complexity | Medium | Medium | Good documentation, examples, gradual adoption | Architect |
| TR-007 | Vault connectivity issues | Medium | Medium | Fallback to env vars, health checks, retry logic | Security Lead |
| TR-008 | Memory leaks in long-running agents | Medium | High | Memory profiling, checkpoint restart, monitoring | Backend Lead |
| TR-009 | Race conditions in async code | Medium | High | Thread safety audit, comprehensive async tests | Backend Lead |
| TR-010 | Provider-specific multimodal quirks | High | Medium | Provider normalization layer, extensive testing | Integration Lead |

### Dependency Risks

| ID | Risk | Probability | Impact | Mitigation | Owner |
|----|------|-------------|--------|------------|-------|
| DR-001 | OpenAI SDK breaking changes | Medium | High | Pin SDK version, monitor changelog | LLM Lead |
| DR-002 | Docker API changes | Low | Medium | Use stable API version, container pin | DevOps Lead |
| DR-003 | Python version compatibility | Low | Medium | Test on 3.11+, clear version requirements | Core Lead |
| DR-004 | Key dependency security CVE | Medium | High | Automated dependency scanning, pin hashes | Security Lead |
| DR-005 | Vault Helm chart issues | Low | Medium | Test in staging, maintain alternative config | DevOps Lead |

### Resource Risks

| ID | Risk | Probability | Impact | Mitigation | Owner |
|----|------|-------------|--------|------------|-------|
| RR-001 | Key developer unavailable | Medium | High | Knowledge sharing, documentation, pair programming | PM |
| RR-002 | Scope creep from stakeholders | High | Medium | Strict MVP definition, change control process | PM |
| RR-003 | Testing environment unavailable | Low | Medium | Local development setup, cloud backup | DevOps Lead |
| RR-004 | Budget overrun (API costs) | Medium | Medium | Budget enforcement, cost monitoring, alerts | PM |

### Market Risks

| ID | Risk | Probability | Impact | Mitigation | Owner |
|----|------|-------------|--------|------------|-------|
| MR-001 | LangChain ecosystem dominance | High | High | Zero-glitch differentiation, local-first focus | Product Lead |
| MR-002 | OpenAI releases built-in agents | Medium | Critical | Provider-agnostic positioning, unique features | Product Lead |
| MR-003 | Enterprise compliance barriers | High | High | Security layer implementation, compliance APIs | Security Lead |
| MR-004 | Developer adoption friction | Medium | Medium | Invest in DX, docs, examples, quick start | Developer Advocacy |

---

## Testing Requirements

### Unit Test Requirements

| Component | Coverage Target | Key Test Areas |
|-----------|-----------------|----------------|
| DI Container | >95% | Registration, resolution, auto-wiring, circular detection |
| Port Protocols | >90% | Protocol compliance, type validation |
| LLM Adapters | >90% | Request building, response parsing, error handling |
| Memory Adapter | >90% | CRUD operations, WAL mode, pooling |
| Efficiency Layer | >90% | Caching, rate limiting, budget, compression |
| Agent Core | >90% | Loop execution, tool calling, error recovery |
| Security Layers | >95% | All 16 layers, attack vectors, compliance |
| Multimodal | >85% | Format conversion, size limits, provider adaptation |
| Hands Scheduler | >85% | Scheduling, execution, checkpoint integration |

### Integration Test Scenarios

| Scenario | Components | Verification |
|----------|------------|-------------|
| Full agent workflow | Agent + LLM + Memory + Tools | End-to-end conversation with tool calls |
| Provider switch | All LLM adapters | Switch provider mid-conversation, verify behavior |
| Security attack | All security layers | Simulate common attacks, verify blocking |
| Multimodal processing | Vision + LLM adapters | Process image with multiple providers |
| Rate limit handling | Rate limiter + LLM adapters | Verify backoff and retry on 429 |
| Budget enforcement | Budget + LLM adapters | Verify hard stop at budget limit |
| Multi-agent delegation | Hierarchy + Agents | Verify delegation and result aggregation |
| Hand execution | Scheduler + Agent + Checkpoint | Verify scheduled task execution |
| Checkpoint recovery | Checkpoint + Agent | Kill agent, restore from checkpoint |
| Concurrent access | Memory + SQLite | Multiple agents accessing memory |

### E2E Test Flows

| Flow | Steps | Duration |
|------|-------|----------|
| New user onboarding | Install → Init → First conversation | <5 minutes |
| Provider migration | OpenAI → Ollama → Anthropic | <10 seconds per switch |
| Long-running task | Start → Checkpoint → Kill → Restore | Full recovery |
| Autonomous hand | Schedule → Execute → Verify → Alert | Complete cycle |
| Security incident | Attack → Detect → Alert → Isolate → Recover | Full incident response |

### Performance Benchmarks

| Benchmark | Target | Measurement Method |
|-----------|--------|-------------------|
| Cold start | <500ms | Time from launch to ready |
| Provider switch | <100ms | Time to switch and make request |
| Memory operation | <50ms | Average read/write latency |
| Checkpoint restore | <1s | Time to restore full state |
| Multimodal overhead | <200ms | Additional latency for image processing |
| Rate limit overhead | <5ms | Latency added by rate limiting |
| Budget check overhead | <1ms | Latency added by budget check |

### Security Test Requirements

| Test Type | Tools | Coverage |
|-----------|-------|----------|
| Static analysis | bandit, safety | All Python code |
| Dependency audit | pip-audit, safety | All dependencies |
| Container scan | Trivy, Grype | Docker images |
| Penetration testing | Custom scripts | All endpoints |
| Fuzzing | Hypothesis, AFL | Input validation, parsing |

---

## Documentation Checklist

### API Documentation

| Document | Location | Status | Owner |
|----------|----------|--------|-------|
| Port protocols reference | `docs/api/ports.md` | Required | Architect |
| DI container API | `docs/api/container.md` | Required | Core Lead |
| LLM adapter interface | `docs/api/llm.md` | Required | LLM Lead |
| Memory adapter interface | `docs/api/memory.md` | Required | Backend Lead |
| Security API | `docs/api/security.md` | Required | Security Lead |
| REST API spec | `docs/api/rest.md` | Required | API Lead |
| CLI commands | `docs/api/cli.md` | Required | CLI Lead |

### User Guides

| Document | Location | Status | Owner |
|----------|----------|--------|-------|
| Quick Start | `docs/quick-start.md` | Required | Developer Advocacy |
| Configuration Guide | `docs/config.md` | Required | Core Lead |
| Provider Setup | `docs/providers.md` | Required | Integration Lead |
| Security Guide | `docs/security/guide.md` | Required | Security Lead |
| Multimodal Guide | `docs/multimodal.md` | Required | Integration Lead |
| Migration Guides | `docs/migration/` | Required | Integration Lead |
| Hands/Scheduler Guide | `docs/hands.md` | Required | Scheduler Lead |

### Architecture Decision Records

| ADR | Title | Status | Location |
|-----|-------|--------|----------|
| ADR-001 | SQLite as Default Database | Accepted | `docs/adr/001-sqlite-default.md` |
| ADR-002 | Dependency Injection Container | Accepted | `docs/adr/002-di-container.md` |
| ADR-003 | Built-In Efficiency (Not Skills) | Accepted | `docs/adr/003-built-in-efficiency.md` |
| ADR-004 | Docker for Skill Sandboxing | Accepted | `docs/adr/004-docker-sandbox.md` |
| ADR-005 | TOON for Context Compression | Accepted | `docs/adr/005-toon-compression.md` |
| ADR-006 | 12-Week MVP Timeline | Accepted | `docs/adr/006-12-week-timeline.md` |
| ADR-007 | Zero-Glitch Provider Abstraction | Required | `docs/adr/007-zero-glitch.md` |
| ADR-008 | Multimodal Normalization Layer | Required | `docs/adr/008-multimodal-layer.md` |
| ADR-009 | 16 Security Layers | Required | `docs/adr/009-security-layers.md` |
| ADR-010 | Agent Checkpointing | Required | `docs/adr/010-checkpointing.md` |

### Examples

| Example | Location | Purpose |
|---------|----------|---------|
| Basic agent | `examples/basic_agent.py` | Minimal agent setup |
| Multi-provider | `examples/multi_provider.py` | Provider switching demo |
| Custom tool | `examples/custom_tool.py` | Tool creation guide |
| Skill definition | `examples/custom_skill/` | SKILL.md example |
| Multimodal agent | `examples/multimodal_agent.py` | Vision/audio handling |
| Scheduled hand | `examples/scheduled_hand.py` | Autonomous task example |
| Multi-agent | `examples/multi_agent.py` | Delegation example |
| REST server | `examples/rest_server.py` | API integration example |

### Code Documentation Standards

- All modules have `__doc__` strings
- All public classes have docstrings
- All public methods have docstrings with:
  - Brief description
  - Args section with types
  - Returns section with type
  - Raises section if applicable
  - Example usage (for key methods)
- Type hints on all function signatures
- Inline comments for complex logic

---

## Dependency Graph

```
NEXUS-001 (Project Structure)
├── NEXUS-002 (DI Container)
│   ├── NEXUS-003 (Port Protocols)
│   │   ├── NEXUS-004 (OpenAI Adapter)
│   │   │   ├── NEXUS-005 (OpenAI-Compatible)
│   │   │   └── NEXUS-007 (Anthropic)
│   │   ├── NEXUS-006 (Ollama Adapter)
│   │   ├── NEXUS-008 (SQLite Adapter)
│   │   ├── NEXUS-025 (Multimodal Port)
│   │   │   ├── NEXUS-026 (Vision Adapter)
│   │   │   ├── NEXUS-027 (PDF Adapter)
│   │   │   └── NEXUS-028 (Audio Adapter)
│   │   └── NEXUS-038 (Vault Adapter)
│   └── NEXUS-019 (Tool Registry)
│       └── NEXUS-021 (SKILL Parser)
├── NEXUS-009 (CLI Skeleton)
├── NEXUS-010 (Docker Sandbox)
│   └── NEXUS-030 (Enhanced Sandbox)
├── NEXUS-011 (Prompt Caching)
│   └── NEXUS-016 (Statistics)
├── NEXUS-012 (Local Rate Limiter)
│   └── NEXUS-013 (Distributed Rate Limiter)
├── NEXUS-014 (Budget Enforcement)
│   └── NEXUS-016 (Statistics)
├── NEXUS-015 (TOON Compression)
│   ├── NEXUS-022 (Checkpointing)
│   │   └── NEXUS-046 (Hand Checkpoint)
│   └── NEXUS-041 (State Persistence)
├── NEXUS-017 (Agent Loop)
│   ├── NEXUS-018 (Memory Manager)
│   │   ├── NEXUS-042 (Knowledge Graph)
│   │   └── NEXUS-043 (Semantic Search)
│   ├── NEXUS-019 (Tool Registry)
│   ├── NEXUS-020 (Prompt Assembly)
│   └── NEXUS-022 (Checkpointing)
├── NEXUS-023 (Anti-Corruption Layer)
├── NEXUS-024 (Provider Switch Tests)
├── NEXUS-029 (Input Validation)
├── NEXUS-031 (Rate Limit Security)
├── NEXUS-032 (Audit Logging)
│   ├── NEXUS-034 (Auth/Authz)
│   ├── NEXUS-036 (Integrity)
│   └── NEXUS-049 (Audit Dashboard)
├── NEXUS-033 (Output Filtering)
├── NEXUS-035 (Encryption)
│   ├── NEXUS-036 (Integrity)
│   └── NEXUS-037 (Remaining Layers)
├── NEXUS-037 (Security Layers 11-16)
│   └── NEXUS-039 (Security Integration Tests)
├── NEXUS-040 (Multi-Agent Hierarchy)
│   ├── NEXUS-041 (State Persistence)
│   └── NEXUS-044 (Multi-Agent Tests)
├── NEXUS-045 (Hand Scheduler)
│   └── NEXUS-046 (Hand Checkpoint)
├── NEXUS-047 (REST API)
│   ├── NEXUS-048 (Monitoring)
│   └── NEXUS-049 (Audit Dashboard)
└── NEXUS-050 (E2E Tests)
    └── NEXUS-051 (Documentation)
```

---

## Appendix A: Quick Reference

### Task Count by Priority

| Priority | Count | Percentage |
|----------|-------|------------|
| P0-CRITICAL | 20 | 39% |
| P0-HIGH | 15 | 29% |
| P1-MEDIUM | 12 | 24% |
| P2-LOW | 4 | 8% |
| **Total** | **51** | **100%** |

### Task Count by Category

| Category | Count |
|----------|-------|
| core | 14 |
| adapter | 10 |
| efficiency | 6 |
| security | 11 |
| multimodal | 4 |
| scheduler | 2 |
| cli | 2 |
| docs | 1 |
| integration | 1 |

### Effort Summary

| Phase | Duration | Task Count | Total Effort |
|-------|----------|------------|--------------|
| Phase 1 | 2 weeks | 10 tasks | ~12 days |
| Phase 2 | 2 weeks | 6 tasks | ~9 days |
| Phase 3 | 2 weeks | 8 tasks | ~13 days |
| Phase 4 | 2 weeks | 11 tasks | ~14 days |
| Phase 5 | 2 weeks | 5 tasks | ~10 days |
| Phase 6 | 2 weeks | 7 tasks | ~11 days |
| **Total** | **12 weeks** | **51 tasks** | **~69 days** |

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **Port** | Protocol interface defining a contract for adapters |
| **Adapter** | Concrete implementation of a Port |
| **Hand** | Scheduled autonomous agent task |
| **Skill** | Declaratively defined capability (SKILL.md format) |
| **Channel** | Input/output interface (CLI, REST API, etc.) |
| **Dispatcher** | Central message router |
| **Efficiency Layer** | Built-in token optimization features |
| **Zero-Glitch Switching** | Identical behavior across LLM providers |
| **DI Container** | Dependency injection for adapter management |
| **ACL** | Anti-Corruption Layer for framework integration |
| **Checkpoint** | Saved agent state for recovery |
| **TOON** | Token-Oriented Object Notation for compression |
| **WAL** | Write-Ahead Logging for SQLite concurrency |

---

**Document Status:** Complete
**Last Updated:** 2026-04-09
**Next Review:** Sprint 1 Review (End of Week 2)
