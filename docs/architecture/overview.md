# NEXUS Framework Architecture

## Overview

NEXUS is a secure, standalone agentic framework designed with hexagonal architecture, protocol-based interfaces, and 16 security layers. It integrates the best features from Hermes, OpenClaw, Agent Zero, and OpenFang while eliminating their weaknesses.

**Development Status:** All 10 phases complete with P1 features.

## Design Principles

1. **Hexagonal Architecture** - Core logic independent of external frameworks
2. **Protocol-Based Interfaces** - Type-safe, explicit contracts between components
3. **Dependency Injection** - Loose coupling, testability, and flexibility
4. **Security-First** - 16-layer security architecture built into the core
5. **Zero External Dependencies** - No reliance on external backends like Hermes
6. **Production Ready** - Docker, Kubernetes, Prometheus metrics included

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│ Channels Layer (nexus/channels) │
│ - CLI, Telegram, Discord, MQTT, Web UI │
└─────────────────────────────────────────────────────────────┘
┌───────────────────────────────────────────────────────────┐
│ Dispatcher Layer (nexus/dispatcher) │
│ - MessageRouter, SessionManager, ContextBuilder │
└───────────────────────────────────────────────────────────┐
┌───────────────────────────────────────────────────────────┐
│ Agent Layer (nexus/core) │
│ - AgentLoop, ToolRegistry, Skills, Memory, Context │
└───────────────────────────────────────────────────────────┐
┌───────────────────────────────────────────────────────────┐
│ Efficiency Layer (nexus/efficiency, nexus/compression) │
│ - PromptCache, RateLimiter, BudgetEnforcer, TOON │
└───────────────────────────────────────────────────────────┐
┌───────────────────────────────────────────────────────────┐
│ Domain Layer (nexus/core, nexus/knowledge) │
│ - Messages, Memory, Knowledge Graph, Semantic Search │
└───────────────────────────────────────────────────────────┐
┌───────────────────────────────────────────────────────────┐
│ Infrastructure Layer (nexus/container, nexus/config) │
│ - DI Container, Configuration, Ports, Resilience │
└───────────────────────────────────────────────────────────┐
┌───────────────────────────────────────────────────────────┐
│ Adapter Layer (nexus/adapters) │
│ - LLM: OpenAI, Anthropic, Ollama, NVIDIA NIM │
│ - Multimodal: Vision, PDF, Audio │
│ - Storage: SQLite, Redis │
└───────────────────────────────────────────────────────────┐
┌───────────────────────────────────────────────────────────┐
│ Cross-Cutting Concerns │
│ - Security (16 layers), Observability, Events, Plugins │
└───────────────────────────────────────────────────────────┘
```

---

## Phase Structure

### Phase 1: Foundation

| Component | Purpose |
|------------|---------|
| DI Container | Dependency injection with bindings, singletons, and type hints caching |
| Port Protocols | Interface definitions for LLM, Memory, Storage adapters |
| LLM Adapters | OpenAI, Ollama, Anthropic, NVIDIA NIM, OpenAI-compatible |
| Configuration | YAML-based with environment variable expansion |
| CLI | Command-line interface for project management |

### Phase 2: Efficiency Layer

| Component | Purpose |
|------------|---------|
| Prompt Cache | Static prefix caching for token optimization |
| Rate Limiter | Sliding window RPM limiting |
| Distributed Rate Limiter | Redis-backed for multi-process scaling |
| Budget Enforcer | Token budget enforcement with track_usage alias |

### Phase 3: Core Agent

| Component | Purpose |
|------------|---------|
| Messages | Message types: SYSTEM, USER, ASSISTANT, FUNCTION |
| Memory | SQLite-based storage with connection pooling (10x faster) |
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
| MessageBus | Inter-agent communication (pub/sub) |
| PersistenceManager | State persistence with SQLite |
| WorkflowOrchestrator | Multi-step workflow execution |

### Phase 6: Autonomous Features

| Component | Purpose |
|------------|---------|
| HealthMonitor | System health monitoring |
| SelfHealingManager | Auto-recovery with retry/fallback |
| TaskScheduler | Priority-based task scheduling |
| LearningEngine | Rule-based adaptation |

### Phase 7: Core Execution Engine (P0)

| Component | Purpose |
|------------|---------|
| AgentLoop | Monologue cycle execution (LLM → tool → LLM → response) |
| ToolRegistry | Dynamic tool management with JSON Schema validation |
| SKILL.md Parser | Hermes-style skill file parsing |
| DockerSandbox | Secure code execution in containers |
| Anti-Corruption Layer | Framework translation (Hermes, Agent Zero, OpenClaw, OpenFang) |

### Phase 8: Production Hardening

| Component | Purpose |
|------------|---------|
| Prometheus Metrics | LLM, agent, tool, memory, cache metrics |
| Circuit Breaker | Fault tolerance with configurable thresholds |
| Retry with Backoff | Exponential backoff retry logic |
| Docker | Multi-stage Dockerfile, health checks |
| Kubernetes | Deployment, Service, ConfigMap, Secret manifests |

### Phase 9: Channels & Dispatcher

| Component | Purpose |
|------------|---------|
| ChannelPort | Abstract interface for all channels |
| CLIChannel | Command-line input/output |
| TelegramChannel | Telegram bot integration |
| DiscordChannel | Discord bot integration |
| MessageRouter | Route messages to appropriate handlers |
| SessionManager | User session management with LRU cache |
| ContextBuilder | Build agent context from session and memory |

### Phase 10: Advanced Features

| Component | Purpose |
|------------|---------|
| TOON Compression | ~40% token reduction for context |
| Event Sourcing | Full audit trail with SQLite replay |
| Plugin System | Dynamic skill loading with GitHub install |

### P1: Extended Capabilities

| Component | Purpose |
|------------|---------|
| Knowledge Graph | Entity relationships with SQLite backend |
| Semantic Search | Vector search with pluggable embeddings |
| REST API | FastAPI endpoints with auto-documentation |

---

## Security Architecture

### 16 Security Layers

| # | Layer | Description | Implementation |
|---|-------|-------------|---------------|
| 1 | Input Validation | Sanitize and validate all inputs | InputValidationLayer |
| 2 | Skill Sandboxing | Isolated execution environments | DockerSandbox |
| 3 | Rate Limiting | Prevent abuse and DoS | RateLimiter, DistributedRateLimiter |
| 4 | Output Filtering | PII detection and redaction | OutputFilteringLayer |
| 5 | Audit Logging | Comprehensive action logging | EventSourcing |
| 6 | Authentication | JWT, OAuth2 support | AuthenticationLayer |
| 7 | Authorization | RBAC permissions | AuthorizationLayer, ToolRegistry permissions |
| 8 | Encryption | AES-256, TLS 1.3 | (Configurable) |
| 9 | Integrity Verification | Checksums and signatures | (Configurable) |
| 10 | Non-repudiation | Cryptographic proof | EventSourcing |
| 11 | Fail-safe | Circuit breakers | CircuitBreaker |
| 12 | Resource Limits | Memory/CPU constraints | DockerSandbox config |
| 13 | Dependency Verification | Supply chain security | PluginManager validation |
| 14 | Secure Defaults | Security by default | Default config values |
| 15 | Incident Response | Automated threat response | SelfHealingManager |
| 16 | Compliance Controls | GDPR, SOC2 ready | Audit logging, encryption |

---

## Data Flow

```
User Message
 ↓
