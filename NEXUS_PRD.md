# NEXUS Framework - Product Requirements Document (PRD)

**Version:** 2.0.0
**Date:** 2026-04-09
**Status:** Refactored with Research Insights
**Authors:** Meta-Agentic Team
**Research Review:** Incorporated Senior Researcher Feedback

---

## Revision History

| Version | Date | Changes |
|---------|------|----------|
| 1.0.0 | 2026-04-09 | Initial PRD |
| 1.1.0 | 2026-04-09 | Added OpenAI-compatible, Ollama, built-in efficiency |
| 2.0.0 | 2026-04-09 | Refactored with researcher insights - DI container, expanded security, multimodal, 12-week timeline |

---

## Executive Summary

NEXUS is a unified, standalone agentic framework that integrates the best features from four existing frameworks while eliminating their identified weaknesses. It is designed to be:

- **Standalone** - No external backend dependencies required
- **Secure** - Security-first design with 16 fully-implemented layers
- **Performant** - Optimized architecture without sacrificing Python's flexibility
- **Extensible** - Hexagonal architecture with dependency injection container
- **Autonomous** - Built-in scheduling and background agent capabilities with checkpointing
- **User-Friendly** - Zero-glitch provider switching, simple configuration for non-technical users
- **Efficient** - Built-in token optimization, prompt caching, and context compression
- **Multimodal** - Native support for images, PDFs, and audio across all providers

### Research Review Summary

A comprehensive research review identified the following areas for improvement in v1.1.0, now addressed in v2.0.0:

| Issue Identified | Status | Resolution |
|------------------|--------|------------|
| Missing dependency injection | ✅ Fixed | Added DI container to architecture |
| Security layers lack implementation detail | ✅ Fixed | Expanded all 16 layers with algorithms |
| No multimodal normalization | ✅ Fixed | Added MultimodalPort and adapters |
| No anti-corruption layer | ✅ Fixed | Added ACL for framework integration |
| No secrets management | ✅ Fixed | Added HashiCorp Vault integration |
| SQLite concurrency concerns | ✅ Fixed | Added connection pooling, WAL mode docs |
| MVP timeline too aggressive | ✅ Fixed | Extended to 12 weeks |
| Missing ADRs | ✅ Fixed | Added Architecture Decision Records |
| No distributed rate limiting | ✅ Fixed | Added Redis-backed option |
| No budget enforcement | ✅ Fixed | Added hard stop on limits |
| No agent checkpointing | ✅ Fixed | Added state serialization for Hands |

### Framework Integration Summary

| Source Framework | Features Adopted | Problems Avoided |
|------------------|------------------|------------------|
| **Hermes** | SKILL.md format, SQLite memory, offline-first | External dependency, limited orchestration |
| **OpenClaw** | SOUL.md behavioral config, multi-channel gateway, workspace injection | 512 vulnerabilities, RCE CVEs, malicious skills |
| **Agent Zero** | Multi-agent hierarchy, tool abstraction, dynamic prompt assembly, MCP support | No persistent state, context window limits |
| **OpenFang** | Hexagonal architecture, security layers, scheduled Hands, knowledge graphs, 40 channel adapters | Rust complexity, Python integration gap |

### Key Differentiator: Zero-Glitch Provider Switching

**Critical Problem Identified:** All analyzed frameworks suffer from glitches when switching LLM providers or models - broken tool calls, lost context, format inconsistencies, and configuration complexity.

**NEXUS Solution:** Unified LLM abstraction with:
- Single configuration change switches provider/model
- Identical behavior across all OpenAI-compatible endpoints
- Built-in Ollama support for local models
- Automatic tool call translation per provider
- Graceful degradation with automatic fallbacks
- **NEW:** Multimodal normalization (images, PDFs, audio)
- **NEW:** Provider API version negotiation

---

## 1. Problem Statement

### 1.1 Current Landscape

The agentic AI ecosystem is fragmented across multiple frameworks, each with significant limitations:

1. **Hermes** requires external backend integration and lacks multi-agent orchestration
2. **OpenClaw** has critical security vulnerabilities (512 CVEs) and malicious skill ecosystem
3. **Agent Zero** lacks persistent state management and has context window limitations
4. **OpenFang** is Rust-based, creating integration challenges for Python ecosystems

### 1.2 Additional Problems Identified

| Problem | Impact | Framework(s) Affected |
|---------|--------|----------------------|
| **Provider switching glitches** | Broken tool calls, lost context, format errors | All frameworks |
| **Complex configuration** | Non-technical users cannot set up | OpenClaw, OpenFang |
| **External skill dependencies** | Skills loaded at every interaction, performance overhead | Hermes, OpenClaw |
| **No local model support** | Requires cloud API, privacy concerns | Hermes, Agent Zero |
| **Token inefficiency** | Context bloat, higher costs, rate limits | All frameworks |
| **No multimodal normalization** | Vision models work differently per provider | All frameworks |
| **No secrets management** | API keys in env vars, security risk | All frameworks |
| **No checkpointing** | Long tasks lost on failure | All frameworks |

### 1.3 Target Users

| User Persona | Description | Primary Needs |
|--------------|-------------|---------------|
| **Non-Technical User** | New to AI, wants simple setup | One-command install, easy config |
| **AI Developer** | Building AI-powered applications | Simple API, good DX, extensibility |
| **DevOps Engineer** | Deploying agents at scale | Security, monitoring, scheduling |
| **Researcher** | Experimenting with agent architectures | Flexibility, reproducibility |
| **Enterprise** | Production AI deployments | Security, compliance, reliability |
| **Privacy-Conscious User** | Wants local-only operation | Ollama support, offline capability |

### 1.4 Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Cold start time | <500ms | Benchmark suite |
| Memory footprint | <100MB idle | Resource monitoring |
| Security vulnerabilities | 0 critical/high | Security audit |
| Test coverage | >90% | pytest-cov |
| Provider switch time | <100ms | Benchmark |
| Provider switch errors | 0 | Integration tests |
| Setup time (non-technical) | <5 minutes | User testing |
| Token efficiency | 40% reduction | Cost comparison |
| Developer satisfaction | >4.5/5 | User survey |
| Multimodal latency | <200ms overhead | Benchmark |
| Checkpoint restore | <1s | Benchmark |

---

