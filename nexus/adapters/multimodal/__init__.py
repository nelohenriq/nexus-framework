"""
NEXUS Framework - Multimodal Adapters

Vision, PDF, and Audio processing adapters with provider normalization.
"""

from __future__ import annotations

import base64
import mimetypes
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union


class ModalityType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    PDF = "pdf"
    VIDEO = "video"


@dataclass
class MultimodalContent:
    modality: ModalityType
    content: Union[str, bytes]
    mime_type: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    
    def to_api_format(self, provider: str = "openai") -> dict:
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
            metadata={"provider": provider}
        )
    
    def _detect_image_mime(self, content: bytes) -> str:
        if content[:8] == b"\x89PNG\r\n\x1a\n":
            return "image/png"
        elif content[:2] == b"\xff\xd8":
            return "image/jpeg"
        elif content[:6] in (b"GIF87a", b"GIF89a"):
            return "image/gif"
        return "image/png"


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
            mime_type="application/pdf"
        )


class AudioAdapter(BaseMultimodalAdapter):
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
            mime_type=mime
        )
    
    def _detect_audio_mime(self, content: bytes) -> str:
        if content[:3] == b"ID3" or content[:2] == b"\xff\xfb":
            return "audio/mpeg"
        elif content[:4] == b"RIFF":
            return "audio/wav"
        return "audio/mpeg"


class MultimodalManager:
    def __init__(self) -> None:
        self._adapters = {
            ModalityType.IMAGE: VisionAdapter(),
            ModalityType.PDF: PDFAdapter(),
            ModalityType.AUDIO: AudioAdapter(),
        }
    
    def process(self, content: Union[str, bytes, Path], modality: ModalityType = None) -> MultimodalContent:
        if modality is None:
            modality = self._detect_modality(content)
        adapter = self._adapters.get(modality)
        if not adapter:
            raise ValueError(f"Unsupported modality: {modality}")
        return adapter.process(content)
    
    def _detect_modality(self, content: Union[str, bytes, Path]) -> ModalityType:
        path = Path(content) if isinstance(content, (str, Path)) else None
        if path and path.suffix:
            ext = path.suffix.lower().lstrip(".")
            if ext in ("png", "jpg", "jpeg", "gif", "webp"):
                return ModalityType.IMAGE
            elif ext == "pdf":
                return ModalityType.PDF
            elif ext in ("mp3", "wav", "flac", "ogg"):
                return ModalityType.AUDIO
        return ModalityType.TEXT


__all__ = ["ModalityType", "MultimodalContent", "VisionAdapter", "PDFAdapter", "AudioAdapter", "MultimodalManager"]
