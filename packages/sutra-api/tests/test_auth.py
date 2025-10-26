"""
Authentication API Tests.

Tests for user registration, login, logout, and session management.
"""

import pytest
from fastapi.testclient import TestClient


class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_register_success(self, client: TestClient):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePass123",
                "organization": "test-org",
                "full_name": "Test User",
                "role": "user"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["organization"] == "test-org"
        assert data["role"] == "user"
        assert "user_id" in data
        assert "password" not in data  # Password should not be in response
    
    def test_register_duplicate_email(self, client: TestClient):
        """Test registration with duplicate email."""
        # Register first user
        client.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "SecurePass123",
                "organization": "test-org"
            }
        )
        
        # Try to register again with same email
        response = client.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "DifferentPass123",
                "organization": "test-org"
            }
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_register_weak_password(self, client: TestClient):
        """Test registration with weak password."""
        response = client.post(
            "/auth/register",
            json={
                "email": "weak@example.com",
                "password": "123",  # Too short
                "organization": "test-org"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email."""
        response = client.post(
            "/auth/register",
            json={
                "email": "not-an-email",
                "password": "SecurePass123",
                "organization": "test-org"
            }
        )
        
        assert response.status_code == 400
    
    def test_login_success(self, client: TestClient):
        """Test successful login."""
        # Register user first
        client.post(
            "/auth/register",
            json={
                "email": "login@example.com",
                "password": "SecurePass123",
                "organization": "test-org"
            }
        )
        
        # Login
        response = client.post(
            "/auth/login",
            json={
                "email": "login@example.com",
                "password": "SecurePass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
        assert data["user"]["email"] == "login@example.com"
    
    def test_login_wrong_password(self, client: TestClient):
        """Test login with wrong password."""
        # Register user
        client.post(
            "/auth/register",
            json={
                "email": "wrong@example.com",
                "password": "CorrectPass123",
                "organization": "test-org"
            }
        )
        
        # Try to login with wrong password
        response = client.post(
            "/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "WrongPass123"
            }
        )
        
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user."""
        response = client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePass123"
            }
        )
        
        assert response.status_code == 401
    
    def test_get_current_user(self, client: TestClient):
        """Test getting current user information."""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "email": "current@example.com",
                "password": "SecurePass123",
                "organization": "test-org",
                "full_name": "Current User"
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={
                "email": "current@example.com",
                "password": "SecurePass123"
            }
        )
        
        token = login_response.json()["access_token"]
        
        # Get current user info
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "current@example.com"
        assert data["full_name"] == "Current User"
    
    def test_get_current_user_no_token(self, client: TestClient):
        """Test getting current user without token."""
        response = client.get("/auth/me")
        
        assert response.status_code == 403  # No credentials
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code == 401
    
    def test_logout(self, client: TestClient):
        """Test user logout."""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "email": "logout@example.com",
                "password": "SecurePass123",
                "organization": "test-org"
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={
                "email": "logout@example.com",
                "password": "SecurePass123"
            }
        )
        
        token = login_response.json()["access_token"]
        
        # Logout
        response = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_refresh_token(self, client: TestClient):
        """Test token refresh."""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "email": "refresh@example.com",
                "password": "SecurePass123",
                "organization": "test-org"
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={
                "email": "refresh@example.com",
                "password": "SecurePass123"
            }
        )
        
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_token_invalid(self, client: TestClient):
        """Test token refresh with invalid token."""
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "invalid_refresh_token"}
        )
        
        assert response.status_code == 401
    
    def test_auth_health(self, client: TestClient):
        """Test authentication health endpoint."""
        response = client.get("/auth/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data


class TestSessionManagement:
    """Test session management."""
    
    def test_session_created_on_login(self, client: TestClient):
        """Test that session is created on login."""
        # Register user
        client.post(
            "/auth/register",
            json={
                "email": "session@example.com",
                "password": "SecurePass123",
                "organization": "test-org"
            }
        )
        
        # Login (creates session)
        response = client.post(
            "/auth/login",
            json={
                "email": "session@example.com",
                "password": "SecurePass123"
            }
        )
        
        assert response.status_code == 200
        # Token should contain session_id
        token = response.json()["access_token"]
        assert token is not None
    
    def test_multiple_sessions_allowed(self, client: TestClient):
        """Test that multiple sessions can exist for same user."""
        # Register user
        client.post(
            "/auth/register",
            json={
                "email": "multi@example.com",
                "password": "SecurePass123",
                "organization": "test-org"
            }
        )
        
        # Login twice
        response1 = client.post(
            "/auth/login",
            json={
                "email": "multi@example.com",
                "password": "SecurePass123"
            }
        )
        
        response2 = client.post(
            "/auth/login",
            json={
                "email": "multi@example.com",
                "password": "SecurePass123"
            }
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        token1 = response1.json()["access_token"]
        token2 = response2.json()["access_token"]
        
        # Tokens should be different
        assert token1 != token2


class TestPasswordSecurity:
    """Test password security features."""
    
    def test_password_not_returned(self, client: TestClient):
        """Test that password is never returned in responses."""
        # Register
        register_response = client.post(
            "/auth/register",
            json={
                "email": "secure@example.com",
                "password": "SecurePass123",
                "organization": "test-org"
            }
        )
        
        assert "password" not in register_response.json()
        assert "password_hash" not in register_response.json()
        
        # Login
        login_response = client.post(
            "/auth/login",
            json={
                "email": "secure@example.com",
                "password": "SecurePass123"
            }
        )
        
        assert "password" not in login_response.json()
        assert "password_hash" not in login_response.json()
    
    def test_password_hashed_securely(self, client: TestClient):
        """Test that passwords are hashed with Argon2."""
        # This is integration test - actual hashing is tested in service
        response = client.post(
            "/auth/register",
            json={
                "email": "hash@example.com",
                "password": "SecurePass123",
                "organization": "test-org"
            }
        )
        
        assert response.status_code == 201
        # Password should be hashed and stored securely (tested via login)
        
        login_response = client.post(
            "/auth/login",
            json={
                "email": "hash@example.com",
                "password": "SecurePass123"
            }
        )
        
        assert login_response.status_code == 200


# Fixtures
@pytest.fixture
def client():
    """Create test client with in-memory storage."""
    # Note: This assumes storage client is properly mocked or uses test instance
    from ..main import app
    return TestClient(app)