## 2. Technical Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ NEXUS FRAMEWORK ARCHITECTURE v2.0 │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ CHANNELS LAYER (OpenClaw/OpenFang inspired) │ │
│ │ CLI │ REST API │ Telegram │ Discord │ MQTT │ Web UI │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ DISPATCHER LAYER (OpenFang inspired) │ │
│ │ Message Router │ Session Manager │ Context Builder │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ AGENT LAYER (Agent Zero + Hermes inspired) │ │
│ │ Agent Loop │ Tool Registry │ Prompt Assembly │ │
│ │ Multi-Agent Hierarchy │ Skill Loader │ Checkpoint Manager │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ BUILT-IN EFFICIENCY LAYER (Not Skills!) │ │
│ │ Token Optimization │ Prompt Caching │ TOON Compression │ │
│ │ Rate Limiting (Local + Distributed) │ Budget Enforcement │ Statistics │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ MULTIMODAL LAYER (NEW) │ │
│ │ Image Normalization │ PDF Processing │ Audio Transcription │ │
│ │ Vision Adapter (GPT-4V, Claude, LLaVA) │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ PORTS LAYER (OpenFang hexagonal architecture) │ │
│ │ MemoryPort │ ChannelPort │ LLMPort │ StoragePort │ MultimodalPort │ │
│ │ KnowledgePort │ SchedulePort │ SecretsPort │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ DEPENDENCY INJECTION CONTAINER (NEW) │ │
│ │ Adapter Registry │ Configuration Binding │ Lifecycle Management │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ LLM ADAPTERS LAYER (Zero-Glitch Provider Switching) │ │
│ │ OpenAI (native) │ OpenAI-Compatible │ Ollama (local) │ │
│ │ Anthropic │ NVIDIA NIM │ Custom Endpoints │ │
│ │ API Version Negotiation │ Graceful Fallbacks │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ ANTI-CORRUPTION LAYER (NEW) │ │
│ │ Hermes ACL │ OpenClaw ACL │ Agent Zero ACL │ OpenFang ACL │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ SECURITY LAYER (16 Layers - Fully Implemented) │ │
│ │ Sandbox │ Validation │ Rate Limiting │ Audit Log │ │
│ │ Input Sanitization │ Output Filtering │ Secrets Management │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ PERSISTENCE LAYER (Hermes + Agent Zero inspired) │ │
│ │ SQLite (structured, WAL mode) │ Vector DB (semantic) │ Knowledge Graph │ │
│ │ Redis (distributed rate limits, sessions) │ Event Sourcing │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Core Components

#### 2.2.1 Dependency Injection Container (NEW)

**Critical Addition:** The DI Container enables proper hexagonal architecture with runtime adapter injection.

```python
# nexus/container/__init__.py
"""Dependency Injection Container for NEXUS Framework.

Provides:
- Adapter registry with lifecycle management
- Configuration binding
- Singleton and transient lifetimes
- Auto-wiring of dependencies
"""

from typing import TypeVar, Type, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import inspect

class Lifetime(Enum):
 SINGLETON = "singleton"
 TRANSIENT = "transient"
 SCOPED = "scoped"

@dataclass
class ServiceDescriptor:
 service_type: Type
 implementation: Type | Callable | None
 lifetime: Lifetime
 instance: Any = None
 factory: Callable | None = None

class DIContainer:
 """Dependency injection container for NEXUS.
 
 Usage:
 container = DIContainer()
 
 # Register adapter
 container.register_singleton(MemoryPort, SQLiteAdapter)
 container.register_singleton(LLMPort, OpenAIAdapter)
 
 # Resolve with auto-wiring
 memory = container.resolve(MemoryPort)
 llm = container.resolve(LLMPort)
 """
 
 def __init__(self):
 self._services: dict[Type, ServiceDescriptor] = {}
 self._instances: dict[Type, Any] = {}
 
 def register_singleton(
 self,
 service_type: Type,
 implementation: Type | Callable | None = None
 ) -> None:
 """Register a singleton service."""
 self._services[service_type] = ServiceDescriptor(
 service_type=service_type,
 implementation=implementation or service_type,
 lifetime=Lifetime.SINGLETON
 )
 
 def register_transient(
 self,
 service_type: Type,
 implementation: Type | Callable | None = None
 ) -> None:
 """Register a transient (new instance each time) service."""
 self._services[service_type] = ServiceDescriptor(
 service_type=service_type,
 implementation=implementation or service_type,
 lifetime=Lifetime.TRANSIENT
 )
 
 def register_factory(
 self,
 service_type: Type,
 factory: Callable[[], Any],
 lifetime: Lifetime = Lifetime.SINGLETON
 ) -> None:
 """Register a factory for complex object creation."""
 self._services[service_type] = ServiceDescriptor(
 service_type=service_type,
 implementation=None,
 lifetime=lifetime,
 factory=factory
 )
 
 def resolve(self, service_type: Type) -> Any:
 """Resolve a service with auto-wiring."""
 if service_type not in self._services:
 raise ValueError(f"Service {service_type} not registered")
 
 descriptor = self._services[service_type]
 
 if descriptor.lifetime == Lifetime.SINGLETON:
 if service_type in self._instances:
 return self._instances[service_type]
 
 instance = self._create_instance(descriptor)
 self._instances[service_type] = instance
 return instance
 
 return self._create_instance(descriptor)
 
 def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
 """Create instance with dependency injection."""
 if descriptor.factory:
 return descriptor.factory()
 
 implementation = descriptor.implementation
 
 # Auto-wire constructor dependencies
 sig = inspect.signature(implementation.__init__)
 kwargs = {}
 
 for name, param in sig.parameters.items():
 if name == 'self':
 continue
 if param.annotation != inspect.Parameter.empty:
 if param.annotation in self._services:
 kwargs[name] = self.resolve(param.annotation)
 
 return implementation(**kwargs)
 
 def configure_from_yaml(self, config_path: str) -> None:
 """Auto-configure container from nexus.yaml."""
 import yaml
 
 with open(config_path) as f:
 config = yaml.safe_load(f)
 
 # Register LLM adapter based on config
 llm_config = config.get('llm', {})
 provider = llm_config.get('provider', 'ollama')
 
 if provider == 'openai':
 self.register_singleton(LLMPort, OpenAIAdapter)
 elif provider == 'ollama':
 self.register_singleton(LLMPort, OllamaAdapter)
 elif provider == 'anthropic':
 self.register_singleton(LLMPort, AnthropicAdapter)
 # ... other providers
```

**Adapter Registry Integration:**

```python
# nexus/container/adapter_registry.py
class AdapterRegistry:
 """Registry for all adapters with provider detection."""
 
 ADAPTERS = {
 'memory': {
 'sqlite': 'nexus.adapters.memory.sqlite:SQLiteAdapter',
 'postgres': 'nexus.adapters.memory.postgres:PostgresAdapter',
 'chromadb': 'nexus.adapters.memory.chromadb:ChromaAdapter',
 },
 'llm': {
 'openai': 'nexus.adapters.llm.openai:OpenAIAdapter',
 'ollama': 'nexus.adapters.llm.ollama:OllamaAdapter',
 'anthropic': 'nexus.adapters.llm.anthropic:AnthropicAdapter',
 'openai-compatible': 'nexus.adapters.llm.openai_compatible:OpenAICompatibleAdapter',
 },
 'secrets': {
 'env': 'nexus.adapters.secrets.env:EnvSecretsAdapter',
 'vault': 'nexus.adapters.secrets.vault:VaultAdapter',
 'aws': 'nexus.adapters.secrets.aws:AWSSecretsAdapter',
 },
 'multimodal': {
 'pillow': 'nexus.adapters.multimodal.pillow:PillowAdapter',
 'pypdf': 'nexus.adapters.multimodal.pypdf:PDFAdapter',
 'whisper': 'nexus.adapters.multimodal.whisper:WhisperAdapter',
 },
 }
 
 @classmethod
 def load_adapter(cls, port_type: str, provider: str) -> Type:
 """Dynamically load an adapter."""
 import importlib
 
 path = cls.ADAPTERS.get(port_type, {}).get(provider)
 if not path:
 raise ValueError(f"Unknown adapter: {port_type}/{provider}")
 
 module_path, class_name = path.rsplit(':', 1)
 module = importlib.import_module(module_path)
 return getattr(module, class_name)
```

