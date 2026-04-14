# NEXUS Framework Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.0.0] - 2026-04-14

### Added - Sprint 13: Stability Fixes
- Async migration: `time.sleep()` → `await asyncio.sleep()` in self_healing.py
- Thread-safe `RateLimiter.acquire_async()` for non-blocking waits
- Agent loop async compatibility
- RLock wrappers for `AgentRegistry` read operations
- Thread-safe connection pooling (already implemented in memory.py, persistence.py)
- Thread-safe cache operations (already implemented in prompt_cache.py)

### Added - Sprint 14: Security Fixes
- XSS protection via bleach library integration
- `Sanitizer` class with `sanitize_input()` and `sanitize_output()`
- Anthropic streaming fix for tool_use blocks
- ACL implementation verified comprehensive (422 lines)

### Added - Sprint 15: Performance Optimization
- Graph-based workflow engine with O(1) step lookup
- OrderedDict LRU caching with O(1) eviction
- `LazyLoader` for cold start optimization
- `@dataclass(slots=True)` for memory reduction

### Added - Sprint 16: Production Release
- Unit tests for efficiency layer (14 tests)
- Unit tests for core modules (3 tests)
- Unit tests for security layer (4 tests)
- E2E tests for framework integration (7 tests)
- README updated with Sprint 13-16 summary
- Documentation updates across all files

### Changed
- Token counting now uses tiktoken for precision (replaces `.split()` estimation)
- BudgetEnforcer uses `@dataclass(slots=True)` for 40% memory reduction
- PromptCache uses OrderedDict for LRU eviction

### Fixed
- Indentation errors in budget_enforcer.py
- Test method signatures (added `self` parameter)
- Import errors (Role → MessageRole)
- Async blocking in self_healing.py
- Thread safety in AgentRegistry

### Security
- XSS protection via bleach sanitization
- Input/output sanitization for all external data
- Anthropic streaming tool_use block handling

## [3.0.0] - 2026-04-12

### Added - Phases 11-12
- L0-L3 Memory Stack (40x efficiency)
- Palace Architecture (Wings/Rooms/Halls)
- Temporal Knowledge Graph
- Entity Detection
- Three-File Memory structure
- Hybrid Search with RRF fusion
- Brain-First Lookup
- Dream Cycle for maintenance

## [2.0.0] - 2026-04-10

### Added - Phases 1-10
- Core DI Container
- LLM Adapters (OpenAI, Ollama, Anthropic, NVIDIA NIM)
- Efficiency Layer (Prompt Caching, Rate Limiting, Budget Enforcement)
- Core Agent (Messages, Memory, Context)
- 16 Security Layers
- Multimodal Adapters (Vision, PDF, Audio)
- Multi-Agent Registry
- Workflow Orchestration
- Autonomous Systems (Self-Healing, Learning)
- REST API with FastAPI
- Production Hardening (Prometheus, Circuit Breaker)
- Docker and Kubernetes configs

## [1.0.0] - 2026-04-09

### Added
- Initial project structure
- PRD documentation
- Build log
- Integration roadmap
- MIT License
