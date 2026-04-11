# NEXUS Framework - Getting Started Guide

## Overview

NEXUS is a production-ready, security-first Python framework for building AI agents. This guide will help you get started quickly.

---

## Prerequisites

- Python 3.11 or higher
- pip package manager
- Git
- (Optional) Docker for containerized execution
- (Optional) Redis for distributed rate limiting

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/nelohenriq/nexus-framework.git
cd nexus-framework
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate # Linux/macOS
# or: venv\Scripts\activate # Windows
```

### 3. Install Dependencies

```bash
pip install -e ".[dev]"
```

---

## Quick Start

### Option 1: Interactive Setup (Recommended)

```bash
nexus setup
```

The interactive wizard will guide you through:
1. **Provider Selection** - Choose from NVIDIA NIM, OpenAI, Anthropic, Ollama, or custom
2. **Model Selection** - Pick from provider-specific models
3. **API Key Configuration** - Enter directly or use environment variables
4. **Efficiency Settings** - Configure caching, rate limits, budget
5. **Security Settings** - Enable security layers

### Option 2: Manual Configuration

Create `nexus.yaml` in your project root:

```yaml
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

Set your API key:

```bash
export NVIDIA_API_KEY="nvapi-xxx"
```

---

## Verify Installation

### Run the Demo

```bash
python nexus_demo.py
```

This will test all 10 phases:
- Phase 1-6: Core framework components
- Phase 7: Agent loop, tools, skills, sandbox, ACL
- Phase 8: Production hardening
- Phase 9: Channels & dispatcher
- Phase 10: Advanced features
- P1: Extended capabilities

### Check Provider Connectivity

```bash
nexus provider verify
```

---

## Basic Usage

### 1. Create a Simple Agent

```python
from nexus.core.agent import AgentLoop, AgentConfig
from nexus.core.tools import ToolRegistry
from nexus.adapters.llm import NVIDIAAdapter

# Create LLM adapter
llm = NVIDIAAdapter(
 api_key="nvapi-xxx",
 model="moonshotai/kimi-k2.5"
)

# Create tool registry
tools = ToolRegistry()

# Configure agent
config = AgentConfig(
 agent_id="my_agent",
 max_iterations=100
)

# Create agent loop
agent = AgentLoop(config, llm, tools)

# Run agent
response = agent.run(context, "Write a Python function to check if a number is prime")
print(response)
```

### 2. Register Custom Tools

```python
from nexus.core.tools import tool, PermissionLevel

@tool(
 name="calculate",
 description="Perform a calculation",
 parameters={"type": "object", "properties": {"expression": {"type": "string"}}},
 permission=PermissionLevel.READ
)
def calculate(expression: str) -> float:
 return eval(expression)

tools.register("calculate", calculate)
```

### 3. Use Memory

```python
from nexus.core import MemoryManager

memory = MemoryManager(db_path="memory.db")

# Save data
memory.save("task_result", {"status": "success", "output": "Hello"})

# Load data
data = memory.load("task_result")

# Search memory
results = memory.search("task", limit=10)
```

### 4. Multi-Agent Workflow

```python
from nexus.multiagent import AgentRegistry, WorkflowOrchestrator, WorkflowStep

# Create registry
registry = AgentRegistry()

# Register agents
registry.register(AgentInfo(
 agent_id="researcher",
 name="Research Agent",
 capabilities=["research", "analysis"]
))

registry.register(AgentInfo(
 agent_id="writer",
 name="Writer Agent",
 capabilities=["writing", "summarization"]
))

# Create workflow
workflow = [
 WorkflowStep(agent_id="researcher", task="Research topic X"),
 WorkflowStep(agent_id="writer", task="Write report", depends_on="researcher")
]

# Execute workflow
orchestrator = WorkflowOrchestrator()
result = await orchestrator.execute_workflow(workflow)
```

---

## Channels & Dispatcher

### CLI Channel

```python
from nexus.channels import CLIChannel
from nexus.dispatcher import Dispatcher

# Create channel
cli = CLIChannel()

# Create dispatcher
dispatcher = Dispatcher()
dispatcher.register_channel(cli)
dispatcher.register_handler("cli", handle_message)

# Start listening
await dispatcher.start()
```

### Telegram Channel

```python
from nexus.channels import TelegramChannel

telegram = TelegramChannel(
 bot_token="YOUR_BOT_TOKEN",
 allowed_chats=["-1001234567890"]
)

dispatcher.register_channel(telegram)
```

### Discord Channel

```python
from nexus.channels import DiscordChannel

discord = DiscordChannel(
 bot_token="YOUR_BOT_TOKEN",
 guild_id="YOUR_GUILD_ID"
)

dispatcher.register_channel(discord)
```

---

## Knowledge Graph

```python
from nexus.knowledge import KnowledgeGraph, Entity, Relation, RelationType

# Create graph
graph = KnowledgeGraph()

# Add entities
func_entity = Entity(id="func1", type="function", name="calculate_sum")
doc_entity = Entity(id="doc1", type="documentation", name="func_docs")
graph.add_entity(func_entity)
graph.add_entity(doc_entity)

# Add relation
relation = Relation(
 source_id="func1",
 target_id="doc1",
 relation_type=RelationType.DOCUMENTED_BY
)
graph.add_relation(relation)

# Find path
path = graph.find_path("func1", "doc1")
```

