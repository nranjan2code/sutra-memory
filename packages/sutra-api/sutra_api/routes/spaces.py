"""
Space Management API Routes.

Endpoints for creating, managing spaces, and managing space members/permissions.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from ..services.space_service import SpaceService
from ..models.space import (
    CreateSpaceRequest,
    UpdateSpaceRequest,
    AddMemberRequest,
    UpdateMemberRoleRequest,
    RemoveMemberRequest,
    SpaceResponse,
    SpaceListResponse,
    SpaceMemberResponse,
    SpaceMemberListResponse,
    SpaceActionResponse,
)
from ..middleware.auth import get_current_active_user
from ..dependencies import get_user_storage_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/spaces", tags=["spaces"])


def get_space_service(
    user_storage: Any = Depends(get_user_storage_client)
) -> SpaceService:
    """Dependency to get space service."""
    return SpaceService(user_storage_client=user_storage)


@router.post(
    "/create",
    response_model=SpaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new space",
    description="Create a new space (workspace) for organizing conversations."
)
async def create_space(
    request: CreateSpaceRequest,
    current_user: Dict = Depends(get_current_active_user),
    space_service: SpaceService = Depends(get_space_service)
):
    """
    Create a new space.
    
    Spaces organize conversations by project, department, or domain. Each space
    is associated with a specific domain storage for knowledge queries.
    
    The creator is automatically added as an admin of the space.
    
    Args:
        request: Space creation request
        current_user: Currently authenticated user
        space_service: Space service instance
        
    Returns:
        SpaceResponse with the created space details
    """
    try:
        space = await space_service.create_space(
            name=request.name,
            organization_id=current_user["organization"],
            creator_user_id=current_user["user_id"],
            domain_storage=request.domain_storage,
            description=request.description,
            icon=request.icon,
            color=request.color
        )
        
        logger.info(
            f"User {current_user['user_id']} created space {space['space_id']}"
        )
        
        return SpaceResponse(**space)
    
    except ValueError as e:
        logger.warning(f"Invalid request to create space: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating space: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create space"
        )


@router.get(
    "/list",
    response_model=SpaceListResponse,
    summary="List spaces",
    description="List all spaces accessible to the current user."
)
async def list_spaces(
    include_inactive: bool = False,
    current_user: Dict = Depends(get_current_active_user),
    space_service: SpaceService = Depends(get_space_service)
):
    """
    List all spaces accessible to the current user.
    
    Returns spaces where the user has any permission (admin, write, or read).
    Each space includes the user's role in that space.
    
    Args:
        include_inactive: Whether to include soft-deleted spaces
        current_user: Currently authenticated user
        space_service: Space service instance
        
    Returns:
        SpaceListResponse with list of spaces
    """
    try:
        spaces = await space_service.list_spaces(
            user_id=current_user["user_id"],
            organization_id=current_user["organization"],
            include_inactive=include_inactive
        )
        
        return SpaceListResponse(
            spaces=[SpaceResponse(**space) for space in spaces],
            total=len(spaces)
        )
    
    except ValueError as e:
        logger.warning(f"Invalid request to list spaces: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error listing spaces: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list spaces"
        )


@router.get(
    "/{space_id}",
    response_model=SpaceResponse,
    summary="Get space details",
    description="Get details for a specific space."
)
async def get_space(
    space_id: str,
    current_user: Dict = Depends(get_current_active_user),
    space_service: SpaceService = Depends(get_space_service)
):
    """
    Get details for a specific space.
    
    Requires read permission on the space.
    
    Args:
        space_id: Space ID
        current_user: Currently authenticated user
        space_service: Space service instance
        
    Returns:
        SpaceResponse with space details and user's role
    """
    try:
        space = await space_service.get_space(
            space_id=space_id,
            user_id=current_user["user_id"],
            organization_id=current_user["organization"]
        )
        
        return SpaceResponse(**space)
    
    except ValueError as e:
        logger.warning(f"Invalid request to get space: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting space: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get space"
        )


@router.put(
    "/{space_id}",
    response_model=SpaceResponse,
    summary="Update space",
    description="Update space details (name, description, icon, color)."
)
async def update_space(
    space_id: str,
    request: UpdateSpaceRequest,
    current_user: Dict = Depends(get_current_active_user),
    space_service: SpaceService = Depends(get_space_service)
):
    """
    Update space details.
    
    Requires admin or write permission on the space.
    
    Args:
        space_id: Space ID
        request: Update request with new values
        current_user: Currently authenticated user
        space_service: Space service instance
        
    Returns:
        SpaceResponse with updated space details
    """
    try:
        space = await space_service.update_space(
            space_id=space_id,
            user_id=current_user["user_id"],
            organization_id=current_user["organization"],
            name=request.name,
            description=request.description,
            icon=request.icon,
            color=request.color
        )
        
        logger.info(f"User {current_user['user_id']} updated space {space_id}")
        
        return SpaceResponse(**space)
    
    except ValueError as e:
        logger.warning(f"Invalid request to update space: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating space: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update space"
        )


@router.delete(
    "/{space_id}",
    response_model=SpaceActionResponse,
    summary="Delete space",
    description="Soft delete a space (sets active=False)."
)
async def delete_space(
    space_id: str,
    current_user: Dict = Depends(get_current_active_user),
    space_service: SpaceService = Depends(get_space_service)
):
    """
    Soft delete a space.
    
    Requires admin permission. Sets active=False but preserves data for audit.
    
    Args:
        space_id: Space ID
        current_user: Currently authenticated user
        space_service: Space service instance
        
    Returns:
        SpaceActionResponse with success message
    """
    try:
        result = await space_service.delete_space(
            space_id=space_id,
            user_id=current_user["user_id"],
            organization_id=current_user["organization"]
        )
        
        logger.info(f"User {current_user['user_id']} deleted space {space_id}")
        
        return SpaceActionResponse(**result)
    
    except ValueError as e:
        logger.warning(f"Invalid request to delete space: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting space: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete space"
        )


# Member Management Endpoints


@router.post(
    "/{space_id}/members",
    response_model=SpaceActionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add member to space",
    description="Add a user to a space with a specific role."
)
async def add_member(
    space_id: str,
    request: AddMemberRequest,
    current_user: Dict = Depends(get_current_active_user),
    space_service: SpaceService = Depends(get_space_service)
):
    """
    Add a member to a space.
    
    Requires admin permission on the space.
    
    Args:
        space_id: Space ID
        request: Member addition request (user_id and role)
        current_user: Currently authenticated user
        space_service: Space service instance
        
    Returns:
        SpaceActionResponse with success message
    """
    try:
        result = await space_service.add_member(
            space_id=space_id,
            user_id=current_user["user_id"],
            target_user_id=request.user_id,
            role=request.role,
            organization_id=current_user["organization"]
        )
        
        logger.info(
            f"User {current_user['user_id']} added {request.user_id} "
            f"to space {space_id} with role {request.role}"
        )
        
        return SpaceActionResponse(**result)
    
    except ValueError as e:
        logger.warning(f"Invalid request to add member: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding member: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add member"
        )


@router.get(
    "/{space_id}/members",
    response_model=SpaceMemberListResponse,
    summary="List space members",
    description="List all members of a space with their roles."
)
async def list_members(
    space_id: str,
    current_user: Dict = Depends(get_current_active_user),
    space_service: SpaceService = Depends(get_space_service)
):
    """
    List all members of a space.
    
    Requires read permission on the space.
    
    Args:
        space_id: Space ID
        current_user: Currently authenticated user
        space_service: Space service instance
        
    Returns:
        SpaceMemberListResponse with list of members
    """
    try:
        members = await space_service.list_members(
            space_id=space_id,
            user_id=current_user["user_id"],
            organization_id=current_user["organization"]
        )
        
        return SpaceMemberListResponse(
            members=[SpaceMemberResponse(**member) for member in members],
            total=len(members)
        )
    
    except ValueError as e:
        logger.warning(f"Invalid request to list members: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error listing members: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list members"
        )


@router.delete(
    "/{space_id}/members/{user_id}",
    response_model=SpaceActionResponse,
    summary="Remove member from space",
    description="Remove a user from a space."
)
async def remove_member(
    space_id: str,
    user_id: str,
    current_user: Dict = Depends(get_current_active_user),
    space_service: SpaceService = Depends(get_space_service)
):
    """
    Remove a member from a space.
    
    Requires admin permission. Cannot remove the last admin.
    
    Args:
        space_id: Space ID
        user_id: User ID to remove
        current_user: Currently authenticated user
        space_service: Space service instance
        
    Returns:
        SpaceActionResponse with success message
    """
    try:
        result = await space_service.remove_member(
            space_id=space_id,
            user_id=current_user["user_id"],
            target_user_id=user_id,
            organization_id=current_user["organization"]
        )
        
        logger.info(
            f"User {current_user['user_id']} removed {user_id} from space {space_id}"
        )
        
        return SpaceActionResponse(**result)
    
    except ValueError as e:
        logger.warning(f"Invalid request to remove member: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error removing member: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove member"
        )


@router.put(
    "/{space_id}/members/{user_id}/role",
    response_model=SpaceActionResponse,
    summary="Update member role",
    description="Update a member's role in a space."
)
async def update_member_role(
    space_id: str,
    user_id: str,
    request: UpdateMemberRoleRequest,
    current_user: Dict = Depends(get_current_active_user),
    space_service: SpaceService = Depends(get_space_service)
):
    """
    Update a member's role in a space.
    
    Requires admin permission. Cannot demote the last admin.
    
    Args:
        space_id: Space ID
        user_id: User ID to update
        request: New role request
        current_user: Currently authenticated user
        space_service: Space service instance
        
    Returns:
        SpaceActionResponse with success message and new role
    """
    try:
        result = await space_service.update_member_role(
            space_id=space_id,
            user_id=current_user["user_id"],
            target_user_id=user_id,
            new_role=request.new_role,
            organization_id=current_user["organization"]
        )
        
        logger.info(
            f"User {current_user['user_id']} updated {user_id} "
            f"role to {request.new_role} in space {space_id}"
        )
        
        return SpaceActionResponse(**result)
    
    except ValueError as e:
        logger.warning(f"Invalid request to update member role: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating member role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update member role"
        )
