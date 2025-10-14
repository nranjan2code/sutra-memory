# API Endpoints Reference

Base URL: `http://localhost:8000`

## Health & Status

### GET /health

Health check endpoint.

**Response 200:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 3600.5,
  "concepts_loaded": 1234
}
```

### GET /stats

Get system statistics.

**Response 200:**
```json
{
  "total_concepts": 1234,
  "total_associations": 5678,
  "total_embeddings": 1234,
  "embedding_provider": "tfidf-100d",
  "embedding_dimension": 100,
  "average_strength": 2.45,
  "memory_usage_mb": null
}
```

### GET /

Root endpoint with API information.

**Response 200:**
```json
{
  "name": "Sutra AI API",
  "version": "1.0.0",
  "description": "REST API for Sutra AI graph reasoning system",
  "docs_url": "/docs",
  "openapi_url": "/openapi.json"
}
```

## Learning Endpoints

### POST /learn

Learn single knowledge item.

**Request Body:**
```json
{
  "content": "Python is a high-level programming language",
  "source": "documentation",
  "metadata": {
    "category": "programming",
    "difficulty": "beginner"
  }
}
```

**Response 201:**
```json
{
  "concept_id": "8e1ea4ca-d3f2-4b7e-9c8f-1a2b3c4d5e6f",
  "message": "Knowledge learned successfully",
  "concepts_created": 3,
  "associations_created": 2
}
```

**Fields:**
- `content` (required): Text content to learn
- `source` (optional): Source identifier
- `metadata` (optional): Key-value metadata

### POST /learn/batch

Learn multiple knowledge items.

**Request Body:**
```json
{
  "items": [
    {
      "content": "JavaScript runs in web browsers",
      "source": "web_docs"
    },
    {
      "content": "SQL queries databases",
      "source": "database_docs"
    }
  ]
}
```

**Response 201:**
```json
{
  "concept_ids": [
    "8e1ea4ca-d3f2-4b7e-9c8f-1a2b3c4d5e6f",
    "9f2fb5db-e4g3-5c8g-0d9g-2b3c4d5e6f7g"
  ],
  "total_concepts": 6,
  "total_associations": 8,
  "message": "Successfully learned 2 items"
}
```

## Reasoning Endpoints

### POST /reason

Perform reasoning query using graph traversal.

**Request Body:**
```json
{
  "query": "How do neural networks learn?",
  "max_steps": 3,
  "num_paths": 3,
  "threshold": 0.3
}
```

**Response 200:**
```json
{
  "query": "How do neural networks learn?",
  "answer": "Neural networks learn patterns from training data",
  "confidence": 0.85,
  "paths": [
    {
      "concepts": [
        "8e1ea4ca-d3f2-4b7e-9c8f-1a2b3c4d5e6f"
      ],
      "confidence": 0.85,
      "explanation": "Found: Neural networks learn patterns from..."
    }
  ],
  "concepts_accessed": 5
}
```

**Parameters:**
- `query` (required): Question or reasoning query
- `max_steps` (optional): Maximum traversal depth (1-10, default: 3)
- `num_paths` (optional): Number of paths to explore (1-10, default: 3)
- `threshold` (optional): Minimum confidence (0.0-1.0, default: 0.3)

### POST /semantic-search

Search for similar concepts using embeddings.

**Request Body:**
```json
{
  "query": "machine learning algorithms",
  "top_k": 5,
  "threshold": 0.5
}
```

**Response 200:**
```json
{
  "query": "machine learning algorithms",
  "results": [
    {
      "concept_id": "8e1ea4ca-d3f2-4b7e-9c8f-1a2b3c4d5e6f",
      "content": "Neural networks learn patterns from data",
      "similarity": 0.87,
      "strength": 2.34
    },
    {
      "concept_id": "9f2fb5db-e4g3-5c8g-0d9g-2b3c4d5e6f7g",
      "content": "Decision trees classify data",
      "similarity": 0.76,
      "strength": 1.85
    }
  ],
  "total_found": 2
}
```

**Parameters:**
- `query` (required): Search query
- `top_k` (optional): Number of results (1-100, default: 5)
- `threshold` (optional): Minimum similarity (0.0-1.0, default: 0.5)

### GET /concepts/{concept_id}

Get detailed information about a concept.

**Response 200:**
```json
{
  "id": "8e1ea4ca-d3f2-4b7e-9c8f-1a2b3c4d5e6f",
  "content": "Python is a programming language",
  "strength": 2.34,
  "access_count": 15,
  "created_at": "2025-10-14T12:00:00Z",
  "source": "documentation",
  "associations": [
    "9f2fb5db-e4g3-5c8g-0d9g-2b3c4d5e6f7g",
    "af3gc6ec-f5h4-6d9h-1e0h-3c4d5e6f7g8h"
  ]
}
```

**Response 404:**
```json
{
  "detail": "Concept 8e1ea4ca-d3f2-4b7e-9c8f-1a2b3c4d5e6f not found"
}
```

## Management Endpoints

### POST /save

Save current knowledge to disk.

**Response 200:**
```json
{
  "message": "Knowledge saved successfully"
}
```

**Response 500:**
```json
{
  "detail": "Failed to save knowledge: {error_message}"
}
```

### POST /load

Reload knowledge from disk.

**Response 200:**
```json
{
  "message": "Knowledge loaded successfully",
  "concepts_loaded": 1234
}
```

**Response 500:**
```json
{
  "detail": "Failed to load knowledge: {error_message}"
}
```

### DELETE /reset

Reset system and clear all knowledge.

**⚠️ Warning:** This permanently deletes all concepts and associations!

**Response 200:**
```json
{
  "message": "System reset successfully",
  "concepts": 0
}
```

## Error Responses

### 400 Bad Request

Invalid request data or validation error.

```json
{
  "error": "ValidationError",
  "message": "Invalid request parameters",
  "detail": "field 'content' is required"
}
```

### 404 Not Found

Resource not found.

```json
{
  "detail": "Concept {id} not found"
}
```

### 500 Internal Server Error

Unexpected server error.

```json
{
  "error": "InternalServerError",
  "message": "An unexpected error occurred",
  "detail": null
}
```

## Rate Limiting

Default limits (configurable via environment variables):

- `/learn`: 60 requests/minute
- `/reason`: 30 requests/minute
- `/semantic-search`: 100 requests/minute

## Authentication

Currently no authentication required. For production:

1. Add API key authentication
2. Implement OAuth2/JWT
3. Use reverse proxy (nginx) for rate limiting
4. Enable HTTPS

## CORS

Default configuration allows all origins. Configure via:

```bash
export SUTRA_ALLOW_ORIGINS='["https://example.com"]'
```

## Pagination

Not currently implemented. All results returned in single response.
For large result sets, use `top_k` parameter to limit results.

## Webhooks

Not currently implemented. Planned for future releases.

## WebSocket Support

Not currently implemented. All endpoints are REST/HTTP.

## Examples

### Python Client

```python
import requests

