# NEXUS Framework - Final Development Plan

**Version:** 4.0.0 (State-of-the-Art Edition)
**Created:** 2026-04-12
**Status:** 🎯 Ready for Execution
**Timeline:** 16 Weeks (4 Sprints × 4 Weeks)

---

## Executive Summary

This document merges ALL existing NEXUS documentation into a single, authoritative development plan that will transform NEXUS into the definitive state-of-the-art AI agent framework. It consolidates:

| Source Document | Lines | Key Insights |
|-----------------|-------|-------------|
| **NEXUS_PRD.md** | 1655 | Product requirements, architecture, security layers |
| **NEXUS_BUILD_LOG.md** | 467 | Completed phases 1-15, integration history |
| **NEXUS_INTEGRATION_ROADMAP.md** | 613 | 7 trending repos integrated (Phases 11-15) |
| **CODE_REVIEW_REPORT.md** | 63 | 6 critical issues identified |
| **ENGINEERING_SPECS.md** | 84 | 8 engineering fixes specified |

---

## 🚨 Critical Issues to Address First

Based on CODE_REVIEW_REPORT.md, these issues MUST be fixed before production:

| # | Issue | Severity | Impact | Fix Complexity |
|---|-------|----------|--------|----------------|
| 1 | **Async Loop Blocking** | 🔴 Critical | `time.sleep()` freezes entire system | Low |
| 2 | **Thread Safety** | 🟡 High | Race conditions under load | Low |
| 3 | **Inaccurate Tokenizing** | 🟡 High | Budget/context overflow | Medium |
| 4 | **Weak XSS Protection** | 🟡 High | Security bypass | Low |
| 5 | **Anthropic Stream Bug** | 🟡 High | Tool calls dropped | Medium |
| 6 | ~~Missing ACL~~ | ✅ False Alarm | `acl.py` EXISTS | N/A |

---

## 📋 Complete Feature Matrix

### Phase 1-10: Core Framework (COMPLETE ✅)

| Phase | Components | Status |
|-------|------------|--------|
| **1** | DI Container, Ports, LLM Adapters, Config, CLI | ✅ |
| **2** | PromptCache, RateLimiter, BudgetEnforcer | ✅ |
| **3** | Message, MemoryManager, AgentContext | ✅ |
| **4** | SecurityManager (16 layers), Multimodal Adapters | ✅ |
| **5** | AgentRegistry, MessageBus, Persistence, Workflow | ✅ |
| **6** | HealthMonitor, SelfHealing, TaskScheduler, Learning | ✅ |
| **7** | AgentLoop, ToolRegistry, SKILL.md Parser, DockerSandbox, ACL | ✅ |
| **8** | Prometheus Metrics, Circuit Breaker, Docker, Kubernetes | ✅ |
| **9** | Channels (CLI, Telegram, Discord), Dispatcher | ✅ |
| **10** | TOON Compression, Event Sourcing, Plugin System | ✅ |
| **P1** | Knowledge Graph, Semantic Search, REST API, Distributed Rate Limiting | ✅ |

### Phase 11-15: Integration Features (COMPLETE ✅)

| Phase | Components | Source | Status |
|-------|------------|--------|--------|
| **11** | L0-L3 Memory Stack, Palace, Temporal KG, Entity Detection, Three-File Memory | MemPalace/GBrain | ✅ |
| **12** | Hybrid Search, RRF Fusion, Brain-First Lookup, Dream Cycle | GBrain | ✅ |
| **13** | Agent Templates, Heartbeat, Task Queue, Daemon Polling, Unified Backend | Cabinet/Multica | ✅ |
| **14** | Goal-Driven Execution, Surgical Changes, Ambiguity Detection, Diff Gates | Karpathy-Skills | ✅ |
| **15** | OpenTUI Bridge, Dashboard, Setup Wizard TUI, Real-time Monitoring, AI Automation | OpenTUI | ✅ |

### Phase 16-19: Critical Fixes (NEW - REQUIRED)