#### 2.2.2 Security Layers (Fully Implemented)

**Each security layer now has complete implementation specifications:**

| Layer | Purpose | Implementation |
|-------|---------|----------------|
| 1. Input Validation | Sanitize all inputs | **Algorithm:** Recursive type validation with depth limiting (max 100 levels). Uses Pydantic v2 for schema validation. Regex DoS protection with timeout (100ms max per regex). |
| 2. Skill Sandboxing | Isolate skill execution | **Implementation:** Docker containers with resource limits (512MB RAM, 1 CPU, 30s timeout). seccomp profiles to restrict syscalls. No network access by default. |
| 3. Rate Limiting | Prevent abuse | **Algorithm:** Token bucket with sliding window. Local (in-memory) or distributed (Redis) backends. Configurable per-provider defaults. Auto-backoff on 429. |
| 4. Output Filtering | Redact sensitive data | **Algorithm:** PII detection using presidio (Microsoft). Custom regex patterns for secrets (API keys, tokens). Audit trail of redactions. |
| 5. Audit Logging | Track all operations | **Implementation:** Structured JSON logs with append-only files. Log rotation (100MB max). Integrity via HMAC-SHA256 chain (blockchain-style). |
| 6. Authentication | Verify identity | **Implementation:** JWT with RS256 (RSA 2048). Token lifetime: 1 hour access, 7 day refresh. Refresh token rotation. OAuth2 PKCE flow for web. |
| 7. Authorization | Control access | **Implementation:** RBAC with permission inheritance. Roles: admin, developer, user, guest. Permission model: resource:action (e.g., `agent:execute`, `skill:read`). |
| 8. Encryption | Protect data at rest/transit | **Implementation:** AES-256-GCM for data at rest. TLS 1.3 for transit. Key derivation: Argon2id. Key rotation: 90-day cycle. |
| 9. Integrity | Detect tampering | **Algorithm:** SHA-256 for data, Ed25519 for code signatures. Merkle trees for audit logs. Signature verification before skill execution. |
| 10. Non-repudiation | Prove actions occurred | **Implementation:** Event sourcing with immutable event log. Each event signed with user's private key. Timestamp authority integration (RFC 3161). |
| 11. Fail-safe | Graceful degradation | **Implementation:** Circuit breaker (half-open after 30s). Retry with exponential backoff (max 3 retries, 2^n delay). Dead letter queue for failed messages. |
| 12. Resource Limits | Prevent exhaustion | **Implementation:** Memory limit via cgroups (configurable). CPU limit via taskset. File descriptors: 1024 max. Timeout middleware: 30s default. |
| 13. Dependency Verification | Validate dependencies | **Implementation:** pip-audit for CVE scanning. Hash verification for wheel files. Signed commits for internal packages. SLSA Level 3 compliance. |
| 14. Secure Defaults | Safe out of the box | **Implementation:** All features opt-in for risks. Sandbox enabled by default. No eval() or exec() allowed. HTTPS only for API endpoints. |
| 15. Incident Response | Handle security events | **Implementation:** Runbook in docs/security/runbook.md. Alerting via webhook. Isolation mode (skill disabled, agent paused). Recovery checklist. |
| 16. Compliance | Meet regulatory requirements | **Implementation:** GDPR: Data subject rights API. SOC2: Audit trail retention (7 years). HIPAA: PHI handling with BAA support. PCI-DSS: No card data storage. |

**Secrets Management Integration (Layer 8 Enhanced):**

```python
# nexus/adapters/secrets/vault.py
class VaultAdapter:
 """HashiCorp Vault integration for enterprise secrets management.
 
 Features:
 - Dynamic secrets (database credentials, API keys)
 - Automatic lease renewal
 - Audit logging for secret access
 - Encryption as a Service
 """
 
 def __init__(
 self,
 vault_addr: str = "http://localhost:8200",
 vault_token: str | None = None,
 role_id: str | None = None,
 secret_id: str | None = None
 ):
 self.client = hvac.Client(
 url=vault_addr,
 token=vault_token,
 )
 
 if role_id and secret_id:
 # AppRole authentication for production
 self.client.auth.approle.login(
 role_id=role_id,
 secret_id=secret_id
 )
 
 async def get_secret(self, path: str, key: str) -> str:
 """Retrieve a secret from Vault."""
 response = self.client.secrets.kv.v2.read_secret_version(
 path=path,
 mount_point='secret'
 )
 return response['data']['data'][key]
 
 async def get_dynamic_db_creds(self, db_name: str) -> dict:
 """Get dynamic database credentials."""
 response = self.client.secrets.database.generate_credentials(
 name=db_name
 )
 return {
 'username': response['data']['username'],
 'password': response['data']['password'],
 'lease_id': response['lease_id'],
 'lease_duration': response['lease_duration'],
 }
 
 async def renew_lease(self, lease_id: str) -> None:
 """Renew a dynamic secret lease."""
 self.client.sys.renew_lease(lease_id=lease_id)
```

#### 2.2.3 Multimodal Normalization Layer (NEW)

**Critical Addition:** Normalizes images, PDFs, and audio across all providers.

```python
# nexus/ports/multimodal_port.py
class MultimodalPort(Protocol):
 """Multimodal input/output abstraction."""
 
 async def process_image(
 self,
 image: bytes | Path,
 format: str = "auto"
 ) -> ProcessedImage: ...
 
 async def process_pdf(
 self,
 pdf: bytes | Path,
 extract_images: bool = True
 ) -> ProcessedPDF: ...
 
 async def transcribe_audio(
 self,
 audio: bytes | Path,
 language: str = "en"
 ) -> Transcription: ...

@dataclass
class ProcessedImage:
 """Normalized image representation."""
 data: bytes # Original or converted bytes
 format: str # PNG, JPEG, WEBP
 width: int
 height: int
 base64: str | None = None # For API transmission
 provider_optimized: dict[str, bytes] | None = None # Per-provider variants

@dataclass
class ProcessedPDF:
 """Normalized PDF representation."""
 text: str # Extracted text
 pages: list[str] # Per-page text
 images: list[ProcessedImage] | None = None # Extracted images
 metadata: dict # PDF metadata

@dataclass
class Transcription:
 """Audio transcription result."""
 text: str
 segments: list[dict] # Timestamp segments
 language: str
 confidence: float
```

**Vision Adapter Implementation:**

