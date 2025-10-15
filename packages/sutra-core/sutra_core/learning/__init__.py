"""
Learning components for the Sutra AI system.

This package contains:
- Association extraction and pattern matching
- Adaptive focus learning algorithms
- Knowledge integration strategies
- Batch embedding generation with MPS support
- Parallel association extraction for high performance
- Entity caching for LLM-based extraction (Phase 10)
"""

from .adaptive import AdaptiveLearner
from .associations import AssociationExtractor
from .associations_parallel import ParallelAssociationExtractor
from .embeddings import EmbeddingBatchProcessor, create_embedding_processor
from .entity_cache import EntityCache

__all__ = [
    "AssociationExtractor",
    "ParallelAssociationExtractor",
    "AdaptiveLearner",
    "EmbeddingBatchProcessor",
    "create_embedding_processor",
    "EntityCache",
]
