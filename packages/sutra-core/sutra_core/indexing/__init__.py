"""
Vector indexing and search for fast semantic retrieval.

This module provides efficient vector search capabilities using HNSW
(Hierarchical Navigable Small World) graphs for O(log N) search complexity.
"""

from .vector_search import VectorIndex

__all__ = ["VectorIndex"]
