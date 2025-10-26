"""
Conversation Management Service

Manages conversations, messages, and context in user storage.
Integrates with domain storage for reasoning queries.
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, TYPE_CHECKING, AsyncGenerator
import logging

from ..schema import ConceptType, AssociationType

if TYPE_CHECKING:
    from sutra_storage_client import StorageClient

logger = logging.getLogger(__name__)


def utc_now() -> str:
    """Get current UTC timestamp as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


class ConversationService:
    """
    Service for managing conversations and messages.
    
    This service handles:
    - Creating and managing conversations in user storage
    - Sending messages and getting AI responses
    - Loading conversation history and context
    - Integrating with domain storage for reasoning
    """
    
    def __init__(
        self,
        user_storage_client: Any,  # StorageClient
        domain_storage_clients: Dict[str, Any]  # Dict[str, StorageClient]
    ):
        """
        Initialize conversation service.
        
        Args:
            user_storage_client: Client for user storage (conversations, messages)
            domain_storage_clients: Dictionary mapping storage names to clients
        """
        self.user_storage = user_storage_client
        self.domain_storages = domain_storage_clients
        logger.info(
            f"ConversationService initialized with {len(domain_storage_clients)} "
            f"domain storage clients"
        )
    
    async def create_conversation(
        self,
        user_id: str,
        space_id: str,
        organization: str,
        domain_storage: str,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversation.
        
        Args:
            user_id: ID of the user creating the conversation
            space_id: ID of the space this conversation belongs to
            organization: Organization ID
            domain_storage: Name of the domain storage to use
            title: Optional conversation title
            
        Returns:
            Dictionary containing conversation details
            
        Raises:
            ValueError: If domain storage name is invalid
        """
        if domain_storage not in self.domain_storages:
            raise ValueError(
                f"Invalid domain storage: {domain_storage}. "
                f"Available: {list(self.domain_storages.keys())}"
            )
        
        # Create conversation concept
        conv_content = title or "New conversation"
        conv = await self.user_storage.create_concept(
            content=conv_content,
            semantic_patterns=["Conversation", "Active"],
            metadata={
                "type": ConceptType.CONVERSATION.value,
                "user_id": user_id,
                "space_id": space_id,
                "organization_id": organization,
                "domain_storage": domain_storage,
                "message_count": 0,
                "created_at": utc_now(),
                "updated_at": utc_now(),
                "title": conv_content,
                "starred": False,
                "tags": [],
                "active": True
            }
        )
        
        # Create associations
        await self.user_storage.create_association(
            user_id,
            conv.id,
            AssociationType.OWNS_CONVERSATION.value
        )
        
        await self.user_storage.create_association(
            space_id,
            conv.id,
            AssociationType.CONTAINS_CONVERSATION.value
        )
        
        logger.info(
            f"Created conversation {conv.id} for user {user_id} "
            f"in space {space_id}"
        )
        
        return {
            "id": conv.id,
            "title": conv_content,
            "user_id": user_id,
            "space_id": space_id,
            "organization_id": organization,
            "domain_storage": domain_storage,
            "message_count": 0,
            "created_at": conv.metadata["created_at"],
            "updated_at": conv.metadata["updated_at"],
            "starred": False,
            "tags": []
        }
    
    async def load_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Load conversation details.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Dictionary containing conversation details
        """
        conv = await self.user_storage.get_concept(conversation_id)
        
        if conv.metadata.get("type") != ConceptType.CONVERSATION.value:
            raise ValueError(f"Concept {conversation_id} is not a conversation")
        
        return {
            "id": conv.id,
            "title": conv.metadata.get("title", conv.content),
            "user_id": conv.metadata["user_id"],
            "space_id": conv.metadata["space_id"],
            "organization_id": conv.metadata["organization_id"],
            "domain_storage": conv.metadata["domain_storage"],
            "message_count": conv.metadata["message_count"],
            "created_at": conv.metadata["created_at"],
            "updated_at": conv.metadata["updated_at"],
            "starred": conv.metadata.get("starred", False),
            "tags": conv.metadata.get("tags", [])
        }
    
    async def load_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Load messages from a conversation.
        
        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to load
            offset: Offset for pagination
            
        Returns:
            List of message dictionaries, ordered by timestamp
        """
        # Query for messages associated with this conversation
        messages = await self.user_storage.semantic_search(
            query=f"conversation {conversation_id} messages",
            filters={
                "metadata.conversation_id": conversation_id,
                "metadata.type": [
                    ConceptType.USER_MESSAGE.value,
                    ConceptType.ASSISTANT_MESSAGE.value
                ]
            },
            limit=limit + offset
        )
        
        # Sort by timestamp
        messages = sorted(
            messages,
            key=lambda m: m.metadata.get("timestamp", ""),
            reverse=False
        )
        
        # Apply pagination
        messages = messages[offset:offset + limit]
        
        # Format messages
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "id": msg.id,
                "conversation_id": conversation_id,
                "role": (
                    "user"
                    if msg.metadata["type"] == ConceptType.USER_MESSAGE.value
                    else "assistant"
                ),
                "content": msg.content,
                "timestamp": msg.metadata["timestamp"],
                "metadata": {
                    k: v
                    for k, v in msg.metadata.items()
                    if k not in [
                        "type",
                        "conversation_id",
                        "timestamp",
                        "organization_id"
                    ]
                }
            })
        
        return formatted_messages
    
    async def load_context(
        self,
        conversation_id: str,
        window: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Load recent context for a conversation (last N messages).
        
        Args:
            conversation_id: ID of the conversation
            window: Number of recent messages to load
            
        Returns:
            List of recent messages for context
        """
        return await self.load_messages(conversation_id, limit=window, offset=0)
    
    async def send_message(
        self,
        conversation_id: str,
        user_id: str,
        message: str,
        reasoning_depth: str = "balanced"
    ) -> Dict[str, Any]:
        """
        Send a message and get AI response.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user sending the message
            message: Message content
            reasoning_depth: Reasoning depth (quick/balanced/deep)
            
        Returns:
            Dictionary containing the assistant's response
        """
        # Load conversation to get domain storage
        conv = await self.user_storage.get_concept(conversation_id)
        
        if conv.metadata.get("type") != ConceptType.CONVERSATION.value:
            raise ValueError(f"Concept {conversation_id} is not a conversation")
        
        # Create user message concept
        user_msg = await self.user_storage.create_concept(
            content=message,
            semantic_patterns=["UserMessage", "Question"],
            metadata={
                "type": ConceptType.USER_MESSAGE.value,
                "conversation_id": conversation_id,
                "user_id": user_id,
                "organization_id": conv.metadata["organization_id"],
                "timestamp": utc_now()
            }
        )
        
        # Create association to conversation
        await self.user_storage.create_association(
            conversation_id,
            user_msg.id,
            AssociationType.HAS_MESSAGE.value
        )
        
        # Load context (last 10 messages)
        context = await self.load_context(conversation_id, window=10)
        
        # Format context for domain storage query
        context_str = self._format_context(context)
        
        # Query domain storage
        domain_storage_name = conv.metadata["domain_storage"]
        domain_storage = self.domain_storages[domain_storage_name]
        
        # Build query with context
        query_with_context = f"{context_str}\n\nQuestion: {message}"
        
        # Perform reasoning query
        reasoning_result = await domain_storage.semantic_search(
            query=query_with_context,
            limit=20  # Get top concepts for reasoning
        )
        
        # Format answer (for now, simple concatenation)
        # In production, this would use the reasoning engine
        answer = self._generate_answer(message, reasoning_result)
        
        # Create assistant message concept
        assistant_msg = await self.user_storage.create_concept(
            content=answer,
            semantic_patterns=["AssistantMessage", "Response", "Reasoning"],
            metadata={
                "type": ConceptType.ASSISTANT_MESSAGE.value,
                "conversation_id": conversation_id,
                "organization_id": conv.metadata["organization_id"],
                "timestamp": utc_now(),
                "reasoning_depth": reasoning_depth,
                "concepts_used": [c.id for c in reasoning_result[:5]],
                "confidence": 0.85  # Placeholder
            }
        )
        
        # Create association to conversation
        await self.user_storage.create_association(
            conversation_id,
            assistant_msg.id,
            AssociationType.HAS_MESSAGE.value
        )
        
        # Update conversation metadata
        message_count = conv.metadata["message_count"] + 2
        await self.user_storage.update_concept_metadata(
            conversation_id,
            {
                "message_count": message_count,
                "updated_at": utc_now(),
                "title": (
                    # Update title from first user message
                    message[:50] + "..."
                    if message_count == 2 and len(message) > 50
                    else message if message_count == 2
                    else conv.metadata.get("title", "New conversation")
                )
            }
        )
        
        logger.info(
            f"Processed message in conversation {conversation_id}, "
            f"used {len(reasoning_result)} concepts"
        )
        
        return {
            "id": assistant_msg.id,
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": answer,
            "timestamp": assistant_msg.metadata["timestamp"],
            "metadata": {
                "reasoning_depth": reasoning_depth,
                "concepts_used": assistant_msg.metadata["concepts_used"],
                "confidence": assistant_msg.metadata["confidence"]
            }
        }
    
    async def send_message_stream(
        self,
        conversation_id: str,
        user_id: str,
        message: str,
        reasoning_depth: str = "balanced"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Send a message and stream AI response with progressive refinement.
        
        This is an async generator that yields updates as reasoning progresses:
        1. User message creation
        2. Reasoning progress updates
        3. Partial answer updates
        4. Final answer with metadata
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user sending the message
            message: Message content
            reasoning_depth: Reasoning depth (quick/balanced/deep)
            
        Yields:
            Dict with event type and data:
            - {"event": "user_message", "data": {...}}
            - {"event": "progress", "data": {"stage": "...", "confidence": 0.5}}
            - {"event": "chunk", "data": {"content": "...", "confidence": 0.7}}
            - {"event": "complete", "data": {...}}
        """
        # Load conversation
        conv = await self.user_storage.get_concept(conversation_id)
        
        if conv.metadata.get("type") != ConceptType.CONVERSATION.value:
            raise ValueError(f"Concept {conversation_id} is not a conversation")
        
        # Create user message
        user_msg = await self.user_storage.create_concept(
            content=message,
            semantic_patterns=["UserMessage", "Question"],
            metadata={
                "type": ConceptType.USER_MESSAGE.value,
                "conversation_id": conversation_id,
                "user_id": user_id,
                "organization_id": conv.metadata["organization_id"],
                "timestamp": utc_now()
            }
        )
        
        await self.user_storage.create_association(
            conversation_id,
            user_msg.id,
            AssociationType.HAS_MESSAGE.value
        )
        
        # Yield user message created event
        yield {
            "event": "user_message",
            "data": {
                "id": user_msg.id,
                "content": message,
                "timestamp": user_msg.metadata["timestamp"]
            }
        }
        
        # Yield progress: loading context
        yield {
            "event": "progress",
            "data": {
                "stage": "loading_context",
                "message": "Loading conversation context..."
            }
        }
        
        # Load context
        context = await self.load_context(conversation_id, window=10)
        context_str = self._format_context(context)
        
        # Yield progress: querying knowledge
        yield {
            "event": "progress",
            "data": {
                "stage": "querying_knowledge",
                "message": "Searching domain knowledge..."
            }
        }
        
        # Query domain storage
        domain_storage_name = conv.metadata["domain_storage"]
        domain_storage = self.domain_storages[domain_storage_name]
        query_with_context = f"{context_str}\n\nQuestion: {message}"
        
        reasoning_result = await domain_storage.semantic_search(
            query=query_with_context,
            limit=20
        )
        
        # Yield progress: reasoning
        yield {
            "event": "progress",
            "data": {
                "stage": "reasoning",
                "message": f"Analyzing {len(reasoning_result)} concepts...",
                "confidence": 0.5
            }
        }
        
        # Generate answer (simulate streaming by chunking)
        answer = self._generate_answer(message, reasoning_result)
        
        # Stream answer in chunks (simulate progressive generation)
        words = answer.split()
        chunk_size = max(1, len(words) // 10)  # ~10 chunks
        
        partial_content = ""
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            partial_content += (" " if partial_content else "") + chunk_text
            
            # Calculate confidence (increases as we generate more)
            confidence = min(0.95, 0.5 + (i / len(words)) * 0.45)
            
            yield {
                "event": "chunk",
                "data": {
                    "content": partial_content,
                    "confidence": round(confidence, 2)
                }
            }
        
        # Create assistant message concept
        assistant_msg = await self.user_storage.create_concept(
            content=answer,
            semantic_patterns=["AssistantMessage", "Response", "Reasoning"],
            metadata={
                "type": ConceptType.ASSISTANT_MESSAGE.value,
                "conversation_id": conversation_id,
                "organization_id": conv.metadata["organization_id"],
                "timestamp": utc_now(),
                "reasoning_depth": reasoning_depth,
                "concepts_used": [c.id for c in reasoning_result[:5]],
                "confidence": 0.85
            }
        )
        
        await self.user_storage.create_association(
            conversation_id,
            assistant_msg.id,
            AssociationType.HAS_MESSAGE.value
        )
        
        # Update conversation metadata
        message_count = conv.metadata["message_count"] + 2
        await self.user_storage.update_concept_metadata(
            conversation_id,
            {
                "message_count": message_count,
                "updated_at": utc_now(),
                "title": (
                    message[:50] + "..."
                    if message_count == 2 and len(message) > 50
                    else message if message_count == 2
                    else conv.metadata.get("title", "New conversation")
                )
            }
        )
        
        # Yield final complete event
        yield {
            "event": "complete",
            "data": {
                "id": assistant_msg.id,
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": answer,
                "timestamp": assistant_msg.metadata["timestamp"],
                "metadata": {
                    "reasoning_depth": reasoning_depth,
                    "concepts_used": assistant_msg.metadata["concepts_used"],
                    "confidence": assistant_msg.metadata["confidence"]
                }
            }
        }
        
        logger.info(
            f"Streamed message in conversation {conversation_id}, "
            f"used {len(reasoning_result)} concepts"
        )
    
    async def update_conversation_metadata(
        self,
        conversation_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update conversation metadata (e.g., star, tags).
        
        Args:
            conversation_id: ID of the conversation
            updates: Dictionary of metadata updates
            
        Returns:
            Updated conversation details
        """
        # Allowed updates
        allowed_fields = ["starred", "tags", "title"]
        filtered_updates = {
            k: v for k, v in updates.items() if k in allowed_fields
        }
        
        if not filtered_updates:
            raise ValueError("No valid fields to update")
        
        # Add updated_at timestamp
        filtered_updates["updated_at"] = utc_now()
        
        await self.user_storage.update_concept_metadata(
            conversation_id,
            filtered_updates
        )
        
        return await self.load_conversation(conversation_id)
    
    async def list_conversations(
        self,
        user_id: str,
        space_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List user's conversations.
        
        Args:
            user_id: ID of the user
            space_id: Optional space ID to filter by
            filters: Optional additional filters (starred, tags)
            limit: Maximum number of conversations to return
            offset: Offset for pagination
            
        Returns:
            List of conversation dictionaries
        """
        # Build filters
        search_filters = {
            "metadata.type": ConceptType.CONVERSATION.value,
            "metadata.user_id": user_id,
            "metadata.active": True
        }
        
        if space_id:
            search_filters["metadata.space_id"] = space_id
        
        if filters:
            if "starred" in filters:
                search_filters["metadata.starred"] = filters["starred"]
            if "tags" in filters:
                search_filters["metadata.tags"] = filters["tags"]
        
        # Search for conversations
        conversations = await self.user_storage.semantic_search(
            query=f"user {user_id} conversations",
            filters=search_filters,
            limit=limit + offset
        )
        
        # Sort by updated_at (most recent first)
        conversations = sorted(
            conversations,
            key=lambda c: c.metadata.get("updated_at", ""),
            reverse=True
        )
        
        # Apply pagination
        conversations = conversations[offset:offset + limit]
        
        # Format conversations
        formatted_conversations = []
        for conv in conversations:
            formatted_conversations.append({
                "id": conv.id,
                "title": conv.metadata.get("title", conv.content),
                "user_id": conv.metadata["user_id"],
                "space_id": conv.metadata["space_id"],
                "organization_id": conv.metadata["organization_id"],
                "domain_storage": conv.metadata["domain_storage"],
                "message_count": conv.metadata["message_count"],
                "created_at": conv.metadata["created_at"],
                "updated_at": conv.metadata["updated_at"],
                "starred": conv.metadata.get("starred", False),
                "tags": conv.metadata.get("tags", [])
            })
        
        return formatted_conversations
    
    def _format_context(self, messages: List[Dict[str, Any]]) -> str:
        """Format conversation context for domain storage query."""
        if not messages:
            return ""
        
        context_lines = ["Previous conversation:"]
        for msg in messages:
            role = msg["role"].capitalize()
            content = msg["content"]
            context_lines.append(f"{role}: {content}")
        
        return "\n".join(context_lines)
    
    def _generate_answer(
        self,
        question: str,
        concepts: List[Any]
    ) -> str:
        """
        Generate answer from retrieved concepts.
        
        This is a simplified implementation. In production, this would:
        1. Use the reasoning engine for path finding
        2. Implement Multi-Path Plan Aggregation (MPPA)
        3. Apply quality gates and confidence thresholds
        """
        if not concepts:
            return (
                "I don't have enough information to answer that question. "
                "Could you provide more context or try a different question?"
            )
        
        # Simple answer generation (placeholder)
        answer_parts = [
            "Based on the available knowledge, here's what I found:\n"
        ]
        
        for i, concept in enumerate(concepts[:3], 1):
            answer_parts.append(f"{i}. {concept.content}")
        
        return "\n".join(answer_parts)
