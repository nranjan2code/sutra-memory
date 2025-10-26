"""
Graph API Routes

REST API endpoints for knowledge graph visualization.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging

from ..middleware.auth import get_current_active_user
from ..dependencies import get_user_storage_client, get_domain_storage_clients, get_graph_service
from ..models.graph import (
    MessageGraphRequest,
    MessageGraphResponse,
    ConceptGraphRequest,
    ConceptGraphResponse,
    QueryGraphRequest,
    QueryGraphResponse,
    GraphStatisticsResponse,
    GraphData,
    GraphNode as GraphNodeModel,
    GraphEdge as GraphEdgeModel
)
from ..services.graph_service import GraphService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graph", tags=["graph"])


@router.post("/message", response_model=MessageGraphResponse)
async def get_message_graph(
    request: MessageGraphRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    user_storage=Depends(get_user_storage_client),
    graph_service: GraphService = Depends(get_graph_service)
):
    """
    Get knowledge graph visualization for a message's reasoning.
    
    Extracts reasoning paths and concepts used to generate an assistant message,
    then builds a graph visualization showing how the answer was derived.
    
    **Args:**
    - `message_id`: ID of the assistant message
    - `conversation_id`: ID of conversation containing the message
    - `max_depth`: Maximum depth to expand concepts (1-5)
    
    **Returns:**
    - Graph data with nodes and edges
    - Reasoning paths used
    - Confidence score
    
    **Example:**
    ```json
    {
      "message_id": "msg_123",
      "conversation_id": "conv_456",
      "max_depth": 2
    }
    ```
    """
    try:
        # Load message from user storage
        try:
            message_concept = await user_storage.get_concept(request.message_id)
        except Exception as e:
            logger.error(f"Failed to load message {request.message_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message not found: {request.message_id}"
            )
        
        if not message_concept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message not found: {request.message_id}"
            )
        
        # Verify message belongs to conversation
        metadata = message_concept.metadata
        if metadata.get("conversation_id") != request.conversation_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Message does not belong to specified conversation"
            )
        
        # Verify message belongs to user's organization
        if metadata.get("organization") != current_user.get("organization"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this message"
            )
        
        # Get conversation to determine domain storage
        try:
            conversation_concept = await user_storage.get_concept(request.conversation_id)
        except Exception as e:
            logger.error(f"Failed to load conversation {request.conversation_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation not found: {request.conversation_id}"
            )
        
        if not conversation_concept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation not found: {request.conversation_id}"
            )
        
        domain_storage = conversation_concept.metadata.get("domain_storage", "default")
        
        # Extract graph data
        graph_data = await graph_service.get_message_reasoning_graph(
            message_metadata=metadata,
            domain_storage=domain_storage,
            max_depth=request.max_depth
        )
        
        # Convert to response model
        nodes = [GraphNodeModel(**node) for node in graph_data["nodes"]]
        edges = [GraphEdgeModel(**edge) for edge in graph_data["edges"]]
        
        return MessageGraphResponse(
            message_id=request.message_id,
            graph=GraphData(
                nodes=nodes,
                edges=edges,
                concept_count=graph_data["concept_count"],
                edge_count=graph_data["edge_count"]
            ),
            reasoning_paths=graph_data["reasoning_paths"],
            confidence=graph_data["confidence"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get message graph: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get message graph: {str(e)}"
        )


@router.post("/concept", response_model=ConceptGraphResponse)
async def get_concept_graph(
    request: ConceptGraphRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    graph_service: GraphService = Depends(get_graph_service)
):
    """
    Get subgraph around a specific concept.
    
    Fetches a concept and expands outward following associations to build
    a local subgraph showing related concepts.
    
    **Args:**
    - `concept_id`: Central concept ID
    - `domain_storage`: Name of domain storage to query
    - `depth`: How many hops to expand (1-5)
    - `max_nodes`: Maximum nodes to return (10-200)
    
    **Returns:**
    - Graph data with nodes and edges
    - Central concept ID
    - Depth used
    
    **Example:**
    ```json
    {
      "concept_id": "concept_123",
      "domain_storage": "medical_knowledge",
      "depth": 2,
      "max_nodes": 50
    }
    ```
    """
    try:
        # Get subgraph
        graph_data = await graph_service.get_concept_subgraph(
            concept_id=request.concept_id,
            domain_storage=request.domain_storage,
            depth=request.depth,
            max_nodes=request.max_nodes
        )
        
        # Convert to response model
        nodes = [GraphNodeModel(**node) for node in graph_data["nodes"]]
        edges = [GraphEdgeModel(**edge) for edge in graph_data["edges"]]
        
        return ConceptGraphResponse(
            concept_id=request.concept_id,
            graph=GraphData(
                nodes=nodes,
                edges=edges,
                concept_count=graph_data["concept_count"],
                edge_count=graph_data["edge_count"]
            ),
            depth=graph_data["depth"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get concept graph: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get concept graph: {str(e)}"
        )


@router.post("/query", response_model=QueryGraphResponse)
async def get_query_graph(
    request: QueryGraphRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    graph_service: GraphService = Depends(get_graph_service)
):
    """
    Get reasoning paths for a query (without full reasoning execution).
    
    Finds relevant concepts and potential reasoning paths without executing
    full reasoning. Useful for previewing how a query might be answered.
    
    **Args:**
    - `query`: Query text
    - `domain_storage`: Name of domain storage to query
    - `max_paths`: Maximum paths to return (1-20)
    
    **Returns:**
    - List of reasoning paths
    - Path count
    
    **Example:**
    ```json
    {
      "query": "What is machine learning?",
      "domain_storage": "ai_knowledge",
      "max_paths": 5
    }
    ```
    """
    try:
        # Get reasoning paths
        paths = await graph_service.get_reasoning_paths_for_query(
            query=request.query,
            domain_storage=request.domain_storage,
            max_paths=request.max_paths
        )
        
        return QueryGraphResponse(
            query=request.query,
            paths=paths,
            path_count=len(paths)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get query graph: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get query graph: {str(e)}"
        )


@router.get("/statistics/{domain_storage}", response_model=GraphStatisticsResponse)
async def get_graph_statistics(
    domain_storage: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    graph_service: GraphService = Depends(get_graph_service)
):
    """
    Get statistics about a knowledge graph.
    
    Returns basic statistics like concept count, association count, etc.
    
    **Args:**
    - `domain_storage`: Name of domain storage to query
    
    **Returns:**
    - Total concepts
    - Total associations
    - Storage name
    - Timestamp
    
    **Example:**
    ```
    GET /graph/statistics/medical_knowledge
    ```
    """
    try:
        stats = await graph_service.get_graph_statistics(domain_storage)
        return GraphStatisticsResponse(**stats)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get graph statistics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get graph statistics: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for graph service.
    
    **Returns:**
    - Status message
    """
    return {
        "status": "healthy",
        "service": "graph"
    }
