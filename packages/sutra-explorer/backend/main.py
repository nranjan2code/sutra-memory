"""
Sutra Explorer Backend API

Production-grade FastAPI service for knowledge graph visualization.
Integrates with Sutra platform via storage clients (NO direct storage access).

Architecture:
- Storage access: ONLY via sutra-storage-client (TCP binary protocol)
- Multi-domain support: Connect to user-storage + N domain storages
- Edition-aware: Respects Simple/Community/Enterprise limits
- Read-only: Safe exploration, no graph modification
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global storage clients
_storage_clients: Dict[str, Any] = {}
_start_time = datetime.utcnow()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    logger.info("Starting Sutra Explorer Backend v2.0")
    logger.info("Initializing storage clients...")
    
    try:
        from sutra_storage_client import StorageClient
        
        # User storage (conversations, messages, bookmarks)
        user_storage_addr = os.getenv("SUTRA_USER_STORAGE", "user-storage-server:50051")
        logger.info(f"Connecting to user storage: {user_storage_addr}")
        _storage_clients["user"] = StorageClient(user_storage_addr)
        logger.info("✓ User storage connected")
        
        # Domain storage (knowledge graphs)
        domain_storage_addr = os.getenv("SUTRA_DOMAIN_STORAGE", "storage-server:50051")
        logger.info(f"Connecting to domain storage: {domain_storage_addr}")
        _storage_clients["domain"] = StorageClient(domain_storage_addr)
        logger.info("✓ Domain storage connected")
        
        # Optional: Additional domain storages (comma-separated)
        additional_storages = os.getenv("SUTRA_ADDITIONAL_STORAGES", "")
        if additional_storages:
            for storage_spec in additional_storages.split(","):
                if "=" in storage_spec:
                    name, addr = storage_spec.split("=", 1)
                    logger.info(f"Connecting to {name}: {addr}")
                    _storage_clients[name] = StorageClient(addr)
                    logger.info(f"✓ {name} connected")
        
        app.state.storage_clients = _storage_clients
        logger.info(f"Storage clients initialized: {list(_storage_clients.keys())}")
        
    except Exception as e:
        logger.error(f"Failed to initialize storage clients: {e}")
        raise RuntimeError(f"Storage initialization failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Sutra Explorer Backend...")
    for name, client in _storage_clients.items():
        try:
            client.flush()
            logger.info(f"Flushed {name} storage")
        except Exception as e:
            logger.warning(f"Error flushing {name} storage: {e}")
    
    _storage_clients.clear()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Sutra Explorer API",
    version="2.0.0",
    description="Knowledge graph visualization and exploration API",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ============================================================================
# DEPENDENCIES
# ============================================================================

def get_user_storage(request: Request):
    """Get user storage client from app state."""
    return request.app.state.storage_clients.get("user")


def get_domain_storage(request: Request, storage_name: str = "domain"):
    """Get domain storage client by name."""
    storage = request.app.state.storage_clients.get(storage_name)
    if not storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Storage '{storage_name}' not found"
        )
    return storage


# ============================================================================
# MODELS
# ============================================================================

from pydantic import BaseModel, Field
from typing import List, Optional


class NodeResponse(BaseModel):
    """Graph node (concept)."""
    id: str
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    strength: float = Field(ge=0.0, le=1.0)
    access_count: int = 0
    created_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    edge_count: int = 0


class EdgeResponse(BaseModel):
    """Graph edge (association)."""
    source_id: str
    target_id: str
    confidence: float = Field(ge=0.0, le=1.0)
    edge_type: str = "association"


class GraphResponse(BaseModel):
    """Complete graph data."""
    nodes: List[NodeResponse]
    edges: List[EdgeResponse]
    total_nodes: int
    total_edges: int
    storage_name: str


class PathResponse(BaseModel):
    """Reasoning path between concepts."""
    source_id: str
    target_id: str
    path: List[str]
    confidence: float
    total_hops: int


class NeighborhoodResponse(BaseModel):
    """N-hop neighborhood around a concept."""
    center_id: str
    depth: int
    graph: GraphResponse


class SearchResponse(BaseModel):
    """Search results."""
    query: str
    results: List[NodeResponse]
    total_results: int


class StatsResponse(BaseModel):
    """Storage statistics."""
    storage_name: str
    total_concepts: int
    total_associations: int
    avg_confidence: float
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    uptime_seconds: float
    storage_clients: List[str]
    timestamp: str


# ============================================================================
# ROUTES
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """
    Health check endpoint.
    
    Returns service status and connected storage clients.
    """
    uptime = (datetime.utcnow() - _start_time).total_seconds()
    
    return HealthResponse(
        status="healthy",
        uptime_seconds=uptime,
        storage_clients=list(request.app.state.storage_clients.keys()),
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/storages")
async def list_storages(request: Request):
    """
    List available storage clients.
    
    Returns:
    - List of storage names (user, domain, custom domains)
    """
    return {
        "storages": list(request.app.state.storage_clients.keys()),
        "default": "domain"
    }


@app.get("/concepts", response_model=GraphResponse)
async def get_concepts(
    request: Request,
    storage: str = "domain",
    limit: int = 100,
    offset: int = 0,
    min_confidence: float = 0.0
):
    """
    List concepts from storage.
    
    Args:
    - storage: Storage name (default: "domain")
    - limit: Max concepts to return (1-500, default: 100)
    - offset: Pagination offset (default: 0)
    - min_confidence: Filter by confidence (0.0-1.0, default: 0.0)
    
    Returns:
    - List of concepts (nodes)
    - Empty edges (use /associations/{id} for edges)
    """
    # Validate params
    limit = max(1, min(limit, 500))
    offset = max(0, offset)
    min_confidence = max(0.0, min(min_confidence, 1.0))
    
    # Get storage client
    storage_client = get_domain_storage(request, storage)
    
    try:
        # Search all concepts (empty query returns all)
        result = storage_client.search("", limit=limit)
        
        # Convert to NodeResponse
        nodes = []
        for concept in result.get("results", []):
            # Apply confidence filter
            if concept.get("confidence", 0.0) >= min_confidence:
                nodes.append(NodeResponse(
                    id=concept["id"],
                    content=concept.get("content", ""),
                    confidence=concept.get("confidence", 0.0),
                    strength=concept.get("strength", 0.0),
                    access_count=concept.get("access_count", 0),
                    created_at=concept.get("created_at"),
                    metadata=concept.get("metadata"),
                    edge_count=len(concept.get("associations", []))
                ))
        
        return GraphResponse(
            nodes=nodes,
            edges=[],
            total_nodes=len(nodes),
            total_edges=0,
            storage_name=storage
        )
        
    except Exception as e:
        logger.error(f"Failed to get concepts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get concepts: {str(e)}"
        )


@app.get("/concepts/{concept_id}", response_model=NodeResponse)
async def get_concept(
    concept_id: str,
    request: Request,
    storage: str = "domain"
):
    """
    Get concept details by ID.
    
    Args:
    - concept_id: Concept ID
    - storage: Storage name (default: "domain")
    
    Returns:
    - Complete concept data
    """
    storage_client = get_domain_storage(request, storage)
    
    try:
        concept = storage_client.get_concept(concept_id)
        
        if not concept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Concept not found: {concept_id}"
            )
        
        return NodeResponse(
            id=concept["id"],
            content=concept.get("content", ""),
            confidence=concept.get("confidence", 0.0),
            strength=concept.get("strength", 0.0),
            access_count=concept.get("access_count", 0),
            created_at=concept.get("created_at"),
            metadata=concept.get("metadata"),
            edge_count=len(concept.get("associations", []))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get concept {concept_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get concept: {str(e)}"
        )


@app.get("/associations/{concept_id}", response_model=List[EdgeResponse])
async def get_associations(
    concept_id: str,
    request: Request,
    storage: str = "domain"
):
    """
    Get associations (edges) for a concept.
    
    Args:
    - concept_id: Concept ID
    - storage: Storage name (default: "domain")
    
    Returns:
    - List of edges
    """
    storage_client = get_domain_storage(request, storage)
    
    try:
        concept = storage_client.get_concept(concept_id)
        
        if not concept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Concept not found: {concept_id}"
            )
        
        edges = []
        for assoc in concept.get("associations", []):
            edges.append(EdgeResponse(
                source_id=concept_id,
                target_id=assoc["target_id"],
                confidence=assoc.get("confidence", 0.0),
                edge_type=assoc.get("type", "association")
            ))
        
        return edges
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get associations for {concept_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get associations: {str(e)}"
        )


@app.post("/search", response_model=SearchResponse)
async def search_concepts(
    query: str,
    request: Request,
    storage: str = "domain",
    limit: int = 20
):
    """
    Full-text search for concepts.
    
    Args:
    - query: Search query
    - storage: Storage name (default: "domain")
    - limit: Max results (1-100, default: 20)
    
    Returns:
    - List of matching concepts
    """
    limit = max(1, min(limit, 100))
    
    storage_client = get_domain_storage(request, storage)
    
    try:
        result = storage_client.search(query, limit=limit)
        
        nodes = []
        for concept in result.get("results", []):
            nodes.append(NodeResponse(
                id=concept["id"],
                content=concept.get("content", ""),
                confidence=concept.get("confidence", 0.0),
                strength=concept.get("strength", 0.0),
                access_count=concept.get("access_count", 0),
                created_at=concept.get("created_at"),
                metadata=concept.get("metadata"),
                edge_count=len(concept.get("associations", []))
            ))
        
        return SearchResponse(
            query=query,
            results=nodes,
            total_results=len(nodes)
        )
        
    except Exception as e:
        logger.error(f"Search failed for query '{query}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@app.post("/neighborhood", response_model=NeighborhoodResponse)
async def get_neighborhood(
    concept_id: str,
    request: Request,
    storage: str = "domain",
    depth: int = 2,
    max_nodes: int = 50
):
    """
    Get N-hop neighborhood around a concept.
    
    Args:
    - concept_id: Central concept ID
    - storage: Storage name (default: "domain")
    - depth: How many hops (1-5, default: 2)
    - max_nodes: Max nodes to return (10-200, default: 50)
    
    Returns:
    - Subgraph around concept
    """
    # Validate params
    depth = max(1, min(depth, 5))
    max_nodes = max(10, min(max_nodes, 200))
    
    storage_client = get_domain_storage(request, storage)
    
    try:
        # BFS traversal to collect neighborhood
        visited = set()
        nodes_data = {}
        edges_data = []
        queue = [(concept_id, 0)]
        
        while queue and len(nodes_data) < max_nodes:
            current_id, current_depth = queue.pop(0)
            
            if current_id in visited or current_depth > depth:
                continue
            
            visited.add(current_id)
            
            # Get concept
            concept = storage_client.get_concept(current_id)
            if not concept:
                continue
            
            nodes_data[current_id] = concept
            
            # Add neighbors to queue
            if current_depth < depth:
                for assoc in concept.get("associations", []):
                    target_id = assoc["target_id"]
                    
                    # Add edge
                    edges_data.append(EdgeResponse(
                        source_id=current_id,
                        target_id=target_id,
                        confidence=assoc.get("confidence", 0.0),
                        edge_type=assoc.get("type", "association")
                    ))
                    
                    if target_id not in visited:
                        queue.append((target_id, current_depth + 1))
        
        # Convert to NodeResponse
        nodes = [
            NodeResponse(
                id=cid,
                content=c.get("content", ""),
                confidence=c.get("confidence", 0.0),
                strength=c.get("strength", 0.0),
                access_count=c.get("access_count", 0),
                created_at=c.get("created_at"),
                metadata=c.get("metadata"),
                edge_count=len(c.get("associations", []))
            )
            for cid, c in nodes_data.items()
        ]
        
        graph = GraphResponse(
            nodes=nodes,
            edges=edges_data,
            total_nodes=len(nodes),
            total_edges=len(edges_data),
            storage_name=storage
        )
        
        return NeighborhoodResponse(
            center_id=concept_id,
            depth=depth,
            graph=graph
        )
        
    except Exception as e:
        logger.error(f"Failed to get neighborhood for {concept_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get neighborhood: {str(e)}"
        )


@app.get("/statistics/{storage_name}", response_model=StatsResponse)
async def get_statistics(
    storage_name: str,
    request: Request
):
    """
    Get storage statistics.
    
    Args:
    - storage_name: Storage name
    
    Returns:
    - Total concepts, associations, avg confidence
    """
    storage_client = get_domain_storage(request, storage_name)
    
    try:
        # Get all concepts (sample)
        result = storage_client.search("", limit=1000)
        concepts = result.get("results", [])
        
        total_concepts = len(concepts)
        total_associations = sum(len(c.get("associations", [])) for c in concepts)
        avg_confidence = (
            sum(c.get("confidence", 0.0) for c in concepts) / total_concepts
            if total_concepts > 0 else 0.0
        )
        
        return StatsResponse(
            storage_name=storage_name,
            total_concepts=total_concepts,
            total_associations=total_associations,
            avg_confidence=avg_confidence,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to get statistics for {storage_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8100")),
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
