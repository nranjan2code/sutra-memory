"""
Dependency injection for FastAPI endpoints.

Provides shared instances and dependency functions using FastAPI app.state
instead of global variables for better testability and multi-worker support.
"""

import logging
import time
from typing import Optional

from fastapi import FastAPI, Request
from sutra_core.graph.concepts import AssociationType
from sutra_core.reasoning import ReasoningEngine
from sutra_hybrid import HybridAI

from .config import settings

logger = logging.getLogger(__name__)

# Track service start time
_start_time: float = time.time()


def init_dependencies(app: FastAPI) -> None:
    """
    Initialize dependencies and store them in app.state.
    Called during lifespan startup.
    
    Args:
        app: FastAPI application instance
    """
    logger.info("Initializing dependencies...")
    
    # Create HybridAI instance
    app.state.ai_instance = HybridAI(
        use_semantic=settings.use_semantic_embeddings,
        storage_path=settings.storage_path,
    )
    
    # Map configured compositional type to AssociationType
    type_map = {
        "compositional": AssociationType.COMPOSITIONAL,
        "hierarchical": AssociationType.HIERARCHICAL,
        "semantic": AssociationType.SEMANTIC,
        "causal": AssociationType.CAUSAL,
        "temporal": AssociationType.TEMPORAL,
    }
    link_type = type_map.get(
        str(getattr(settings, "compositional_type", "compositional")).lower(),
        AssociationType.COMPOSITIONAL,
    )

    # Create reasoning engine bound to HybridAI knowledge
    app.state.reasoner_instance = ReasoningEngine(
        enable_caching=True,
        cache_ttl_seconds=settings.cache_ttl_seconds,
        enable_central_links=settings.compositional_links,
        central_link_confidence=settings.compositional_confidence,
        central_link_type=link_type,
    )
    
    # Bind engine data structures to HybridAI's live state
    ai = app.state.ai_instance
    reasoner = app.state.reasoner_instance
    reasoner.concepts = ai.concepts
    reasoner.associations = ai.associations
    reasoner.concept_neighbors = ai.concept_neighbors
    reasoner.word_to_concepts = ai.word_to_concepts
    # Rebuild indexes to ensure consistency
    reasoner._rebuild_indexes()
    
    logger.info("Dependencies initialized successfully")


def shutdown_dependencies(app: FastAPI) -> None:
    """
    Clean up dependencies during shutdown.
    Called during lifespan shutdown.
    
    Args:
        app: FastAPI application instance
    """
    if settings.auto_save and hasattr(app.state, "ai_instance"):
        logger.info("Saving knowledge before shutdown...")
        app.state.ai_instance.save()
        logger.info("Knowledge saved")
    
    # Clean up references
    if hasattr(app.state, "ai_instance"):
        delattr(app.state, "ai_instance")
    if hasattr(app.state, "reasoner_instance"):
        delattr(app.state, "reasoner_instance")


def get_ai(request: Request) -> HybridAI:
    """
    Dependency to get HybridAI instance from request state.
    
    Args:
        request: FastAPI request containing app.state
        
    Returns:
        HybridAI instance
    """
    return request.app.state.ai_instance


def get_uptime() -> float:
    """
    Get service uptime in seconds.

    Returns:
        Uptime in seconds
    """
    return time.time() - _start_time


def get_reasoner(request: Request) -> ReasoningEngine:
    """
    Dependency to get ReasoningEngine instance from request state.
    
    The engine is bound to HybridAI's knowledge graph, ensuring they
    stay synchronized.
    
    Args:
        request: FastAPI request containing app.state
        
    Returns:
        ReasoningEngine instance
    """
    ai = request.app.state.ai_instance
    reasoner = request.app.state.reasoner_instance
    
    # Ensure bindings are fresh (in case of multi-worker scenarios)
    reasoner.concepts = ai.concepts
    reasoner.associations = ai.associations
    reasoner.concept_neighbors = ai.concept_neighbors
    reasoner.word_to_concepts = ai.word_to_concepts
    
    return reasoner
