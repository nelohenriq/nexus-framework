"""
NEXUS Framework - Setup Wizard

Interactive configuration wizard for NEXUS framework.
"""

from __future__ import annotations

import os
import sys
import yaml
import time
import threading
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field


@dataclass
class ProviderConfig:
    """LLM Provider configuration."""
    name: str
    provider: str
    model: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096


class SetupWizard:
    """Interactive setup wizard for NEXUS configuration."""

    PROVIDERS = {
        "openai": {"name": "OpenAI", "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"], "api_base": "https://api.openai.com/v1"},
        "anthropic": {"name": "Anthropic", "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"], "api_base": "https://api.anthropic.com/v1"},
        "ollama": {"name": "Ollama (Local)", "models": ["llama2", "codellama", "mistral"], "api_base": "http://localhost:11434"},
        "nvidia": {"name": "NVIDIA NIM", "models": ["meta/llama3-8b-instruct", "deepseek-ai/deepseek-coder-6.7b-instruct"], "api_base": "https://integrate.api.nvidia.com/v1"},
        "openai-compatible": {"name": "OpenAI-Compatible", "models": ["custom-model"], "api_base": "http://localhost:8000/v1"}
    }

    def __init__(self, config_path: str = "nexus.yaml"):
        self.config_path = Path(config_path)
        self.config: dict[str, Any] = {}
        self.providers: list[ProviderConfig] = []

    def run(self) -> bool:
        """Run the interactive setup wizard."""
        print("=" * 60)
        print(" NEXUS Framework Setup Wizard")
        print("=" * 60)
        print()

        # Step 1: LLM Provider Configuration
        print("[Step 1] LLM Provider Configuration")
        print("-" * 40)
        self._configure_provider()

        # Step 2: Efficiency Settings
        print()
        print("[Step 2] Efficiency Settings")
        print("-" * 40)
        self._configure_efficiency()

        # Step 3: Security Settings
        print()
        print("[Step 3] Security Settings")
        print("-" * 40)
        self._configure_security()

        # Step 4: Save Configuration
        print()
        print("[Step 4] Save Configuration")
        print("-" * 40)
        return self._save_config()

    def _configure_provider(self) -> None:
        """Configure LLM provider."""
        print()
        print("Available providers:")
        for i, (key, info) in enumerate(self.PROVIDERS.items(), 1):
            name = info.get("name", key)
            print(f" {i}. {name}")
        print()

        while True:
            try:
                choice = input("Select provider [1-5]: ").strip()
                idx = int(choice) - 1
                provider_key = list(self.PROVIDERS.keys())[idx]
                break
            except (ValueError, IndexError):
                print("Invalid choice. Please enter 1-5.")

        provider_info = self.PROVIDERS[provider_key]
        name = provider_info.get("name", provider_key)
        print(f"\nSelected: {name}")

        # Select model
        print("\nAvailable models:")
        models = provider_info.get("models", [])
        for i, model in enumerate(models, 1):
            print(f" {i}. {model}")
        print()

        while True:
            try:
                num_models = len(models)
                prompt = f"Select model [1-{num_models}]: "
                choice = input(prompt).strip()
                idx = int(choice) - 1
                model = models[idx]
                break
            except (ValueError, IndexError):
                print("Invalid choice.")

        # API Key
        api_key = None
        if provider_key not in ["ollama"]:
            key_name = provider_key.upper().replace("-", "_")
            env_var = f"{key_name}_API_KEY"
            prompt = f"API Key (or press Enter to use ${env_var}): "
            api_key = input(prompt).strip()
            if not api_key:
                api_key = f"${{{env_var}}}"

        # Temperature
        temp_input = input("Temperature [0.7]: ").strip()
        temperature = float(temp_input) if temp_input else 0.7

        # Store provider config
        api_base = provider_info.get("api_base", "")
        self.config["llm"] = {
            "provider": provider_key,
            "model": model,
            "api_key": api_key,
            "api_base": api_base,
            "temperature": temperature,
            "max_tokens": 4096
        }

        print(f"\nProvider configured: {provider_key}/{model}")

    def _configure_efficiency(self) -> None:
        """Configure efficiency settings."""
        print()

        # Prompt Caching
        cache_input = input("Enable prompt caching? [Y/n]: ").strip().lower()
        cache_enabled = cache_input != "n"

        # Rate Limiting
        rpm_input = input("Max requests per minute [60]: ").strip()
        max_rpm = int(rpm_input) if rpm_input else 60

        # Budget
        budget_input = input("Max tokens budget [100000]: ").strip()
        max_tokens = int(budget_input) if budget_input else 100000

        self.config["efficiency"] = {
            "cache_enabled": cache_enabled,
            "max_rpm": max_rpm,
            "budget": {"max_tokens": max_tokens}
        }

        print(f"\nEfficiency: cache={cache_enabled}, rpm={max_rpm}, budget={max_tokens}")

    def _configure_security(self) -> None:
        """Configure security settings."""
        print()

        sec_input = input("Enable security layers? [Y/n]: ").strip().lower()
        security_enabled = sec_input != "n"

        layers = []
        if security_enabled:
            print("\nAvailable security layers:")
            all_layers = ["input_validation", "authentication", "authorization", "rate_limiting", "audit_logging"]
            for i, layer in enumerate(all_layers, 1):
                print(f" {i}. {layer}")

            layers_input = input("Select layers (comma-separated) [1,2,3]: ").strip()
            if not layers_input:
                layers = ["input_validation", "authentication", "authorization"]
            else:
                parts = layers_input.split(",")
                indices = []
                for p in parts:
                    p = p.strip()
                    if p.isdigit():
                        indices.append(int(p) - 1)
                valid_layers = []
                for i in indices:
                    if 0 <= i < len(all_layers):
                        valid_layers.append(all_layers[i])
                layers = valid_layers

        self.config["security"] = {
            "enabled": security_enabled,
            "layers": layers
        }

        num_layers = len(layers)
        print(f"\nSecurity: enabled={security_enabled}, layers={num_layers}")

    def _save_config(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_path, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            print(f"\nConfiguration saved to: {self.config_path}")
            return True
        except Exception as e:
            print(f"\nError saving configuration: {e}")
            return False


class ProviderVerifier:
    """Verify LLM provider connectivity."""

    def __init__(self):
        self.results: dict[str, Any] = {}

    def verify_provider(self, provider: str, api_key: Optional[str] = None, api_base: Optional[str] = None, model: Optional[str] = None) -> tuple[bool, str]:
        """Verify provider connection."""
        print(f"\nVerifying {provider}...")

        # Expand environment variables
        if api_key and api_key.startswith("$"):
            if api_key.startswith("${"):
                env_var = api_key[2:-1]
            else:
                env_var = api_key[1:]
            api_key = os.environ.get(env_var, "")

        # Provider-specific verification
        if provider == "ollama":
            return self._verify_ollama(model)
        elif provider == "openai":
            return self._verify_openai(api_key, model)
        elif provider == "anthropic":
            return self._verify_anthropic(api_key, model)
        elif provider == "nvidia":
            return self._verify_nvidia(api_key, model)
        else:
            return self._verify_openai_compatible(api_key, api_base, model)

    def _verify_ollama(self, model: Optional[str]) -> tuple[bool, str]:
        """Verify Ollama connection."""
        import urllib.request
        import json

        try:
            url = "http://localhost:11434/api/tags"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                models = [m["name"] for m in data.get("models", [])]
                num = len(models)
                return True, f"Connected. {num} models available."
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    def _verify_openai(self, api_key: Optional[str], model: Optional[str]) -> tuple[bool, str]:
        """Verify OpenAI connection."""
        if not api_key:
            return False, "No API key provided."
        return self._verify_openai_compatible(api_key, "https://api.openai.com/v1", model)

    def _verify_anthropic(self, api_key: Optional[str], model: Optional[str]) -> tuple[bool, str]:
        """Verify Anthropic connection."""
        if not api_key:
            return False, "No API key provided."
        return True, "API key provided (verification pending)."

    def _verify_nvidia(self, api_key: Optional[str], model: Optional[str]) -> tuple[bool, str]:
        """Verify NVIDIA NIM connection."""
        if not api_key:
            return False, "No API key provided."
        return self._verify_openai_compatible(api_key, "https://integrate.api.nvidia.com/v1", model)

    def _verify_openai_compatible(self, api_key: Optional[str], api_base: Optional[str], model: Optional[str]) -> tuple[bool, str]:
        """Verify OpenAI-compatible endpoint."""
        import urllib.request
        import json

        if not api_key:
            return False, "No API key provided."

        try:
            url = f"{api_base}/models"
            req = urllib.request.Request(url)
            req.add_header("Authorization", f"Bearer {api_key}")
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                models = data.get("data", [])
                num = len(models)
                return True, f"Connected. {num} models available."
        except Exception as e:
            return False, f"Connection failed: {str(e)}"


def add_provider(config_path: str = "nexus.yaml") -> bool:
    """Add a new provider to existing configuration."""
    wizard = SetupWizard(config_path)

    # Load existing config if exists
    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                loaded = yaml.safe_load(f)
                wizard.config = loaded if loaded else {}
        except Exception:
            pass

    print("=" * 60)
    print(" Add Provider Wizard")
    print("=" * 60)

    # Configure new provider
    wizard._configure_provider()

    # Verify
    verifier = ProviderVerifier()
    llm_config = wizard.config.get("llm", {})
    success, message = verifier.verify_provider(
        provider=llm_config.get("provider"),
        api_key=llm_config.get("api_key"),
        api_base=llm_config.get("api_base"),
        model=llm_config.get("model")
    )

    print(f"\nVerification: {message}")

    if success:
        save = input("Save configuration? [Y/n]: ").strip().lower()
        if save != "n":
            return wizard._save_config()
    return True

    return False


def run_setup(config_path: str = "nexus.yaml") -> bool:
    """Run the setup wizard."""
    wizard = SetupWizard(config_path)
    return wizard.run()