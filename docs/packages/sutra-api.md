# sutra-api

FastAPI-based REST service exposing learning, reasoning, and management endpoints.

## Structure

```
sutra_api/
├── __init__.py
├── main.py          # FastAPI app and endpoints
├── models.py        # Pydantic request/response schemas
├── config.py        # Settings (env-driven)
└── dependencies.py  # DI for HybridAI instance
```

## Running

### Development

```bash
python -m sutra_api.main
# or
uvicorn sutra_api.main:app --reload --port 8000
```

### Production

```bash
uvicorn sutra_api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Configuration

Environment variables (prefix `SUTRA_`):

- `HOST` (default `0.0.0.0`)
- `PORT` (default `8000`)
- `STORAGE_PATH` (default `./api_knowledge`)
- `USE_SEMANTIC_EMBEDDINGS` (default `true`)
- `LOG_LEVEL` (default `INFO`)
- `ALLOW_ORIGINS` (JSON array, default `[*]`)

Example:

```bash
export SUTRA_HOST=0.0.0.0
export SUTRA_PORT=8000
export SUTRA_STORAGE_PATH=./api_knowledge
export SUTRA_USE_SEMANTIC_EMBEDDINGS=true
export SUTRA_LOG_LEVEL=INFO
```

## Endpoints

- `GET /health` — Service status
- `GET /stats` — System metrics
- `POST /learn` — Learn a single item
- `POST /learn/batch` — Learn multiple items
- `POST /reason` — Reasoning query
- `POST /semantic-search` — Embedding-based search
- `GET /concepts/{id}` — Concept detail
- `POST /save` — Persist knowledge
- `POST /load` — Reload knowledge
- `DELETE /reset` — Reset system

See: `docs/api/endpoints.md` for request/response examples.

## Error Handling

- 4xx: Validation and domain errors (SutraError mapped to 400)
- 5xx: Unhandled exceptions (with minimal detail unless DEBUG)

## CORS

Configured via `ALLOW_ORIGINS`, `ALLOW_METHODS`, `ALLOW_HEADERS`, `ALLOW_CREDENTIALS`.

## OpenAPI

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- Spec: `/openapi.json`

## Testing (to add)

Use `httpx.AsyncClient` with `pytest-asyncio` to test endpoints without a running server.
