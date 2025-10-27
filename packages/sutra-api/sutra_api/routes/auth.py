"""
Authentication routes.

Handles user registration, login, logout, and session management.
"""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ..config import settings
from ..middleware.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from ..models import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    PasswordResetResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    UserResponse,
)
from ..services import UserService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
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


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email and password."
)
async def register(
    request: RegisterRequest,
    user_service: UserService = Depends(get_user_service)
):
    """
    Register a new user account.
    
    Creates a User concept in user-storage.dat with securely hashed password.
    
    **Returns:**
    - User information (without password)
    
    **Raises:**
    - 400: Invalid input or user already exists
    - 500: Server error during registration
    """
    try:
        user_info = await user_service.register(
            email=request.email,
            password=request.password,
            organization=request.organization,
            full_name=request.full_name,
            role=request.role,
        )
        
        return UserResponse(**user_info)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User login",
    description="Authenticate user and create session with JWT tokens."
)
async def login(
    request: LoginRequest,
    user_service: UserService = Depends(get_user_service)
):
    """
    Authenticate user and create session.
    
    Verifies credentials and creates:
    - Session concept in user-storage.dat
    - JWT access token (24 hours)
    - JWT refresh token (7 days)
    
    **Returns:**
    - Access token and refresh token
    - User information
    
    **Raises:**
    - 401: Invalid credentials
    - 500: Server error during login
    """
    try:
        session_info = await user_service.login(
            email=request.email,
            password=request.password
        )
        
        # Create JWT tokens
        token_data = {
            "user_id": session_info["user_id"],
            "session_id": session_info["session_id"],
            "email": session_info["email"],
            "organization": session_info["organization"],
            "role": session_info["role"],
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        user_response = UserResponse(
            user_id=session_info["user_id"],
            email=session_info["email"],
            organization=session_info["organization"],
            role=session_info["role"],
            full_name=session_info.get("full_name"),
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_expiration_hours * 3600,
            user=user_response
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="User logout",
    description="Invalidate current session."
)
async def logout(
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Logout user and invalidate session.
    
    Marks the session as inactive in user-storage.dat.
    Client should discard JWT tokens after logout.
    
    **Returns:**
    - Logout confirmation
    
    **Raises:**
    - 401: Invalid or expired token
    - 500: Server error during logout
    """
    try:
        session_id = current_user["session_id"]
        await user_service.logout(session_id)
        
        return LogoutResponse(
            message="Successfully logged out",
            success=True
        )
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get information about the currently authenticated user."
)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get current user information.
    
    Validates session and returns user details from user-storage.dat.
    
    **Returns:**
    - User information
    
    **Raises:**
    - 401: Invalid or expired token
    - 404: User not found
    """
    try:
        # Validate session
        session_info = await user_service.validate_session(
            current_user["session_id"]
        )
        
        if not session_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get full user details
        user_info = await user_service.get_user(session_info["user_id"])
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(**user_info)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )


@router.post(
    "/refresh",
    response_model=LoginResponse,
    summary="Refresh access token",
    description="Use refresh token to get a new access token."
)
async def refresh_token(
    request: RefreshTokenRequest,
    user_service: UserService = Depends(get_user_service)
):
    """
    Refresh access token using refresh token.
    
    Validates refresh token and issues new access and refresh tokens.
    
    **Returns:**
    - New access token and refresh token
    - User information
    
    **Raises:**
    - 401: Invalid or expired refresh token
    - 500: Server error during refresh
    """
    try:
        # Decode refresh token
        payload = decode_token(request.refresh_token)
        
        # Validate session still exists
        session_id = payload.get("session_id")
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        session_info = await user_service.validate_session(session_id)
        
        if not session_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new tokens
        token_data = {
            "user_id": session_info["user_id"],
            "session_id": session_info["session_id"],
            "email": session_info["email"],
            "organization": session_info["organization"],
            "role": session_info["role"],
        }
        
        access_token = create_access_token(token_data)
        refresh_token_new = create_refresh_token(token_data)
        
        user_response = UserResponse(
            user_id=session_info["user_id"],
            email=session_info["email"],
            organization=session_info["organization"],
            role=session_info["role"],
            full_name=session_info.get("full_name"),
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token_new,
            token_type="bearer",
            expires_in=settings.jwt_expiration_hours * 3600,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/health",
    summary="Auth service health",
    description="Check authentication service health."
)
async def auth_health(request: Request):
    """
    Check authentication service health.
    
    Verifies user storage connection.
    
    **Returns:**
    - Health status
    """
    try:
        if not hasattr(request.app.state, "user_storage_client"):
            return {
                "status": "unhealthy",
                "message": "User storage not connected"
            }
        
        # Try to get stats
        try:
            stats = request.app.state.user_storage_client.stats()
            user_concepts = stats.get("concepts", 0)
        except:
            user_concepts = 0
        
        return {
            "status": "healthy",
            "message": "Authentication service operational",
            "user_concepts": user_concepts
        }
        
    except Exception as e:
        logger.error(f"Auth health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": str(e)
        }


@router.put(
    "/change-password",
    summary="Change password",
    description="Change user password (requires current password)."
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Change user password.
    
    Requires current password for verification.
    
    **Returns:**
    - Success confirmation
    
    **Raises:**
    - 400: Current password incorrect or validation failed
    - 401: Invalid or expired token
    - 500: Server error
    """
    try:
        success = await user_service.change_password(
            user_id=current_user["user_id"],
            old_password=request.old_password,
            new_password=request.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password change failed"
            )
        
        return {
            "message": "Password changed successfully",
            "success": True
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Password change failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.post(
    "/forgot-password",
    response_model=PasswordResetResponse,
    summary="Request password reset",
    description="Request a password reset token (sent via email in production)."
)
async def forgot_password(
    request: ForgotPasswordRequest,
    user_service: UserService = Depends(get_user_service)
):
    """
    Request password reset token.
    
    Generates a secure token and returns it (in production, would send via email).
    Always returns success even if email doesn't exist (security best practice).
    
    **Returns:**
    - Success message
    
    **Note:** In production, the token would be sent via email, not returned in response.
    """
    try:
        token = await user_service.generate_password_reset_token(request.email)
        
        # In production, send token via email
        # For now, we return it (NOT secure for production!)
        if token:
            logger.info(f"Password reset token generated: {token[:8]}...")
        
        # Always return success (don't reveal if email exists)
        return PasswordResetResponse(
            message="If the email exists, a password reset link has been sent",
            success=True
        )
        
    except Exception as e:
        logger.error(f"Forgot password request failed: {e}")
        # Still return success (don't reveal errors)
        return PasswordResetResponse(
            message="If the email exists, a password reset link has been sent",
            success=True
        )


@router.post(
    "/reset-password",
    response_model=PasswordResetResponse,
    summary="Reset password with token",
    description="Reset password using the reset token."
)
async def reset_password(
    request: ResetPasswordRequest,
    user_service: UserService = Depends(get_user_service)
):
    """
    Reset password using token.
    
    Uses the token from forgot-password endpoint to set a new password.
    
    **Returns:**
    - Success confirmation
    
    **Raises:**
    - 400: Invalid or expired token
    - 500: Server error
    """
    try:
        success = await user_service.reset_password_with_token(
            token=request.token,
            new_password=request.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password reset failed"
            )
        
        return PasswordResetResponse(
            message="Password reset successfully",
            success=True
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Password reset failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )

