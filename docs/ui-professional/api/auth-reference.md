# Authentication API - Quick Reference

**Sutra AI Authentication System**

Base URL: `http://localhost:8000`

---

## 📋 Endpoints

### 1. Register User

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "organization": "my-org",
  "full_name": "John Doe",
  "role": "user"
}
```

**Response (201):**
```json
{
  "user_id": "concept_abc123",
  "email": "user@example.com",
  "organization": "my-org",
  "role": "user",
  "full_name": "John Doe",
  "created_at": "2025-10-26T10:00:00Z"
}
```

---

### 2. Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "user_id": "concept_abc123",
    "email": "user@example.com",
    "organization": "my-org",
    "role": "user",
    "full_name": "John Doe"
  }
}
```

---

### 3. Get Current User

```http
GET /auth/me
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "user_id": "concept_abc123",
  "email": "user@example.com",
  "organization": "my-org",
  "role": "user",
  "full_name": "John Doe",
  "created_at": "2025-10-26T10:00:00Z",
  "last_login": "2025-10-26T10:30:00Z"
}
```

---

### 4. Logout

```http
POST /auth/logout
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Successfully logged out",
  "success": true
}
```

---

### 5. Refresh Token

```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "user_id": "concept_abc123",
    "email": "user@example.com",
    "organization": "my-org",
    "role": "user",
    "full_name": "John Doe"
  }
}
```

---

### 6. Health Check

```http
GET /auth/health
```

**Response (200):**
```json
{
  "status": "healthy",
  "message": "Authentication service operational",
  "user_concepts": 42
}
```

---

## 🔐 Authentication

All protected endpoints require the `Authorization` header:

```
Authorization: Bearer <access_token>
```

---

## ⏱️ Token Expiration

- **Access Token**: 24 hours
- **Refresh Token**: 7 days

When access token expires, use refresh token to get new tokens.

---

## ⚠️ Error Responses

### 400 Bad Request
```json
{
  "detail": "User with email user@example.com already exists"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

---

## 📝 Password Requirements

- Minimum 8 characters
- No complexity requirements (for now)

---

## 🔧 Configuration

Environment variables:

```bash
# User Storage
SUTRA_USER_STORAGE_SERVER=user-storage-server:50051

# JWT Configuration
SUTRA_JWT_SECRET_KEY=your-secret-key-here
SUTRA_JWT_ALGORITHM=HS256
SUTRA_JWT_EXPIRATION_HOURS=24
SUTRA_JWT_REFRESH_EXPIRATION_DAYS=7
```

---

## 🧪 Testing with curl

### Register
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123",
    "organization": "test-org",
    "full_name": "Test User"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

### Get Current User
```bash
TOKEN="your_access_token_here"

curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Logout
```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎯 Common Workflows

### 1. New User Registration
```
1. POST /auth/register
2. POST /auth/login
3. Store access_token and refresh_token
4. Use access_token for all requests
```

### 2. Returning User
```
1. POST /auth/login
2. Store access_token and refresh_token
3. Use access_token for all requests
```

### 3. Token Refresh
```
1. Access token expires (401 response)
2. POST /auth/refresh with refresh_token
3. Store new access_token
4. Retry original request
```

### 4. Logout
```
1. POST /auth/logout
2. Clear stored tokens
3. Redirect to login page
```

---

## 📚 Interactive Documentation

FastAPI provides interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Try endpoints directly in the browser!

---

## 🔍 Troubleshooting

### "User storage not connected"
- Check user-storage-server is running
- Verify SUTRA_USER_STORAGE_SERVER env var
- Check Docker network connectivity

### "Invalid credentials"
- Verify email and password
- Check user is active
- Ensure account exists

### "Token has expired"
- Use refresh token to get new access token
- If refresh token expired, user must login again

### "Session is invalid or expired"
- Session may have been logged out
- User must login again

---

**For more details, see:**
- [SESSION_1_3_COMPLETE.md](./SESSION_1_3_COMPLETE.md) - Implementation summary
- [CONVERSATION_FIRST_ARCHITECTURE.md](./CONVERSATION_FIRST_ARCHITECTURE.md) - Full architecture