```python
# nexus/adapters/multimodal/vision.py
class VisionAdapter:
 """Normalize vision inputs across providers.
 
 Provider Differences:
 - OpenAI GPT-4V: Base64 PNG/JPEG/WebP/GIF, max 20MB
 - Anthropic Claude: Base64 PNG/JPEG/WebP/GIF, max 5MB per image
 - Ollama LLaVA: Base64 PNG/JPEG, depends on model
 - Google Gemini: Base64 or URI, various formats
 """
 
 PROVIDER_LIMITS = {
 'openai': {'max_size': 20_000_000, 'formats': ['PNG', 'JPEG', 'WEBP', 'GIF']},
 'anthropic': {'max_size': 5_000_000, 'formats': ['PNG', 'JPEG', 'WEBP', 'GIF']},
 'ollama': {'max_size': 10_000_000, 'formats': ['PNG', 'JPEG']},
 'gemini': {'max_size': 20_000_000, 'formats': ['PNG', 'JPEG', 'WEBP', 'HEIC', 'HEIF']},
 }
 
 async def process_for_provider(
 self,
 image: ProcessedImage,
 provider: str
 ) -> dict:
 """Convert image to provider-specific format."""
 limits = self.PROVIDER_LIMITS.get(provider, self.PROVIDER_LIMITS['openai'])
 
 # Resize if needed
 if len(image.data) > limits['max_size']:
 image = await self._resize_image(
 image,
 target_size=limits['max_size']
 )
 
 # Convert format if needed
 if image.format not in limits['formats']:
 image = await self._convert_format(image, target_format='PNG')
 
 return {
 'type': 'image',
 'media_type': f'image/{image.format.lower()}',
 'data': base64.b64encode(image.data).decode(),
 }
```

#### 2.2.4 Anti-Corruption Layer (NEW)

**Critical Addition:** Decouples NEXUS from source framework patterns during integration.

```python
# nexus/acl/__init__.py
"""Anti-Corruption Layer for framework integration.

Purpose:
- Translate external framework patterns to NEXUS patterns
- Isolate NEXUS core from external changes
- Enable gradual migration from source frameworks
"""

# nexus/acl/hermes_acl.py
class HermesACL:
 """Translates Hermes patterns to NEXUS patterns."""
 
 def translate_skill(self, hermes_skill: dict) -> SkillSpec:
 """Convert Hermes SKILL.md to NEXUS SkillSpec.
 
 Hermes Format:
 - Frontmatter: name, description, tags, requirements
 - Body: Free-form markdown
 
 NEXUS Format:
 - Structured SkillSpec with validation
 - Optional parameter schemas
 - Tool bindings
 """
 return SkillSpec(
 id=hermes_skill.get('id', ''),
 name=hermes_skill.get('name', ''),
 description=hermes_skill.get('description', ''),
 tags=hermes_skill.get('tags', []),
 requirements=hermes_skill.get('requirements', []),
 # NEXUS extensions
 parameters=self._parse_parameters(hermes_skill),
 tools=self._parse_tools(hermes_skill),
 )
 
 def translate_memory(self, hermes_memory: dict) -> MemoryEvent:
 """Convert Hermes memory format to NEXUS format."""
 return MemoryEvent(
 id=hermes_memory.get('id', ''),
 content=hermes_memory.get('content', ''),
 metadata=self._translate_metadata(hermes_memory.get('metadata', {})),
 created_at=hermes_memory.get('timestamp'),
 )

# nexus/acl/agent_zero_acl.py
class AgentZeroACL:
 """Translates Agent Zero patterns to NEXUS patterns."""
 
 def translate_tool(self, az_tool: dict) -> ToolSpec:
 """Convert Agent Zero tool to NEXUS ToolSpec.
 
 Agent Zero Format:
 - tool_name: string
 - tool_args: dict
 - tool_result: string
 
 NEXUS Format:
 - Structured ToolSpec with JSON Schema
 - Permission levels
 - Async support
 """
 return ToolSpec(
 name=az_tool.get('name', ''),
 description=az_tool.get('description', ''),
 parameters=self._infer_schema(az_tool.get('args', {})),
 permission=self._map_permission(az_tool.get('permission', 'read')),
 async_supported=True,
 )
```

#### 2.2.5 LLM Adapters (Enhanced)

**API Version Negotiation (NEW):**

```python
# nexus/adapters/llm/base.py
class LLMAdapter(Protocol):
 """Unified LLM interface - all providers behave identically."""
 
 # ... existing methods ...
 
 async def negotiate_api_version(
 self,
 min_version: str = "2024-01-01"
 ) -> str:
 """Negotiate API version with provider.
 
 Prevents breaking changes by:
 1. Checking provider's supported versions
 2. Selecting highest compatible version
 3. Failing gracefully if no compatible version
 """
 ...
 
 async def get_model_capabilities(self, model: str) -> ModelCapabilities:
 """Get model capabilities for prompt adaptation.
 
 Returns:
 - context_length: Max tokens
 - supports_vision: bool
 - supports_function_calling: bool
 - supports_streaming: bool
 - supports_prompt_caching: bool
 - supports_parallel_tool_calls: bool
 """
 ...

# nexus/adapters/llm/openai.py
class OpenAIAdapter:
 """OpenAI native adapter with version negotiation."""
 
 API_VERSIONS = {
 '2024-02-15-preview': {'chat': True, 'vision': True, 'tools': True},
 '2024-01-01': {'chat': True, 'vision': False, 'tools': True},
 }
 
 async def negotiate_api_version(
 self,
 min_version: str = "2024-01-01"
 ) -> str:
 # Get server-supported versions
 response = await self.client.models.list()
 # ... negotiation logic ...
 return compatible_version
```

#### 2.2.6 Built-In Efficiency Layer (Enhanced)

**Distributed Rate Limiting (NEW):**

```python
# nexus/efficiency/rate_limiter.py
class DistributedRateLimiter:
 """Redis-backed rate limiting for multi-instance deployments.
 
 Features:
 - Sliding window algorithm (not fixed window)
 - Atomic operations via Lua scripts
 - Automatic cleanup of expired entries
 - High availability with Redis Sentinel
 """
 
 LUA_SCRIPT = """
 local key = KEYS[1]
 local window = tonumber(ARGV[1])
 local limit = tonumber(ARGV[2])
 local now = tonumber(ARGV[3])
 local id = ARGV[4]
 
 -- Remove expired entries
 redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
 
 -- Count entries in window
 local count = redis.call('ZCARD', key)
 
 if count < limit then
 redis.call('ZADD', key, now, id)
 redis.call('EXPIRE', key, math.ceil(window / 1000))
 return 1
 else
 return 0
 end
 """
 
 def __init__(
 self,
 redis_url: str = "redis://localhost:6379",
 max_rpm: int = 60,
 window_ms: int = 60000
 ):
 self.redis = aioredis.from_url(redis_url)
 self.max_rpm = max_rpm
 self.window_ms = window_ms
 
 async def acquire(self, key: str) -> bool:
 """Acquire a rate limit slot."""
 now = int(time.time() * 1000)
 unique_id = f"{key}:{uuid.uuid4()}"
 
 result = await self.redis.eval(
 self.LUA_SCRIPT,
 1,
 f"ratelimit:{key}",
 self.window_ms,
 self.max_rpm,
 now,
 unique_id
 )
 
 return result == 1
```

**Budget Enforcement (NEW):**

