"""
NEXUS Framework - Multimodal Adapters

Vision, PDF, and Audio processing adapters with provider normalization.
"""

from __future__ import annotations

import base64
import mimetypes
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional, Union


class ModalityType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    PDF = "pdf"
    VIDEO = "video"


@dataclass(slots=True)
class MultimodalContent:
    modality: ModalityType
    content: Union[str, bytes]
    mime_type: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    _api_cache: dict = field(default_factory=dict, repr=False)

    def to_api_format(self, provider: str = "openai") -> dict:
        cache_key = provider
        if cache_key in self._api_cache:
            return self._api_cache[cache_key]
        result = self._compute_api_format(provider)
        self._api_cache[cache_key] = result
        return result

    def _compute_api_format(self, provider: str) -> dict:
        if self.modality == ModalityType.TEXT:
            return {"type": "text", "text": self.content}
        elif self.modality == ModalityType.IMAGE:
            if isinstance(self.content, bytes):
                b64 = base64.b64encode(self.content).decode()
                return {"type": "image_url", "image_url": {"url": f"data:{self.mime_type};base64,{b64}"}}
            return {"type": "image_url", "image_url": {"url": self.content}}
        return {"type": "text", "text": str(self.content)}


class BaseMultimodalAdapter(ABC):
    def __init__(self, max_size_mb: int = 20) -> None:
        self.max_size_bytes = max_size_mb * 1024 * 1024

    @abstractmethod
    def process(self, content: Union[str, bytes, Path], **kwargs) -> MultimodalContent:
        pass

    def _validate_size(self, content: bytes) -> None:
        if len(content) > self.max_size_bytes:
            raise ValueError(f"Content exceeds max size")


class VisionAdapter(BaseMultimodalAdapter):
    PROVIDER_LIMITS = {
        "openai": {"max_px": 2048, "formats": ["png", "jpeg", "gif", "webp"]},
        "anthropic": {"max_px": 8000, "formats": ["png", "jpeg", "gif", "webp"]},
    }

    # Pre-compiled magic bytes for image type detection
    _MAGIC_BYTES = {
        b"\x89PNG": "image/png",
        b"\xff\xd8\xff": "image/jpeg",
        b"GIF87a": "image/gif",
        b"GIF89a": "image/gif",
        b"RIFF": "image/webp",
    }

    def __init__(self, default_provider: str = "openai") -> None:
        super().__init__(max_size_mb=20)
        self.default_provider = default_provider

    def process(self, content: Union[str, bytes, Path], provider: str = None) -> MultimodalContent:
        provider = provider or self.default_provider
        if isinstance(content, Path):
            content = content.read_bytes()
        elif isinstance(content, str) and os.path.exists(content):
            content = Path(content).read_bytes()
        self._validate_size(content)
        mime = self._detect_image_mime(content)
        return MultimodalContent(
            modality=ModalityType.IMAGE,
            content=content,
            mime_type=mime,
            metadata={"provider": provider, "timestamp": time.monotonic()}
        )

    def _detect_image_mime(self, content: bytes) -> str:
        for magic, mime in self._MAGIC_BYTES.items():
            if content[:len(magic)] == magic:
                return mime
        return "application/octet-stream"


class PDFAdapter(BaseMultimodalAdapter):
    def __init__(self) -> None:
        super().__init__(max_size_mb=50)

    def process(self, content: Union[str, bytes, Path], **kwargs) -> MultimodalContent:
        if isinstance(content, Path):
            content = content.read_bytes()
        elif isinstance(content, str) and os.path.exists(content):
            content = Path(content).read_bytes()
        self._validate_size(content)
        return MultimodalContent(
            modality=ModalityType.PDF,
            content=content,
            mime_type="application/pdf",
            metadata={"timestamp": time.monotonic()}
        )


class AudioAdapter(BaseMultimodalAdapter):
    SUPPORTED_FORMATS = {"mp3", "wav", "ogg", "m4a", "flac"}

    def __init__(self) -> None:
        super().__init__(max_size_mb=25)

    def process(self, content: Union[str, bytes, Path], **kwargs) -> MultimodalContent:
        if isinstance(content, Path):
            content = content.read_bytes()
        elif isinstance(content, str) and os.path.exists(content):
            content = Path(content).read_bytes()
        self._validate_size(content)
        mime = self._detect_audio_mime(content)
        return MultimodalContent(
            modality=ModalityType.AUDIO,
            content=content,
            mime_type=mime,
            metadata={"timestamp": time.monotonic()}
        )

    def _detect_audio_mime(self, content: bytes) -> str:
        if content[:3] == b"ID3" or content[:2] == b"\xff\xfb":
            return "audio/mpeg"
        elif content[:4] == b"RIFF":
            return "audio/wav"
        elif content[:4] == b"OggS":
            return "audio/ogg"
        return "application/octet-stream"


class MultimodalManager:
    def __init__(self, default_provider: str = "openai") -> None:
        self.vision = VisionAdapter(default_provider)
        self.pdf = PDFAdapter()
        self.audio = AudioAdapter()

    def process_image(self, content: Union[str, bytes, Path], provider: str = None) -> MultimodalContent:
        return self.vision.process(content, provider)

    def process_pdf(self, content: Union[str, bytes, Path]) -> MultimodalContent:
        return self.pdf.process(content)

    def process_audio(self, content: Union[str, bytes, Path]) -> MultimodalContent:
        return self.audio.process(content)


__all__ = ["ModalityType", "MultimodalContent", "BaseMultimodalAdapter", "VisionAdapter", "PDFAdapter", "AudioAdapter", "MultimodalManager"]