Channel (CLI/Telegram/Discord)
 ↓
MessageRouter → SessionManager
 ↓
ContextBuilder (loads memory, history)
 ↓
AgentLoop
 ├→ ToolRegistry (execute tools)
 ├→ MemoryManager (save/retrieve)
 ├→ Knowledge Graph (entity lookup)
 └→ LLM Adapter (generate response)
 ↓
Response
```

---

## Module Dependencies

```
nexus/
├── container/ # No dependencies
├── ports/ # No dependencies
├── config/ # container
├── adapters/llm/ # ports, config
├── core/messages.py # No dependencies
├── core/memory.py # No dependencies
├── core/context.py # messages, memory
├── core/tools.py # No dependencies
├── core/skills.py # No dependencies
├── core/agent.py # context, tools, adapters
├── efficiency/ # No dependencies
├── security/ # core
├── multiagent/ # core, persistence
├── autonomous/ # core, multiagent
├── sandbox/ # No dependencies
├── acl/ # No dependencies
├── observability/ # No dependencies
├── resilience/ # No dependencies
├── channels/ # No dependencies
├── dispatcher/ # channels, core
├── knowledge/ # No dependencies
├── compression/ # No dependencies
├── events/ # No dependencies
├── plugins/ # core/skills
├── api/ # all modules
└── cli/ # config, adapters
```

---

## Configuration Architecture

### Hierarchical Configuration

```
1. Default values (code)
 ↓
