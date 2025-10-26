# Sutra AI - API Reference

**Complete REST API documentation for Sutra AI**

Version: 2.0.0  
Base URL: `http://localhost:8000` (development)

---

## Table of Contents

1. [Authentication](#authentication)
2. [Conversations](#conversations)
3. [Spaces](#spaces)
4. [Search](#search)
5. [Knowledge Graphs](#knowledge-graphs)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [SDK Examples](#sdk-examples)

---

## Overview

### Base URL

```
Development: http://localhost:8000
Production:  https://your-domain.com/api
```

### Authentication

All endpoints (except auth endpoints) require JWT token in Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### Content Type

```http
Content-Type: application/json
```

### API Documentation (Interactive)

Swagger UI: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

---

## Authentication

### Register

Create a new user account.

```http
POST /auth/register
```

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "organization": "Acme Corp"
}
```

**Response:** `201 Created`

```json
{
  "user": {
    "id": "usr_abc123",
    "email": "user@example.com",
    "organization": "Acme Corp",
    "created_at": "2024-10-26T10:00:00Z"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Errors:**

- `400 Bad Request`: Validation error (weak password, invalid email)
- `409 Conflict`: Email already registered

**Example:**

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "organization": "Acme Corp"
  }'
```

---

### Login

Authenticate and receive JWT token.

```http
POST /auth/login
```

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`

```json
{
  "user": {
    "id": "usr_abc123",
    "email": "user@example.com",
    "organization": "Acme Corp"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Errors:**

- `401 Unauthorized`: Invalid credentials
- `404 Not Found`: User not found

**Example:**

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

---

### Logout

Invalidate the current session.

```http
POST /auth/logout
```

**Headers:**

```
Authorization: Bearer <token>
```

**Response:** `200 OK`

```json
{
  "message": "Successfully logged out"
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer <your-token>"
```

---

### Get Current User

Retrieve the authenticated user's profile.

```http
GET /auth/me
```

**Headers:**

```
Authorization: Bearer <token>
```

**Response:** `200 OK`

```json
{
  "id": "usr_abc123",
  "email": "user@example.com",
  "organization": "Acme Corp",
  "created_at": "2024-10-26T10:00:00Z"
}
```

**Errors:**

- `401 Unauthorized`: Invalid or expired token

**Example:**

```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer <your-token>"
```

---

### Refresh Token

Get a new access token using refresh token.

```http
POST /auth/refresh
```

**Request Body:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Errors:**

- `401 Unauthorized`: Invalid or expired refresh token

---

### Auth Health Check

Check if authentication service is operational.

```http
GET /auth/health
```

**Response:** `200 OK`

```json
{
  "status": "healthy",
  "service": "auth",
  "timestamp": "2024-10-26T10:00:00Z"
}
```

---

## Conversations

### Create Conversation

Start a new conversation in a space.

```http
POST /conversations/create
```

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "space_id": "spc_xyz789",
  "domain_storage": "medical-protocols"
}
```

**Response:** `201 Created`

```json
{
  "id": "conv_def456",
  "user_id": "usr_abc123",
  "space_id": "spc_xyz789",
  "domain_storage": "medical-protocols",
  "title": "New Conversation",
  "starred": false,
  "tags": [],
  "created_at": "2024-10-26T10:00:00Z",
  "updated_at": "2024-10-26T10:00:00Z"
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/conversations/create \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "space_id": "spc_xyz789",
    "domain_storage": "medical-protocols"
  }'
```

---

### List Conversations

Get all conversations for the authenticated user.

```http
GET /conversations/list
```

**Headers:**

```
Authorization: Bearer <token>
```

**Query Parameters:**

- `space_id` (optional): Filter by space
- `limit` (optional, default 50): Number of results
- `offset` (optional, default 0): Pagination offset
- `starred` (optional): Filter starred conversations

**Response:** `200 OK`

```json
{
  "conversations": [
    {
      "id": "conv_def456",
      "user_id": "usr_abc123",
      "space_id": "spc_xyz789",
      "title": "FDA 510(k) Process",
      "starred": true,
      "message_count": 15,
      "last_message_at": "2024-10-26T09:00:00Z",
      "created_at": "2024-10-25T10:00:00Z",
      "updated_at": "2024-10-26T09:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

**Example:**

```bash
curl -X GET "http://localhost:8000/conversations/list?space_id=spc_xyz789&limit=20" \
  -H "Authorization: Bearer <your-token>"
```

---

### Get Conversation

Retrieve conversation details.

```http
GET /conversations/{id}
```

**Headers:**

```
Authorization: Bearer <token>
```

**Response:** `200 OK`

```json
{
  "id": "conv_def456",
  "user_id": "usr_abc123",
  "space_id": "spc_xyz789",
  "domain_storage": "medical-protocols",
  "title": "FDA 510(k) Process",
  "starred": true,
  "tags": ["fda", "regulatory"],
  "created_at": "2024-10-25T10:00:00Z",
  "updated_at": "2024-10-26T09:00:00Z"
}
```

**Errors:**

- `404 Not Found`: Conversation not found
- `403 Forbidden`: No access to conversation

---

### Load Messages

Get messages from a conversation.

```http
GET /conversations/{id}/messages
```

**Headers:**

```
Authorization: Bearer <token>
```

**Query Parameters:**

- `limit` (optional, default 50): Number of messages
- `offset` (optional, default 0): Pagination offset

**Response:** `200 OK`

```json
{
  "messages": [
    {
      "id": "msg_ghi789",
      "conversation_id": "conv_def456",
      "role": "user",
      "content": "What is the FDA 510(k) process?",
      "timestamp": "2024-10-26T09:00:00Z"
    },
    {
      "id": "msg_jkl012",
      "conversation_id": "conv_def456",
      "role": "assistant",
      "content": "The FDA 510(k) premarket notification process...",
      "confidence": 0.95,
      "reasoning_path_id": "path_mno345",
      "timestamp": "2024-10-26T09:00:15Z"
    }
  ],
  "total": 2,
  "limit": 50,
  "offset": 0
}
```

---

### Send Message

Send a message and get AI response.

```http
POST /conversations/{id}/message
```

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "content": "What is the FDA 510(k) process?"
}
```

**Response:** `200 OK`

```json
{
  "user_message": {
    "id": "msg_ghi789",
    "conversation_id": "conv_def456",
    "role": "user",
    "content": "What is the FDA 510(k) process?",
    "timestamp": "2024-10-26T09:00:00Z"
  },
  "assistant_message": {
    "id": "msg_jkl012",
    "conversation_id": "conv_def456",
    "role": "assistant",
    "content": "The FDA 510(k) premarket notification process...",
    "confidence": 0.95,
    "reasoning_path_id": "path_mno345",
    "timestamp": "2024-10-26T09:00:15Z"
  }
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/conversations/conv_def456/message \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "What is the FDA 510(k) process?"
  }'
```

---

### Send Message (Streaming)

Send a message and receive AI response as Server-Sent Events (SSE).

```http
POST /conversations/{id}/message/stream
```

**Headers:**

```
Authorization: Bearer <token>
Content-Type: application/json
Accept: text/event-stream
```

**Request Body:**

```json
{
  "content": "What is the FDA 510(k) process?"
}
```

**Response:** `200 OK` (text/event-stream)

**Event Types:**

1. `user_message`: User message stored
2. `progress`: Reasoning stage update
3. `chunk`: Partial answer text
4. `complete`: Final answer with metadata
5. `error`: Error occurred

**Example Events:**

```
event: user_message
data: {"id": "msg_ghi789", "content": "What is the FDA 510(k) process?"}

event: progress
data: {"stage": "loading_context", "message": "Loading conversation context..."}

event: progress
data: {"stage": "querying_knowledge", "message": "Querying domain knowledge..."}

event: chunk
data: {"text": "The FDA 510(k) ", "confidence": 0.5}

event: chunk
data: {"text": "premarket notification ", "confidence": 0.75}

event: complete
data: {
  "id": "msg_jkl012",
  "content": "The FDA 510(k) premarket notification process...",
  "confidence": 0.95,
  "reasoning_path_id": "path_mno345"
}
```

**JavaScript Example:**

```javascript
const response = await fetch('http://localhost:8000/conversations/conv_def456/message/stream', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer <your-token>',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ content: 'What is the FDA 510(k) process?' })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('event: ')) {
      const eventType = line.substring(7);
    } else if (line.startsWith('data: ')) {
      const data = JSON.parse(line.substring(6));
      console.log(eventType, data);
    }
  }
}
```

---

### Update Conversation

Update conversation metadata (title, starred, tags).

```http
PATCH /conversations/{id}
```

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "title": "FDA 510(k) Process Guide",
  "starred": true,
  "tags": ["fda", "regulatory", "510k"]
}
```

**Response:** `200 OK`

```json
{
  "id": "conv_def456",
  "title": "FDA 510(k) Process Guide",
  "starred": true,
  "tags": ["fda", "regulatory", "510k"],
  "updated_at": "2024-10-26T10:00:00Z"
}
```

---

### Delete Conversation

Soft delete a conversation (for audit compliance).

```http
DELETE /conversations/{id}
```

**Headers:**

```
Authorization: Bearer <token>
```

**Response:** `200 OK`

```json
{
  "message": "Conversation deleted successfully",
  "id": "conv_def456"
}
```

**Note**: Soft delete marks as deleted but preserves data for audit trails.

---

## Spaces

### Create Space

Create a new space for organizing conversations.

```http
POST /spaces/create
```

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "name": "Medical Research",
  "description": "Space for medical device research",
  "icon": "🏥",
  "domain_storage": "medical-protocols"
}
```

**Response:** `201 Created`

```json
{
  "id": "spc_xyz789",
  "name": "Medical Research",
  "description": "Space for medical device research",
  "icon": "🏥",
  "domain_storage": "medical-protocols",
  "organization": "Acme Corp",
  "created_by": "usr_abc123",
  "created_at": "2024-10-26T10:00:00Z"
}
```

---

### List Spaces

Get all spaces accessible to the authenticated user.

```http
GET /spaces/list
```

**Headers:**

```
Authorization: Bearer <token>
```

**Response:** `200 OK`

```json
{
  "spaces": [
    {
      "id": "spc_xyz789",
      "name": "Medical Research",
      "description": "Space for medical device research",
      "icon": "🏥",
      "conversation_count": 15,
      "member_count": 5,
      "role": "admin",
      "created_at": "2024-10-26T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

### Get Space

Retrieve space details.

```http
GET /spaces/{id}
```

**Headers:**

```
Authorization: Bearer <token>
```

**Response:** `200 OK`

```json
{
  "id": "spc_xyz789",
  "name": "Medical Research",
  "description": "Space for medical device research",
  "icon": "🏥",
  "domain_storage": "medical-protocols",
  "organization": "Acme Corp",
  "created_by": "usr_abc123",
  "created_at": "2024-10-26T10:00:00Z",
  "conversation_count": 15,
  "member_count": 5,
  "your_role": "admin"
}
```

---

### Update Space

Update space metadata.

```http
PUT /spaces/{id}
```

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "name": "Medical Device Research",
  "description": "Updated description",
  "icon": "🏥"
}
```

**Response:** `200 OK`

```json
{
  "id": "spc_xyz789",
  "name": "Medical Device Research",
  "description": "Updated description",
  "icon": "🏥",
  "updated_at": "2024-10-26T11:00:00Z"
}
```

**Permissions**: Admin role required

---

### Delete Space

Soft delete a space.

```http
DELETE /spaces/{id}
```

**Headers:**

```
Authorization: Bearer <token>
```

**Response:** `200 OK`

```json
{
  "message": "Space deleted successfully",
  "id": "spc_xyz789"
}
```

**Permissions**: Admin role required

---

### Add Space Member

Invite a user to the space.

```http
POST /spaces/{id}/members
```

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "user_email": "colleague@example.com",
  "role": "writer"
}
```

**Roles:**
- `admin`: Full control
- `writer`: Read/write
- `reader`: Read-only

**Response:** `201 Created`

```json
{
  "user_id": "usr_def456",
  "space_id": "spc_xyz789",
  "role": "writer",
  "added_at": "2024-10-26T11:00:00Z"
}
```

**Permissions**: Admin role required

---

### List Space Members

Get all members of a space.

```http
GET /spaces/{id}/members
```

**Headers:**

```
Authorization: Bearer <token>
```

**Response:** `200 OK`

```json
{
  "members": [
    {
      "user_id": "usr_abc123",
      "email": "user@example.com",
      "role": "admin",
      "added_at": "2024-10-26T10:00:00Z"
    },
    {
      "user_id": "usr_def456",
      "email": "colleague@example.com",
      "role": "writer",
      "added_at": "2024-10-26T11:00:00Z"
    }
  ],
  "total": 2
}
```

---

### Update Member Role

Change a member's role in the space.

```http
PUT /spaces/{id}/members/{user_id}/role
```

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "role": "admin"
}
```

**Response:** `200 OK`

```json
{
  "user_id": "usr_def456",
  "space_id": "spc_xyz789",
  "role": "admin",
  "updated_at": "2024-10-26T12:00:00Z"
}
```

**Permissions**: Admin role required

---

### Remove Space Member

Remove a user from the space.

```http
DELETE /spaces/{id}/members/{user_id}
```

**Headers:**

```
Authorization: Bearer <token>
```

**Response:** `200 OK`

```json
{
  "message": "Member removed successfully",
  "user_id": "usr_def456",
  "space_id": "spc_xyz789"
}
```

**Permissions**: Admin role required  
**Note**: Cannot remove last admin from space

---

## Search

### Unified Search

Search across conversations, messages, and spaces.

```http
POST /search/query
```

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "query": "FDA approval process",
  "space_id": "spc_xyz789",
  "limit": 20
}
```

**Parameters:**
- `query` (required): Search query
- `space_id` (optional): Filter by space
- `limit` (optional, default 20, max 100): Result count

**Response:** `200 OK`

```json
{
  "results": {
    "conversations": [
      {
        "id": "conv_def456",
        "type": "conversation",
        "title": "FDA 510(k) Process",
        "snippet": "Discussion about FDA approval...",
        "relevance_score": 0.95,
        "message_count": 15,
        "starred": true,
        "last_updated": "2024-10-26T09:00:00Z"
      }
    ],
    "messages": [
      {
        "id": "msg_jkl012",
        "type": "message",
        "conversation_id": "conv_def456",
        "conversation_title": "FDA 510(k) Process",
        "role": "assistant",
        "snippet": "...the FDA 510(k) premarket notification process requires...",
        "relevance_score": 0.92,
        "timestamp": "2024-10-26T09:00:15Z"
      }
    ],
    "spaces": [
      {
        "id": "spc_xyz789",
        "type": "space",
        "name": "Medical Research",
        "description": "Space for medical device research",
        "relevance_score": 0.88,
        "conversation_count": 15
      }
    ]
  },
  "total": 3,
  "query": "FDA approval process"
}
```

---

### Quick Search

Optimized search for command palette (15 results max, fast).

```http
GET /search/quick
```

**Headers:**

```
Authorization: Bearer <token>
```

**Query Parameters:**

- `q` (required): Search query
- `space_id` (optional): Filter by space

**Response:** `200 OK`

```json
{
  "results": {
    "conversations": [...],
    "messages": [...],
    "spaces": [...]
  },
  "total": 15
}
```

**Example:**

```bash
curl -X GET "http://localhost:8000/search/quick?q=FDA%20approval" \
  -H "Authorization: Bearer <your-token>"
```

---

### Search Conversations Only

```http
POST /search/conversations
```

**Request Body:**

```json
{
  "query": "FDA approval",
  "space_id": "spc_xyz789",
  "limit": 50
}
```

---

### Search Messages Only

```http
POST /search/messages
```

**Request Body:**

```json
{
  "query": "premarket notification",
  "conversation_id": "conv_def456",
  "limit": 50
}
```

---

### Search Spaces Only

```http
POST /search/spaces
```

**Request Body:**

```json
{
  "query": "medical",
  "limit": 20
}
```

---

## Knowledge Graphs

### Get Message Reasoning Graph

Retrieve the knowledge graph for a specific message.

```http
POST /graph/message
```

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "message_id": "msg_jkl012",
  "max_depth": 3
}
```

**Response:** `200 OK`

```json
{
  "nodes": [
    {
      "id": "node_001",
      "type": "concept",
      "content": "FDA 510(k) Process",
      "confidence": 0.95,
      "metadata": {
        "source": "FDA Guidance Document"
      }
    },
    {
      "id": "node_002",
      "type": "concept",
      "content": "Premarket Notification",
      "confidence": 0.90,
      "metadata": {}
    }
  ],
  "edges": [
    {
      "from": "node_001",
      "to": "node_002",
      "type": "requires",
      "weight": 0.85
    }
  ],
  "reasoning_steps": [
    {
      "step": 1,
      "description": "Identified query as FDA-related",
      "node_ids": ["node_001"]
    },
    {
      "step": 2,
      "description": "Retrieved 510(k) process documentation",
      "node_ids": ["node_001", "node_002"]
    }
  ]
}
```

---

### Get Concept Subgraph

Retrieve subgraph around a specific concept.

```http
POST /graph/concept
```

**Request Body:**

```json
{
  "concept_id": "node_001",
  "domain_storage": "medical-protocols",
  "max_depth": 2,
  "max_nodes": 50
}
```

**Response:** Same structure as message graph

---

### Get Reasoning Paths for Query

Retrieve possible reasoning paths without executing full query.

```http
POST /graph/query
```

**Request Body:**

```json
{
  "query": "What is the FDA 510(k) process?",
  "domain_storage": "medical-protocols",
  "max_paths": 5
}
```

**Response:** `200 OK`

```json
{
  "paths": [
    {
      "confidence": 0.95,
      "steps": [
        {
          "concept_id": "node_001",
          "content": "FDA 510(k) Process",
          "confidence": 0.95
        },
        {
          "concept_id": "node_002",
          "content": "Premarket Notification",
          "confidence": 0.90
        }
      ]
    }
  ],
  "query": "What is the FDA 510(k) process?"
}
```

---

### Get Graph Statistics

Retrieve statistics about a domain storage graph.

```http
GET /graph/statistics/{domain_storage}
```

**Response:** `200 OK`

```json
{
  "domain_storage": "medical-protocols",
  "total_concepts": 150000,
  "total_associations": 450000,
  "avg_confidence": 0.87,
  "concept_types": {
    "fact": 50000,
    "inference": 75000,
    "question": 25000
  }
}
```

---

### Graph Health Check

```http
GET /graph/health
```

**Response:** `200 OK`

```json
{
  "status": "healthy",
  "service": "graph",
  "timestamp": "2024-10-26T10:00:00Z"
}
```

---

## Error Handling

### Error Response Format

All errors follow this structure:

```json
{
  "detail": {
    "error": "error_code",
    "message": "Human-readable error message",
    "field": "problematic_field (if applicable)"
  }
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH, DELETE |
| 201 | Created | Successful POST (resource created) |
| 400 | Bad Request | Validation error, malformed request |
| 401 | Unauthorized | Missing or invalid auth token |
| 403 | Forbidden | Authenticated but no permission |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists (e.g., duplicate email) |
| 422 | Unprocessable Entity | Pydantic validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Common Errors

**Authentication Error:**

```json
{
  "detail": {
    "error": "invalid_token",
    "message": "Token is invalid or expired"
  }
}
```

**Validation Error:**

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

**Permission Error:**

```json
{
  "detail": {
    "error": "insufficient_permissions",
    "message": "Admin role required to perform this action"
  }
}
```

---

## Rate Limiting

### Default Limits

- **Anonymous**: 10 requests/minute
- **Authenticated**: 100 requests/minute
- **Search**: 20 requests/minute (per user)
- **Streaming**: 5 concurrent connections

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1698328800
```

### Rate Limit Exceeded

```json
{
  "detail": {
    "error": "rate_limit_exceeded",
    "message": "Too many requests. Retry after 60 seconds.",
    "retry_after": 60
  }
}
```

---

## SDK Examples

### Python

```python
import requests

class SutraClient:
    def __init__(self, base_url="http://localhost:8000", token=None):
        self.base_url = base_url
        self.token = token
        
    def login(self, email, password):
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]
        return self.token
        
    def create_conversation(self, space_id, domain_storage):
        response = requests.post(
            f"{self.base_url}/conversations/create",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"space_id": space_id, "domain_storage": domain_storage}
        )
        response.raise_for_status()
        return response.json()
        
    def send_message(self, conversation_id, content):
        response = requests.post(
            f"{self.base_url}/conversations/{conversation_id}/message",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"content": content}
        )
        response.raise_for_status()
        return response.json()

# Usage
client = SutraClient()
client.login("user@example.com", "password123")
conv = client.create_conversation("spc_xyz789", "medical-protocols")
result = client.send_message(conv["id"], "What is the FDA 510(k) process?")
print(result["assistant_message"]["content"])
```

### JavaScript/TypeScript

```typescript
class SutraClient {
  private baseUrl: string;
  private token: string | null = null;
  
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }
  
  async login(email: string, password: string): Promise<string> {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    this.token = data.access_token;
    return this.token;
  }
  
  async createConversation(spaceId: string, domainStorage: string) {
    const response = await fetch(`${this.baseUrl}/conversations/create`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ space_id: spaceId, domain_storage: domainStorage })
    });
    return response.json();
  }
  
  async sendMessage(conversationId: string, content: string) {
    const response = await fetch(`${this.baseUrl}/conversations/${conversationId}/message`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content })
    });
    return response.json();
  }
  
  async *sendMessageStream(conversationId: string, content: string) {
    const response = await fetch(`${this.baseUrl}/conversations/${conversationId}/message/stream`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content })
    });
    
    const reader = response.body!.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('event: ')) {
          const eventType = line.substring(7);
        } else if (line.startsWith('data: ')) {
          const data = JSON.parse(line.substring(6));
          yield { eventType, data };
        }
      }
    }
  }
}

// Usage
const client = new SutraClient();
await client.login('user@example.com', 'password123');
const conv = await client.createConversation('spc_xyz789', 'medical-protocols');

// Streaming
for await (const { eventType, data } of client.sendMessageStream(conv.id, 'What is FDA 510(k)?')) {
  console.log(eventType, data);
}
```

---

## Changelog

### v2.0.0 (2024-10-26)

- Initial API release
- Authentication endpoints
- Conversation management
- Spaces and RBAC
- Semantic search
- Knowledge graph visualization
- SSE streaming responses

---

## Support

- **Documentation**: [User Guide](./USER_GUIDE.md)
- **FAQ**: [FAQ.md](./FAQ.md)
- **Issues**: GitHub Issues
- **Interactive Docs**: http://localhost:8000/docs

---

**Last Updated**: October 26, 2025  
**API Version**: 2.0.0
