"""
Main FastAPI application with all API endpoints.

Provides REST API for Sutra AI graph-based reasoning system.
"""

import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sutra_core import SutraError
from sutra_hybrid import HybridAI

from .config import settings
from .dependencies import get_ai, get_uptime
from .models import (
    BatchLearnRequest,
    BatchLearnResponse,
    ConceptDetail,
    ErrorResponse,
    HealthResponse,
    LearnRequest,
    LearnResponse,
    ReasonRequest,
    ReasonResponse,
    ReasoningPath,
    SearchResult,
    SemanticSearchRequest,
    SemanticSearchResponse,
    SystemStats,
)

# Configure logging
logging.basicConfig(level=settings.log_level, format=settings.log_format)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"Storage path: {settings.storage_path}")
    logger.info(
        f"Semantic embeddings: {settings.use_semantic_embeddings}"
    )

    # Initialize AI instance
    ai = get_ai()
    logger.info(
        f"Loaded {len(ai.concepts)} concepts, "
        f"{len(ai.associations)} associations"
    )

    yield

    # Shutdown
    if settings.auto_save:
        logger.info("Saving knowledge before shutdown...")
        ai = get_ai()
        ai.save()
        logger.info("Knowledge saved")

    logger.info("Shutting down API service")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=settings.allow_methods,
    allow_headers=settings.allow_headers,
)