2. nexus.yaml (project)
 ↓
3. Environment variables
 ↓
4. CLI arguments (highest priority)
```

### Environment Variable Expansion

```yaml
llm:
 api_key: ${NVIDIA_API_KEY} # Expands from environment
 api_base: ${NVIDIA_URL:-https://integrate.api.nvidia.com/v1} # Default value
```

---

## Deployment Architecture

### Docker Compose Stack

```
┌─────────────────────────────────────────────────────────────┐
│ NEXUS Container (Port 8000) │
│ - REST API │
│ - Agent Loop │
│ - All modules │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│ Redis Container (Port 6379) │
│ - Distributed rate limiting │
│ - Session caching │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│ Prometheus Container (Port 9091) │
│ - Metrics collection │
│ - Alerting │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│ Grafana Container (Port 3000) │
│ - Visualization dashboards │
└─────────────────────────────────────────────────────────────┘
```

### Kubernetes Deployment

```yaml
# Key components:
- Deployment: 3 replicas, resource limits
- Service: ClusterIP + LoadBalancer
- ConfigMap: Configuration
- Secret: API keys
- HPA: Auto-scaling (optional)
```

---

## Extensibility Points

### 1. LLM Providers

```python
# Implement LLMPort protocol
class MyCustomAdapter:
 async def complete(self, messages, tools, config) -> CompletionResult: ...

# Register in container
container.bind(LLMPort, MyCustomAdapter)
```

### 2. Channels

```python
# Implement ChannelPort protocol
class MyChannel(ChannelPort):
 async def connect(self) -> None: ...
 async def listen(self) -> AsyncIterator[ChannelMessage]: ...
 async def send(self, response: ChannelResponse) -> None: ...

# Register with dispatcher
dispatcher.register_channel(MyChannel())
```

### 3. Tools

```python
# Register with tool registry
@tool(name="my_tool", description="...")
async def my_tool(arg: str) -> str:
 return result

registry.register("my_tool", my_tool)
```

### 4. Plugins

```python
# Install from GitHub
manager.load_from_github("https://github.com/user/nexus-skill")

# Or create SKILL.md
name: my-skill
description: My custom skill
---
Instructions here...
```

---

## Performance Characteristics

| Component | Performance | Notes |
|-----------|-------------|-------|
| DI Container | O(1) resolution | Type hints cached |
| Memory Manager | 10x faster | Connection pooling |
| Rate Limiter | O(1) acquire | Sliding window |
| Knowledge Graph | O(log n) queries | Indexed SQLite |
| Semantic Search | O(n) brute force | In-memory vectors |
| TOON Compression | ~40% reduction | Lossless encoding |

---

## Testing Strategy

### Unit Tests
- Each module independently testable
- Protocol mocks for adapters
- No external dependencies required

### Integration Tests
- Module interaction tests
- Docker sandbox tests
- LLM adapter tests (mocked)

### E2E Tests
- Full agent execution
- Multi-agent workflows
- Channel integration

---

## Future Considerations

| Area | Potential Enhancement |
|------|----------------------|
| Channels | WebSocket, Slack, Matrix, IRC |
| Storage | PostgreSQL, MongoDB, Qdrant |
| ML | Fine-tuned models, RAG |
| Security | mTLS, secrets management |
| Scaling | Horizontal pod autoscaling |
