"""
Conversation Management API Routes.

Endpoints for creating, managing, and messaging in conversations.
"""

import logging
from typing import Dict, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
import json

from ..services.conversation_service import ConversationService
from ..models.conversation import (
    CreateConversationRequest,
    ConversationResponse,
    SendMessageRequest,
    SendMessageResponse,
    MessageResponse,
    UpdateConversationRequest,
    ListConversationsRequest,
    ListConversationsResponse,
    LoadMessagesRequest,
    LoadMessagesResponse,
)
from ..middleware.auth import get_current_active_user
from ..dependencies import get_user_storage_client, get_storage_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["conversations"])


def get_conversation_service(
    request: Request,
    user_storage: Any = Depends(get_user_storage_client),
    domain_storage: Any = Depends(get_storage_client)
) -> ConversationService:
    """
    Dependency to get conversation service.
    
    For now, we assume a single domain storage. In production, this would
    be a registry of multiple domain storages.
    """
    # Create domain storage registry (single storage for now)
    domain_storages: Dict[str, Any] = {
        "default": domain_storage
    }
    
    return ConversationService(
        user_storage_client=user_storage,
        domain_storage_clients=domain_storages
    )


@router.post(
    "/create",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation",
    description="Create a new conversation in a space with the specified domain storage."
)
async def create_conversation(
    request: CreateConversationRequest,
    current_user: Dict = Depends(get_current_active_user),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Create a new conversation.
    
    Conversations are created in a specific space and use a specific domain storage
    for reasoning queries. All messages in the conversation will query this domain
    storage.
    
    Args:
        request: Conversation creation request
        current_user: Currently authenticated user
        conversation_service: Conversation service instance
        
    Returns:
        ConversationResponse with the created conversation details
    """
    try:
        conversation = await conversation_service.create_conversation(
            user_id=current_user["user_id"],
            space_id=request.space_id,
            organization=current_user["organization"],
            domain_storage=request.domain_storage,
            title=request.title
        )
        
        logger.info(
            f"User {current_user['user_id']} created conversation {conversation['id']}"
        )
        
        return ConversationResponse(**conversation)
    
    except ValueError as e:
        logger.warning(f"Invalid request to create conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )


@router.get(
    "/list",
    response_model=ListConversationsResponse,
    summary="List user's conversations",
    description="List all conversations for the current user with optional filters."
)
async def list_conversations(
    space_id: Optional[str] = None,
    starred: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: Dict = Depends(get_current_active_user),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    List conversations for the current user.
    
    Args:
        space_id: Optional space ID to filter by
        starred: Optional starred status filter
        limit: Maximum number of results (1-100)
        offset: Offset for pagination
        current_user: Currently authenticated user
        conversation_service: Conversation service instance
        
    Returns:
        ListConversationsResponse with conversations
    """
    try:
        # Build filters
        filters = {}
        if starred is not None:
            filters["starred"] = starred
        
        conversations = await conversation_service.list_conversations(
            user_id=current_user["user_id"],
            space_id=space_id,
            filters=filters if filters else None,
            limit=limit,
            offset=offset
        )
        
        # For now, we don't have total count, use len(conversations)
        # In production, we'd query total count separately
        total = len(conversations) + offset
        
        return ListConversationsResponse(
            conversations=[ConversationResponse(**c) for c in conversations],
            total=total,
            limit=limit,
            offset=offset
        )
    
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list conversations"
        )


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
    summary="Get conversation details",
    description="Get detailed information about a specific conversation."
)
async def get_conversation(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Get conversation details.
    
    Args:
        conversation_id: Conversation ID
        current_user: Currently authenticated user
        conversation_service: Conversation service instance
        
    Returns:
        ConversationResponse with conversation details
    """
    try:
        conversation = await conversation_service.load_conversation(conversation_id)
        
        # Verify user owns conversation
        if conversation["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this conversation"
            )
        
        return ConversationResponse(**conversation)
    
    except ValueError as e:
        logger.warning(f"Invalid conversation request: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversation"
        )


@router.get(
    "/{conversation_id}/messages",
    response_model=LoadMessagesResponse,
    summary="Load conversation messages",
    description="Load messages from a conversation with pagination."
)
async def load_messages(
    conversation_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Load messages from a conversation.
    
    Args:
        conversation_id: Conversation ID
        limit: Maximum number of messages (1-100)
        offset: Offset for pagination
        current_user: Currently authenticated user
        conversation_service: Conversation service instance
        
    Returns:
        LoadMessagesResponse with messages
    """
    try:
        # Verify user owns conversation (load conversation also checks type)
        conversation = await conversation_service.load_conversation(conversation_id)
        
        if conversation["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this conversation"
            )
        
        messages = await conversation_service.load_messages(
            conversation_id=conversation_id,
            limit=limit,
            offset=offset
        )
        
        return LoadMessagesResponse(
            conversation_id=conversation_id,
            messages=[MessageResponse(**m) for m in messages],
            total=conversation["message_count"],
            limit=limit,
            offset=offset
        )
    
    except ValueError as e:
        logger.warning(f"Invalid messages request: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load messages: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load messages"
        )


@router.post(
    "/{conversation_id}/message",
    response_model=SendMessageResponse,
    summary="Send a message",
    description="Send a message in a conversation and get AI response."
)
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Send a message and get AI response.
    
    This is the main chat endpoint. It:
    1. Creates a user message concept
    2. Loads conversation context
    3. Queries the domain storage for reasoning
    4. Creates an assistant message with the response
    
    Args:
        conversation_id: Conversation ID
        request: Message request
        current_user: Currently authenticated user
        conversation_service: Conversation service instance
        
    Returns:
        SendMessageResponse with both user and assistant messages
    """
    try:
        # Verify user owns conversation
        conversation = await conversation_service.load_conversation(conversation_id)
        
        if conversation["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to send messages in this conversation"
            )
        
        # Create user message first (for response)
        user_message = {
            "id": f"pending-{conversation_id}",
            "conversation_id": conversation_id,
            "role": "user",
            "content": request.message,
            "timestamp": "",  # Will be set by service
            "metadata": {}
        }
        
        # Send message and get response
        assistant_message = await conversation_service.send_message(
            conversation_id=conversation_id,
            user_id=current_user["user_id"],
            message=request.message,
            reasoning_depth=request.reasoning_depth
        )
        
        # Load the actual user message that was created
        messages = await conversation_service.load_messages(
            conversation_id=conversation_id,
            limit=2,  # Get last 2 messages (user + assistant)
            offset=0
        )
        
        # Find the user message (second to last)
        user_msg = None
        for msg in messages:
            if msg["role"] == "user" and msg["content"] == request.message:
                user_msg = msg
                break
        
        if not user_msg:
            # Fallback if we can't find it
            user_msg = user_message
        
        logger.info(
            f"User {current_user['user_id']} sent message in conversation "
            f"{conversation_id}, got response {assistant_message['id']}"
        )
        
        return SendMessageResponse(
            user_message=MessageResponse(**user_msg),
            assistant_message=MessageResponse(**assistant_message)
        )
    
    except ValueError as e:
        logger.warning(f"Invalid message request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send message: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )


@router.post(
    "/{conversation_id}/message/stream",
    summary="Send a message with streaming response",
    description="Send a message and stream the AI response with progressive refinement."
)
async def send_message_stream(
    conversation_id: str,
    request: SendMessageRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Send a message and stream AI response using Server-Sent Events (SSE).
    
    The response is streamed as a series of events:
    - user_message: User message was created
    - progress: Reasoning progress updates
    - chunk: Partial answer chunks with increasing confidence
    - complete: Final answer with full metadata
    
    Args:
        conversation_id: Conversation ID
        request: Message request
        current_user: Currently authenticated user
        conversation_service: Conversation service instance
        
    Returns:
        StreamingResponse with text/event-stream content type
    """
    
    async def event_generator():
        """Generate SSE events from the conversation service stream."""
        try:
            # Verify user owns conversation
            conversation = await conversation_service.load_conversation(conversation_id)
            
            if conversation["user_id"] != current_user["user_id"]:
                # Send error event
                error_event = {
                    "event": "error",
                    "data": {
                        "message": "You don't have permission to send messages in this conversation"
                    }
                }
                yield f"data: {json.dumps(error_event)}\n\n"
                return
            
            # Stream message processing
            async for event in conversation_service.send_message_stream(
                conversation_id=conversation_id,
                user_id=current_user["user_id"],
                message=request.message,
                reasoning_depth=request.reasoning_depth
            ):
                # Format as SSE
                event_type = event["event"]
                event_data = event["data"]
                
                # Send event
                yield f"event: {event_type}\n"
                yield f"data: {json.dumps(event_data)}\n\n"
            
            logger.info(
                f"User {current_user['user_id']} sent streaming message in conversation "
                f"{conversation_id}"
            )
            
        except ValueError as e:
            logger.warning(f"Invalid streaming message request: {e}")
            error_event = {
                "event": "error",
                "data": {"message": str(e)}
            }
            yield f"data: {json.dumps(error_event)}\n\n"
            
        except Exception as e:
            logger.error(f"Failed to stream message: {e}", exc_info=True)
            error_event = {
                "event": "error",
                "data": {"message": "Failed to process message"}
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.patch(
    "/{conversation_id}",
    response_model=ConversationResponse,
    summary="Update conversation metadata",
    description="Update conversation properties like starred status or tags."
)
async def update_conversation(
    conversation_id: str,
    request: UpdateConversationRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Update conversation metadata.
    
    Args:
        conversation_id: Conversation ID
        request: Update request
        current_user: Currently authenticated user
        conversation_service: Conversation service instance
        
    Returns:
        ConversationResponse with updated conversation
    """
    try:
        # Verify user owns conversation
        conversation = await conversation_service.load_conversation(conversation_id)
        
        if conversation["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this conversation"
            )
        
        # Build updates dictionary (only include provided fields)
        updates = {}
        if request.starred is not None:
            updates["starred"] = request.starred
        if request.tags is not None:
            updates["tags"] = request.tags
        if request.title is not None:
            updates["title"] = request.title
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )
        
        updated_conversation = await conversation_service.update_conversation_metadata(
            conversation_id=conversation_id,
            updates=updates
        )
        
        logger.info(
            f"User {current_user['user_id']} updated conversation {conversation_id}"
        )
        
        return ConversationResponse(**updated_conversation)
    
    except ValueError as e:
        logger.warning(f"Invalid update request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update conversation"
        )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a conversation",
    description="Soft delete a conversation (mark as inactive)."
)
async def delete_conversation(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """
    Delete a conversation (soft delete).
    
    Args:
        conversation_id: Conversation ID
        current_user: Currently authenticated user
        conversation_service: Conversation service instance
    """
    try:
        # Verify user owns conversation
        conversation = await conversation_service.load_conversation(conversation_id)
        
        if conversation["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this conversation"
            )
        
        # Soft delete by marking as inactive
        await conversation_service.update_conversation_metadata(
            conversation_id=conversation_id,
            updates={"active": False}
        )
        
        logger.info(
            f"User {current_user['user_id']} deleted conversation {conversation_id}"
        )
        
        return None
    
    except ValueError as e:
        logger.warning(f"Invalid delete request: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )
