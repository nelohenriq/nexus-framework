# Getting Started with NEXUS Framework

## Prerequisites

- Python 3.10 or higher
- pip package manager
- (Optional) OpenAI, Anthropic, or NVIDIA API key for LLM features

## Installation

```bash
# Clone the repository
git clone https://github.com/nelohenriq/nexus-framework.git
cd nexus-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Initialize a New Project

```bash
nexus init my_agent_project
cd my_agent_project
```

### 2. Create Configuration File

Create `nexus.yaml` in your project directory:

```yaml
# LLM Configuration
llm:
 provider: openai  # or ollama, anthropic, openai-compatible
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
 enabled: true
 layers:
 - input_validation
 - authentication
 - authorization
```

### 3. Basic Usage

```python
from nexus.container import DIContainer
from nexus.core import Message, MessageRole, AgentContext, MemoryManager

# Create DI container
container = DIContainer()

# Create agent context
context = AgentContext(agent_id="my_agent")

# Add messages
context.add_message(Message(
 role=MessageRole.USER,
 content="Hello, NEXUS!"
))

# Create memory
memory = MemoryManager()
memory.save("session", {"started": True})
```

### 4. Multi-Agent Example

```python
from nexus.multiagent import AgentRegistry, MessageBus

# Create registry
registry = AgentRegistry()

# Register agents
worker = registry.register("worker", ["compute"])
coordinator = registry.register("coordinator", ["orchestrate"])

# Create message bus
bus = MessageBus()
bus.register_agent(worker)
```

## Running Examples

The framework includes several examples:

```bash
# Simple agent example
python3 examples/simple-agent/example.py

# Multi-agent example
python3 examples/multi-agent/example.py

# Workflow example
python3 examples/workflow/example.py

# LLM chat example
python3 examples/llm-chat/example.py

# Security demo
python3 examples/security-demo/example.py
```

## Running the Demo

```bash
# Run comprehensive demo for all 6 phases
python3 nexus_demo.py
```

## Using the CLI

```bash
# Show version
nexus version

# Run diagnostics
nexus doctor
```

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `NVIDIA_API_KEY` | NVIDIA NIM API key |
| `OLLAMA_BASE_URL` | Ollama base URL (default: http://localhost:11434) |

### LLM Providers

| Provider | Configuration |
|----------|---------------|
| OpenAI | `provider: openai` |
| Anthropic | `provider: anthropic` |
| Ollama | `provider: ollama` |
| NVIDIA NIM | `provider: openai-compatible` |
| Custom | `provider: openai-compatible` with custom `api_base` |

## Next Steps

1. Read the [API Reference](../api/README.md)
2. Explore the [Examples](../../examples/)
3. Learn about [Architecture](../architecture/overview.md)
---

## Quick Setup with Setup Wizard

NEXUS provides an interactive setup wizard to configure your framework easily.

### Using `nexus setup`

The setup wizard guides you through configuring your NEXUS framework:

```bash
nexus setup
```

**Steps:**

1. **Select LLM Provider**
 ```
 Available providers:
 1. OpenAI
 2. Anthropic
 3. Ollama (Local)
 4. NVIDIA NIM
 5. OpenAI-Compatible
 
 Select provider [1-5]: 1
 ```

2. **Choose Model**
 ```
 Available models:
 1. gpt-4
 2. gpt-4-turbo
 3. gpt-3.5-turbo
 
 Select model [1-3]: 1
 ```

3. **Enter API Key**
 ```
 API Key (or press Enter to use $OPENAI_API_KEY): sk-...
 ```

4. **Configure Temperature**
 ```
 Temperature [0.7]: 0.7
 ```

5. **Configure Efficiency Settings**
 ```
 Enable prompt caching? [Y/n]: Y
 Max requests per minute [60]: 60
 Max tokens budget [100000]: 100000
 ```

6. **Configure Security Settings**
 ```
 Enable security layers? [Y/n]: Y
 
 Available security layers:
 1. input_validation
 2. authentication
 3. authorization
 4. rate_limiting
 5. audit_logging
 
 Select layers (comma-separated) [1,2,3]: 1,2,3
 ```

### Provider Management

#### Add a New Provider

```bash
nexus provider add
```

This will:
- Guide you through provider selection
- Test the connection before saving
- Validate your API key
- Confirm model availability

#### List Configured Provider

```bash
nexus provider list
```

Output:
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

#### Verify Provider Connectivity

```bash
nexus provider verify
```

Tests:
- API key validity
- Endpoint availability
- Model availability

---

## Environment Variables

You can also configure providers using environment variables:

```bash
# OpenAI
export OPENAI_API_KEY=sk-...

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# NVIDIA NIM
export NVIDIA_API_KEY=nvapi-...

# Generic LLM
export LLM_API_KEY=your-key
export LLM_BASE_URL=https://your-api-endpoint/v1
```

---

## Supported Providers

| Provider | Models | API Base |
|----------|--------|----------|
| **OpenAI** | gpt-4, gpt-4-turbo, gpt-3.5-turbo | https://api.openai.com/v1 |
| **Anthropic** | claude-3-opus, claude-3-sonnet, claude-3-haiku | https://api.anthropic.com/v1 |
| **Ollama** | llama2, codellama, mistral | http://localhost:11434 |
| **NVIDIA NIM** | llama3-8b-instruct, deepseek-coder-6.7b-instruct | https://integrate.api.nvidia.com/v1 |
| **OpenAI-Compatible** | Custom models | Custom endpoint |
