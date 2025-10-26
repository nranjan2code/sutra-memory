"""
Search Service

Semantic search across conversations, messages, and spaces in user storage.
Provides unified search with result grouping and ranking.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging

from ..schema import ConceptType

logger = logging.getLogger(__name__)


def utc_now() -> str:
    """Get current UTC timestamp as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


class SearchResult:
    """Unified search result with metadata."""
    
    def __init__(
        self,
        result_type: str,
        id: str,
        title: str,
        content: str,
        metadata: Dict[str, Any],
        score: float
    ):
        self.result_type = result_type  # conversation, message, space
        self.id = id
        self.title = title
        self.content = content
        self.metadata = metadata
        self.score = score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.result_type,
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
            "score": round(self.score, 4)
        }


class GroupedSearchResults:
    """Search results grouped by type."""
    
    def __init__(self):
        self.conversations: List[SearchResult] = []
        self.messages: List[SearchResult] = []
        self.spaces: List[SearchResult] = []
        self.total_count: int = 0
    
    def add_result(self, result: SearchResult):
        """Add a result to the appropriate group."""
        if result.result_type == "conversation":
            self.conversations.append(result)
        elif result.result_type == "message":
            self.messages.append(result)
        elif result.result_type == "space":
            self.spaces.append(result)
        self.total_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_count": self.total_count,
            "groups": {
                "conversations": {
                    "count": len(self.conversations),
                    "results": [r.to_dict() for r in self.conversations]
                },
                "messages": {
                    "count": len(self.messages),
                    "results": [r.to_dict() for r in self.messages]
                },
                "spaces": {
                    "count": len(self.spaces),
                    "results": [r.to_dict() for r in self.spaces]
                }
            }
        }