```python
# nexus/efficiency/budget.py
class BudgetEnforcer:
 """Hard stop on token/cost limits.
 
 Features:
 - Pre-flight cost estimation
 - Running total tracking
 - Hard stop when budget exceeded
 - Alert thresholds (50%, 75%, 90%, 100%)
 """
 
 def __init__(
 self,
 max_tokens: int | None = None,
 max_cost_usd: float | None = None,
 alert_callback: Callable[[float, str], None] | None = None
 ):
 self.max_tokens = max_tokens
 self.max_cost_usd = max_cost_usd
 self.alert_callback = alert_callback
 
 self._tokens_used = 0
 self._cost_usd = 0.0
 
 # Pricing per 1K tokens (update periodically)
 self.PRICING = {
 ('openai', 'gpt-4-turbo'): {'input': 0.01, 'output': 0.03},
 ('openai', 'gpt-4'): {'input': 0.03, 'output': 0.06},
 ('openai', 'gpt-3.5-turbo'): {'input': 0.0005, 'output': 0.0015},
 ('anthropic', 'claude-3-opus'): {'input': 0.015, 'output': 0.075},
 ('anthropic', 'claude-3-sonnet'): {'input': 0.003, 'output': 0.015},
 ('ollama', '*'): {'input': 0, 'output': 0}, # Free
 }
 
 def estimate_cost(
 self,
 provider: str,
 model: str,
 input_tokens: int,
 estimated_output_tokens: int = 500
 ) -> float:
 """Estimate cost for a request."""
 key = (provider, model) if (provider, model) in self.PRICING else (provider, '*')
 pricing = self.PRICING.get(key, {'input': 0.01, 'output': 0.03})
 
 return (
 (input_tokens / 1000) * pricing['input'] +
 (estimated_output_tokens / 1000) * pricing['output']
 )
 
 def check_budget(self, provider: str, model: str, input_tokens: int) -> bool:
 """Check if request is within budget.
 
 Raises:
 BudgetExceededError: If budget would be exceeded
 """
 estimated_cost = self.estimate_cost(provider, model, input_tokens)
 
 if self.max_cost_usd is not None:
 projected_cost = self._cost_usd + estimated_cost
 
 # Alert thresholds
 for threshold in [0.5, 0.75, 0.9, 1.0]:
 if projected_cost >= self.max_cost_usd * threshold:
 self._alert(threshold, projected_cost)
 
 if projected_cost > self.max_cost_usd:
 raise BudgetExceededError(
 f"Budget exceeded: ${projected_cost:.2f} > ${self.max_cost_usd:.2f}"
 )
 
 if self.max_tokens is not None:
 projected_tokens = self._tokens_used + input_tokens
 if projected_tokens > self.max_tokens:
 raise BudgetExceededError(
 f"Token budget exceeded: {projected_tokens} > {self.max_tokens}"
 )
 
 return True
 
 def record_usage(
 self,
 provider: str,
 model: str,
 input_tokens: int,
 output_tokens: int
 ) -> None:
 """Record actual usage after request."""
 self._tokens_used += input_tokens + output_tokens
 cost = self.estimate_cost(provider, model, input_tokens, output_tokens)
 self._cost_usd += cost
```

#### 2.2.7 Agent Checkpointing (NEW)

```python
# nexus/core/checkpoint.py
class CheckpointManager:
 """Save and restore agent state for long-running tasks.
 
 Features:
 - Automatic checkpointing at defined intervals
 - Manual checkpoint on critical operations
 - Recovery from last checkpoint on failure
 - Checkpoint compression (TOON format)
 """
 
 def __init__(
 self,
 storage_path: Path,
 auto_checkpoint_interval: int = 60, # seconds
 max_checkpoints: int = 10
 ):
 self.storage_path = storage_path
 self.auto_checkpoint_interval = auto_checkpoint_interval
 self.max_checkpoints = max_checkpoints
 
 async def save(
 self,
 agent_id: str,
 state: dict,
 metadata: dict | None = None
 ) -> str:
 """Save agent state to checkpoint.
 
 Returns checkpoint ID.
 """
 checkpoint_id = f"{agent_id}_{int(time.time())}"
 checkpoint_path = self.storage_path / f"{checkpoint_id}.toon"
 
 # Compress state using TOON
 compressed = self._compress_state(state)
 
 checkpoint = {
 'id': checkpoint_id,
 'agent_id': agent_id,
 'timestamp': datetime.now().isoformat(),
 'state': compressed,
 'metadata': metadata or {},
 }
 
 async with aiofiles.open(checkpoint_path, 'w') as f:
 await f.write(toon.dumps(checkpoint))
 
 # Cleanup old checkpoints
 await self._cleanup_old_checkpoints(agent_id)
 
 return checkpoint_id
 
 async def restore(
 self,
 agent_id: str,
 checkpoint_id: str | None = None
 ) -> dict | None:
 """Restore agent state from checkpoint.
 
 If checkpoint_id is None, restores from latest checkpoint.
 """
 if checkpoint_id is None:
 checkpoint_id = await self._get_latest_checkpoint(agent_id)
 
 if not checkpoint_id:
 return None
 
 checkpoint_path = self.storage_path / f"{checkpoint_id}.toon"
 
 if not checkpoint_path.exists():
 return None
 
 async with aiofiles.open(checkpoint_path, 'r') as f:
 content = await f.read()
 
 checkpoint = toon.loads(content)
 return self._decompress_state(checkpoint['state'])
```

---

## 3. Configuration System

### 3.1 Design Principle: Simple for Non-Technical Users

**Three-tier configuration:**

1. **Zero Config** - Works out of the box with defaults
2. **Simple Config** - Single file for common settings
3. **Advanced Config** - Full control for power users

### 3.2 Zero Configuration (Default)

```bash
# One command setup for non-technical users
pip install nexus-ai
nexus init

# Auto-detect:
# - Local Ollama (if available) → use it, no API key needed
# - SQLite → zero-config database
# - Built-in efficiency → always on
# - Secure defaults → sandbox enabled
```

### 3.3 Simple Configuration

```yaml
# nexus.yaml - Simple configuration for most users

llm:
 provider: openai # or: ollama, anthropic, openai-compatible
 model: gpt-4-turbo
 api_key: ${OPENAI_API_KEY}

# Budget enforcement (optional)
budget:
 max_cost_usd: 10.0 # Stop after $10 spent
 alert_at: [0.5, 0.75, 0.9] # Alert at 50%, 75%, 90%

# That's all you need! Everything else has sensible defaults.
```

### 3.4 Provider-Specific Examples

**OpenAI:**
```yaml
llm:
 provider: openai
 model: gpt-4-turbo
 api_key: ${OPENAI_API_KEY}
 api_version: "2024-02-15-preview" # Optional: pin API version
```

**Ollama (Local):**
```yaml
llm:
 provider: ollama
 model: llama3.2
 # No API key needed!
 # base_url: http://localhost:11434 # Auto-detected
```

**OpenAI-Compatible:**
```yaml
llm:
 provider: openai-compatible
 base_url: http://localhost:8000/v1
 model: my-model
```

**With Distributed Rate Limiting:**
```yaml
efficiency:
 rate_limit:
 type: distributed # or: local
 redis_url: redis://localhost:6379
 max_rpm: 100
```

**With Budget Enforcement:**
```yaml
budget:
 max_tokens: 1000000 # 1M tokens
 max_cost_usd: 50.0 # $50 budget
 alert_webhook: https://hooks.slack.com/services/xxx
```

