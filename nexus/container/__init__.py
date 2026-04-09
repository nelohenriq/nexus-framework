"""
NEXUS Framework - Dependency Injection Container

This module provides the DI container for hexagonal architecture.
Enables clean separation between Ports (protocols) and Adapters (implementations).

Features:
- Auto-wiring of dependencies
- Lifecycle management (singleton, scoped, transient)
- Adapter registry for dynamic loading
- Configuration-based binding
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, TypeVar, get_type_hints

T = TypeVar("T")


class Lifecycle(str, Enum):
 """Adapter lifecycle options."""
 SINGLETON = "singleton" # One instance for entire application
 SCOPED = "scoped" # One instance per scope (e.g., request)
 TRANSIENT = "transient" # New instance every time


@dataclass
class Binding:
 """Represents a binding between a Port and an Adapter."""
 port: type
 adapter: type | Callable[..., T]
 lifecycle: Lifecycle = Lifecycle.SINGLETON
 instance: Any = None
 factory: Callable[[], T] | None = None


class AdapterRegistry:
 """Registry for dynamic adapter discovery.

 Allows registering adapters by name and retrieving them dynamically.
 Useful for configuration-based adapter loading.
 """

 def __init__(self) -> None:
 self._adapters: dict[str, type] = {}
 self._defaults: dict[type, str] = {}

 def register(
 self,
 name: str,
 adapter: type,
 default_for: type | None = None,
 ) -> None:
 """Register an adapter.

 Args:
 name: Adapter name (e.g., 'openai', 'ollama')
 adapter: Adapter class
 default_for: Port this is the default adapter for
 """
 self._adapters[name] = adapter
 if default_for:
 self._defaults[default_for] = name

 def get(self, name: str) -> type | None:
 """Get an adapter by name."""
 return self._adapters.get(name)

 def get_default(self, port: type) -> type | None:
 """Get the default adapter for a Port."""
 name = self._defaults.get(port)
 if name:
 return self._adapters.get(name)
 return None

 def list_all(self) -> dict[str, type]:
 """List all registered adapters."""
 return self._adapters.copy()


class DIContainer:
 """Dependency Injection Container for hexagonal architecture.

 Features:
 - Auto-wiring: Automatically resolves constructor dependencies
 - Lifecycle management: Singleton, scoped, transient instances
 - Configuration-based binding: Bind from config dict
 - Adapter registry: Dynamic adapter loading

 Usage:
 >>> container = DIContainer()
 >>> container.bind(LLMPort, OpenAIAdapter)
 >>> llm = container.resolve(LLMPort)

 Configuration-based:
 >>> config = {
 ... 'llm': {'provider': 'openai', 'model': 'gpt-4'},
 ... 'memory': {'provider': 'sqlite'}
 ... }
 >>> container.configure(config)
 """

 def __init__(self) -> None:
 self._bindings: dict[type, Binding] = {}
 self._singletons: dict[type, Any] = {}
 self._registry = AdapterRegistry()
 self._config: dict[str, Any] = {}

 def bind(
 self,
 port: type[T],
 adapter: type | Callable[..., T],
 lifecycle: Lifecycle = Lifecycle.SINGLETON,
 ) -> None:
 """Bind a Port to an Adapter.

 Args:
 port: The Port protocol/interface
 adapter: The Adapter implementation
 lifecycle: Instance lifecycle
 """
 self._bindings[port] = Binding(
 port=port,
 adapter=adapter,
 lifecycle=lifecycle,
 )

 def bind_instance(self, port: type[T], instance: T) -> None:
 """Bind a Port to a specific instance.

 Useful for pre-configured instances.

 Args:
 port: The Port protocol/interface
 instance: The instance to use
 """
 self._bindings[port] = Binding(
 port=port,
 adapter=type(instance),
 lifecycle=Lifecycle.SINGLETON,
 instance=instance,
 )

 def bind_factory(
 self,
 port: type[T],
 factory: Callable[[], T],
 lifecycle: Lifecycle = Lifecycle.SINGLETON,
 ) -> None:
 """Bind a Port to a factory function.

 Useful when construction needs custom logic.

 Args:
 port: The Port protocol/interface
 factory: Factory function that creates instances
 lifecycle: Instance lifecycle
 """
 self._bindings[port] = Binding(
 port=port,
 adapter=factory,
 lifecycle=lifecycle,
 factory=factory,
 )

 def resolve(self, port: type[T]) -> T:
 """Resolve a Port to its Adapter instance.

 Handles auto-wiring of dependencies.

 Args:
 port: The Port protocol/interface to resolve

 Returns:
 An instance of the bound adapter

 Raises:
 KeyError: If no binding exists for the port
 """
 if port not in self._bindings:
 # Try to find default from registry
 default_adapter = self._registry.get_default(port)
 if default_adapter:
 self.bind(port, default_adapter)
 else:
 raise KeyError(f"No binding for {port.__name__}")

 binding = self._bindings[port]

 # Check for cached singleton
 if binding.lifecycle == Lifecycle.SINGLETON and port in self._singletons:
 return self._singletons[port]

 # Create instance
 if binding.instance is not None:
 instance = binding.instance
 elif binding.factory is not None:
 instance = binding.factory()
 else:
 instance = self._create(binding.adapter)

 # Cache singleton
 if binding.lifecycle == Lifecycle.SINGLETON:
 self._singletons[port] = instance

 return instance

 def _create(self, adapter: type | Callable[..., T]) -> T:
 """Create an instance with auto-wiring.

 Args:
 adapter: The adapter class or factory

 Returns:
 A new instance with dependencies resolved
 """
 if callable(adapter) and not inspect.isclass(adapter):
 # It's a factory function
 return adapter()

 # Get constructor hints
 hints = get_type_hints(adapter.__init__)

 # Resolve dependencies
 kwargs = {}
 for name, hint in hints.items():
 if name == 'return' or name == 'self':
 continue
 try:
 kwargs[name] = self.resolve(hint)
 except KeyError:
 # Optional dependency
 pass

 return adapter(**kwargs)

 def configure(self, config: dict[str, Any]) -> None:
 """Configure bindings from a config dictionary.

 Config format:
 {
 'llm': {'provider': 'openai', 'model': 'gpt-4'},
 'memory': {'provider': 'sqlite', 'path': ':memory:'},
 }

 Args:
 config: Configuration dictionary
 """
 self._config = config
 # Configuration is used by adapters during resolve
 # Adapters can access container.config in their factory

 @property
 def config(self) -> dict[str, Any]:
 """Access configuration."""
 return self._config

 def get_registry(self) -> AdapterRegistry:
 """Get the adapter registry."""
 return self._registry

 def create_scope(self) -> 'DIScope':
 """Create a new scope for scoped instances.

 Returns:
 A new DIScope tied to this container
 """
 return DIScope(self)


class DIScope:
 """Scoped container for request-scoped instances.

 Instances created within a scope are shared within that scope,
 but different scopes get different instances.
 """

 def __init__(self, container: DIContainer) -> None:
 self._container = container
 self._scoped_instances: dict[type, Any] = {}

 def resolve(self, port: type[T]) -> T:
 """Resolve a Port within this scope.

 Args:
 port: The Port to resolve

 Returns:
 Instance appropriate for this scope
 """
 binding = self._container._bindings.get(port)

 if binding and binding.lifecycle == Lifecycle.SCOPED:
 if port not in self._scoped_instances:
 self._scoped_instances[port] = self._container._create(binding.adapter)
 return self._scoped_instances[port]

 return self._container.resolve(port)


__all__ = [
 'Lifecycle',
 'Binding',
 'AdapterRegistry',
 'DIContainer',
 'DIScope',
]