| Phase | Components | Priority | Status |
|-------|------------|----------|--------|
| **16** | Async Migration, Thread Safety, Precision Tokenization | 🔴 P0 | 📋 Pending |
| **17** | Input Sanitization, Anthropic Stream Fix, ACL Enhancement | 🟡 P1 | 📋 Pending |
| **18** | Graph-Based Workflows, Algorithmic Refinement | 🟢 P2 | 📋 Pending |
| **19** | Test Coverage, Documentation, Production Hardening | 🟢 P2 | 📋 Pending |

---

## 🎯 Sprint Plan (16 Weeks)

### Sprint 1: Stability Fixes (Weeks 1-4)

#### Week 1: Async Migration

| Task | File | Change | Effort |
|------|------|--------|--------|
| 16.1 | `nexus/autonomous/self_healing.py` | Convert to async, `await asyncio.sleep()` | 2h |
| 16.2 | `nexus/efficiency/rate_limiter.py` | Convert `acquire()` to async | 2h |
| 16.3 | `nexus/core/agent.py` | Ensure agent loop is async-compatible | 2h |
| 16.4 | `tests/unit/test_async.py` | Add async tests | 2h |

#### Week 2: Thread Safety

| Task | File | Change | Effort |
|------|------|--------|--------|
| 17.1 | `nexus/multiagent/registry.py` | Add `RLock` to all read methods | 2h |
| 17.2 | `nexus/memory/memory.py` | Add thread-safe connection pooling | 2h |
| 17.3 | `nexus/efficiency/prompt_cache.py` | Add thread-safe cache operations | 2h |
| 17.4 | `tests/unit/test_thread_safety.py` | Add concurrent access tests | 2h |

#### Week 3: Precision Tokenization

| Task | File | Change | Effort |
|------|------|--------|--------|
| 18.1 | `nexus/utils/tokenizer.py` | Create `Tokenizer` class with `tiktoken` | 3h |
| 18.2 | `nexus/core/context.py` | Replace `.split()` with tokenizer | 2h |
| 18.3 | `nexus/adapters/llm/base.py` | Add token counting to base adapter | 2h |
| 18.4 | `nexus/efficiency/budget_enforcer.py` | Use accurate token counting | 2h |

#### Week 4: Integration Testing

| Task | Description | Effort |
|------|-------------|--------|
| 19.1 | Run full test suite with fixes | 2h |
| 19.2 | Performance benchmarking | 2h |
| 19.3 | Fix any regressions | 4h |
| 19.4 | Sprint 1 documentation update | 2h |

---

### Sprint 2: Security & Quality (Weeks 5-8)

#### Week 5: Input Sanitization

| Task | File | Change | Effort |
|------|------|--------|--------|
| 20.1 | `nexus/security/sanitization.py` | Create `BleachSanitizer` class | 3h |
| 20.2 | `nexus/security/security_manager.py` | Replace regex with bleach | 2h |
| 20.3 | `nexus/security/input_validation.py` | Update validation layer | 2h |
| 20.4 | `tests/security/test_sanitization.py` | Add XSS bypass tests | 2h |

#### Week 6: Anthropic Stream Fix

| Task | File | Change | Effort |
|------|------|--------|--------|
| 21.1 | `nexus/adapters/llm/anthropic.py` | Handle `tool_use` blocks in stream | 3h |
| 21.2 | `nexus/core/messages.py` | Add `StreamChunk` with `tool_call` | 2h |
| 21.3 | `tests/adapters/test_anthropic_stream.py` | Add streaming tool tests | 2h |
| 21.4 | Integration test with Claude | 2h |

#### Week 7: ACL Enhancement

| Task | File | Change | Effort |
|------|------|--------|--------|
| 22.1 | `nexus/acl/acl.py` | Add resource-level permissions | 3h |
| 22.2 | `nexus/acl/decorators.py` | Create `@require_permission` decorator | 2h |
| 22.3 | `nexus/security/authorization.py` | Integrate ACL with security layers | 2h |
| 22.4 | `tests/acl/test_permissions.py` | Add permission tests | 2h |