---

## Semantic Search

```python
from nexus.knowledge import SemanticSearch, SearchConfig

# Create search engine
config = SearchConfig(top_k=5, similarity_threshold=0.7)
search = SemanticSearch(config=config)

# Index documents
search.index_document("Python is a programming language", {"source": "wiki"})
search.index_document("Machine learning uses algorithms", {"source": "ml"})

# Search
results = search.search("programming languages")
for result in results:
 print(f"{result.id}: {result.score:.2f} - {result.content}")
```

---

## Docker Sandbox

```python
from nexus.sandbox import DockerSandbox, SandboxConfig

# Create sandbox with limits
config = SandboxConfig(
 memory_limit="256m",
 cpu_limit=0.5,
 timeout=30,
 network_disabled=True
)
sandbox = DockerSandbox(config)

# Execute Python code
result = sandbox.execute_python("print(1 + 1)")
print(result.stdout) # "2"
print(result.exit_code) # 0

# Execute JavaScript
result = sandbox.execute_javascript("console.log(1 + 1)")
```

---

## REST API

### Start Server

```bash
# Using CLI
nexus api

# Or programmatically
python -m nexus.api.rest
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/status` | GET | Framework status |
| `/agents` | POST | Create new agent |
| `/agents/{id}/run` | POST | Run agent with prompt |
| `/memory/store` | POST | Store memory entry |
| `/memory/search` | POST | Search memory |
| `/tools/execute` | POST | Execute a tool |

### Auto-Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Docker Deployment

### Build and Run

```bash
# Build image
cd docker
docker-compose build

# Run full stack
docker-compose up -d
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| NEXUS | 8000 | REST API |
| Prometheus | 9091 | Metrics collection |
| Grafana | 3000 | Visualization dashboards |
| Redis | 6379 | Distributed caching |

---

## Kubernetes Deployment

```bash
# Deploy to Kubernetes
kubectl apply -f docker/kubernetes.yml

# Check status
kubectl get pods -l app=nexus
kubectl get services
```

---

## Monitoring

### Prometheus Metrics

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

# Start metrics server
metrics.start_server(port=9090)
```

### Available Metrics

| Category | Metrics |
|----------|--------|
| LLM | `llm_requests_total`, `llm_tokens_total`, `llm_request_duration_seconds` |
| Agent | `agent_executions_total`, `agent_active` |
| Tool | `tool_executions_total`, `tool_errors_total` |
| Memory | `memory_operations_total`, `memory_size_bytes` |
| Cache | `cache_hits_total`, `cache_misses_total` |

---

## TOON Compression

```python
from nexus.compression import to_toon, from_toon

# Compress data (40% token reduction)
data = {"messages": [{"role": "user", "content": "Hello"}]}
toon_str = to_toon(data)

# Decompress
original = from_toon(toon_str)
```

---

## Event Sourcing

```python
from nexus.events import EventSourcing

# Create event sourcing
es = EventSourcing()

# Emit event
event = es.emit(
 event_type="agent_action",
 aggregate_id="agent_001",
 data={"action": "tool_call", "tool": "execute_code"}
)

# Replay events
state = es.replay("agent_001")

# Get audit trail
trail = es.get_audit_trail("agent_001")
```

---

## Plugin System

```python
from nexus.plugins import PluginManager

# Create manager
manager = PluginManager(plugin_dir=Path("plugins/"))

# Discover plugins
plugins = manager.discover()

# Load plugin
module = manager.load("my_skill")

# Install from GitHub
manager.load_from_github("https://github.com/user/nexus-skill")
```

---

## CLI Commands Reference

| Command | Description |
|---------|-------------|
| `nexus setup` | Interactive configuration wizard |
| `nexus init [PATH]` | Initialize a new project |
| `nexus run` | Run the NEXUS agent |
| `nexus doctor` | Run diagnostics |
| `nexus version` | Show version |
| `nexus provider add` | Add provider with verification |
| `nexus provider list` | List configured providers |
| `nexus provider verify` | Test provider connectivity |
| `nexus api` | Start REST API server |

---

## Makefile Commands

```bash
make install # Install dependencies
make test # Run tests with coverage
make lint # Check code quality
make format # Format with black/isort
make clean # Clean build artifacts
make run # Run NEXUS CLI
make demo # Run demo script
make api # Start REST API server
```

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=nexus

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

---

## Troubleshooting

### API Key Issues

```bash
# Verify API key is set
echo $NVIDIA_API_KEY

# Test provider connectivity
nexus provider verify
```

### Rate Limiting

If you see "Rate limit exceeded" errors:
- Reduce `rate_limit_rpm` in config
- Use distributed rate limiting with Redis

### Memory Issues

If memory is not persisting:
- Check database path permissions
- Ensure `db_path` is writable

### Docker Issues

If Docker sandbox fails:
- Ensure Docker is running: `docker ps`
- Check Docker socket permissions
- Verify image exists: `docker images`

---

## Next Steps

1. Read the [API Reference](api/README.md) for detailed documentation
2. Explore the [Architecture](architecture/overview.md) for design decisions
3. Check the [Examples](../examples/) for more usage patterns
4. Review the [PRD](../../NEXUS_PRD.md) for project scope

---

## Getting Help

- **GitHub Issues**: https://github.com/nelohenriq/nexus-framework/issues
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
