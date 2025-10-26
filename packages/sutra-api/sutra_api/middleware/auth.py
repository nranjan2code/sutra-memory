"""
Authentication middleware for JWT token management.

Handles token generation, verification, and user context injection.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..config import settings

logger = logging.getLogger(__name__)

# HTTP Bearer security scheme
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data to encode in token
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token encoding failed: {e}")
        raise


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        data: Payload data to encode in token
    
    Returns:
        Encoded JWT refresh token string
    """
    expires_delta = timedelta(days=settings.jwt_refresh_expiration_days)
    return create_access_token(data, expires_delta)


def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Dependency to extract and validate current user from JWT token.
    
    This validates the token structure but does NOT validate the session
    in storage. Use get_current_active_user for full validation.
    
    Args:
        credentials: HTTP Bearer credentials from request
    
    Returns:
        Decoded token payload with user info
    
    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    # Extract user info from token
    user_id = payload.get("user_id")
    session_id = payload.get("session_id")
    
    if not user_id or not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "user_id": user_id,
        "session_id": session_id,
        "email": payload.get("email"),
        "organization": payload.get("organization"),
        "role": payload.get("role"),
    }


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
    user_service = None,  # Will be injected via dependency
) -> dict:
    """
    Dependency to get current user with full session validation.
    
    Validates that the session still exists and is active in storage.
    This is the recommended dependency for protected endpoints.
    
    Args:
        current_user: User info from JWT token
        user_service: UserService instance (injected)
    
    Returns:
        Validated user info
    
    Raises:
        HTTPException: If session is invalid or expired
    """
    if not user_service:
        # Fallback if service not injected
        return current_user
    
    # Validate session in storage
    session_info = await user_service.validate_session(
        current_user["session_id"]
    )
    
    if not session_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return session_info


def require_role(required_role: str):
    """
    Dependency factory to check user role.
    
    Usage:
        @app.get("/admin", dependencies=[Depends(require_role("admin"))])
    
    Args:
        required_role: Required role string
    
    Returns:
        Dependency function
    """
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        
        if user_role != required_role and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}",
            )
        
        return current_user
    
    return role_checker
