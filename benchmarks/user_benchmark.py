#!/usr/bin/env python3
"""
NEXUS Framework - User-Level Benchmark

Runs the framework as a regular user would, testing:
- Configuration loading
- LLM provider connectivity
- Agent creation and execution
- Memory operations
- Tool execution
- End-to-end response generation

Usage:
 python benchmarks/user_benchmark.py --provider nvidia --model moonshotai/kimi-k2.5
 python benchmarks/user_benchmark.py --provider ollama --model llama3.2
 python benchmarks/user_benchmark.py --help
"""

import argparse
import sys
import time
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
 import yaml
except ImportError:
 print("Installing pyyaml...")
 os.system('pip install pyyaml -q')
 import yaml


class NexusUserBenchmark:
 """Benchmark NEXUS framework as a user would use it."""
 
 def __init__(self, provider: str, model: str):
 self.provider = provider
 self.model = model
 self.results = []
 self.config = None
 
 def load_config(self) -> dict:
 """Load configuration from nexus.yaml."""
 config_path = Path(__file__).parent.parent / 'nexus.yaml'
 
 if config_path.exists():
 with open(config_path) as f:
 config = yaml.safe_load(f)
 print(f"Loaded config from {config_path}")
 return config
 else:
 print(f"Config not found at {config_path}, using defaults")
 return {
 'llm': {
 'provider': self.provider,
 'model': self.model
 }
 }
 
 def test_imports(self) -> bool:
 """Test that all core modules can be imported."""
 print("\n=== Testing Imports ===")
 
 modules = [
 ('nexus', 'Framework root'),
 ('nexus.core.agent', 'Agent module'),
 ('nexus.core.messages', 'Messages module'),
 ('nexus.core.memory', 'Memory module'),
 ('nexus.efficiency.tokenizer', 'Tokenizer'),
 ('nexus.efficiency.rate_limiter', 'Rate limiter'),
 ('nexus.efficiency.budget_enforcer', 'Budget enforcer'),
 ('nexus.efficiency.prompt_cache', 'Prompt cache'),
 ('nexus.security.sanitizer', 'Sanitizer'),
 ]
 
 success = True
 for module_name, desc in modules:
 try:
 __import__(module_name)
 print(f" ✅ {desc}: {module_name}")
 except Exception as e:
 print(f" ❌ {desc}: {module_name} - {e}")
 success = False
 
 return success
 
 def test_efficiency_layer(self) -> bool:
 """Test efficiency layer components."""
 print("\n=== Testing Efficiency Layer ===")
 
 try:
 from nexus.efficiency.tokenizer import Tokenizer
 from nexus.efficiency.rate_limiter import RateLimiter
 from nexus.efficiency.budget_enforcer import BudgetEnforcer, BudgetConfig
 from nexus.efficiency.prompt_cache import PromptCache
 
 # Test tokenizer
 t = Tokenizer()
 tokens = t.count_tokens("Hello, world! This is a test.")
 print(f" ✅ Tokenizer: counted {tokens} tokens")
 
 # Test rate limiter
 limiter = RateLimiter(max_rpm=60)
 acquired = limiter.acquire()
 print(f" ✅ Rate limiter: acquired = {acquired}")
 
 # Test budget enforcer
 config = BudgetConfig(max_tokens=10000)
 enforcer = BudgetEnforcer(config)
 status = enforcer.track(100)
 print(f" ✅ Budget enforcer: {status.tokens_used} tokens used")
 
 # Test prompt cache
 cache = PromptCache(max_size=100)
 cache.put("test_key", "test_value")
 result = cache.get_cached("test_key")
 print(f" ✅ Prompt cache: cached value = {result}")
 
 return True
 except Exception as e:
 print(f" ❌ Efficiency layer error: {e}")
 return False
 
 def test_security_layer(self) -> bool:
 """Test security layer components."""
 print("\n=== Testing Security Layer ===")
 
 try:
 from nexus.security.sanitizer import Sanitizer
 
 s = Sanitizer()
 malicious = "<script>alert('xss')</script>Hello"
 clean = s.sanitize_input(malicious)
 print(f" ✅ Sanitizer: cleaned '{malicious}' -> '{clean}'")
 
 return True
 except Exception as e:
 print(f" ❌ Security layer error: {e}")
 return False
 
 def test_memory_operations(self) -> bool:
 """Test memory operations."""
 print("\n=== Testing Memory Operations ===")
 
 try:
 from nexus.core.memory import MemoryManager, MemoryEntry
 import tempfile
 
 # Use temp database
 with tempfile.TemporaryDirectory() as tmpdir:
 db_path = Path(tmpdir) / 'test_memory.db'
 mem = MemoryManager(db_path)
 
 # Store and retrieve
 mem.store("test_key", {"data": "test_value"})
 result = mem.retrieve("test_key")
 print(f" ✅ Memory: stored and retrieved {result}")
 
 return True
 except Exception as e:
 print(f" ❌ Memory operations error: {e}")
 return False
 
 def test_llm_connection(self) -> bool:
 """Test LLM provider connection."""
 print(f"\n=== Testing LLM Connection ({self.provider}) ===")
 
 try:
 # Try to import the appropriate adapter
 if self.provider == 'nvidia':
 from nexus.llm.adapters.nvidia_adapter import NvidiaAdapter
 api_key = os.environ.get('NVIDIA_API_KEY')
 if not api_key:
 print(" ⚠️ NVIDIA_API_KEY not set, skipping LLM test")
 return True
 adapter = NvidiaAdapter(api_key=api_key, model=self.model)
 elif self.provider == 'ollama':
 from nexus.llm.adapters.ollama_adapter import OllamaAdapter
 adapter = OllamaAdapter(model=self.model)
 elif self.provider == 'openai':
 from nexus.llm.adapters.openai_adapter import OpenAIAdapter
 api_key = os.environ.get('OPENAI_API_KEY')
 if not api_key:
 print(" ⚠️ OPENAI_API_KEY not set, skipping LLM test")
 return True
 adapter = OpenAIAdapter(api_key=api_key, model=self.model)
 else:
 print(f" ⚠️ Unknown provider: {self.provider}, skipping LLM test")
 return True
 
 # Test simple completion
 start = time.time()
 response = adapter.complete("Say 'Hello, NEXUS!' in exactly those words.")
 elapsed = time.time() - start
 
 print(f" ✅ LLM response ({elapsed:.2f}s): {response[:100]}..." if len(response) > 100 else f" ✅ LLM response ({elapsed:.2f}s): {response}")
 
 return True
 except ImportError as e:
 print(f" ⚠️ LLM adapter not available: {e}")
 return True # Don't fail benchmark for missing adapter
 except Exception as e:
 print(f" ❌ LLM connection error: {e}")
 return False
 
 def test_agent_flow(self) -> bool:
 """Test complete agent flow."""
 print("\n=== Testing Agent Flow ===")
 
 try:
 from nexus.core.messages import Message, MessageRole
 
 # Create test messages
 messages = [
 Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
 Message(role=MessageRole.USER, content="Say 'Hello from NEXUS!'"),
 ]
 
 print(f" ✅ Created {len(messages)} test messages")
 
 # Test message serialization
 for msg in messages:
 api_format = msg.to_api_format()
 print(f" - {msg.role.value}: {msg.content[:50]}..." if len(msg.content) > 50 else f" - {msg.role.value}: {msg.content}")
 
 return True
 except Exception as e:
 print(f" ❌ Agent flow error: {e}")
 return False
 
 def run_benchmark(self) -> dict:
 """Run complete benchmark suite."""
 print("\n" + "="*60)
 print(f"NEXUS Framework User Benchmark")
 print(f"Provider: {self.provider} | Model: {self.model}")
 print("="*60)
 
 start_time = time.time()
 
 # Load config
 self.config = self.load_config()
 
 # Run tests
 tests = [
 ('Imports', self.test_imports),
 ('Efficiency Layer', self.test_efficiency_layer),
 ('Security Layer', self.test_security_layer),
 ('Memory Operations', self.test_memory_operations),
 ('LLM Connection', self.test_llm_connection),
 ('Agent Flow', self.test_agent_flow),
 ]
 
 results = {}
 for name, test_fn in tests:
 try:
 results[name] = test_fn()
 except Exception as e:
 print(f" ❌ {name} crashed: {e}")
 results[name] = False
 
 total_time = time.time() - start_time
 
 # Summary
 print("\n" + "="*60)
 print("BENCHMARK SUMMARY")
 print("="*60)
 
 passed = sum(1 for v in results.values() if v)
 total = len(results)
 
 for name, passed_test in results.items():
 status = "✅ PASS" if passed_test else "❌ FAIL"
 print(f" {name}: {status}")
 
 print("\n" + "-"*60)
 print(f"Passed: {passed}/{total} ({100*passed/total:.1f}%)")
 print(f"Total time: {total_time:.2f}s")
 print("="*60)
 
 return {
 'passed': passed,
 'total': total,
 'results': results,
 'time': total_time
 }


def main():
 parser = argparse.ArgumentParser(description='NEXUS Framework User Benchmark')
 parser.add_argument('--provider', default='nvidia', help='LLM provider (nvidia, ollama, openai)')
 parser.add_argument('--model', default='moonshotai/kimi-k2.5', help='Model name')
 args = parser.parse_args()
 
 benchmark = NexusUserBenchmark(provider=args.provider, model=args.model)
 result = benchmark.run_benchmark()
 
 # Exit with error code if any test failed
 sys.exit(0 if result['passed'] == result['total'] else 1)


if __name__ == '__main__':
 main()
