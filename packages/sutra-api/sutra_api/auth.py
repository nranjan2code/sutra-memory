"""
Production-grade authentication middleware for Sutra API.

Supports:
- HMAC-based API keys
- JWT tokens (HS256)
- Role-based access control
- Token validation with expiration
"""

import os
import time
import hmac
import hashlib
import json
import base64
from typing import Optional, List, Dict
from enum import Enum

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware

import logging

logger = logging.getLogger(__name__)


class Role(str, Enum):
    """User roles for RBAC"""
    ADMIN = "Admin"
    WRITER = "Writer"
    READER = "Reader"
    SERVICE = "Service"


class Claims:
    """Authentication claims"""
    
    def __init__(self, sub: str, roles: List[Role], exp: int, iat: int):
        self.sub = sub
        self.roles = roles
        self.exp = exp
        self.iat = iat
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return time.time() > self.exp
    
    def has_role(self, role: Role) -> bool:
        """Check if claims have specific role"""
        return role in self.roles
    
    def can_perform(self, operation: str) -> bool:
        """Check if claims allow specific operation"""
        # Admin can do everything
        if self.has_role(Role.ADMIN):
            return True
        
        # Role-based defaults
        if operation in ["read", "query", "search", "health"]:
            return (self.has_role(Role.READER) or 
                   self.has_role(Role.WRITER) or 
                   self.has_role(Role.SERVICE))
        elif operation in ["write", "learn", "create"]:
            return (self.has_role(Role.WRITER) or 
                   self.has_role(Role.SERVICE))
        elif operation in ["delete", "flush", "admin"]:
            return self.has_role(Role.ADMIN)
        
        return False


class AuthManager:
    """
    Production-grade authentication manager.
    
    Validates HMAC-signed or JWT tokens and enforces RBAC.
    """
    
    def __init__(self, secret: str, method: str = "hmac"):
        if len(secret) < 32:
            raise ValueError("Secret must be at least 32 characters")
        
        self.secret = secret.encode()
        self.method = method
    
    @classmethod
    def from_env(cls) -> "AuthManager":
        """Load authentication from environment variables"""
        secret = os.getenv("SUTRA_AUTH_SECRET")
        if not secret:
            raise ValueError("SUTRA_AUTH_SECRET environment variable required")
        
        method = os.getenv("SUTRA_AUTH_METHOD", "hmac")
        return cls(secret, method)
    
    def validate_token(self, token: str) -> Claims:
        """Validate authentication token and extract claims"""
        if self.method == "hmac":
            return self._validate_hmac_token(token)
        elif self.method in ["jwt", "jwt-hs256"]:
            return self._validate_jwt_token(token)
        else:
            raise ValueError(f"Unknown auth method: {self.method}")
    
    def _validate_hmac_token(self, token: str) -> Claims:
        """Validate HMAC-signed token"""
        try:
            # Split token
            parts = token.split(".")
            if len(parts) != 2:
                raise ValueError("Invalid token format")
            
            payload_b64, signature_b64 = parts
            
            # Verify signature
            expected_sig = hmac.new(
                self.secret,
                payload_b64.encode(),
                hashlib.sha256
            ).digest()
            
            provided_sig = base64.urlsafe_b64decode(
                signature_b64 + "=" * (4 - len(signature_b64) % 4)
            )
            
            if not hmac.compare_digest(expected_sig, provided_sig):
                raise ValueError("Invalid signature")
            
            # Decode payload
            payload_bytes = base64.urlsafe_b64decode(
                payload_b64 + "=" * (4 - len(payload_b64) % 4)
            )
            payload = json.loads(payload_bytes)
            
            # Extract claims
            claims = Claims(
                sub=payload["sub"],
                roles=[Role(r) for r in payload["roles"]],
                exp=payload["exp"],
                iat=payload["iat"]
            )
            
            # Check expiration
            if claims.is_expired():
                raise ValueError("Token expired")
            
            return claims
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
    
    def _validate_jwt_token(self, token: str) -> Claims:
        """Validate JWT token (HS256)"""
        try:
            # Split JWT
            parts = token.split(".")
            if len(parts) != 3:
                raise ValueError("Invalid JWT format")
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            signing_input = f"{header_b64}.{payload_b64}"
            expected_sig = hmac.new(
                self.secret,
                signing_input.encode(),
                hashlib.sha256
            ).digest()
            
            provided_sig = base64.urlsafe_b64decode(
                signature_b64 + "=" * (4 - len(signature_b64) % 4)
            )
            
            if not hmac.compare_digest(expected_sig, provided_sig):
                raise ValueError("Invalid JWT signature")
            
            # Decode payload
            payload_bytes = base64.urlsafe_b64decode(
                payload_b64 + "=" * (4 - len(payload_b64) % 4)
            )
            payload = json.loads(payload_bytes)
            
            # Extract claims
            claims = Claims(
                sub=payload["sub"],
                roles=[Role(r) for r in payload["roles"]],
                exp=payload["exp"],
                iat=payload["iat"]
            )
            
            # Check expiration
            if claims.is_expired():
                raise ValueError("Token expired")
            
            return claims
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid JWT: {str(e)}"
            )


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware for FastAPI.
    
    Validates authentication tokens and attaches claims to request state.
    """
    
    def __init__(
        self, 
        app,
        auth_manager: AuthManager,
        exempt_paths: List[str] = None
    ):
        super().__init__(app)
        self.auth_manager = auth_manager
        self.exempt_paths = exempt_paths or ["/health", "/docs", "/openapi.json", "/"]
    
    async def dispatch(self, request: Request, call_next):
        """Process request with authentication"""
        
        # Skip authentication for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return self._unauthorized_response("Missing Authorization header")
        
        # Parse Bearer token
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return self._unauthorized_response("Invalid Authorization header format")
        
        token = parts[1]
        
        # Validate token
        try:
            claims = self.auth_manager.validate_token(token)
        except HTTPException as e:
            return self._unauthorized_response(str(e.detail))
        
        # Attach claims to request state
        request.state.claims = claims
        request.state.user_id = claims.sub
        
        # Log authentication
        logger.info(f"✅ Authenticated: {claims.sub} ({request.client.host if request.client else 'unknown'})")
        
        # Process request
        return await call_next(request)
    
    def _unauthorized_response(self, detail: str):
        """Return 401 Unauthorized response"""
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "Unauthorized",
                "detail": detail
            },
            headers={"WWW-Authenticate": "Bearer"}
        )


def require_permission(operation: str):
    """
    Dependency for requiring specific permission.
    
    Usage:
        @app.post("/learn", dependencies=[Depends(require_permission("write"))])
        async def learn(...):
            ...
    """
    from fastapi import Depends
    
    def check_permission(request: Request):
        if not hasattr(request.state, "claims"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        claims: Claims = request.state.claims
        if not claims.can_perform(operation):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: requires '{operation}'"
            )
        
        return claims
    
    return check_permission


def get_current_user(request: Request) -> Claims:
    """
    Dependency for getting current authenticated user.
    
    Usage:
        @app.get("/me")
        async def get_me(claims: Claims = Depends(get_current_user)):
            return {"user": claims.sub}
    """
    if not hasattr(request.state, "claims"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    return request.state.claims