#### Week 8: Security Audit

| Task | Description | Effort |
|------|-------------|--------|
| 23.1 | Run security audit tools | 2h |
| 23.2 | Fix identified vulnerabilities | 4h |
| 23.3 | Update security documentation | 2h |
| 23.4 | Sprint 2 documentation update | 2h |

---

### Sprint 3: Performance Optimization (Weeks 9-12)

#### Week 9: Graph-Based Workflows

| Task | File | Change | Effort |
|------|------|--------|--------|
| 24.1 | `nexus/multiagent/workflow.py` | Implement adjacency list DAG | 4h |
| 24.2 | `nexus/multiagent/workflow.py` | Add `pending_dependencies_count` | 2h |
| 24.3 | `tests/multiagent/test_workflow_perf.py` | Add O(1) trigger tests | 2h |
| 24.4 | Benchmark workflow performance | 2h |

#### Week 10: Algorithmic Refinement

| Task | File | Change | Effort |
|------|------|--------|--------|
| 25.1 | `nexus/autonomous/learning.py` | Use `bisect` for rule sorting | 2h |
| 25.2 | `nexus/efficiency/prompt_cache.py` | Use `OrderedDict` for LRU | 2h |
| 25.3 | `nexus/orchestration/task_queue.py` | Use `PriorityQueue` | 2h |
| 25.4 | Performance benchmarking | 2h |

#### Week 11: Memory Optimization

| Task | File | Change | Effort |
|------|------|--------|--------|
| 26.1 | `nexus/memory/stack.py` | Optimize L0-L3 access patterns | 3h |
| 26.2 | `nexus/memory/palace.py` | Add search indexing | 2h |
| 26.3 | `nexus/search/hybrid.py` | Optimize RRF fusion | 2h |
| 26.4 | Memory benchmarking | 2h |

#### Week 12: Caching Optimization

| Task | Description | Effort |
|------|-------------|--------|
| 27.1 | Implement distributed caching | 3h |
| 27.2 | Add cache warming strategies | 2h |
| 27.3 | Cache hit rate optimization | 2h |
| 27.4 | Sprint 3 documentation update | 2h |

---

### Sprint 4: Production Readiness (Weeks 13-16)

#### Week 13: Test Coverage

| Task | Description | Target | Effort |
|------|-------------|--------|--------|
| 28.1 | Unit tests for all modules | >90% coverage | 8h |
| 28.2 | Integration tests | All adapters | 4h |
| 28.3 | E2E tests | Full workflow | 4h |
| 28.4 | Security tests | All 16 layers | 4h |

#### Week 14: Documentation

| Task | Description | Effort |
|------|-------------|--------|
| 29.1 | API reference documentation | 4h |
| 29.2 | Architecture diagrams | 2h |
| 29.3 | Getting started guide | 2h |
| 29.4 | Example projects | 4h |

#### Week 15: Deployment

| Task | Description | Effort |
|------|-------------|--------|
| 30.1 | Docker optimization | 2h |
| 30.2 | Kubernetes manifests | 2h |
| 30.3 | CI/CD pipeline | 2h |
| 30.4 | Monitoring setup | 2h |

#### Week 16: Release

| Task | Description | Effort |
|------|-------------|--------|
| 31.1 | PyPI package preparation | 2h |
| 31.2 | Version 4.0.0 release | 2h |
| 31.3 | Community files (CONTRIBUTING, etc.) | 2h |
| 31.4 | Final documentation update | 2h |

---

## 📊 Success Metrics