BASE_URL = "http://localhost:8000"

# Learn
response = requests.post(
    f"{BASE_URL}/learn",
    json={"content": "Python is easy to learn"}
)
concept_id = response.json()["concept_id"]

# Search
response = requests.post(
    f"{BASE_URL}/semantic-search",
    json={"query": "programming", "top_k": 3}
)
results = response.json()["results"]

# Get concept
response = requests.get(
    f"{BASE_URL}/concepts/{concept_id}"
)
concept = response.json()
```

### cURL Examples

```bash
# Learn
curl -X POST http://localhost:8000/learn \
  -H "Content-Type: application/json" \
  -d '{"content": "Python is easy"}'

# Search
curl -X POST http://localhost:8000/semantic-search \
  -H "Content-Type: application/json" \
  -d '{"query": "programming", "top_k": 3}'

# Stats
curl http://localhost:8000/stats

# Save
curl -X POST http://localhost:8000/save
```

### JavaScript (Fetch)

```javascript
// Learn
const response = await fetch('http://localhost:8000/learn', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    content: 'Python is easy to learn'
  })
});
const data = await response.json();

// Search
const searchResp = await fetch('http://localhost:8000/semantic-search', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    query: 'programming',
    top_k: 3
  })
});
const results = await searchResp.json();
```

## OpenAPI Specification

Interactive documentation available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Next Steps

- [Request/Response Models](models.md)
- [Error Handling](errors.md)
- [API Usage Tutorial](../tutorials/api-usage.md)