**With Secrets Management:**
```yaml
secrets:
 provider: vault # or: env, aws
 vault_addr: http://vault:8200
 vault_role_id: ${VAULT_ROLE_ID}
 vault_secret_id: ${VAULT_SECRET_ID}
```

### 3.5 Advanced Configuration

```yaml
# advanced-nexus.yaml - Full control for power users

llm:
 provider: openai
 model: gpt-4-turbo
 api_key: ${OPENAI_API_KEY}
 api_version: "2024-02-15-preview"
 
 params:
 temperature: 0.7
 max_tokens: 4096
 
 fallbacks:
 - provider: anthropic
 model: claude-3-sonnet
 api_key: ${ANTHROPIC_API_KEY}
 - provider: ollama
 model: llama3.2

efficiency:
 prompt_caching: true
 rate_limit:
 type: distributed
 redis_url: redis://localhost:6379
 max_rpm: 60
 context_compression: true
 budget:
 max_cost_usd: 100.0
 alert_at: [0.5, 0.75, 0.9, 0.95]

memory:
 provider: sqlite
 path: ~/.nexus/memory.db
 wal_mode: true
 pool_size: 5
 
 semantic_search: true
 embedding_model: text-embedding-3-small

secrets:
 provider: vault
 vault_addr: http://vault:8200
 vault_role_id: ${VAULT_ROLE_ID}
 vault_secret_id: ${VAULT_SECRET_ID}

security:
 sandbox:
 enabled: true
 memory_limit_mb: 512
 cpu_limit: 1.0
 timeout_seconds: 30
 network_access: false
 
 audit:
 enabled: true
 path: ~/.nexus/audit.log
 retention_days: 90

multimodal:
 image:
 max_size_mb: 20
 default_format: PNG
 resize_on_exceed: true
 pdf:
 extract_images: true
 extract_text: true
 audio:
 transcription_model: whisper-1
 language: en

checkpoint:
 enabled: true
 interval_seconds: 60
 max_checkpoints: 10
 storage_path: ~/.nexus/checkpoints

agents:
 default: assistant
 
 assistant:
 model: gpt-4-turbo
 skills: [code-review, web-search]
 checkpoint: true
 
 researcher:
 model: claude-3-sonnet
 skills: [research, analysis]
 checkpoint: true

hands:
 daily_summary:
 agent_id: researcher
 schedule: "0 9 * * *"
 task: "Summarize yesterday's conversations"
 enabled: true
 checkpoint: true
```

---

## 4. MVP Scope

### 4.1 In Scope (v0.1.0)

| Feature | Priority | Source | Description |
|---------|----------|--------|-------------|
| **Dependency Injection Container** | P0 | NEW | DI container with auto-wiring |
| **Core Agent Loop** | P0 | Agent Zero | Basic agent execution with state persistence |
| **LLM Adapters** | P0 | NEW | OpenAI, OpenAI-Compatible, Ollama |
| **Zero-Glitch Switching** | P0 | NEW | Identical behavior across providers |
| **API Version Negotiation** | P0 | NEW | Prevent breaking changes |
| **Built-In Efficiency** | P0 | NEW | Prompt caching, rate limiting, compression |
| **Budget Enforcement** | P0 | NEW | Hard stop on token/cost limits |
| **Memory System** | P0 | Hermes | SQLite-based memory with WAL mode |
| **Tool Registry** | P0 | Agent Zero | Dynamic tool loading and execution |
| **SKILL.md Parser** | P0 | Hermes | Parse and load skills from Markdown |
| **CLI** | P0 | All | One-command setup for non-technical users |
| **Security Sandbox** | P0 | OpenFang | Docker-based skill sandboxing |
| **Simple Configuration** | P0 | NEW | Zero-config + simple YAML |
| **Anti-Corruption Layer** | P0 | NEW | Framework integration translation |
| **Checkpointing** | P0 | NEW | Agent state save/restore |
| **Multimodal Layer** | P1 | NEW | Image, PDF, audio normalization |
| **Distributed Rate Limiting** | P1 | NEW | Redis-backed rate limiting |
| **Secrets Management** | P1 | NEW | Vault integration |
| **Multi-Agent Hierarchy** | P1 | Agent Zero | Delegate to sub-agents |
| **Knowledge Graph** | P1 | OpenFang | Basic entity relationship storage |
| **Hands (Scheduler)** | P1 | OpenFang | Schedule autonomous tasks |
| **REST API** | P1 | OpenFang | HTTP interface for integration |

### 4.2 Out of Scope (Future Versions)

| Feature | Planned Version | Reason |
|---------|-----------------|--------|
| Telegram/Discord channels | v0.2.0 | Requires additional adapters |
| Web UI Dashboard | v0.3.0 | Significant frontend work |
| Distributed execution | v0.4.0 | Complex infrastructure |
| Plugin marketplace | v1.0.0 | Requires ecosystem |

### 4.3 MVP Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Provider switch time | <100ms | Benchmark |
| Provider switch errors | 0 | Integration tests |
| Setup time (new user) | <5 min | User testing |
| Agent execution | 100% basic tasks pass | Test suite |
| Memory operations | <50ms latency | Benchmark |
| Cold start | <500ms | Benchmark |
| Memory footprint | <100MB | Resource monitor |
| Security audit | 0 critical/high | Static analysis |
| Test coverage | >80% | pytest-cov |
| Token efficiency | 40% reduction | Cost comparison |
| Checkpoint restore | <1s | Benchmark |
| Multimodal overhead | <200ms | Benchmark |

---

## 5. Package Structure

