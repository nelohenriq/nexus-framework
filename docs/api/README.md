# NEXUS Framework API Reference

## Table of Contents

1. [Core Modules](#core-modules)
2. [Efficiency Layer](#efficiency-layer)
3. [Security Layer](#security-layer)
4. [Multi-Agent](#multi-agent)
5. [Autonomous Features](#autonomous-features)
6. [Channels & Dispatcher](#channels--dispatcher)
7. [Knowledge & Search](#knowledge--search)
8. [Compression & Events](#compression--events)
9. [Plugins & Sandbox](#plugins--sandbox)
10. [Observability & Resilience](#observability--resilience)
11. [REST API](#rest-api)
12. [Adapters](#adapters)
13. [Configuration](#configuration)

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

### Agent Loop (`nexus.core.agent`)

Monologue cycle execution engine.

```python
from nexus.core.agent import AgentLoop, AgentConfig

# Configure agent
config = AgentConfig(
 agent_id="my_agent",
 max_iterations=100,
 context_window_limit=128000,
 enable_memory=True
)

# Create agent loop
agent = AgentLoop(config, llm_adapter, tool_registry)

# Run agent
response = agent.run(context, "Write a Python function")
```

#### AgentConfig

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `agent_id` | str | required | Unique agent identifier |
| `max_iterations` | int | 100 | Maximum loop iterations |
| `context_window_limit` | int | 128000 | Token limit for context |
| `enable_memory` | bool | True | Enable memory injection |
| `enable_tools` | bool | True | Enable tool execution |

---

### Tool Registry (`nexus.core.tools`)

Dynamic tool management with JSON Schema validation.

```python
from nexus.core.tools import ToolRegistry, tool, PermissionLevel

# Create registry
registry = ToolRegistry()

# Register a tool
@tool(
 name="execute_code",
 description="Execute Python code",
 parameters={"type": "object", "properties": {"code": {"type": "string"}}},
 permission=PermissionLevel.EXECUTE
)
async def execute_code(code: str) -> str:
 return result

registry.register("execute_code", execute_code)

# Execute tool
result = await registry.execute_async("execute_code", {"code": "print(1+1)"})
```

#### Permission Levels

| Level | Value | Description |
|-------|-------|-------------|
| `READ` | 1 | Read-only operations |
| `WRITE` | 2 | Write operations |
| `EXECUTE` | 3 | Code execution |
| `ADMIN` | 4 | Administrative operations |

---

### SKILL.md Parser (`nexus.core.skills`)

Parse Hermes-style SKILL.md files.

```python
from nexus.core.skills import SkillParser, SkillRegistry

# Parse a SKILL.md file
parser = SkillParser()
skill = parser.parse_file(Path("skills/my_skill/SKILL.md"))

# Access skill data
print(skill.name)
print(skill.description)
print(skill.instructions)
print(skill.parameters)

# Use skill registry
registry = SkillRegistry()
registry.register(skill)
skills = registry.find_relevant("code review", limit=5)
```

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

# Search memory
results = memory.search("query", limit=10)
```

#### Methods

| Method | Description |
|--------|-------------|
| `save(key, data)` | Save data by key |
| `load(key)` | Load data by key |
| `delete(key)` | Delete data by key |
| `list_keys()` | List all keys |
| `search(query, limit)` | Search memory by similarity |

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
| `get_token_count()` | Get approximate token count |

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

---

### Rate Limiter (`nexus.efficiency.rate_limiter`)

Sliding window rate limiting.

```python
from nexus.efficiency import RateLimiter

# Create limiter
limiter = RateLimiter(max_rpm=40)

# Acquire slot
if limiter.acquire():
 # Make API call
 pass

# Get status
status = limiter.get_status()
```

---

### Distributed Rate Limiter (`nexus.efficiency.distributed_rate_limiter`)

Redis-backed distributed rate limiting.

```python
from nexus.efficiency import DistributedRateLimiter, RedisRateLimitBackend

# Create with Redis backend
backend = RedisRateLimitBackend("redis://localhost:6379/0")
limiter = DistributedRateLimiter(backend=backend)

# Or auto-detect (falls back to in-memory)
limiter = DistributedRateLimiter()

# Acquire rate limit slot
result = await limiter.acquire("api_calls")
if result.allowed:
 # Make API call
 pass
else:
 print(f"Retry after {result.retry_after}s")
```

---

### Budget Enforcer (`nexus.efficiency.budget_enforcer`)

Token budget enforcement.

```python
from nexus.efficiency import BudgetEnforcer, BudgetConfig

# Create config
config = BudgetConfig(
 max_tokens=100000,
 max_cost_usd=10.0
)

# Create enforcer
budget = BudgetEnforcer(config)

# Track usage
budget.track(1000) # or budget.track_usage(1000)

# Check if within budget
if budget.is_within_budget():
 # Continue
 pass
```

---

## Security Layer

### Security Manager (`nexus.security`)

16-layer security architecture.

```python
from nexus.security import SecurityManager

# Create manager
security = SecurityManager()

# Validate input
validated = security.validate_input(user_input)

# Check permission
if security.check_permission(user, "execute_code"):
 # Allow execution
 pass
```

---

## Multi-Agent

### Agent Registry (`nexus.multiagent.registry`)

Agent discovery and registration.

```python
from nexus.multiagent import AgentRegistry, AgentInfo

# Create registry
registry = AgentRegistry()

# Register agent
agent_info = AgentInfo(
 agent_id="worker_1",
 name="Worker Agent",
 capabilities=["code_generation", "analysis"]
)
registry.register(agent_info)

# Find agents
agents = registry.find_by_capability("code_generation")
```

---

### Message Bus (`nexus.multiagent.messaging`)

Inter-agent communication.

```python
from nexus.multiagent import MessageBus, AgentMessage

# Create bus
bus = MessageBus()

# Subscribe to channel
bus.subscribe("tasks", handler_function)

# Publish message
message = AgentMessage(
 from_agent="agent_1",
 to_agent="agent_2",
 content="Process this task"
)
await bus.publish("tasks", message)
```

---

### Persistence Manager (`nexus.multiagent.persistence`)

State persistence with SQLite.

```python
from nexus.multiagent import PersistenceManager, AgentState

# Create manager
persistence = PersistenceManager(db_path="state.db")

# Save agent state
state = AgentState(
 agent_id="agent_1",
 name="Worker",
 status="active",
 context={"task": "processing"}
)
persistence.save_agent_state(state)

# Load agent state
loaded = persistence.load_agent_state("agent_1")
```

---

### Workflow Orchestrator (`nexus.multiagent.workflow`)

Multi-step workflow execution.

```python
from nexus.multiagent import WorkflowOrchestrator, WorkflowStep

# Create orchestrator
orchestrator = WorkflowOrchestrator()

# Define workflow
steps = [
 WorkflowStep(agent_id="researcher", task="Research topic"),
 WorkflowStep(agent_id="writer", task="Write report", depends_on="researcher"),
]

# Execute workflow
result = await orchestrator.execute_workflow(steps)
```

---

## Autonomous Features

### Health Monitor (`nexus.autonomous.health_monitor`)

System health monitoring.

```python
from nexus.autonomous import HealthMonitor

# Create monitor
monitor = HealthMonitor()

# Check health
health = monitor.check_health()
print(f"Status: {health.status}")
print(f"Components: {health.components}")
```

---

### Self-Healing Manager (`nexus.autonomous.self_healing`)

Auto-recovery with retry/fallback.

```python
from nexus.autonomous import SelfHealingManager

# Create manager
healing = SelfHealingManager()

# Register recovery strategy
healing.register_strategy("llm_error", retry_with_backoff)

# Handle error
result = await healing.handle_error(error, context)
```

---

### Task Scheduler (`nexus.autonomous.task_scheduler`)

Priority-based task scheduling.

```python
from nexus.autonomous import TaskScheduler, Task

# Create scheduler
scheduler = TaskScheduler()

# Schedule task
task = Task(
 id="task_1",
 priority=1,
 handler=async_function
)
scheduler.schedule(task)

# Run scheduler
await scheduler.run()
```

---

### Learning Engine (`nexus.autonomous.learning`)

Rule-based adaptation.

```python
from nexus.autonomous import LearningEngine

# Create engine
learning = LearningEngine()

# Add rule
learning.add_rule(
 condition=lambda ctx: ctx.get("error_count", 0) > 3,
 action=lambda ctx: {"strategy": "fallback"}
)

# Evaluate context
adaptation = learning.evaluate(context)
```

---

## Channels & Dispatcher

### Channel Port (`nexus.channels`)

Abstract interface for all channels.

```python
from nexus.channels import ChannelPort, ChannelMessage, ChannelResponse

# Implement custom channel
class MyChannel(ChannelPort):
 async def connect(self) -> None:
 # Connect to channel
 pass
 
 async def listen(self) -> AsyncIterator[ChannelMessage]:
 # Yield incoming messages
 pass
 
 async def send(self, response: ChannelResponse) -> None:
 # Send response
 pass
 
 async def disconnect(self) -> None:
 # Disconnect from channel
 pass
```

#### Built-in Channels

| Channel | Class | Description |
|---------|-------|-------------|
| CLI | `CLIChannel` | Command-line interface |
| Telegram | `TelegramChannel` | Telegram bot |
| Discord | `DiscordChannel` | Discord bot |

---

### Dispatcher (`nexus.dispatcher`)

Message routing and session management.

```python
from nexus.dispatcher import Dispatcher, MessageRouter, SessionManager

# Create dispatcher
dispatcher = Dispatcher()

# Register channel
dispatcher.register_channel(telegram_channel)

# Register handler
dispatcher.register_handler("telegram", handle_message)

# Start dispatcher
await dispatcher.start()

# Process message
response = await dispatcher.process(message)
```

---

## Knowledge & Search

### Knowledge Graph (`nexus.knowledge.graph`)

Entity relationships with SQLite backend.

```python
from nexus.knowledge import KnowledgeGraph, Entity, Relation, RelationType

# Create graph
graph = KnowledgeGraph()

# Add entities
entity1 = Entity(id="func1", type="function", name="calculate")
entity2 = Entity(id="doc1", type="documentation", name="func_docs")
graph.add_entity(entity1)
graph.add_entity(entity2)

# Add relation
relation = Relation(
 source_id="func1",
 target_id="doc1",
 relation_type=RelationType.DOCUMENTED_BY
)
graph.add_relation(relation)

# Find path
path = graph.find_path("func1", "doc1")

# Get neighbors
neighbors = graph.get_neighbors("func1", depth=2)
```

---

### Semantic Search (`nexus.knowledge.search`)

Vector search with pluggable embeddings.

```python
from nexus.knowledge import SemanticSearch, SearchConfig

# Create search engine
config = SearchConfig(top_k=5, similarity_threshold=0.7)
search = SemanticSearch(config=config)

# Index documents
search.index_document("Python is a programming language", {"source": "wiki"})

# Search
results = search.search("programming languages")
for result in results:
 print(f"{result.id}: {result.score:.2f} - {result.content}")
```

---

## Compression & Events

### TOON Compression (`nexus.compression`)

~40% token reduction for context.

```python
from nexus.compression import to_toon, from_toon, toon

# Encode data to TOON
data = {"messages": [{"role": "user", "content": "Hello"}]}
toon_str = to_toon(data)

# Decode back to dictionary
original = from_toon(toon_str)

# Check compression ratio
ratio = toon.get_compression_ratio(data)
print(f"TOON is {ratio:.1%} the size of JSON")
```

---

### Event Sourcing (`nexus.events`)

Full audit trail with SQLite replay.

```python
from nexus.events import EventSourcing, Event

# Create event sourcing
es = EventSourcing()

# Emit an event
event = es.emit(
 event_type="agent_action",
 aggregate_id="agent_001",
 aggregate_type="agent",
 data={"action": "tool_call", "tool": "execute_code"}
)

# Replay events to reconstruct state
state = es.replay("agent_001")

# Get audit trail
trail = es.get_audit_trail("agent_001")
```

---

## Plugins & Sandbox

### Plugin Manager (`nexus.plugins`)

Dynamic skill loading with GitHub install.

```python
from nexus.plugins import PluginManager

# Create manager
manager = PluginManager(plugin_dir=Path("plugins/"))

# Discover plugins
plugins = manager.discover()

# Load a plugin
module = manager.load("my_skill")

# Install from GitHub
manager.load_from_github("https://github.com/user/nexus-skill")
```

---

### Docker Sandbox (`nexus.sandbox`)

Secure code execution in containers.

```python
from nexus.sandbox import DockerSandbox, SandboxConfig

# Create sandbox
config = SandboxConfig(
 memory_limit="256m",
 cpu_limit=0.5,
 timeout=30,
 network_disabled=True
)
sandbox = DockerSandbox(config)

# Execute code
result = sandbox.execute_python("print(1 + 1)")
print(result.stdout) # "2"
print(result.exit_code) # 0
```

---

## Observability & Resilience

### Prometheus Metrics (`nexus.observability`)

Metrics for LLM, agents, tools, memory, cache.

```python
from nexus.observability import metrics

# Track LLM request
metrics.track_llm_request(
 provider="nvidia",
 model="kimi-k2.5",
 status="success",
 duration=42.66,
 prompt_tokens=37,
 completion_tokens=431
)

# Start metrics server (port 9090)
metrics.start_server()
```

---

### Circuit Breaker (`nexus.resilience`)

Fault tolerance with configurable thresholds.

```python
from nexus.resilience import CircuitBreaker, CircuitBreakerConfig

# Create circuit breaker
config = CircuitBreakerConfig(
 failure_threshold=5,
 success_threshold=3,
 timeout=60.0
)
circuit = CircuitBreaker(config)

# Execute with protection
try:
 result = circuit.call(llm_api_call)
except CircuitBreakerOpenError:
 print("Service unavailable")
```

---

### Retry with Backoff (`nexus.resilience`)

Exponential backoff retry logic.

```python
from nexus.resilience import retry_with_backoff, RetryConfig

# Configure retry
config = RetryConfig(
 max_retries=3,
 base_delay=1.0,
 max_delay=30.0
)

# Use decorator
@retry_with_backoff(config)
async def call_api():
 return await llm_adapter.complete(messages)
```

---

## REST API

### FastAPI Endpoints (`nexus.api`)

REST API with auto-documentation.

```python
from nexus.api import create_app, run_server

# Create app
app = create_app()

# Run server
run_server(host="0.0.0.0", port=8000)
```

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/status` | GET | Framework status |
| `/agents` | POST | Create new agent |
| `/agents/{id}` | GET | Get agent status |
| `/agents/{id}/run` | POST | Run agent with prompt |
| `/agents/{id}` | DELETE | Delete agent |
| `/memory/store` | POST | Store memory entry |
| `/memory/{key}` | GET | Retrieve memory |
| `/memory/search` | POST | Search memory |
| `/tools` | GET | List available tools |
| `/tools/execute` | POST | Execute a tool |
| `/config` | GET | Get current config |
| `/config` | PATCH | Update config |

### Auto-Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Adapters

### LLM Adapters (`nexus.adapters.llm`)

Zero-glitch provider switching.

```python
from nexus.adapters.llm import OpenAIAdapter, OllamaAdapter, NVIDIAAdapter

# Create adapter
adapter = NVIDIAAdapter(
 api_key="nvapi-xxx",
 model="moonshotai/kimi-k2.5"
)

# Generate completion
result = await adapter.complete(
 messages=[{"role": "user", "content": "Hello"}],
 tools=[...],
 config={"temperature": 0.7}
)
```

### Supported Providers

| Provider | Adapter | Models |
|----------|---------|--------|
| NVIDIA NIM | `NVIDIAAdapter` | DeepSeek, Llama, Mistral, Kimi |
| OpenAI | `OpenAIAdapter` | GPT-4, GPT-4-turbo, GPT-3.5 |
| Anthropic | `AnthropicAdapter` | Claude 3 (Opus, Sonnet, Haiku) |
| Ollama | `OllamaAdapter` | Llama2, CodeLlama, Mistral |
| Custom | `OpenAICompatibleAdapter` | Any OpenAI-compatible API |

---

## Configuration

### YAML Configuration (`nexus.config`)

```yaml
# nexus.yaml
llm:
 provider: nvidia
 model: moonshotai/kimi-k2.5
 api_key: ${NVIDIA_API_KEY}
 api_base: https://integrate.api.nvidia.com/v1
 temperature: 0.7
 max_tokens: 4096

efficiency:
 cache_enabled: true
 rate_limit_rpm: 40
 budget_tokens: 100000

security:
 enabled: true
 layers:
 - input_validation
 - rate_limiting
 - audit_logging
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `NVIDIA_API_KEY` | NVIDIA NIM API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `OLLAMA_BASE_URL` | Ollama server URL |
| `REDIS_URL` | Redis connection URL |