| Metric | Current | Target | Sprint |
|--------|---------|--------|--------|
| **Test Coverage** | ~40% | >90% | Sprint 4 |
| **Security Vulnerabilities** | 5 issues | 0 critical/high | Sprint 2 |
| **Async Compatibility** | ❌ Blocking | ✅ Non-blocking | Sprint 1 |
| **Thread Safety** | ❌ Race conditions | ✅ Fully safe | Sprint 1 |
| **Token Accuracy** | ~70% | >99% | Sprint 1 |
| **Workflow Complexity** | O(N²) | O(1) triggers | Sprint 3 |
| **Cache Eviction** | O(N) | O(1) LRU | Sprint 3 |
| **Cold Start Time** | ~500ms | <200ms | Sprint 3 |
| **Memory Footprint** | ~100MB | <50MB | Sprint 3 |
| **Documentation** | Partial | Complete | Sprint 4 |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ NEXUS FRAMEWORK v4.0 - STATE-OF-THE-ART ARCHITECTURE │
├─────────────────────────────────────────────────────────────────────────────┤
│ │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ PRESENTATION LAYER │ │
│ │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │ │
│ │ │ OpenTUI CLI │ │ REST API │ │ Channels │ │ Dashboard │ │ │
│ │ │ (Phase 15) │ │ (Phase P1) │ │ (Phase 9) │ │ (Phase 15) │ │ │
│ │ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│ │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ ORCHESTRATION LAYER │ │
│ │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │ │
│ │ │ Task Queue │ │ Heartbeat │ │ Agent Router │ │ Session Manager │ │ │
│ │ │ (Phase 13) │ │ (Phase 13) │ │ (Phase 5) │ │ (Phase 9) │ │ │
│ │ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│ │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ BEHAVIOR & QUALITY LAYER (NEW) │ │
│ │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │ │
│ │ │ Goal-Driven │ │ Surgical │ │ Ambiguity │ │ Diff Quality │ │ │
│ │ │ Execution │ │ Changes │ │ Detection │ │ Gates │ │ │
│ │ │ (Phase 14) │ │ (Phase 14) │ │ (Phase 14) │ │ (Phase 14) │ │ │
│ │ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│ │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ MEMORY LAYER (ADVANCED) │ │
│ │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │ │
│ │ │ L0-L3 Stack │ │ Palace │ │ Entity │ │ Temporal KG │ │ │
│ │ │ (Phase 11) │ │ (Phase 11) │ │ Detection │ │ (Phase 11) │ │ │
│ │ │ │ │ │ │ (Phase 11) │ │ │ │ │
│ │ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘ │ │
│ │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │ │
│ │ │ Hybrid Search│ │ Brain-First │ │ Three-File │ │ Dream Cycle │ │ │
│ │ │ (Phase 12) │ │ Lookup │ │ Memory │ │ (Phase 12) │ │ │
│ │ │ │ │ (Phase 12) │ │ (Phase 11) │ │ │ │ │
│ │ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│ │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ EFFICIENCY LAYER (OPTIMIZED) │ │
│ │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │ │
│ │ │ Prompt Cache │ │ Rate Limiter │ │ Budget │ │ Token Tracker │ │ │
│ │ │ (O(1) LRU) │ │ (Async) │ │ Enforcer │ │ (tiktoken) │ │ │
│ │ │ Sprint 3 │ │ Sprint 1 │ │ Sprint 1 │ │ Sprint 1 │ │ │
│ │ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│ │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ SECURITY LAYER (16 LAYERS + ENHANCED) │ │
│ │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │ │
│ │ │ Bleach │ │ ACL │ │ Thread-Safe │ │ Input │ │ │
│ │ │ Sanitization │ │ Enhancement │ │ Registry │ │ Validation │ │ │
│ │ │ Sprint 2 │ │ Sprint 2 │ │ Sprint 1 │ │ Sprint 2 │ │ │
│ │ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│ │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ PORTS & ADAPTERS LAYER │ │
│ │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │ │
│ │ │ LLMPort │ │ MemoryPort │ │ MultimodalPort│ │ KnowledgePort │ │ │
│ │ │ (6 providers)│ │ (SQLite+) │ │ (Vision+) │ │ (Graph+Vector) │ │ │
│ │ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│ │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ DI CONTAINER (Phase 1) │ │
│ │ Adapter Registry │ Configuration Binding │ Lifecycle Management │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure (Final State)

