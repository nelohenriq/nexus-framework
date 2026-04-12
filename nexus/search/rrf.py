"""Reciprocal Rank Fusion (RRF) Implementation."""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass(slots=True)
class RRFConfig:
    k: int = 60
    top_k: int = 10


def reciprocal_rank_fusion(rankings: List[List[Tuple[str, float]]], k: int = 60) -> List[Tuple[str, float]]:
    """
    Apply Reciprocal Rank Fusion to multiple ranked lists.
    
    RRF score = sum(1 / (k + rank_i) for each list)
    
    Args:
     rankings: List of ranked lists, each containing (doc_id, score) tuples
     k: RRF constant (default 60)
    
    Returns:
     Fused ranked list of (doc_id, rrf_score) tuples
    """
    doc_scores: Dict[str, float] = {}
    for ranking in rankings:
        for rank, (doc_id, score) in enumerate(ranking, 1):
            rrf_score = 1.0 / (k + rank)
            if doc_id not in doc_scores:
                doc_scores[doc_id] = 0.0
            doc_scores[doc_id] += rrf_score
    fused = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
    return fused


def rrf_fuse_keyword_vector(keyword_results: List[Tuple[str, float]], vector_results: List[Tuple[str, float]], k: int = 60, top_k: int = 10) -> List[Tuple[str, float]]:
    """Fuse keyword and vector search results using RRF."""
    rankings = [keyword_results, vector_results]
    fused = reciprocal_rank_fusion(rankings, k=k)
    return fused[:top_k]


class RRFFusion:
    def __init__(self, k: int = 60, top_k: int = 10):
        self.k = k
        self.top_k = top_k

    def fuse(self, *rankings: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        return reciprocal_rank_fusion(list(rankings), k=self.k)[:self.top_k]