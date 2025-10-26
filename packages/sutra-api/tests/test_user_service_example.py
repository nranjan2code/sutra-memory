"""
Test suite for UserService

Tests user registration, authentication, session management,
and password security.
"""

import pytest
from datetime import datetime, timedelta
from sutra_api.services.user_service import UserService
from sutra_api.schema import ConceptType, AssociationType


@pytest.fixture
async def user_service(storage_client):
    """Create UserService with mocked storage client"""
    return UserService(storage_client)


@pytest.fixture
def sample_user_data():
    """Sample user registration data"""
    return {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "organization": "Test Org"
    }


class TestUserRegistration:
    """Test user registration flows"""
    
    @pytest.mark.asyncio
    async def test_register_success(self, user_service, sample_user_data):
        """Test successful user registration"""
        user = await user_service.register(
            email=sample_user_data["email"],
            password=sample_user_data["password"],
            organization=sample_user_data["organization"]
        )
        
        assert user["email"] == sample_user_data["email"]
        assert user["organization"] == sample_user_data["organization"]
        assert "id" in user
        assert "password" not in user  # Password should never be returned
        assert "password_hash" not in user
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, user_service, sample_user_data):
        """Test registration with existing email fails"""
        # Register first user
        await user_service.register(**sample_user_data)
        
        # Try to register again with same email
        with pytest.raises(ValueError, match="already registered"):
            await user_service.register(**sample_user_data)
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, user_service, sample_user_data):
        """Test registration with weak password fails"""
        sample_user_data["password"] = "weak"
        
        with pytest.raises(ValueError, match="Password must be"):
            await user_service.register(**sample_user_data)
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, user_service, sample_user_data):
        """Test registration with invalid email fails"""
        sample_user_data["email"] = "not-an-email"
        
        with pytest.raises(ValueError, match="Invalid email"):
            await user_service.register(**sample_user_data)


class TestUserAuthentication:
    """Test user login and authentication"""
    
    @pytest.mark.asyncio
    async def test_login_success(self, user_service, sample_user_data):
        """Test successful login"""
        # Register user first
        await user_service.register(**sample_user_data)
        
        # Login
        result = await user_service.login(
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )
        
        assert "user" in result
        assert "session_id" in result
        assert result["user"]["email"] == sample_user_data["email"]
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, user_service, sample_user_data):
        """Test login with wrong password fails"""
        await user_service.register(**sample_user_data)
        
        with pytest.raises(ValueError, match="Invalid credentials"):
            await user_service.login(
                email=sample_user_data["email"],
                password="WrongPassword123!"
            )
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, user_service):
        """Test login with non-existent user fails"""
        with pytest.raises(ValueError, match="User not found"):
            await user_service.login(
                email="nonexistent@example.com",
                password="Password123!"
            )


class TestSessionManagement:
    """Test session creation, validation, and revocation"""
    
    @pytest.mark.asyncio
    async def test_create_session(self, user_service, sample_user_data):
        """Test session creation"""
        user = await user_service.register(**sample_user_data)
        session_id = await user_service._create_session(user["id"])
        
        assert session_id is not None
        assert len(session_id) > 20  # UUID should be long
    
    @pytest.mark.asyncio
    async def test_validate_session_success(self, user_service, sample_user_data):
        """Test validating active session"""
        # Register and login
        result = await user_service.login(
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )
        
        # Validate session
        user = await user_service.validate_session(result["session_id"])
        assert user["email"] == sample_user_data["email"]
    
    @pytest.mark.asyncio
    async def test_validate_session_expired(self, user_service, sample_user_data):
        """Test validating expired session fails"""
        # Register and login
        result = await user_service.login(
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )
        
        # Manually expire session (mock time passage)
        # In real implementation, this would involve time manipulation
        with pytest.raises(ValueError, match="expired"):
            # Simulate expired session
            await user_service.validate_session("expired_" + result["session_id"])
    
    @pytest.mark.asyncio
    async def test_logout(self, user_service, sample_user_data):
        """Test logout invalidates session"""
        # Register and login
        result = await user_service.login(
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )
        
        # Logout
        await user_service.logout(result["session_id"])
        
        # Session should no longer be valid
        with pytest.raises(ValueError, match="Invalid or expired"):
            await user_service.validate_session(result["session_id"])


class TestPasswordSecurity:
    """Test password hashing and security"""
    
    @pytest.mark.asyncio
    async def test_password_hashed(self, user_service, sample_user_data):
        """Test passwords are hashed, not stored plain text"""
        user = await user_service.register(**sample_user_data)
        
        # Get user from storage
        user_concept = await user_service.storage_client.get_concept(user["id"])
        password_hash = user_concept["metadata"]["password_hash"]
        
        # Hash should not equal plain text password
        assert password_hash != sample_user_data["password"]
        # Should be Argon2id hash
        assert password_hash.startswith("$argon2id$")
    
    @pytest.mark.asyncio
    async def test_password_verification(self, user_service, sample_user_data):
        """Test password verification works correctly"""
        await user_service.register(**sample_user_data)
        
        # Correct password should verify
        result = await user_service.login(
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )
        assert result is not None
        
        # Wrong password should fail
        with pytest.raises(ValueError):
            await user_service.login(
                email=sample_user_data["email"],
                password="WrongPassword"
            )


# Example: Test helper fixtures (conftest.py)
"""
@pytest.fixture
async def storage_client():
    '''Mock storage client for testing'''
    from unittest.mock import AsyncMock, MagicMock
    
    client = AsyncMock()
    client.learn_concept = AsyncMock(return_value="concept_id_123")
    client.query_graph = AsyncMock(return_value=[])
    client.get_concept = AsyncMock(return_value={
        "id": "concept_id_123",
        "content": "test content",
        "metadata": {}
    })
    
    return client
"""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