```
nexus/
├── core/ # Agent loop, memory, context, tools
├── memory/ # Phase 11: L0-L3 Stack, Palace, Temporal KG
├── search/ # Phase 12: Hybrid Search, RRF, Brain-First
├── orchestration/ # Phase 13: Templates, Heartbeat, Task Queue
├── behavior/ # Phase 14: Goal-Driven, Surgical, Ambiguity
├── efficiency/ # Optimized caching, rate limiting, budget
├── security/ # 16 layers + enhanced sanitization
├── multiagent/ # Registry, messaging, workflow (DAG)
├── autonomous/ # Health, self-healing, learning (async)
├── channels/ # CLI, Telegram, Discord
├── dispatcher/ # Message routing, sessions
├── knowledge/ # Graph, semantic search
├── acl/ # Access control (enhanced)
├── sandbox/ # Docker-based execution
├── observability/ # Prometheus metrics
├── resilience/ # Circuit breaker, retry
├── api/ # REST API (FastAPI)
├── adapters/ # LLM & multimodal adapters
│ ├── llm/ # OpenAI, Anthropic (fixed), Ollama, NVIDIA
│ └── multimodal/ # Vision, PDF, Audio
├── cli/ # Command-line interface
│ └── tui/ # Phase 15: OpenTUI integration
├── container/ # Dependency injection
├── config/ # Configuration management
├── plugins/ # Dynamic loading
├── events/ # Event sourcing
├── compression/ # TOON compression
└── utils/ # Utilities (tokenizer, logging)
```

---

## 🔧 Dependencies

### Core Dependencies (Existing)
```
pydantic>=2.0
pyyaml>=6.0
structlog>=23.0
aiofiles>=23.0
httpx>=0.25
fastapi>=0.104
uvicorn>=0.24
prometheus-client>=0.18
```

### New Dependencies (Sprint 1-2)
```
tiktoken>=0.5.0 # Accurate tokenization
bleach>=6.1.0 # XSS sanitization
```

### Optional Dependencies
```
redis>=5.0 # Distributed rate limiting
faiss-cpu>=1.7 # Vector search
docker>=7.0 # Sandbox execution
```

---

## 📝 Documentation Deliverables

| Document | Status | Update Required |
|----------|--------|-----------------|
| README.md | ✅ Updated | Add v4.0 features |
| NEXUS_PRD.md | ✅ Complete | Add Sprint 1-4 items |
| NEXUS_BUILD_LOG.md | ✅ Updated | Add Sprint 1-4 logs |
| NEXUS_INTEGRATION_ROADMAP.md | ✅ Complete | Mark 100% complete |
| API Reference | 📝 Partial | Complete in Sprint 4 |
| Architecture Diagrams | 📝 Partial | Update for v4.0 |
| Getting Started Guide | 📝 Partial | Enhance for beginners |
| CONTRIBUTING.md | ❌ Missing | Create in Sprint 4 |
| CHANGELOG.md | ❌ Missing | Create in Sprint 4 |

---

## 🎯 Definition of Done

Each phase is considered complete when:

- [ ] All code changes implemented
- [ ] Unit tests pass (>90% coverage)
- [ ] Integration tests pass
- [ ] Documentation updated
- [ ] Performance benchmarks run
- [ ] Security audit passed (for security phases)
- [ ] Code review approved
- [ ] Merged to main branch
- [ ] Version tagged

---

## 📅 Milestones

| Milestone | Date | Deliverable |
|-----------|------|-------------|
| **M1: Stability** | Week 4 | Async-safe, thread-safe, accurate tokens |
| **M2: Security** | Week 8 | XSS-safe, stream-fixed, ACL-enhanced |
| **M3: Performance** | Week 12 | O(1) workflows, optimized caching |
| **M4: Release** | Week 16 | v4.0.0 production release |

---
---

