# NEXUS Framework API Reference

## Table of Contents

1. [Core Modules](#core-modules)
2. [Efficiency Layer](#efficiency-layer)
3. [Security Layer](#security-layer)
4. [Multi-Agent](#multi-agent)
5. [Autonomous Features](#autonomous-features)
6. [Adapters](#adapters)
7. [Configuration](#configuration)

---

## Core Modules

### DI Container (`nexus.container`)

Dependency injection container for managing service bindings.

```python
from nexus.container import DIContainer

# Create container
container = DIContainer()

# Bind a service
container.bind(Interface, Implementation)

# Bind a singleton
container.singleton(Interface, instance)

# Resolve a service
service = container.get(Interface)
```

#### Methods

| Method | Description |
|--------|-------------|
| `bind(interface, implementation)` | Bind interface to implementation |
| `singleton(interface, instance)` | Register a singleton instance |
| `get(interface)` | Resolve and return service |
| `has(interface)` | Check if binding exists |

---

### Messages (`nexus.core.messages`)

Message types for agent communication.

```python
from nexus.core import Message, MessageRole

# Create a message
msg = Message(
 role=MessageRole.USER,
 content="Hello, NEXUS!"
)
```

#### Message Roles

| Role | Description |
|------|-------------|
| `SYSTEM` | System instructions |
| `USER` | User input |
| `ASSISTANT` | Agent response |
| `FUNCTION` | Function call result |

---

### Memory (`nexus.core.memory`)

SQLite-based memory management with connection pooling.

```python
from nexus.core import MemoryManager

# Create memory manager
memory = MemoryManager(db_path=":memory:")

# Save data
memory.save("key", {"data": "value"})

# Load data
data = memory.load("key")
```

#### Methods

| Method | Description |
|--------|-------------|
| `save(key, data)` | Save data by key |
| `load(key)` | Load data by key |
| `delete(key)` | Delete data by key |
| `list_keys()` | List all keys |

---

### Context (`nexus.core.context`)

Agent conversation context with checkpointing.

```python
from nexus.core import AgentContext

# Create context
context = AgentContext(agent_id="my_agent")

# Add messages
context.add_message(message)

# Create checkpoint
checkpoint = context.create_checkpoint()

# Restore checkpoint
context.restore_checkpoint(checkpoint)
```

#### Methods

| Method | Description |
|--------|-------------|
| `add_message(message)` | Add message to context |
| `get_messages(limit)` | Get messages (optional limit) |
| `create_checkpoint()` | Create state checkpoint |
| `restore_checkpoint(checkpoint)` | Restore from checkpoint |
| `clear()` | Clear all messages |

---

## Efficiency Layer

### Prompt Cache (`nexus.efficiency.prompt_cache`)

Caches static prefixes to reduce token usage.

```python
from nexus.efficiency import PromptCache

# Create cache
cache = PromptCache(max_entries=100)

# Cache a prefix
cache.put("System prompt...", tokens=50)

# Get cached entry
entry = cache.get_cached("System prompt...")
```

#### Methods

| Method | Description |
|--------|-------------|
| `put(prefix, tokens)` | Cache a prefix |
| `get_cached(prefix)` | Get cached entry |
| `get_stats()` | Get cache statistics |

---

### Rate Limiter (`nexus.efficiency.rate_limiter`)

Sliding window rate limiting for API protection.

```python
from nexus.efficiency import RateLimiter

# Create limiter
limiter = RateLimiter(max_rpm=60)

# Acquire permission (blocks if limited)
limiter.acquire()

# Check status
status = limiter.get_status()
print(f"Remaining: {status.requests_remaining}")
```

#### RateLimitStatus Attributes

| Attribute | Description |
|-----------|-------------|
| `requests_made` | Requests in current window |
| `requests_remaining` | Remaining requests |
| `reset_in_seconds` | Seconds until reset |
| `is_limited` | Currently rate limited |

---

### Budget Enforcer (`nexus.efficiency.budget_enforcer`)

Token budget enforcement for cost control.

```python
from nexus.efficiency import BudgetEnforcer, BudgetConfig

# Create budget
config = BudgetConfig(max_tokens=10000)
budget = BudgetEnforcer(config)

# Check budget
if budget.can_use(tokens=100):
 budget.use(tokens=100)
```

---

## Security Layer

### Security Manager (`nexus.security`)

16-layer security architecture for input validation, authentication, and authorization.

```python
from nexus.security import SecurityManager

# Create security manager
security = SecurityManager()

# Check input
passed, errors = security.check_input(data)

# Access security layers
for name, layer in security.layers.items():
 print(f"{name}: {type(layer).__name__}")
```

#### Security Layers

| Layer | Description |
|-------|-------------|
| `input_validation` | Input sanitization and validation |
| `authentication` | Authentication checks |
| `authorization` | Authorization and permissions |

---

## Multi-Agent

### Agent Registry (`nexus.multiagent.registry`)

Agent discovery and registration.

```python
from nexus.multiagent import AgentRegistry

# Create registry
registry = AgentRegistry()

# Register agent
agent_id = registry.register("worker", ["compute", "analyze"])

# Find by capability
agents = registry.find_by_capability("compute")

# Find best for task
best = registry.find_best_for_task(["compute", "math"])
```

---

### Message Bus (`nexus.multiagent.messaging`)

Inter-agent communication.

```python
from nexus.multiagent import MessageBus, AgentMessage, MessageType, MessagePriority

# Create bus
bus = MessageBus()

# Register agent
bus.register_agent(agent_id)

# Send message
msg = AgentMessage(
 message_id=str(uuid.uuid4()),
 sender_id=sender,
 receiver_id=receiver,
 message_type=MessageType.TASK,
 priority=MessagePriority.HIGH,
 content={"task": "data"}
)
bus.send(msg)

# Receive message
received = bus.receive(agent_id)
```

#### Message Types

| Type | Description |
|------|-------------|
| `TASK` | Task assignment |
| `RESULT` | Task result |
| `STATUS` | Status update |
| `ERROR` | Error message |
| `CONTROL` | Control message |

#### Message Priorities

| Priority | Description |
|----------|-------------|
| `LOW` | Low priority |
| `NORMAL` | Normal priority |
| `HIGH` | High priority |
| `CRITICAL` | Critical priority |

---

### Workflow Orchestrator (`nexus.multiagent.workflow`)

Multi-step workflow execution.

```python
from nexus.multiagent import WorkflowOrchestrator

# Create orchestrator
orchestrator = WorkflowOrchestrator()

# Define steps
steps = [
 {"name": "step1", "agent_id": agent1, "task": "Process data"},
 {"name": "step2", "agent_id": agent2, "task": "Analyze results"}
]

# Create workflow
workflow = orchestrator.create_workflow("my_workflow", steps)
```

---

## Autonomous Features

### Health Monitor (`nexus.autonomous.health_monitor`)

System health monitoring.

```python
from nexus.autonomous import HealthMonitor

# Create monitor
health = HealthMonitor(check_interval=5.0)

# Register health check
health.register_check("database", check_func)

# Get status
status = health.get_status()
```

---

### Self-Healing Manager (`nexus.autonomous.self_healing`)

Auto-recovery with retry/fallback strategies.

```python
from nexus.autonomous import SelfHealingManager

# Create manager
healing = SelfHealingManager(max_retries=3)

# Handle error
result = healing.handle_error(error, context)
```

---

### Task Scheduler (`nexus.autonomous.task_scheduler`)

Priority-based task scheduling.

```python
from nexus.autonomous import TaskScheduler

# Create scheduler
scheduler = TaskScheduler(max_workers=4)

# Schedule task
task_id = scheduler.schedule("task_name", func, priority=5)
```

---

### Learning Engine (`nexus.autonomous.learning`)

Rule-based adaptation and learning.

```python
from nexus.autonomous import LearningEngine

# Create engine
learning = LearningEngine()

# Record learning
learning.record_learning("event", data, outcome)

# Get recommendations
recs = learning.get_recommendations(context)
```

---

## Adapters

### LLM Adapters (`nexus.adapters.llm`)

Supports OpenAI, Ollama, Anthropic, and OpenAI-compatible endpoints.

```python
from nexus.adapters.llm import OpenAIAdapter, OllamaAdapter, AnthropicAdapter

# OpenAI
openai = OpenAIAdapter(api_key="...", model="gpt-4")

# Ollama (local)
ollama = OllamaAdapter(model="llama2")

# Anthropic
anthropic = AnthropicAdapter(api_key="...", model="claude-3")
```

---

### Multimodal Adapters (`nexus.adapters.multimodal`)

Vision, PDF, and audio processing.

```python
from nexus.adapters.multimodal import MultimodalAdapter

# Create adapter
adapter = MultimodalAdapter()

# Process image
result = adapter.process("image.png", "vision")
```

---

## Configuration

### Configuration Manager (`nexus.config`)

YAML-based configuration with environment variable support.

```python
from nexus.config import ConfigManager

# Load configuration
config = ConfigManager()
config.load("nexus.yaml")

# Get value
value = config.get("llm.model")

# Get with default
value = config.get("llm.temperature", default=0.7)
```

### Configuration File (nexus.yaml)

```yaml
# LLM Configuration
llm:
 provider: openai
 model: gpt-4
 api_key: ${OPENAI_API_KEY}
 temperature: 0.7

# Efficiency Configuration
efficiency:
 cache_enabled: true
 max_rpm: 60
 budget:
 max_tokens: 100000

# Security Configuration
security:
 enabled_layers:
 - input_validation
 - authentication
 - authorization
```

---

## CLI Commands

### nexus init
Initialize a new NEXUS project.

```bash
nexus init my_project
```

### nexus version
Show framework version.

```bash
nexus version
```

### nexus doctor
Run diagnostics.

```bash
nexus doctor
```

---

## License

MIT License - See LICENSE file for details.
---

## CLI Commands

### Setup & Configuration

#### `nexus setup`

Interactive configuration wizard for setting up NEXUS.

```bash
nexus setup [--config PATH]
```

**Steps:**
1. Select LLM Provider (OpenAI, Anthropic, Ollama, NVIDIA NIM, OpenAI-Compatible)
2. Choose Model
3. Enter API Key (or use environment variable)
4. Configure Temperature
5. Configure Efficiency Settings (caching, rate limits, budget)
6. Configure Security Settings (layers)

**Example:**
```bash
$ nexus setup
============================================================
 NEXUS Framework Setup Wizard
============================================================

[Step 1] LLM Provider Configuration
----------------------------------------

Available providers:
 1. OpenAI
 2. Anthropic
 3. Ollama (Local)
 4. NVIDIA NIM
 5. OpenAI-Compatible

Select provider [1-5]: 1
...
```

#### `nexus init`

Initialize a new NEXUS project.

```bash
nexus init [PATH] [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--name, -n` | Agent name (default: nexus-agent) |
| `--provider, -p` | LLM provider (default: ollama) |
| `--model, -m` | Model name (default: llama3.2) |
| `--force, -f` | Overwrite existing project |

---

### Provider Management

#### `nexus provider add`

Add a new LLM provider with automatic verification.

```bash
nexus provider add [--config PATH]
```

**Features:**
- Tests connection before saving
- Validates API key
- Confirms model availability

**Supported Providers:**

| Provider | Models | Verification |
|----------|--------|-------------|
| OpenAI | gpt-4, gpt-4-turbo, gpt-3.5-turbo | ✅ API endpoint |
| Anthropic | claude-3-opus, claude-3-sonnet, claude-3-haiku | ✅ API key check |
| Ollama | llama2, codellama, mistral | ✅ Local connection |
| NVIDIA NIM | llama3-8b, deepseek-coder-6.7b | ✅ API endpoint |
| OpenAI-Compatible | Custom | ✅ Custom endpoint |

#### `nexus provider list`

List currently configured provider.

```bash
nexus provider list [--config PATH]
```

**Output:**
```
Configured Provider
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Setting ┃ Value ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ Provider │ openai │
│ Model │ gpt-4 │
│ API Base │ https://api.openai.com/v1 │
└───────────┴──────────────────────┘
```

#### `nexus provider verify`

Verify provider connectivity.

```bash
nexus provider verify [--config PATH]
```

**Checks:**
- Validates API key
- Tests endpoint availability
- Lists available models

---

### Diagnostics

#### `nexus doctor`

Run diagnostics on NEXUS configuration.

```bash
nexus doctor [--config PATH]
```

**Checks:**
- Configuration file exists
- Configuration loads correctly
- LLM adapter creates successfully
- Provider connectivity

#### `nexus version`

Show NEXUS version.

```bash
nexus version
```

---

### Running Agents

#### `nexus run`

Run the NEXUS agent.

```bash
nexus run [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--config, -c` | Configuration file path |
| `--prompt, -p` | Initial prompt |
| `--interactive/-i` | Interactive mode (default: True) |
| `--batch/-b` | Batch mode |

---

## Configuration File

### YAML Structure

```yaml
# NEXUS Configuration
llm:
 provider: openai
 model: gpt-4
 api_key: ${OPENAI_API_KEY}
 api_base: https://api.openai.com/v1
 temperature: 0.7
 max_tokens: 4096

memory:
 provider: sqlite
 path: ./nexus.db

security:
 sandbox_enabled: true
 audit_logging: true

efficiency:
 cache_enabled: true
 max_rpm: 60
 budget:
 max_tokens: 100000

agent_name: my-agent
log_level: INFO
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `NVIDIA_API_KEY` | NVIDIA NIM API key |
| `LLM_API_KEY` | Generic API key |
| `LLM_BASE_URL` | Generic API endpoint |
