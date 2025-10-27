"""
User management routes.

Handles user profile updates, user listing, and admin functions.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from ..middleware.auth import get_current_user, require_role
from ..models import (
    DeleteUserResponse,
    UpdateUserRequest,
    UserListResponse,
    UserResponse,
)
from ..services import UserService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/users",
    tags=["User Management"],
)


def get_user_service(request: Request) -> UserService:
    """
    Dependency to get UserService instance.
    
    Args:
        request: FastAPI request
    
    Returns:
        UserService instance
    """
    if not hasattr(request.app.state, "user_storage_client"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User storage service not available"
        )
    
    return UserService(request.app.state.user_storage_client)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Get user information by user ID."
)
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get user information.
    
    Users can only view their own profile unless they are admin.
    
    **Returns:**
    - User information
    
    **Raises:**
    - 403: Forbidden (trying to view another user's profile)
    - 404: User not found
    """
    # Check authorization
    if current_user["user_id"] != user_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' profiles"
        )
    
    try:
        user_info = await user_service.get_user(user_id)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(**user_info)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user profile",
    description="Update user profile information."
)
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Update user profile.
    
    Users can only update their own profile unless they are admin.
    
    **Returns:**
    - Updated user information
    
    **Raises:**
    - 400: Validation failed (e.g., email already exists)
    - 403: Forbidden (trying to update another user)
    - 404: User not found
    """
    # Check authorization
    if current_user["user_id"] != user_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update other users' profiles"
        )
    
    try:
        user_info = await user_service.update_user(
            user_id=user_id,
            email=request.email,
            full_name=request.full_name,
            organization=request.organization,
        )
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(**user_info)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.delete(
    "/{user_id}",
    response_model=DeleteUserResponse,
    summary="Delete user account",
    description="Permanently delete user account and all associated data."
)
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Delete user account.
    
    Users can delete their own account, or admins can delete any account.
    This is a permanent action that removes:
    - User concept
    - All user sessions
    - User associations
    
    **Returns:**
    - Deletion confirmation
    
    **Raises:**
    - 403: Forbidden (trying to delete another user without admin)
    - 404: User not found
    """
    # Check authorization
    if current_user["user_id"] != user_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete other users' accounts"
        )
    
    try:
        success = await user_service.delete_user(
            user_id=user_id,
            requesting_user_id=current_user["user_id"]
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User deletion failed"
            )
        
        return DeleteUserResponse(
            message=f"User {user_id} deleted successfully",
            success=True,
            user_id=user_id
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User deletion failed"
        )


@router.get(
    "/",
    response_model=UserListResponse,
    summary="List users (admin only)",
    description="List all users in the system.",
    dependencies=[Depends(require_role("admin"))]
)
async def list_users(
    organization: Optional[str] = Query(None, description="Filter by organization"),
    active_only: bool = Query(True, description="Only show active users"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    user_service: UserService = Depends(get_user_service)
):
    """
    List users (admin only).
    
    Returns a list of all users, optionally filtered by organization and active status.
    
    **Returns:**
    - List of users
    
    **Raises:**
    - 403: Forbidden (not admin)
    """
    try:
        users = await user_service.list_users(
            organization=organization,
            active_only=active_only,
            limit=limit,
        )
        
        return UserListResponse(
            users=users,
            total=len(users)
        )
        
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )


@router.get(
    "/search",
    response_model=UserListResponse,
    summary="Search users (admin only)",
    description="Search for users by email or name.",
    dependencies=[Depends(require_role("admin"))]
)
async def search_users(
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    user_service: UserService = Depends(get_user_service)
):
    """
    Search users (admin only).
    
    Searches users by email or name.
    
    **Returns:**
    - List of matching users
    
    **Raises:**
    - 403: Forbidden (not admin)
    """
    try:
        users = await user_service.search_users(
            query=query,
            limit=limit,
        )
        
        return UserListResponse(
            users=users,
            total=len(users)
        )
        
    except Exception as e:
        logger.error(f"Failed to search users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search users"
        )


@router.post(
    "/{user_id}/deactivate",
    summary="Deactivate user (admin only)",
    description="Deactivate user account (soft delete).",
    dependencies=[Depends(require_role("admin"))]
)
async def deactivate_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Deactivate user account (admin only).
    
    Soft deletes the user account by setting active=false.
    User can no longer log in, but data is preserved.
    
    **Returns:**
    - Success confirmation
    
    **Raises:**
    - 403: Forbidden (not admin)
    - 404: User not found
    """
    try:
        success = await user_service.deactivate_user(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User deactivation failed"
            )
        
        return {
            "message": f"User {user_id} deactivated successfully",
            "success": True
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to deactivate user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User deactivation failed"
        )
