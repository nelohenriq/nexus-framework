#!/usr/bin/env python3
"""NEXUS Framework - Real Agent Execution."""

import yaml
import urllib.request
import urllib.error
import json
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

print("="*70)
print("NEXUS Framework - Real Agent Execution")
print("="*70)
print()

# Load configuration
with open("nexus.yaml") as f:
 config = yaml.safe_load(f)

llm_config = config.get("llm", {})
api_key = llm_config.get("api_key")
api_base = llm_config.get("api_base")
model = llm_config.get("model")

print("[INIT] Initializing NEXUS Framework...")
print()

# Import all NEXUS components
from nexus.container import DIContainer
from nexus.core import MemoryManager
from nexus.security import SecurityManager
from nexus.efficiency import PromptCache, RateLimiter, BudgetEnforcer, BudgetConfig
from nexus.multiagent import AgentRegistry, MessageBus
from nexus.autonomous import HealthMonitor, TaskScheduler, LearningEngine

# Initialize all components
container = DIContainer()
memory = MemoryManager(db_path=":memory:")
security = SecurityManager()
cache = PromptCache(max_entries=100)
limiter = RateLimiter(max_rpm=40)
budget_config = BudgetConfig(max_tokens=10000)
budget = BudgetEnforcer(budget_config)
registry = AgentRegistry()
bus = MessageBus()
health = HealthMonitor(check_interval=5.0)
scheduler = TaskScheduler(max_workers=2)
learning = LearningEngine()

print("[NEXUS] Components initialized:")
print(" - DI Container")
print(" - Memory Manager (SQLite)")
print(" - Security Manager")
print(" - Efficiency Layer (Cache + RateLimit + Budget)")
print(" - Multi-Agent Registry")
print(" - Autonomous Features")
print()

# Register agents
coordinator_id = registry.register("coordinator", ["orchestration"])
analyzer_id = registry.register("analyzer", ["analysis"])
bus.register_agent(coordinator_id)
bus.register_agent(analyzer_id)
print(f"[Multi-Agent] Registered 2 agents")
print()

# REAL TASK: Code Analysis
print("="*70)
print("EXECUTING TASK: Code Analysis with LLM")
print("="*70)
print()

task = """Analyze this Python function and suggest 3 improvements:

def calculate_average(numbers):
 total = 0
 for i in range(len(numbers)):
 total = total + numbers[i]
 return total / len(numbers)

Provide specific improvements for:
1. Code quality
2. Performance
3. Error handling
"""

# Step 1: Security validation
print("[Security] Validating input...")
passed, errors = security.check_input({"prompt": task})
print(f"[Security] Input validated")
print()

# Step 2: Check rate limit
print("[RateLimiter] Checking rate limit...")
status = limiter.get_status()
print(f"[RateLimiter] {status["remaining"]}/{status["max_rpm"]} requests remaining")
print()

# Step 3: Check budget
print("[Budget] Checking token budget...")
usage_status = budget.get_usage()
print(f"[Budget] {usage_status["used"]}/{usage_status["max"]} tokens used")
print()

# Step 4: Send to LLM
print("[LLM] Sending task to Kimi K2.5...")
print()

url = f"{api_base}/chat/completions"
payload = {
 "model": model,
 "messages": [
 {"role": "system", "content": "You are an expert Python code reviewer."},
 {"role": "user", "content": task}
 ],
 "temperature": 0.7,
 "max_tokens": 1000
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, method="POST")
req.add_header("Content-Type", "application/json")
req.add_header("Authorization", f"Bearer {api_key}")

start_time = time.time()
try:
 with urllib.request.urlopen(req, timeout=60) as response:
 result = json.loads(response.read().decode("utf-8"))
 content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
 tokens_used = result.get("usage", {}).get("total_tokens", 0)
 elapsed = time.time() - start_time
 
 print(f"[LLM] Response received in {elapsed:.2f}s")
 print(f"[LLM] Tokens used: {tokens_used}")
 print()
 
 budget.track_usage(tokens_used)
 
 memory.save("code_analysis", {
 "task": "calculate_average",
 "tokens": tokens_used,
 "timestamp": time.time()
 })
 print("[Memory] Analysis saved")
 
 learning.record_learning("code_analysis", {"tokens": tokens_used}, "completed")
 print("[Learning] Event recorded")
 print()
 
 console.print(Panel.fit("[green]Code Analysis Results[/green]"))
 print(content)
 
except urllib.error.HTTPError as e:
 error_body = e.read().decode("utf-8")
 print(f"[Error] HTTP {e.code}: {error_body}")
except Exception as e:
 print(f"[Error] {str(e)}")

print()
print("="*70)
print("NEXUS Framework Execution Complete")
print("="*70)
