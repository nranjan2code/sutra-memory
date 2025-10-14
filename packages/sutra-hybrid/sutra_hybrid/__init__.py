"""
Sutra Hybrid - Semantic embeddings integration for Sutra AI.

This package combines graph-based reasoning with semantic embeddings
to provide enhanced understanding and similarity search capabilities.

Key Features:
- Semantic similarity search using embeddings
- TF-IDF fallback when sentence-transformers unavailable
- Combined graph + semantic reasoning
- Efficient embedding storage and retrieval
"""

from .core import HybridAI
from .embeddings import EmbeddingProvider, SemanticEmbedding, TfidfEmbedding

__version__ = "1.0.0"

__all__ = [
    "HybridAI",
    "EmbeddingProvider",
    "SemanticEmbedding",
    "TfidfEmbedding",
]