```
nexus/
├── __init__.py
├── container/ # NEW: Dependency Injection
│ ├── __init__.py
│ ├── di_container.py # DI container implementation
│ ├── adapter_registry.py # Adapter registry
│ └── lifecycle.py # Service lifecycle management
├── core/
│ ├── __init__.py
│ ├── agent.py # Agent loop implementation
│ ├── memory.py # Memory manager
│ ├── tools.py # Tool registry
│ ├── prompt.py # Prompt assembly
│ ├── knowledge.py # Knowledge graph
│ └── checkpoint.py # NEW: Agent checkpointing
├── acl/ # NEW: Anti-Corruption Layer
│ ├── __init__.py
│ ├── hermes_acl.py # Hermes translation
│ ├── openclaw_acl.py # OpenClaw translation
│ ├── agent_zero_acl.py # Agent Zero translation
│ └── openfang_acl.py # OpenFang translation
├── adapters/
│ ├── __init__.py
│ ├── llm/ # LLM adapters
│ │ ├── __init__.py
│ │ ├── base.py # Base adapter protocol
│ │ ├── openai.py # OpenAI native
│ │ ├── openai_compatible.py # OpenAI-compatible endpoints
│ │ ├── ollama.py # Local models
│ │ ├── anthropic.py # Claude models
│ │ └── nvidia.py # NVIDIA NIM
│ ├── memory/
│ │ ├── sqlite_adapter.py # SQLite with WAL
│ │ ├── postgres_adapter.py # PostgreSQL
│ │ └── chromadb_adapter.py # Vector search
│ ├── secrets/ # NEW: Secrets management
│ │ ├── env_adapter.py # Environment variables
│ │ ├── vault_adapter.py # HashiCorp Vault
│ │ └── aws_adapter.py # AWS Secrets Manager
│ ├── multimodal/ # NEW: Multimodal
│ │ ├── vision_adapter.py # Image processing
│ │ ├── pdf_adapter.py # PDF processing
│ │ └── whisper_adapter.py # Audio transcription
│ ├── channels/
│ │ ├── cli_adapter.py # CLI channel
│ │ ├── rest_adapter.py # REST API
│ │ └── mqtt_adapter.py # MQTT
│ └── storage/
│ ├── file_adapter.py
│ └── s3_adapter.py
├── efficiency/ # Built-in efficiency
│ ├── __init__.py
│ ├── prompt_cache.py
│ ├── token_optimizer.py
│ ├── rate_limiter.py # Local rate limiting
│ ├── distributed_rate_limiter.py # NEW: Redis-backed
│ ├── budget.py # NEW: Budget enforcement
│ ├── context_compression.py
│ └── statistics.py
├── ports/
│ ├── __init__.py
│ ├── memory_port.py
│ ├── llm_port.py
│ ├── channel_port.py
│ ├── storage_port.py
│ ├── secrets_port.py # NEW
│ ├── multimodal_port.py # NEW
│ └── schedule_port.py
├── hands/
│ ├── __init__.py
│ ├── scheduler.py
│ ├── hand.py
│ └── executor.py
├── security/
│ ├── __init__.py
│ ├── sandbox.py # Docker sandboxing
│ ├── validation.py # Input validation
│ ├── rate_limit.py # Security layer
│ ├── audit.py # Audit logging
│ ├── output_filter.py # NEW: PII redaction
│ ├── encryption.py # NEW: AES-256-GCM
│ ├── integrity.py # NEW: Signatures
│ └── layers.py # All 16 layers
├── channels/
│ ├── __init__.py
│ ├── dispatcher.py
│ ├── session.py
│ └── context.py
├── config/
│ ├── __init__.py
│ ├── loader.py
│ ├── defaults.py
│ ├── validation.py
│ ├── agent_config.py
│ ├── skill_config.py
│ └── system_config.py
├── cli/
│ ├── __init__.py
│ ├── main.py
│ ├── setup.py
│ └── commands/
│ ├── agent.py
│ ├── skill.py
│ ├── hand.py
│ ├── config.py
│ └── system.py
└── utils/
 ├── __init__.py
 ├── logging.py
 ├── fs.py
 └── async_helpers.py
```

---

## 6. Implementation Phases (12 Weeks)

### Phase 1: Foundation (Week 1-2)

| Task | Priority | Dependencies |
|------|----------|--------------|
| Set up project structure | P0 | None |
| Implement DI container | P0 | Project structure |
| Implement Port protocols | P0 | DI container |
| Create adapter registry | P0 | DI container |
| Implement OpenAI adapter | P0 | Ports, registry |
| Implement OpenAI-Compatible adapter | P0 | OpenAI adapter |
| Implement Ollama adapter | P0 | Ports, registry |
| Add API version negotiation | P0 | LLM adapters |
| Create base adapters (SQLite, CLI) | P0 | Ports |
| Implement security sandbox (Docker) | P0 | Base adapters |
| Create CLI skeleton | P0 | None |
| Implement one-command setup | P0 | CLI skeleton |

### Phase 2: Built-In Efficiency (Week 3-4)

| Task | Priority | Dependencies |
|------|----------|--------------|
| Implement prompt caching | P0 | LLM adapters |
| Implement local rate limiter | P0 | LLM adapters |
| Implement distributed rate limiter | P0 | Redis setup |
| Implement budget enforcement | P0 | LLM adapters, rate limiter |
| Implement context compression | P0 | Memory manager |
| Implement statistics tracking | P0 | All efficiency components |
| Integrate efficiency into adapters | P0 | All efficiency components |

### Phase 3: Core Agent (Week 5-6)

| Task | Priority | Dependencies |
|------|----------|--------------|
| Implement agent loop | P0 | Phase 1-2 |
| Create memory manager | P0 | Agent loop |
| Build tool registry | P0 | Agent loop |
| Implement prompt assembly | P0 | Agent loop |
| Add SKILL.md parser | P0 | Tool registry |
| Implement checkpointing | P0 | Agent loop, storage |
| Test provider switching | P0 | All components |
| Implement Anti-Corruption Layer | P0 | Core components |

### Phase 4: Multimodal & Security (Week 7-8)

| Task | Priority | Dependencies |
|------|----------|--------------|
| Implement MultimodalPort | P1 | Ports |
| Implement vision adapter | P1 | MultimodalPort |
| Implement PDF adapter | P1 | MultimodalPort |
| Implement audio adapter | P1 | MultimodalPort |
| Implement all 16 security layers | P0 | Security foundation |
| Implement Vault adapter | P1 | SecretsPort |
| Security layer integration tests | P0 | All layers |

### Phase 5: Multi-Agent & Persistence (Week 9-10)

| Task | Priority | Dependencies |
|------|----------|--------------|
| Implement agent hierarchy | P1 | Phase 3 |
| Add state persistence | P1 | Agent hierarchy |
| Create knowledge graph | P1 | Memory manager |
| Implement semantic search | P1 | Memory manager |
| Multi-agent integration tests | P1 | All components |

### Phase 6: Autonomous Features (Week 11-12)

| Task | Priority | Dependencies |
|------|----------|--------------|
| Implement Hand scheduler | P1 | Phase 5 |
| Add checkpoint integration to Hands | P1 | Hand scheduler |
| Add REST API channel | P1 | Channels layer |
| Create monitoring endpoints | P1 | REST API |
| Add audit dashboard | P2 | Monitoring |
| End-to-end testing | P0 | All components |
| Documentation completion | P0 | All components |

---

## 7. Architecture Decision Records (ADRs)

### ADR-001: SQLite as Default Database

**Status:** Accepted

**Context:** Need a zero-configuration database for non-technical users.

**Decision:** Use SQLite with WAL mode as the default storage backend.

**Consequences:**
- ✅ Zero configuration
- ✅ Embedded (no external process)
- ✅ Single file for easy backup
- ⚠️ Write serialization (mitigated by WAL mode)
- ⚠️ Not suitable for distributed deployments (use PostgreSQL)

### ADR-002: Dependency Injection Container

**Status:** Accepted

**Context:** Need proper hexagonal architecture with loose coupling.

**Decision:** Implement a custom DI container with auto-wiring.

**Consequences:**
- ✅ Clean separation of concerns
- ✅ Easy testing with mock injection
- ✅ Configuration-driven adapter selection
- ⚠️ Small performance overhead (negligible)
- ⚠️ Learning curve for contributors

### ADR-003: Built-In Efficiency (Not Skills)

**Status:** Accepted

**Context:** Prompt caching, rate limiting, and compression are core features.

**Decision:** Implement efficiency features as built-in code, not external skills.

**Consequences:**
- ✅ No dependency chicken-and-egg problem
- ✅ Always available, no configuration
- ✅ Performance optimizations in core
- ⚠️ Larger core codebase
- ⚠️ Harder to customize (requires code change)

