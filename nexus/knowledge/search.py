#!/usr/bin/env python3
"""
NEXUS Framework - Semantic Search

Vector-based semantic search using embeddings.
Supports multiple backends: ChromaDB, FAISS, in-memory.
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from abc import ABC, abstractmethod


@dataclass
class SearchResult:
    """A single search result."""
    id: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata
        }


@dataclass
class SearchConfig:
    """Configuration for semantic search."""
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 10
    similarity_threshold: float = 0.7


class EmbeddingBackend(ABC):
    """Abstract base class for embedding backends."""

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts."""
        pass

    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a query."""
        pass


class SimpleEmbeddingBackend(EmbeddingBackend):
    """Simple embedding backend using basic text hashing."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [self._simple_embed(text) for text in texts]

    def embed_query(self, query: str) -> List[float]:
        return self._simple_embed(query)

    def _simple_embed(self, text: str) -> List[float]:
        """Simple embedding using character n-grams."""
        embedding = [0.0] * self.dimension
        for i, char in enumerate(text):
            idx = ord(char) % self.dimension
            embedding[idx] += 1.0 / (i + 1)
        # Normalize
        norm = sum(x * x for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x / norm for x in embedding]
        return embedding


class VectorStore(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    def add(self, id: str, embedding: List[float], metadata: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int) -> List[Tuple[str, float, Dict]]:
        pass

    @abstractmethod
    def delete(self, id: str) -> None:
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, int]:
        pass


class InMemoryVectorStore(VectorStore):
    """In-memory vector store using cosine similarity."""

    def __init__(self):
        self._vectors: Dict[str, List[float]] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

    def add(self, id: str, embedding: List[float], metadata: Dict[str, Any]) -> None:
        self._vectors[id] = embedding
        self._metadata[id] = metadata

    def search(self, query_embedding: List[float], top_k: int) -> List[Tuple[str, float, Dict]]:
        scores: List[Tuple[str, float, Dict]] = []
        for id, embedding in self._vectors.items():
            score = self._cosine_similarity(query_embedding, embedding)
            scores.append((id, score, self._metadata.get(id, {})))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def delete(self, id: str) -> None:
        self._vectors.pop(id, None)
        self._metadata.pop(id, None)

    def get_stats(self) -> Dict[str, int]:
        return {"vectors": len(self._vectors)}


class SemanticSearch:
    """Semantic search engine for knowledge retrieval."""

    def __init__(
        self,
        embedding_backend: Optional[EmbeddingBackend] = None,
        vector_store: Optional[VectorStore] = None,
        config: Optional[SearchConfig] = None
    ):
        self.config = config or SearchConfig()
        self.embedding_backend = embedding_backend or SimpleEmbeddingBackend()
        self.vector_store = vector_store or InMemoryVectorStore()

    def index_document(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Index a document for semantic search."""
        doc_id = hashlib.sha256(content.encode()).hexdigest()[:16]
        embedding = self.embedding_backend.embed([content])[0]
        self.vector_store.add(doc_id, embedding, metadata or {})
        return doc_id

    def index_documents(
        self,
        documents: List[Tuple[str, Dict[str, Any]]]
    ) -> List[str]:
        """Index multiple documents."""
        doc_ids = []
        embeddings = self.embedding_backend.embed([doc[0] for doc in documents])
        for i, (content, metadata) in enumerate(documents):
            doc_id = hashlib.sha256(content.encode()).hexdigest()[:16]
            self.vector_store.add(doc_id, embeddings[i], metadata)
            doc_ids.append(doc_id)
        return doc_ids

    def search(self, query: str, top_k: Optional[int] = None) -> List[SearchResult]:
        """Search for similar documents."""
        top_k = top_k or self.config.top_k
        query_embedding = self.embedding_backend.embed_query(query)
        results = self.vector_store.search(query_embedding, top_k)
        return [
            SearchResult(
                id=id,
                content=metadata.get("content", ""),
                score=score,
                metadata=metadata
            )
            for id, score, metadata in results
        ]

    def delete_document(self, doc_id: str) -> None:
        """Remove a document from the index."""
        self.vector_store.delete(doc_id)

    def get_stats(self) -> Dict[str, Any]:
        return self.vector_store.get_stats()


__all__ = ["SemanticSearch", "SearchResult", "SearchConfig", "EmbeddingBackend", "VectorStore"]