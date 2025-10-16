"""
Embedding providers for semantic understanding.

This module provides different embedding strategies:
- SemanticEmbedding: Using sentence-transformers with EmbeddingGemma (768 dimensions)
- TfidfEmbedding: Lightweight TF-IDF fallback (100 dimensions)
"""

from .base import EmbeddingProvider
from .semantic import SemanticEmbedding
from .tfidf import TfidfEmbedding

__all__ = ["EmbeddingProvider", "SemanticEmbedding", "TfidfEmbedding"]
