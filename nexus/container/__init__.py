"""
NEXUS Framework - Dependency Injection Container

DI container for hexagonal architecture.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, TypeVar, get_type_hints

T = TypeVar("T")

class Lifecycle(str, Enum):
    """Adapter lifecycle options."""
    SINGLETON = "singleton"
    SCOPED = "scoped"
    TRANSIENT = "transient"

@dataclass
class Binding:
    """Binding between Port and Adapter."""
    port: type
    adapter: type | Callable[..., T]
    lifecycle: Lifecycle = Lifecycle.SINGLETON
    instance: Any = None
    factory: Callable[[], T] | None = None

class AdapterRegistry:
    """Registry for dynamic adapter discovery."""
    def __init__(self) -> None:
        self._adapters: dict[str, type] = {}
        self._defaults: dict[type, str] = {}

    def register(self, name: str, adapter: type, default_for: type | None = None) -> None:
        self._adapters[name] = adapter
        if default_for:
            self._defaults[default_for] = name

    def get(self, name: str) -> type | None:
        return self._adapters.get(name)

    def get_default(self, port: type) -> type | None:
        name = self._defaults.get(port)
        if name:
            return self._adapters.get(name)
        return None

    def list_all(self) -> dict[str, type]:
        return self._adapters.copy()

class DIContainer:
    """Dependency Injection Container."""
    def __init__(self) -> None:
        self._bindings: dict[type, Binding] = {}
        self._singletons: dict[type, Any] = {}
        self._registry = AdapterRegistry()
        self._config: dict[str, Any] = {}

    def bind(self, port: type[T], adapter: type, lifecycle: Lifecycle = Lifecycle.SINGLETON) -> None:
        self._bindings[port] = Binding(port=port, adapter=adapter, lifecycle=lifecycle)

    def bind_instance(self, port: type[T], instance: T) -> None:
        self._bindings[port] = Binding(port=port, adapter=type(instance), lifecycle=Lifecycle.SINGLETON, instance=instance)

    def bind_factory(self, port: type[T], factory: Callable[[], T], lifecycle: Lifecycle = Lifecycle.SINGLETON) -> None:
        self._bindings[port] = Binding(port=port, adapter=factory, lifecycle=lifecycle, factory=factory)

    def resolve(self, port: type[T]) -> T:
        if port not in self._bindings:
            default_adapter = self._registry.get_default(port)
            if default_adapter:
                self.bind(port, default_adapter)
            else:
                raise KeyError(f"No binding for {port.__name__}")
        binding = self._bindings[port]
        if binding.lifecycle == Lifecycle.SINGLETON and port in self._singletons:
            return self._singletons[port]
        if binding.instance is not None:
            instance = binding.instance
        elif binding.factory is not None:
            instance = binding.factory()
        else:
            instance = self._create(binding.adapter)
        if binding.lifecycle == Lifecycle.SINGLETON:
            self._singletons[port] = instance
        return instance

    def _create(self, adapter: type | Callable[..., T]) -> T:
        if callable(adapter) and not inspect.isclass(adapter):
            return adapter()
        hints = get_type_hints(adapter.__init__)
        kwargs = {}
        for name, hint in hints.items():
            if name == "return" or name == "self":
                continue
            try:
                kwargs[name] = self.resolve(hint)
            except KeyError:
                pass
        return adapter(**kwargs)

    def configure(self, config: dict[str, Any]) -> None:
        self._config = config

    @property
    def config(self) -> dict[str, Any]:
        return self._config

    def get_registry(self) -> AdapterRegistry:
        return self._registry

    def create_scope(self) -> "DIScope":
        return DIScope(self)

class DIScope:
    """Scoped container for request-scoped instances."""
    def __init__(self, container: DIContainer) -> None:
        self._container = container
        self._scoped_instances: dict[type, Any] = {}

    def resolve(self, port: type[T]) -> T:
        binding = self._container._bindings.get(port)
        if binding and binding.lifecycle == Lifecycle.SCOPED:
            if port not in self._scoped_instances:
                self._scoped_instances[port] = self._container._create(binding.adapter)
            return self._scoped_instances[port]
        return self._container.resolve(port)

__all__ = ["Lifecycle", "Binding", "AdapterRegistry", "DIContainer", "DIScope"]
