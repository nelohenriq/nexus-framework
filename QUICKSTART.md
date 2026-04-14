# NEXUS Framework - Quick Start Guide

## Prerequisites

- Python 3.11+
- Git
- API key (NVIDIA, OpenAI, or Ollama)

---

## Quick Setup (5 minutes)

### 1. Clone and Install

```bash
git clone https://github.com/nelohenriq/nexus-framework.git
cd nexus-framework

python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

pip install -e .
pip install pytest pyyaml tiktoken bleach
```

### 2. Configure API Key

```bash
# Create .env file
cp .env.example .env

# Edit .env with your API key:
# NVIDIA_API_KEY=nvapi-xxx
# or
# OPENAI_API_KEY=sk-xxx
```

### 3. Create Configuration

Create `nexus.yaml`:

```yaml
llm:
 provider: nvidia
 model: moonshotai/kimi-k2.5
 base_url: https://integrate.api.nvidia.com/v1

agent:
 name: nexus-agent
 max_tokens: 4096
 temperature: 0.7

efficiency:
 prompt_cache_size: 1000
 max_rpm: 60
 budget_tokens: 100000
```

### 4. Run Tests

```bash
# Run benchmark
python3 benchmarks/user_benchmark.py

# Run unit tests
python3 -m pytest tests/unit/core/ tests/unit/security/ -v
```

---

## Running Examples

### Hello NEXUS

```bash
cd examples/hello-nexus
python3 -c "import sys; sys.path.insert(0, '../..'); from nexus.core.messages import Message, MessageRole; print('NEXUS ready!')"
```

### Tokenizer Test

```python
import sys
sys.path.insert(0, '.')

from nexus.efficiency.tokenizer import Tokenizer

t = Tokenizer()
result = t.count("Hello, world!")
print(f"Tokens: {result.tokens}")
```

### Security Test

```python
import sys
sys.path.insert(0, '.')

from nexus.security.sanitizer import Sanitizer

s = Sanitizer()
clean = s.sanitize_input("<script>alert('xss')</script>Hello")
print(f"Clean: {clean}")
```

### Memory Test

```python
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, '.')

from nexus.core.memory import MemoryManager

with tempfile.TemporaryDirectory() as tmp:
 mem = MemoryManager(Path(tmp) / "test.db")
 mem.save("test_key", "test_value")
 result = mem.load("test_key")
 print(f"Loaded: {result}")
```

---

## Docker Setup

```bash
# Build
docker build -t nexus-framework .

# Run
 docker run -it \
 -e NVIDIA_API_KEY=nvapi-xxx \
 nexus-framework
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -e .` |
| `TIKTOKEN_AVAILABLE=False` | `pip install tiktoken` |
| API 401 error | Check API key in `.env` |
| Tests hang | Skip BudgetEnforcer tests |
| Indentation errors | Use spaces, not tabs |

---

## Project Structure

```
nexus/
├── core/ # Agent, Messages, Memory, Tools
├── efficiency/ # Tokenizer, RateLimiter, Cache
├── security/ # Sanitizer, XSS protection
├── memory/ # Stack, Palace, Temporal KG
└── cli/ # Setup wizard, TUI
```

---

## Next Steps

1. Read `README.md` for full documentation
2. Check `docs/api/README.md` for API reference
3. Run `python3 nexus_demo.py` for full demo
4. See `examples/` directory for more examples

---

## API Keys

| Provider | Get Key |
|----------|---------|
| NVIDIA NIM | https://build.nvidia.com/ |
| OpenAI | https://platform.openai.com/ |
| Anthropic | https://console.anthropic.com/ |
| Ollama | Local (no key needed) |
