#!/usr/bin/env python3
import urllib.request
import urllib.error
import json
import yaml
from rich.console import Console
from rich.panel import Panel

console = Console()

with open("nexus.yaml") as f:
 config = yaml.safe_load(f)

llm_config = config.get("llm", {})

console.print(Panel.fit("[cyan]Testing NVIDIA NIM with Kimi K2.5[/cyan]"))
console.print(f"Provider: {llm_config.get('provider')}")
console.print(f"Model: {llm_config.get('model')}")
console.print(f"API Base: {llm_config.get('api_base')}")
console.print()

api_key = llm_config.get("api_key")
api_base = llm_config.get("api_base")
model = llm_config.get("model")

url = f"{api_base}/chat/completions"

payload = {
 "model": model,
 "messages": [
 {"role": "system", "content": "You are a helpful coding assistant."},
 {"role": "user", "content": "Write a Python function to check if a number is prime. Return only the function code."}
 ],
 "temperature": 0.7,
 "max_tokens": 500
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, method="POST")
req.add_header("Content-Type", "application/json")
req.add_header("Authorization", f"Bearer {api_key}")

console.print("[cyan]Sending request to NVIDIA NIM...[/cyan]")

try:
 with urllib.request.urlopen(req, timeout=60) as response:
 result = json.loads(response.read().decode("utf-8"))
 content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
 console.print(Panel.fit("[green]Response from Kimi K2.5[/green]"))
 console.print(content)
 usage = result.get("usage", {})
 console.print()
 console.print("[cyan]Usage Statistics:[/cyan]")
 console.print(f" Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
 console.print(f" Completion tokens: {usage.get('completion_tokens', 'N/A')}")
 console.print(f" Total tokens: {usage.get('total_tokens', 'N/A')}")
except urllib.error.HTTPError as e:
 error_body = e.read().decode("utf-8")
 console.print(f"[red]HTTP Error {e.code}: {error_body}[/red]")
except Exception as e:
 console.print(f"[red]Error: {str(e)}[/red]")
