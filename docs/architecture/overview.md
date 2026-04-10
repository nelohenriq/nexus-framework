# NEXUS Framework Architecture

## Overview

NEXUS is a secure, standalone agentic framework designed with hexagonal architecture, protocol-based interfaces, and 16 security layers. It integrates the best features from Hermes, OpenClaw, Agent Zero, and OpenFang while eliminating their weaknesses.

## Design Principles

1. **Hexagonal Architecture** - Core logic independent of external frameworks
2. **Protocol-Based Interfaces** - Type-safe, explicit contracts between components
3. **Dependency Injection** - Loose coupling, testability, and flexibility
4. **Security-First** - 16-layer security architecture built into the core
5. **Zero External Dependencies** - No reliance on external backends like Hermes

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│ CLI Layer (nexus/cli)                                       │
│ - Commands: init, version, doctor, sync                     │
└─────────────────────────────────────────────────────────────┘
 ┌───────────────────────────────────────────────────────────┐
 │ Application Layer (nexus/adapters)                        │
 │ - LLM Adapters: OpenAI, Ollama, Anthropic                 │
 │ - Multimodal: Vision, PDF, Audio                          │
 │ - Storage: SQLite, File System                            │
 └───────────────────────────────────────────────────────────┘
 ┌───────────────────────────────────────────────────────────┐
 │ Domain Layer (nexus/core)                                 │
 │ - Agent, Message, Context, Memory                         │
 │ - Business logic and domain models                        │
 └───────────────────────────────────────────────────────────┘
 ┌───────────────────────────────────────────────────────────┐
 │ Infrastructure Layer (nexus/container, nexus/config)      │
 │ - DI Container, Configuration, Ports                      │
 └───────────────────────────────────────────────────────────┘
```

## Phase Structure

### Phase 1: Foundation

| Component | Purpose |
|------------|---------|
| DI Container | Dependency injection with bindings and singletons |
| Port Protocols | Interface definitions for adapters |
| LLM Adapters | OpenAI, Ollama, Anthropic, OpenAI-compatible |
| Configuration | YAML-based with environment variable expansion |
| CLI | Command-line interface for project management |

### Phase 2: Efficiency Layer

| Component | Purpose |
|------------|---------|
| Prompt Cache | Static prefix caching for token optimization |
| Rate Limiter | Sliding window RPM limiting |
| Budget Enforcer | Token budget enforcement |

### Phase 3: Core Agent

| Component | Purpose |
|------------|---------|
| Messages | Message types: SYSTEM, USER, ASSISTANT, FUNCTION |
| Memory | SQLite-based storage with connection pooling |
| Context | Conversation context with checkpointing |

### Phase 4: Security & Multimodal

| Component | Purpose |
|------------|---------|
| SecurityManager | 16-layer security architecture |
| InputValidationLayer | Injection detection, length limits |
| AuthenticationLayer | Authentication checks |
| AuthorizationLayer | Permission validation |
| Multimodal Adapter | Vision, PDF, Audio processing |

### Phase 5: Multi-Agent & Persistence

| Component | Purpose |
|------------|---------|
| AgentRegistry | Agent discovery and registration |
| MessageBus | Inter-agent communication |
| PersistenceManager | State persistence with SQLite |
| WorkflowOrchestrator | Multi-step workflow execution |

### Phase 6: Autonomous Features

| Component | Purpose |
|------------|---------|
| HealthMonitor | System health monitoring |
| SelfHealingManager | Auto-recovery with retry/fallback |
| TaskScheduler | Priority-based task scheduling |
| LearningEngine | Rule-based adaptation |

## Security Architecture

### 16 Security Layers

| # | Layer | Description |
|---|-------|-------------|
| 1 | Input Validation | Sanitization, length limits, injection detection |
| 2 | Authentication | Identity verification |
| 3 | Authorization | Permission checking |
| 4 | Rate Limiting | DoS protection |
| 5 | Audit Logging | Security event logging |
| 6 | Encryption | Data encryption at rest |
| 7 | Key Management | API key rotation and storage |
| 8 | Sandboxing | Isolated execution |
| 9 | Output Validation | Response sanitization |
| 10 | Content Filtering | Harmful content detection |
| 11 | Prompt Injection | System prompt protection |
| 12 | Context Isolation | Multi-tenant separation |
| 13 | Resource Limits | Memory, CPU, time limits |
| 14 | Secure Defaults | Safe configuration defaults |
| 15 | Dependency Scan | Vulnerability scanning |
| 16 | Incident Response | Error handling and recovery |

## Data Flow

```
User Input → CLI → Security Layer (Validation) → Efficiency Layer (Cache/Rate Limit)
 → Core Agent (Context/Memory) → LLM Adapter → Response
 → Security Layer (Output Validation) → User
```

## LLM Provider Integration

```
 ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
 │ OpenAI │ │ Anthropic │ │ Ollama │ │ NVIDIA NIM │
 └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
 │ │ │ │
 └───────────────────────┴───────────────────────┘
 │
 ┌──────┴──────┐
 │ LLM Adapter │
 │ (Port) │
 └──────┬──────┘
 │
 ┌──────┴──────┐
 │ Core Agent │
 └─────────────┘
```

## Configuration Hierarchy

```
1. Environment Variables (highest priority)
 ↓
2. Configuration File (nexus.yaml)
 ↓
3. Default Values (lowest priority)
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.10+ |
| Database | SQLite with WAL mode |
| Configuration | YAML with environment variable expansion |
| Testing | pytest |
| CLI | argparse |
| Async | threading for concurrency |

## File Structure

```
nexus/
 ├── __init__.py
 ├── container/ # Dependency Injection
 ├── core/ # Messages, Memory, Context
 ├── efficiency/ # Cache, Rate Limiter, Budget
 ├── security/ # Security layers
 ├── multiagent/ # Registry, Messaging, Workflow
 ├── autonomous/ # Health, Healing, Scheduler, Learning
 ├── adapters/ # LLM, Multimodal adapters
 ├── config/ # Configuration management
 └── cli/ # Command-line interface
```

## Comparison with Other Frameworks

| Feature | NEXUS | Hermes | OpenClaw | Agent Zero |
|---------|-------|--------|----------|------------|
| Standalone | ✅ | ❌ | ✅ | ✅ |
| External Backend | ❌ | ✅ | ❌ | ❌ |
| Security Layers | 16 | 5 | 12 | 3 |
| DI Container | ✅ | ❌ | ❌ | ❌ |
| Multi-Agent | ✅ | ✅ | ❌ | ✅ |
| Persistence | ✅ | ✅ | ❌ | ✅ |
| Zero-Glitch Switch | ✅ | ❌ | ❌ | ❌ |

## License

MIT License