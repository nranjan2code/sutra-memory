"""
Dependency injection for FastAPI endpoints.

Provides shared instances and dependency functions.
"""

import time
from typing import Optional

from sutra_hybrid import HybridAI

from .config import settings

# Global instances
_ai_instance: Optional[HybridAI] = None
_start_time: float = time.time()


def get_ai() -> HybridAI:
    """
    Get or create the HybridAI instance.

    Returns:
        HybridAI instance
    """
    global _ai_instance

    if _ai_instance is None:
        _ai_instance = HybridAI(
            use_semantic=settings.use_semantic_embeddings,
            storage_path=settings.storage_path,
        )

    return _ai_instance


def get_uptime() -> float:
    """
    Get service uptime in seconds.

    Returns:
        Uptime in seconds
    """
    return time.time() - _start_time


def reset_ai() -> None:
    """Reset the AI instance (for testing or reset operations)."""
    global _ai_instance
    _ai_instance = None
