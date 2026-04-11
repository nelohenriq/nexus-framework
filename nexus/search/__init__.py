"""NEXUS Search Module - Phase 12: Search & Knowledge."""

from .hybrid import (
    HybridSearchEngine,
    SearchResult,
    HybridSearchResult,
    SearchMethod,
    create_hybrid_engine
)

from .rrf import (
    reciprocal_rank_fusion,
    rrf_fuse_keyword_vector,
    RRFFusion,
    RRFConfig
)

from .brain_first import (
    BrainFirstLookup,
    LookupResult,
    create_brain_first
)

from .dream_cycle import (
    DreamCycle,
    DreamTask,
    DreamResult,
    create_dream_cycle
)

__all__ = [
    "HybridSearchEngine", "SearchResult", "HybridSearchResult", "SearchMethod", "create_hybrid_engine",
    "reciprocal_rank_fusion", "rrf_fuse_keyword_vector", "RRFFusion", "RRFConfig",
    "BrainFirstLookup", "LookupResult", "create_brain_first",
    "DreamCycle", "DreamTask", "DreamResult", "create_dream_cycle"
]