## ⚠️ Risk Assessment & Mitigation

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **Async migration breaks existing code** | Medium | High | Feature flag to toggle sync/async, comprehensive test suite first |
| **tiktoken model mismatch** | Low | Medium | Provider-specific tokenizers, fallback to `.split()` on error |
| **Bleach sanitization too strict** | Low | Low | Configurable allowlist for HTML, gradual rollout |
| **Performance regression** | Medium | Medium | Benchmark before/after each change, rollback plan |
| **Test coverage target unrealistic** | Medium | Low | Phased approach: 40% → 70% → 80% → 90% over 4 sprints |
| **Breaking changes in production** | Low | High | Feature flags, semantic versioning, deprecation warnings |
| **Dependency conflicts** | Low | Medium | Pin versions in requirements, use poetry/pip-tools |
| **DAG workflow edge cases** | Medium | Medium | Feature flag for old list-based approach, extensive testing |

---

## 🔗 Task Dependency Graph

### Critical Path (Must Complete in Order)

```
Sprint 1:
  16.1 (Async self_healing) ──┐
  16.2 (Async rate_limiter) ──┼──► 19.1-19.4 (Integration Testing)
  16.3 (Async agent loop) ────┘

  17.1 (Thread-safe registry) ──► 17.2-17.4 (Thread-safe modules)

  18.1 (Tokenizer) ──► 18.2-18.4 (Tokenizer integration)

Sprint 2 (depends on Sprint 1):
  21.1 (Anthropic stream) ──► 21.2-21.4 (Stream integration)
  [Requires: 16.1-16.3 async patterns]

Sprint 3 (depends on Sprint 2):
  24.1 (DAG workflows) ──► 24.2-24.4 (DAG optimization)
  [Requires: 17.1 thread-safe registry]
```

### Parallelizable Tasks

| Can Run Parallel | Dependencies |
|------------------|--------------|
| 16.1, 16.2, 16.3 (Async) | None |
| 20.1-20.4 (Sanitization) | None (independent) |
| 18.1-18.4 (Tokenizer) | None (independent) |
| 22.1-22.4 (ACL Enhancement) | 17.1 (thread safety) |

---

## 🚦 Validation Gates (Sprint Transitions)

### Sprint 1 → Sprint 2 Gate

| Criterion | Target | Verification |
|-----------|--------|--------------|
| Async tests pass | 100% | `pytest tests/unit/test_async.py` |
| Thread safety verified | No race conditions | `pytest tests/unit/test_thread_safety.py` |
| Tokenizer accuracy | >99% | Unit test against known token counts |
| No regressions | All existing tests pass | Full test suite |

### Sprint 2 → Sprint 3 Gate

| Criterion | Target | Verification |
|-----------|--------|--------------|
| Security audit passed | 0 critical/high | `bandit -r nexus/` |
| XSS tests pass | All bypass attempts blocked | `pytest tests/security/test_sanitization.py` |
| Anthropic streaming | Tool calls verified | Integration test with Claude API |
| ACL permissions | Resource-level control | `pytest tests/acl/` |

### Sprint 3 → Sprint 4 Gate

| Criterion | Target | Verification |
|-----------|--------|--------------|
| Performance improved | No regressions | Benchmark comparison |
| Cold start time | <200ms | Automated benchmark |
| Memory footprint | <50MB | Memory profiling |
| Cache efficiency | O(1) LRU | Performance test |

### Sprint 4 → Release Gate

| Criterion | Target | Verification |
|-----------|--------|--------------|
| Test coverage | >90% | `pytest --cov=nexus --cov-report=term` |
| Documentation complete | All APIs documented | Manual review |
| E2E tests pass | All workflows | `pytest tests/e2e/` |
| Security tests | All 16 layers | `pytest tests/security/` |

---

## 🔙 Rollback Strategy

### Feature Flags (Required for Breaking Changes)

| Feature | Flag | Default | Fallback |
|---------|------|---------|----------|
| Async execution | `NEXUS_ASYNC=true` | `false` | Sync mode |
| Tiktoken tokenizer | `NEXUS_TIKTOKEN=true` | `false` | `.split()` estimation |
| Bleach sanitization | `NEXUS_BLEACH=true` | `false` | Regex patterns |
| DAG workflows | `NEXUS_DAG_WORKFLOW=true` | `false` | List-based approach |
| ACL enhancement | `NEXUS_ACL_V2=true` | `false` | Basic ACL |