class SearchService:
    """
    Service for semantic search across user storage.
    
    This service provides:
    - Unified search across conversations, messages, and spaces
    - Result grouping and ranking
    - Search filtering by user, organization, space
    - Highlighting and relevance scoring
    """
    
    def __init__(self, user_storage_client: Any):
        """
        Initialize search service.
        
        Args:
            user_storage_client: Client for user storage
        """
        self.user_storage = user_storage_client
        logger.info("SearchService initialized")
    
    async def unified_search(
        self,
        query: str,
        user_id: str,
        organization_id: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 30
    ) -> GroupedSearchResults:
        """
        Perform unified search across all content types.
        
        Args:
            query: Search query
            user_id: ID of the user performing search
            organization_id: Organization ID for access control
            filters: Optional filters (space_id, starred, date_range)
            limit: Maximum total results to return
            
        Returns:
            GroupedSearchResults with results grouped by type
        """
        logger.info(
            f"Unified search: query='{query}', user={user_id}, "
            f"org={organization_id}, limit={limit}"
        )
        
        # Build base filters
        base_filters = {
            "metadata.organization_id": organization_id
        }
        
        # Add optional filters
        if filters:
            if "space_id" in filters:
                base_filters["metadata.space_id"] = filters["space_id"]
            if "starred" in filters:
                base_filters["metadata.starred"] = filters["starred"]
        
        # Search conversations
        conversation_results = await self._search_conversations(
            query, user_id, base_filters, limit=limit // 3
        )
        
        # Search messages
        message_results = await self._search_messages(
            query, user_id, base_filters, limit=limit // 3
        )
        
        # Search spaces
        space_results = await self._search_spaces(
            query, user_id, base_filters, limit=limit // 3
        )
        
        # Combine and group results
        grouped_results = GroupedSearchResults()
        
        for result in conversation_results:
            grouped_results.add_result(result)
        
        for result in message_results:
            grouped_results.add_result(result)
        
        for result in space_results:
            grouped_results.add_result(result)
        
        logger.info(
            f"Search complete: {grouped_results.total_count} results "
            f"({len(conversation_results)} conversations, "
            f"{len(message_results)} messages, "
            f"{len(space_results)} spaces)"
        )
        
        return grouped_results
    
    async def search_conversations(
        self,
        query: str,
        user_id: str,
        organization_id: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20
    ) -> List[SearchResult]:
        """
        Search conversations only.
        
        Args:
            query: Search query
            user_id: ID of the user performing search
            organization_id: Organization ID
            filters: Optional filters
            limit: Maximum results to return
            
        Returns:
            List of conversation search results
        """
        base_filters = {
            "metadata.organization_id": organization_id
        }
        
        if filters:
            if "space_id" in filters:
                base_filters["metadata.space_id"] = filters["space_id"]
            if "starred" in filters:
                base_filters["metadata.starred"] = filters["starred"]
        
        return await self._search_conversations(
            query, user_id, base_filters, limit
        )
    
    async def search_messages(
        self,
        query: str,
        user_id: str,
        organization_id: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20
    ) -> List[SearchResult]:
        """
        Search messages only.
        
        Args:
            query: Search query
            user_id: ID of the user performing search
            organization_id: Organization ID
            filters: Optional filters (conversation_id, date_range)
            limit: Maximum results to return
            
        Returns:
            List of message search results
        """
        base_filters = {
            "metadata.organization_id": organization_id
        }
        
        if filters:
            if "conversation_id" in filters:
                base_filters["metadata.conversation_id"] = filters["conversation_id"]
        
        return await self._search_messages(
            query, user_id, base_filters, limit
        )
    
    async def search_spaces(
        self,
        query: str,
        user_id: str,
        organization_id: str,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Search spaces only.
        
        Args:
            query: Search query
            user_id: ID of the user performing search
            organization_id: Organization ID
            limit: Maximum results to return
            
        Returns:
            List of space search results
        """
        base_filters = {
            "metadata.organization_id": organization_id
        }
        
        return await self._search_spaces(
            query, user_id, base_filters, limit
        )
    
    # Private helper methods
    
    async def _search_conversations(
        self,
        query: str,
        user_id: str,
        base_filters: Dict[str, Any],
        limit: int
    ) -> List[SearchResult]:
        """Search conversations with semantic search."""
        search_filters = {
            **base_filters,
            "metadata.type": ConceptType.CONVERSATION.value,
            "metadata.user_id": user_id,
            "metadata.active": True
        }
        
        # Semantic search on conversation titles and content
        concepts = await self.user_storage.semantic_search(
            query=query,
            filters=search_filters,
            limit=limit
        )
        
        results = []
        for concept in concepts:
            # Calculate relevance score (simplified)
            score = self._calculate_relevance_score(
                query, concept.content, concept.metadata
            )
            
            result = SearchResult(
                result_type="conversation",
                id=concept.id,
                title=concept.metadata.get("title", concept.content),
                content=self._create_snippet(concept.content, query, max_length=150),
                metadata={
                    "space_id": concept.metadata["space_id"],
                    "message_count": concept.metadata["message_count"],
                    "updated_at": concept.metadata["updated_at"],
                    "starred": concept.metadata.get("starred", False),
                    "tags": concept.metadata.get("tags", [])
                },
                score=score
            )
            results.append(result)
        
        # Sort by score (highest first)
        results.sort(key=lambda r: r.score, reverse=True)
        
        return results
    
    async def _search_messages(
        self,
        query: str,
        user_id: str,
        base_filters: Dict[str, Any],
        limit: int
    ) -> List[SearchResult]:
        """Search messages with semantic search."""
        search_filters = {
            **base_filters,
            "metadata.type": [
                ConceptType.USER_MESSAGE.value,
                ConceptType.ASSISTANT_MESSAGE.value
            ]
        }
        
        # Semantic search on message content
        concepts = await self.user_storage.semantic_search(
            query=query,
            filters=search_filters,
            limit=limit
        )
        
        results = []
        for concept in concepts:
            # Calculate relevance score
            score = self._calculate_relevance_score(
                query, concept.content, concept.metadata
            )
            
            # Determine role
            role = (
                "user"
                if concept.metadata["type"] == ConceptType.USER_MESSAGE.value
                else "assistant"
            )
            
            # Get conversation title (would need to query in production)
            conversation_id = concept.metadata["conversation_id"]
            
            result = SearchResult(
                result_type="message",
                id=concept.id,
                title=f"Message in conversation",  # Simplified
                content=self._create_snippet(concept.content, query, max_length=200),
                metadata={
                    "conversation_id": conversation_id,
                    "role": role,
                    "timestamp": concept.metadata["timestamp"],
                    "highlighted": self._highlight_matches(concept.content, query)
                },
                score=score
            )
            results.append(result)
        
        # Sort by score
        results.sort(key=lambda r: r.score, reverse=True)
        
        return results
    
    async def _search_spaces(
        self,
        query: str,
        user_id: str,
        base_filters: Dict[str, Any],
        limit: int
    ) -> List[SearchResult]:
        """Search spaces with semantic search."""
        search_filters = {
            **base_filters,
            "metadata.type": ConceptType.SPACE.value
        }
        
        # Semantic search on space names and descriptions
        concepts = await self.user_storage.semantic_search(
            query=query,
            filters=search_filters,
            limit=limit
        )
        
        results = []
        for concept in concepts:
            # Calculate relevance score
            score = self._calculate_relevance_score(
                query, concept.content, concept.metadata
            )
            
            result = SearchResult(
                result_type="space",
                id=concept.id,
                title=concept.metadata.get("name", concept.content),
                content=concept.metadata.get("description", ""),
                metadata={
                    "conversation_count": concept.metadata.get("conversation_count", 0),
                    "created_at": concept.metadata["created_at"],
                    "icon": concept.metadata.get("icon"),
                    "color": concept.metadata.get("color")
                },
                score=score
            )
            results.append(result)
        
        # Sort by score
        results.sort(key=lambda r: r.score, reverse=True)
        
        return results
    
    def _calculate_relevance_score(
        self,
        query: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> float:
        """
        Calculate relevance score for a result.
        
        Factors:
        - Semantic similarity (from storage engine)
        - Exact word matches
        - Recency (more recent = higher score)
        - Starred items get boost
        
        Returns score between 0 and 1.
        """
        score = 0.5  # Base score from semantic similarity
        
        # Boost for exact word matches
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        matches = len(query_words & content_words)
        if matches > 0:
            score += min(0.2, matches * 0.05)
        
        # Boost for starred items
        if metadata.get("starred"):
            score += 0.1
        
        # Boost for recent items (if has updated_at or timestamp)
        if "updated_at" in metadata or "timestamp" in metadata:
            date_str = metadata.get("updated_at") or metadata.get("timestamp")
            try:
                date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - date).days
                
                # Recent items get boost (decay over 30 days)
                if age_days < 30:
                    recency_boost = (30 - age_days) / 30 * 0.15
                    score += recency_boost
            except:
                pass
        
        return min(1.0, score)
    
    def _create_snippet(
        self,
        content: str,
        query: str,
        max_length: int = 150
    ) -> str:
        """
        Create a snippet of content around the query match.
        
        Args:
            content: Full content
            query: Search query
            max_length: Maximum snippet length
            
        Returns:
            Snippet with query context
        """
        content = content.strip()
        
        if len(content) <= max_length:
            return content
        
        # Find query position
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Try to find first query word
        query_words = query_lower.split()
        best_pos = -1
        
        for word in query_words:
            pos = content_lower.find(word)
            if pos != -1:
                best_pos = pos
                break
        
        if best_pos == -1:
            # Query not found, return beginning
            return content[:max_length] + "..."
        
        # Calculate snippet boundaries
        snippet_start = max(0, best_pos - max_length // 2)
        snippet_end = min(len(content), snippet_start + max_length)
        
        snippet = content[snippet_start:snippet_end]
        
        # Add ellipsis
        if snippet_start > 0:
            snippet = "..." + snippet
        if snippet_end < len(content):
            snippet = snippet + "..."
        
        return snippet
    
    def _highlight_matches(
        self,
        content: str,
        query: str,
        max_highlights: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find positions of query matches for highlighting.
        
        Args:
            content: Content to search
            query: Search query
            max_highlights: Maximum number of highlights to return
            
        Returns:
            List of highlight positions with context
        """
        highlights = []
        content_lower = content.lower()
        query_words = query.lower().split()
        
        for word in query_words:
            pos = 0
            while len(highlights) < max_highlights:
                pos = content_lower.find(word, pos)
                if pos == -1:
                    break
                
                # Get context around match
                context_start = max(0, pos - 30)
                context_end = min(len(content), pos + len(word) + 30)
                
                highlights.append({
                    "position": pos,
                    "length": len(word),
                    "context": content[context_start:context_end]
                })
                
                pos += len(word)
            
            if len(highlights) >= max_highlights:
                break
        
        return highlights