### ADR-004: Docker for Skill Sandboxing

**Status:** Accepted

**Context:** Need isolation for untrusted skill execution.

**Decision:** Use Docker containers with seccomp profiles for skill sandboxing.

**Consequences:**
- ✅ Strong isolation (kernel-level)
- ✅ Resource limits enforcement
- ✅ Network isolation
- ⚠️ Docker dependency
- ⚠️ Container startup latency (~100ms)

### ADR-005: TOON for Context Compression

**Status:** Accepted

**Context:** Need efficient context storage and transmission.

**Decision:** Use TOON (Token-Oriented Object Notation) for compression.

**Consequences:**
- ✅ ~40% token reduction
- ✅ Lossless conversion
- ✅ Human-readable
- ⚠️ Non-standard format (needs documentation)
- ⚠️ Parser implementation needed

### ADR-006: 12-Week MVP Timeline

**Status:** Accepted

**Context:** Research review identified 8-week timeline as too aggressive.

**Decision:** Extend MVP timeline from 8 to 12 weeks.

**Consequences:**
- ✅ More realistic estimates
- ✅ Time for security layer implementation
- ✅ Buffer for unexpected issues
- ⚠️ Later market entry
- ⚠️ Extended resource commitment

---

## 8. Testing Strategy

### 8.1 Test Categories

| Category | Coverage Target | Tools |
|----------|-----------------|-------|
| Unit tests | >80% | pytest, pytest-cov |
| Integration tests | >70% | pytest, pytest-asyncio |
| Provider switch tests | 100% | Custom fixtures |
| Security tests | 100% critical paths | bandit, safety |
| Performance tests | Key benchmarks | pytest-benchmark |
| E2E tests | Key user flows | playwright |

### 8.2 Security Testing Requirements

```bash
# Run security tests
pytest tests/security/ -v

# Static analysis
bandit -r nexus/
safety check
pip-audit

# Dependency verification
pip-compile --generate-hashes requirements.in
```

### 8.3 Performance Benchmarks

| Metric | Target | Test |
|--------|--------|------|
| Cold start | <500ms | `pytest tests/performance/test_cold_start.py` |
| Provider switch | <100ms | `pytest tests/performance/test_provider_switch.py` |
| Memory operation | <50ms | `pytest tests/performance/test_memory_latency.py` |
| Checkpoint restore | <1s | `pytest tests/performance/test_checkpoint.py` |
| Multimodal processing | <200ms | `pytest tests/performance/test_multimodal.py` |

---

## 9. Risk Assessment

### 9.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Provider API breaking changes | High | Critical | API version negotiation, pin versions |
| Docker sandbox escape | Low | Critical | seccomp profiles, regular security audits |
| SQLite write contention | Medium | High | WAL mode, connection pooling |
| Ollama version incompatibility | Medium | High | Version detection, compatibility matrix |
| TOON parsing edge cases | Medium | Low | Comprehensive test suite |
| DI container complexity | Medium | Medium | Good documentation, examples |
| Vault connectivity issues | Medium | Medium | Fallback to env vars, health checks |

### 9.2 Market Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| LangChain ecosystem dominance | High | High | Zero-glitch differentiation, local-first |
| OpenAI releases built-in agents | Medium | Critical | Provider-agnostic positioning |
| Enterprise compliance requirements | High | High | Expanded security implementation |
| Developer adoption friction | Medium | Medium | Invest in DX, docs, examples |

---

## 10. Documentation Plan

### 10.1 Required Documentation

| Document | Location | Status |
|----------|----------|--------|
| README | `/README.md` | Required |
| Quick Start | `/docs/quick-start.md` | Required |
| Configuration Guide | `/docs/config.md` | Required |
| Provider Setup | `/docs/providers.md` | Required |
| Security Guide | `/docs/security/` | Required |
| API Reference | `/docs/api/` | Required |
| ADRs | `/docs/adr/` | Required |
| Examples | `/examples/` | Required |

### 10.2 Migration Guides

| Guide | Target Users |
|-------|-------------|
| Hermes → NEXUS | Hermes users |
| OpenClaw → NEXUS | OpenClaw users |
| Agent Zero → NEXUS | Agent Zero users |
| OpenFang → NEXUS | OpenFang users |

---

## 11. Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| **Port** | Protocol interface defining a contract |
| **Adapter** | Concrete implementation of a Port |
| **Hand** | Scheduled autonomous agent task |
| **Skill** | Declaratively defined capability (SKILL.md) |
| **Channel** | Input/output interface (CLI, API, etc.) |
| **Dispatcher** | Central message router |
| **Efficiency Layer** | Built-in token optimization |
| **Zero-Glitch Switching** | Identical behavior across LLM providers |
| **DI Container** | Dependency injection for adapter management |
| **ACL** | Anti-Corruption Layer for framework integration |
| **Checkpoint** | Saved agent state for recovery |
| **Multimodal** | Images, PDFs, audio inputs |
| **Budget Enforcement** | Hard stop on token/cost limits |

### B. References

1. Hermes Agent: https://github.com/happenslol/hermes
2. OpenClaw: https://github.com/openclaw/openclaw
3. Agent Zero: https://github.com/agent0ai/agent-zero
4. OpenFang: https://github.com/RightNow-AI/openfang
5. Ollama: https://github.com/ollama/ollama
6. OpenAI API: https://platform.openai.com/docs/api-reference
7. Anthropic API: https://docs.anthropic.com/claude/reference
8. HashiCorp Vault: https://www.vaultproject.io/docs
9. Hexagonal Architecture: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
10. TOON Format: https://github.com/agent0ai/toon-spec

### C. Decision Log

| Decision | Date | Rationale |
|----------|------|-----------|
| Python over Rust | 2026-04-09 | Ecosystem, DX, integration ease |
| SQLite for MVP storage | 2026-04-09 | Zero-config, proven, embeddable |
| Protocol-based Ports | 2026-04-09 | Flexibility, testability, clean architecture |
| 16 security layers | 2026-04-09 | OpenFang proven approach |
| Built-in efficiency | 2026-04-09 | No external skills for core features |
| Ollama as P0 | 2026-04-09 | Privacy, no API key, local-first |
| OpenAI-Compatible adapter | 2026-04-09 | Works with vLLM, LM Studio, custom endpoints |
| Zero-config setup | 2026-04-09 | Non-technical user adoption |
| TOON compression | 2026-04-09 | 40% token reduction, lossless |
| DI Container | 2026-04-09 | Proper hexagonal architecture |
| 12-week MVP | 2026-04-09 | Research feedback, realistic estimates |
| Multimodal layer | 2026-04-09 | Provider normalization for vision |
| Anti-Corruption Layer | 2026-04-09 | Framework integration isolation |
| Budget enforcement | 2026-04-09 | Cost control for enterprise |
| Distributed rate limiting | 2026-04-09 | Multi-instance deployments |
| Secrets management | 2026-04-09 | Enterprise security requirements |
| Agent checkpointing | 2026-04-09 | Long-running task recovery |
| API version negotiation | 2026-04-09 | Prevent breaking changes |

---

**Document Status:** Refactored with Research Insights
**Next Steps:** Review v2.0.0, create development build log