### Rollback Procedure

```bash
# 1. Identify issue from monitoring
# 2. Set feature flag to false
export NEXUS_ASYNC=false

# 3. Restart services
docker-compose restart

# 4. Verify rollback succeeded
curl http://localhost:8080/health
```

### Version Control Strategy

| Change Type | Branch Strategy | Merge Requirement |
|-------------|-----------------|-------------------|
| Bug fix | `fix/*` branch | 1 approval + passing tests |
| Feature | `feat/*` branch | 2 approvals + passing tests |
| Breaking change | `breaking/*` branch | 2 approvals + manual QA |
| Security fix | `security/*` branch | Immediate merge after verification |

---

## 💻 Resource Requirements

### Development Environment

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| Python | 3.11+ | 3.12+ |
| RAM | 4GB | 8GB+ |
| Disk | 2GB | 10GB+ (with Docker) |
| CPU | 2 cores | 4+ cores |

### External Dependencies

| Service | Purpose | Required |
|---------|---------|----------|
| Docker | Sandbox execution, testing | Yes |
| Redis | Distributed rate limiting | Optional |
| PostgreSQL | Production persistence | Optional |
| NVIDIA NIM API | LLM provider | Yes (or OpenAI/Anthropic) |

### CI/CD Requirements

| Resource | Usage |
|----------|-------|
| GitHub Actions | Free tier sufficient |
| Test runners | 4 parallel jobs |
| Cache storage | ~500MB for dependencies |
| Artifact storage | ~100MB per build |

---

## 📋 Pre-commit & Code Quality Requirements

### Required Hooks (`.pre-commit-config.yaml`)

```yaml
repos:
 - repo: https://github.com/psf/black
 rev: 24.1.0
 hooks:
 - id: black
 language_version: python3.11

 - repo: https://github.com/pycqa/isort
 rev: 5.13.2
 hooks:
 - id: isort
 args: ["--profile", "black"]

 - repo: https://github.com/pycqa/flake8
 rev: 7.0.0
 hooks:
 - id: flake8
 args: ["--max-line-length=100"]

 - repo: https://github.com/pre-commit/mirrors-mypy
 rev: v1.8.0
 hooks:
 - id: mypy
 additional_dependencies: [types-all]

 - repo: https://github.com/pycqa/bandit
 rev: 1.7.22
 hooks:
 - id: bandit
 args: ["-r", "nexus/"]
```

### Code Quality Standards

| Tool | Purpose | Configuration |
|------|---------|--------------|
| **black** | Formatting | Line length: 100 |
| **isort** | Import sorting | Profile: black |
| **flake8** | Linting | Max line: 100, ignore E203,W503 |
| **mypy** | Type checking | Strict mode |
| **bandit** | Security scan | Exclude tests/ |
| **pytest** | Testing | Coverage: >90% |

### Quality Gates (per commit)

```bash
# Run all quality checks
make lint # black --check, isort --check, flake8, mypy
make test # pytest --cov=nexus --cov-fail-under=90
make security # bandit -r nexus/
```

---
## 🏆 Final State Vision

After completing this plan, NEXUS will be:

1. **Most Comprehensive**: 15 development phases + 4 optimization sprints
2. **Most Secure**: 16 security layers + enhanced sanitization + ACL
3. **Most Efficient**: L0-L3 memory, O(1) workflows, async-safe
4. **Most Accurate**: tiktoken integration, precise budget tracking
5. **Most User-Friendly**: OpenTUI CLI, zero-glitch switching
6. **Most Tested**: >90% coverage, security tests, performance tests
7. **Most Documented**: Complete API docs, examples, guides
8. **Production-Ready**: Docker, Kubernetes, CI/CD, monitoring

---

**This is the definitive development plan for NEXUS Framework v4.0.**
