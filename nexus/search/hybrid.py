"""Hybrid Search Engine Implementation."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import re


class SearchMethod(Enum):
    KEYWORD = "keyword"
    VECTOR = "vector"
    METADATA = "metadata"
    SEMANTIC = "semantic"


@dataclass(slots=True)
class SearchResult:
    id: str
    content: str
    score: float
    method: SearchMethod
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "content": self.content, "score": self.score, "method": self.method.value, "metadata": self.metadata}


@dataclass(slots=True)
class HybridSearchResult:
    query: str
    results: List[SearchResult]
    fusion_score: float = 0.0

    def top_k(self, k: int = 5) -> List[SearchResult]:
        sorted_results = sorted(self.results, key=lambda x: x.score, reverse=True)
        return sorted_results[:k]


class HybridSearchEngine:
    """Hybrid search combining multiple search methods."""

    def __init__(self):
        self.keyword_index: Dict[str, List[str]] = {}
        self.vector_index: Dict[str, List[float]] = {}
        self.documents: Dict[str, str] = {}

    def index_document(self, doc_id: str, content: str, embedding: Optional[List[float]] = None):
        self.documents[doc_id] = content
        words = re.findall(r"\w+", content.lower())
        for word in words:
            if word not in self.keyword_index:
                self.keyword_index[word] = []
            if doc_id not in self.keyword_index[word]:
                self.keyword_index[word].append(doc_id)
        if embedding:
            self.vector_index[doc_id] = embedding

    def keyword_search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        words = re.findall(r"\w+", query.lower())
        doc_scores: Dict[str, int] = {}
        for word in words:
            if word in self.keyword_index:
                for doc_id in self.keyword_index[word]:
                    doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1
        results = []
        for doc_id, score in doc_scores.items():
            results.append(SearchResult(id=doc_id, content=self.documents.get(doc_id, ""), score=float(score), method=SearchMethod.KEYWORD))
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def vector_search(self, query_embedding: List[float], top_k: int = 10) -> List[SearchResult]:
        results = []
        for doc_id, doc_embedding in self.vector_index.items():
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            results.append(SearchResult(id=doc_id, content=self.documents.get(doc_id, ""), score=similarity, method=SearchMethod.VECTOR))
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def hybrid_search(self, query: str, query_embedding: Optional[List[float]] = None, top_k: int = 10, fusion: str = "rrf") -> HybridSearchResult:
        keyword_results = self.keyword_search(query, top_k=top_k*2)
        all_results = keyword_results.copy()
        if query_embedding:
            vector_results = self.vector_search(query_embedding, top_k=top_k*2)
            all_results.extend(vector_results)
        if fusion == "rrf":
            all_results = self._rrf_fusion(all_results, k=60)
        return HybridSearchResult(query=query, results=all_results[:top_k])

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x ** 2 for x in a) ** 0.5
        norm_b = sum(x ** 2 for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def _rrf_fusion(self, results: List[SearchResult], k: int = 60) -> List[SearchResult]:
        doc_scores: Dict[str, float] = {}
        for rank, result in enumerate(results, 1):
            rrf_score = 1.0 / (k + rank)
            if result.id not in doc_scores:
                doc_scores[result.id] = 0.0
            doc_scores[result.id] += rrf_score
        fused_results = []
        seen_ids = set()
        for result in results:
            if result.id not in seen_ids:
                seen_ids.add(result.id)
                fused_results.append(SearchResult(id=result.id, content=result.content, score=doc_scores[result.id], method=SearchMethod.KEYWORD, metadata=result.metadata))
        fused_results.sort(key=lambda x: x.score, reverse=True)
        return fused_results


def create_hybrid_engine() -> HybridSearchEngine:
    return HybridSearchEngine()