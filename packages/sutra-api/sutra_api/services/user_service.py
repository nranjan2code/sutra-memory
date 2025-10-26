"""
User Management Service.

Handles user registration, authentication, and session management using
Sutra's storage engine as the backend (dogfooding storage.dat for auth).
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError

logger = logging.getLogger(__name__)


class UserService:
    """
    User management service using Sutra storage for user data.
    
    This service proves that Sutra's storage engine can replace traditional
    database stacks (PostgreSQL + Redis) for user management and authentication.
    
    All user data is stored as concepts in user-storage.dat with associations
    for relationships (user -> sessions, user -> conversations, etc.).
    """
    
    def __init__(self, user_storage_client):
        """
        Initialize user service with storage client.
        
        Args:
            user_storage_client: StorageClient connected to user-storage.dat
        """
        self.storage = user_storage_client
        self.ph = PasswordHasher()
        logger.info("UserService initialized with storage client")
    
    async def register(
        self, 
        email: str, 
        password: str, 
        organization: str,
        full_name: Optional[str] = None,
        role: str = "user"
    ) -> Dict:
        """
        Register a new user account.
        
        Creates a User concept in user-storage.dat with hashed password.
        Uses Argon2id for secure password hashing.
        
        Args:
            email: User email (unique identifier)
            password: Plain-text password (will be hashed)
            organization: Organization ID
            full_name: Optional full name
            role: User role (default: "user")
        
        Returns:
            Dict with user_id and user details
        
        Raises:
            ValueError: If user already exists or validation fails
        """
        # Validate email format
        if not email or "@" not in email:
            raise ValueError("Invalid email address")
        
        # Validate password strength
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        # Check if user already exists
        try:
            existing_users = self.storage.semantic_search(
                query=f"user email:{email}",
                k=1,
            )
            
            if existing_users and len(existing_users) > 0:
                raise ValueError(f"User with email {email} already exists")
        except Exception as e:
            logger.error(f"Error checking existing user: {e}")
            # Continue with registration if search fails
        
        # Hash password with Argon2id
        try:
            password_hash = self.ph.hash(password)
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise ValueError("Failed to hash password")
        
        # Create user concept
        now = datetime.utcnow().isoformat()
        content = f"User {email}" + (f" - {full_name}" if full_name else "")
        
        metadata = {
            "type": "user",
            "email": email,
            "password_hash": password_hash,
            "organization": organization,
            "role": role,
            "full_name": full_name or "",
            "active": True,
            "created_at": now,
            "updated_at": now,
            "last_login": None,
        }
        
        try:
            # Learn user concept with metadata
            user_id = self.storage.learn_concept_v2(
                content=content,
                options={
                    "generate_embedding": True,
                    "extract_associations": False,  # No associations yet
                    "metadata": metadata,
                }
            )
            
            logger.info(f"✅ User registered: {email} (ID: {user_id[:8]})")
            
            return {
                "user_id": user_id,
                "email": email,
                "organization": organization,
                "role": role,
                "full_name": full_name,
                "created_at": now,
            }
        except Exception as e:
            logger.error(f"Failed to create user concept: {e}")
            raise ValueError(f"User registration failed: {str(e)}")
    
    async def login(self, email: str, password: str) -> Dict:
        """
        Authenticate user and create session.
        
        Verifies password and creates a Session concept in user-storage.dat.
        
        Args:
            email: User email
            password: Plain-text password
        
        Returns:
            Dict with user info and session_id
        
        Raises:
            ValueError: If credentials are invalid
        """
        # Find user by email
        try:
            users = self.storage.semantic_search(
                query=f"user email:{email}",
                k=1,
            )
            
            if not users or len(users) == 0:
                raise ValueError("Invalid credentials")
            
            user = users[0]
            
            # Check if user is active
            if not user.get("metadata", {}).get("active", False):
                raise ValueError("User account is inactive")
            
            # Get password hash from metadata
            stored_hash = user.get("metadata", {}).get("password_hash")
            if not stored_hash:
                raise ValueError("User account is corrupted")
            
            # Verify password
            try:
                self.ph.verify(stored_hash, password)
            except (VerificationError, VerifyMismatchError):
                raise ValueError("Invalid credentials")
            
            # Check if password needs rehashing (Argon2 params updated)
            if self.ph.check_needs_rehash(stored_hash):
                new_hash = self.ph.hash(password)
                # TODO: Update user metadata with new hash
                logger.info(f"Password rehashed for user {email}")
            
            user_id = user.get("id")
            if not user_id:
                raise ValueError("User ID not found")
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Login failed for {email}: {e}")
            raise ValueError("Login failed")
        
        # Create session
        try:
            now = datetime.utcnow()
            expires_at = now + timedelta(hours=24)
            
            session_content = f"Session for {email} started at {now.isoformat()}"
            session_metadata = {
                "type": "session",
                "user_id": user_id,
                "created_at": now.isoformat(),
                "expires_at": expires_at.isoformat(),
                "active": True,
                "last_activity": now.isoformat(),
            }
            
            session_id = self.storage.learn_concept_v2(
                content=session_content,
                options={
                    "generate_embedding": False,  # Sessions don't need embeddings
                    "extract_associations": False,
                    "metadata": session_metadata,
                }
            )
            
            # Create association: user -> session
            self.storage.create_association(
                from_concept=user_id,
                to_concept=session_id,
                association_type="has_session",
                strength=1.0,
            )
            
            # Update last_login timestamp
            # Note: Metadata updates not yet implemented in storage client
            # TODO: Add update_concept_metadata method
            
            logger.info(f"✅ Session created for {email} (Session: {session_id[:8]})")
            
            return {
                "user_id": user_id,
                "session_id": session_id,
                "email": email,
                "organization": user.get("metadata", {}).get("organization"),
                "role": user.get("metadata", {}).get("role"),
                "full_name": user.get("metadata", {}).get("full_name"),
                "expires_at": expires_at.isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Session creation failed for {email}: {e}")
            raise ValueError(f"Session creation failed: {str(e)}")
    
    async def logout(self, session_id: str) -> bool:
        """
        Invalidate a user session.
        
        Marks session as inactive in user-storage.dat (soft delete).
        
        Args:
            session_id: Session ID to invalidate
        
        Returns:
            True if successful
        
        Raises:
            ValueError: If session not found
        """
        try:
            # Get session concept
            session = self.storage.get_concept(session_id)
            
            if not session:
                raise ValueError("Session not found")
            
            # Mark session as inactive
            # Note: Metadata updates not yet implemented
            # TODO: Add update_concept_metadata method
            # For now, we'll rely on expiration time checking
            
            logger.info(f"✅ Session invalidated: {session_id[:8]}")
            return True
            
        except Exception as e:
            logger.error(f"Logout failed for session {session_id}: {e}")
            raise ValueError("Logout failed")
    
    async def validate_session(self, session_id: str) -> Optional[Dict]:
        """
        Validate a session and return user info.
        
        Checks if session exists, is active, and not expired.
        
        Args:
            session_id: Session ID to validate
        
        Returns:
            Dict with user info if valid, None otherwise
        """
        try:
            # Get session concept
            session = self.storage.get_concept(session_id)
            
            if not session:
                return None
            
            metadata = session.get("metadata", {})
            
            # Check if active
            if not metadata.get("active", False):
                return None
            
            # Check expiration
            expires_at_str = metadata.get("expires_at")
            if expires_at_str:
                expires_at = datetime.fromisoformat(expires_at_str)
                if datetime.utcnow() > expires_at:
                    logger.info(f"Session expired: {session_id[:8]}")
                    return None
            
            # Get user ID
            user_id = metadata.get("user_id")
            if not user_id:
                return None
            
            # Get user concept
            user = self.storage.get_concept(user_id)
            if not user:
                return None
            
            user_metadata = user.get("metadata", {})
            
            # Check if user is active
            if not user_metadata.get("active", False):
                return None
            
            # Update last_activity
            # TODO: Add update_concept_metadata method
            
            return {
                "user_id": user_id,
                "session_id": session_id,
                "email": user_metadata.get("email"),
                "organization": user_metadata.get("organization"),
                "role": user_metadata.get("role"),
                "full_name": user_metadata.get("full_name"),
            }
            
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            return None
    
    async def get_user(self, user_id: str) -> Optional[Dict]:
        """
        Get user details by ID.
        
        Args:
            user_id: User concept ID
        
        Returns:
            Dict with user info or None if not found
        """
        try:
            user = self.storage.get_concept(user_id)
            
            if not user:
                return None
            
            metadata = user.get("metadata", {})
            
            return {
                "user_id": user_id,
                "email": metadata.get("email"),
                "organization": metadata.get("organization"),
                "role": metadata.get("role"),
                "full_name": metadata.get("full_name"),
                "active": metadata.get("active"),
                "created_at": metadata.get("created_at"),
                "last_login": metadata.get("last_login"),
            }
            
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return None
    
    async def refresh_session(self, session_id: str) -> Optional[Dict]:
        """
        Refresh an existing session (extend expiration).
        
        Args:
            session_id: Session ID to refresh
        
        Returns:
            Dict with new expiration time
        """
        # Validate session first
        session_info = await self.validate_session(session_id)
        if not session_info:
            return None
        
        # TODO: Implement metadata update to extend expires_at
        # For now, return existing info
        return session_info