# Exception handlers
@app.exception_handler(SutraError)
async def sutra_error_handler(request, exc: SutraError):
    """Handle Sutra-specific errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc),
            "detail": None,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "detail": str(exc) if settings.log_level == "DEBUG" else None,
        },
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check(ai: HybridAI = Depends(get_ai)):
    """
    Check API health status.

    Returns service status, version, uptime, and basic metrics.
    """
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        uptime_seconds=get_uptime(),
        concepts_loaded=len(ai.concepts),
    )


# Learning endpoints
@app.post(
    "/learn",
    response_model=LearnResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Learning"],
)
async def learn_knowledge(
    request: LearnRequest, ai: HybridAI = Depends(get_ai)
):
    """
    Learn new knowledge.

    Creates concepts and associations from the provided content.
    """
    concepts_before = len(ai.concepts)
    associations_before = len(ai.associations)

    # Learn the content
    concept_id = ai.learn(
        request.content,
        source=request.source,
        **(request.metadata or {}),
    )

    concepts_created = len(ai.concepts) - concepts_before
    associations_created = len(ai.associations) - associations_before

    return LearnResponse(
        concept_id=concept_id,
        message="Knowledge learned successfully",
        concepts_created=concepts_created,
        associations_created=associations_created,
    )


@app.post(
    "/learn/batch",
    response_model=BatchLearnResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Learning"],
)
async def batch_learn(
    request: BatchLearnRequest, ai: HybridAI = Depends(get_ai)
):
    """
    Learn multiple knowledge items in batch.

    More efficient than calling /learn multiple times.
    """
    concepts_before = len(ai.concepts)
    associations_before = len(ai.associations)

    concept_ids = []
    for item in request.items:
        concept_id = ai.learn(
            item.content,
            source=item.source,
            **(item.metadata or {}),
        )
        concept_ids.append(concept_id)

    total_concepts = len(ai.concepts) - concepts_before
    total_associations = len(ai.associations) - associations_before

    return BatchLearnResponse(
        concept_ids=concept_ids,
        total_concepts=total_concepts,
        total_associations=total_associations,
        message=f"Successfully learned {len(concept_ids)} items",
    )


# Reasoning endpoints
@app.post("/reason", response_model=ReasonResponse, tags=["Reasoning"])
async def reason(
    request: ReasonRequest, ai: HybridAI = Depends(get_ai)
):
    """
    Perform reasoning query.

    Uses multi-path spreading activation to find answers.
    """
    # Perform spreading activation reasoning
    # Note: This is a simplified version. Full implementation would use
    # the spreading activation algorithm from sutra-core
    from sutra_core.utils import extract_words

    query_words = extract_words(request.query)

    # Find relevant concepts
    relevant_concepts = []
    for word in query_words:
        if word in ai.word_to_concepts:
            relevant_concepts.extend(list(ai.word_to_concepts[word]))

    # Build simple reasoning paths
    paths = []
    for concept_id in relevant_concepts[:request.num_paths]:
        concept = ai.concepts.get(concept_id)
        if concept:
            paths.append(
                ReasoningPath(
                    concepts=[concept_id],
                    confidence=min(concept.strength / 10.0, 1.0),
                    explanation=f"Found: {concept.content[:100]}",
                )
            )

    # Generate answer from top path
    answer = "No relevant knowledge found"
    confidence = 0.0
    if paths:
        top_path = max(paths, key=lambda p: p.confidence)
        top_concept = ai.concepts[top_path.concepts[0]]
        answer = top_concept.content
        confidence = top_path.confidence

    return ReasonResponse(
        query=request.query,
        answer=answer,
        confidence=confidence,
        paths=paths,
        concepts_accessed=len(relevant_concepts),
    )


@app.post(
    "/semantic-search",
    response_model=SemanticSearchResponse,
    tags=["Reasoning"],
)
async def semantic_search(
    request: SemanticSearchRequest, ai: HybridAI = Depends(get_ai)
):
    """
    Search for similar concepts using semantic embeddings.

    Returns concepts ranked by similarity score.
    """
    results = ai.semantic_search(
        request.query, top_k=request.top_k, threshold=request.threshold
    )

    search_results = []
    for concept_id, similarity in results:
        concept = ai.concepts.get(concept_id)
        if concept:
            search_results.append(
                SearchResult(
                    concept_id=concept_id,
                    content=concept.content,
                    similarity=similarity,
                    strength=concept.strength,
                )
            )

    return SemanticSearchResponse(
        query=request.query,
        results=search_results,
        total_found=len(search_results),
    )


@app.get(
    "/concepts/{concept_id}",
    response_model=ConceptDetail,
    tags=["Reasoning"],
)
async def get_concept(
    concept_id: str, ai: HybridAI = Depends(get_ai)
):
    """
    Get detailed information about a specific concept.

    Includes associations and metadata.
    """
    concept = ai.concepts.get(concept_id)
    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concept {concept_id} not found",
        )

    # Get associated concept IDs
    associations = list(ai.concept_neighbors.get(concept_id, set()))

    return ConceptDetail(
        id=concept.id,
        content=concept.content,
        strength=concept.strength,
        access_count=concept.access_count,
        created_at=concept.created_at.isoformat() if concept.created_at else None,
        source=concept.source,
        associations=associations,
    )


# Management endpoints
@app.get("/stats", response_model=SystemStats, tags=["System"])
async def get_stats(ai: HybridAI = Depends(get_ai)):
    """
    Get system statistics and metrics.

    Returns information about concepts, embeddings, and performance.
    """
    stats = ai.get_stats()

    return SystemStats(
        total_concepts=stats["total_concepts"],
        total_associations=stats["total_associations"],
        total_embeddings=stats["total_embeddings"],
        embedding_provider=stats["embedding_provider"],
        embedding_dimension=stats["embedding_dimension"],
        average_strength=stats["average_strength"],
        memory_usage_mb=None,  # Could implement memory profiling
    )


@app.post("/save", status_code=status.HTTP_200_OK, tags=["System"])
async def save_knowledge(ai: HybridAI = Depends(get_ai)):
    """
    Save current knowledge to disk.

    Persists all concepts, associations, and embeddings.
    """
    try:
        ai.save()
        return {"message": "Knowledge saved successfully"}
    except Exception as e:
        logger.error(f"Failed to save knowledge: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save knowledge: {str(e)}",
        )


@app.post("/load", status_code=status.HTTP_200_OK, tags=["System"])
async def load_knowledge(ai: HybridAI = Depends(get_ai)):
    """
    Reload knowledge from disk.

    Replaces current knowledge with saved data.
    """
    try:
        ai.load()
        return {
            "message": "Knowledge loaded successfully",
            "concepts_loaded": len(ai.concepts),
        }
    except Exception as e:
        logger.error(f"Failed to load knowledge: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load knowledge: {str(e)}",
        )


@app.delete(
    "/reset", status_code=status.HTTP_200_OK, tags=["System"]
)
async def reset_system():
    """
    Reset the system and clear all knowledge.

    WARNING: This deletes all concepts and associations!
    """
    from .dependencies import reset_ai

    reset_ai()
    ai = get_ai()  # Create fresh instance

    return {
        "message": "System reset successfully",
        "concepts": len(ai.concepts),
    }


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """API root endpoint with basic information."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "sutra_api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        workers=settings.workers,
    )
