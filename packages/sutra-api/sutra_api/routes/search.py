"""
Search API Routes

Endpoints for semantic search across conversations, messages, and spaces.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from ..middleware.auth import get_current_user
from ..services.search_service import SearchService, GroupedSearchResults
from ..dependencies import get_search_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


# Request/Response Models

class SearchQueryRequest(BaseModel):
    """Unified search query request."""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional filters (space_id, starred, date_range)")
    limit: int = Field(30, ge=1, le=100, description="Maximum total results")


class SearchConversationsRequest(BaseModel):
    """Search conversations request."""
    query: str = Field(..., min_length=1, max_length=500)
    filters: Optional[Dict[str, Any]] = None
    limit: int = Field(20, ge=1, le=50)


class SearchMessagesRequest(BaseModel):
    """Search messages request."""
    query: str = Field(..., min_length=1, max_length=500)
    filters: Optional[Dict[str, Any]] = None
    limit: int = Field(20, ge=1, le=50)


class SearchSpacesRequest(BaseModel):
    """Search spaces request."""
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(10, ge=1, le=20)


class SearchResultResponse(BaseModel):
    """Single search result."""
    type: str  # conversation, message, space
    id: str
    title: str
    content: str
    metadata: Dict[str, Any]
    score: float


class SearchGroupResponse(BaseModel):
    """Group of search results."""
    count: int
    results: List[SearchResultResponse]


class GroupedSearchResponse(BaseModel):
    """Grouped search results response."""
    total_count: int
    groups: Dict[str, SearchGroupResponse]


# Routes

@router.post("/query", response_model=GroupedSearchResponse)
async def unified_search(
    request: SearchQueryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Unified search across all content types (conversations, messages, spaces).
    
    Returns results grouped by type with relevance scoring.
    
    Example:
    ```
    POST /search/query
    {
        "query": "machine learning",
        "filters": {
            "space_id": "space_123",
            "starred": true
        },
        "limit": 30
    }
    ```
    """
    try:
        results = await search_service.unified_search(
            query=request.query,
            user_id=current_user["id"],
            organization_id=current_user["organization_id"],
            filters=request.filters,
            limit=request.limit
        )
        
        return GroupedSearchResponse(**results.to_dict())
    
    except Exception as e:
        logger.error(f"Unified search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations", response_model=List[SearchResultResponse])
async def search_conversations(
    request: SearchConversationsRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Search conversations only.
    
    Returns conversations matching the query, ordered by relevance.
    
    Example:
    ```
    POST /search/conversations
    {
        "query": "python tutorial",
        "filters": {
            "space_id": "space_123",
            "starred": true
        },
        "limit": 20
    }
    ```
    """
    try:
        results = await search_service.search_conversations(
            query=request.query,
            user_id=current_user["id"],
            organization_id=current_user["organization_id"],
            filters=request.filters,
            limit=request.limit
        )
        
        return [SearchResultResponse(**r.to_dict()) for r in results]
    
    except Exception as e:
        logger.error(f"Conversation search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages", response_model=List[SearchResultResponse])
async def search_messages(
    request: SearchMessagesRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Search messages only.
    
    Returns messages matching the query, ordered by relevance.
    Useful for finding specific information across conversations.
    
    Example:
    ```
    POST /search/messages
    {
        "query": "API documentation",
        "filters": {
            "conversation_id": "conv_123"
        },
        "limit": 20
    }
    ```
    """
    try:
        results = await search_service.search_messages(
            query=request.query,
            user_id=current_user["id"],
            organization_id=current_user["organization_id"],
            filters=request.filters,
            limit=request.limit
        )
        
        return [SearchResultResponse(**r.to_dict()) for r in results]
    
    except Exception as e:
        logger.error(f"Message search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/spaces", response_model=List[SearchResultResponse])
async def search_spaces(
    request: SearchSpacesRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Search spaces only.
    
    Returns spaces matching the query, ordered by relevance.
    
    Example:
    ```
    POST /search/spaces
    {
        "query": "medical",
        "limit": 10
    }
    ```
    """
    try:
        results = await search_service.search_spaces(
            query=request.query,
            user_id=current_user["id"],
            organization_id=current_user["organization_id"],
            limit=request.limit
        )
        
        return [SearchResultResponse(**r.to_dict()) for r in results]
    
    except Exception as e:
        logger.error(f"Space search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quick")
async def quick_search(
    q: str = Query(..., min_length=1, max_length=200, description="Quick search query"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Quick search for command palette (Cmd+K).
    
    Returns top results across all types, optimized for speed.
    Limited to 15 total results for fast rendering.
    
    Example:
    ```
    GET /search/quick?q=machine+learning
    ```
    """
    try:
        results = await search_service.unified_search(
            query=q,
            user_id=current_user["id"],
            organization_id=current_user["organization_id"],
            filters=None,
            limit=15  # Quick search - fewer results
        )
        
        return results.to_dict()
    
    except Exception as e:
        logger.error(f"Quick search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
