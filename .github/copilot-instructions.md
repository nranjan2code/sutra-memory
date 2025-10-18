# Sutra AI - AI Agent Instructions

## Overview
Sutra AI is a **gRPC-first microservices architecture** for graph-based explainable AI. The system centers around a **Rust storage server** that handles all graph operations, with thin Python services acting as gRPC proxies.

## Critical Architecture Principles

### 1. Single Source of Truth: Storage Server (Rust)
- **ALL** graph operations, path finding, and vector search happen in `sutra-storage-server` (Rust)
- Python services (`sutra-api`, `sutra-hybrid`) are **thin gRPC clients** - they NEVER perform graph operations locally
- Storage uses memory-mapped files with lock-free writes (57K writes/sec, <0.01ms reads)
- **Key file**: `packages/sutra-storage/src/concurrent_memory.rs` - dual-plane architecture (write log + immutable read snapshots)

### 2. gRPC Communication Flow
```
Client → sutra-api (FastAPI) → [gRPC] → storage-server:50051
                                            ↓
                                    Graph ops + Vector search
```

When editing Python services:
- Use `StorageClient` from `packages/sutra-storage-client/` for ALL storage operations
- NEVER import `sutra-core` reasoning engine directly in API services
- API endpoints should be thin proxies: validate request → gRPC call → return response

### 3. Package Dependencies (Critical)
```
sutra-storage (Rust)           # 24MB - Core engine
  ↑ gRPC
sutra-storage-client (Python)  # gRPC client
  ↑
sutra-core (Python)            # Graph reasoning logic (ONLY used by demos/CLI)
  ↑
sutra-hybrid (Python)          # Embeddings + orchestration
  ↑
sutra-api (Python)             # REST API (should NOT depend on sutra-core/hybrid)
```

**Common mistake**: Adding `sutra-hybrid` or `sutra-core` to `sutra-api/setup.py`. DON'T. This bloats images (612MB → 60MB fixed by removing these).

## Development Workflows

### Starting the Full Stack
```bash
# Development (all services)
npm run dev              # Starts API (8000) + Client (3000)
# OR
docker compose up -d     # Full microservices stack

# Individual services
cd packages/sutra-api && python -m sutra_api.main       # API only
cd packages/sutra-client && npm run dev                  # Client only
```

### Building Docker Images
```bash
# Build all images (correct dependency order)
./build-images.sh

# Individual builds (MUST use monorepo root for Python packages)
docker build -t sutra-api:latest -f packages/sutra-api/Dockerfile .  # Note: "." not "./packages"
```

**Why?** Python packages have inter-dependencies. Build context must include all of `packages/`.

### Testing
```bash
# Core reasoning tests
make test-core

# End-to-end workflow (bypasses API)
python test_direct_workflow.py

# API integration tests
cd packages/sutra-api && pytest
cd packages/sutra-hybrid && pytest
```

**Test pattern**: Use fixtures in `tests/conftest.py` for shared `StorageClient` setup.

### Rust Storage Development
```bash
cd packages/sutra-storage

# Build & test
cargo build --release
cargo test

# Build Python bindings (PyO3)
maturin develop --release

# Run gRPC server standalone
cargo run --bin storage-server -- --port 50051 --storage-path ./knowledge
```

**Key files**:
- `src/concurrent_memory.rs` - Core storage with lock-free writes
- `src/python.rs` - PyO3 bindings
- `proto/storage.proto` - gRPC API definition

## Project-Specific Conventions

### Error Handling
- Use `SutraError` base class (see `packages/sutra-core/sutra_core/exceptions.py`)
- gRPC errors map to HTTP status codes in API layer
- Always log errors with `logger.error()` before raising

### Configuration Pattern
```python
# Preferred: Builder pattern
from sutra_core.config import ReasoningEngineConfig
config = ReasoningEngineConfig.builder()
    .with_caching(max_size=500)
    .with_semantic_embeddings(enabled=True)
    .build()
engine = ReasoningEngine.from_config(config)

# Avoid: Direct instantiation with many args
```

### Storage Client Usage
```python
# Correct: Use injected client
from sutra_storage_client import StorageClient

client = StorageClient("storage-server:50051")
sequence = client.learn_concept(
    concept_id="python_001",
    content="Python is a language",
    embedding=None,  # Optional
    strength=1.0
)

# Incorrect: Don't instantiate ConcurrentStorage directly
# from sutra_storage import ConcurrentStorage  # ❌ Only for legacy code
```

### API Endpoint Pattern
```python
# sutra_api/endpoints/learn.py
@router.post("/learn")
async def learn(
    request: LearnRequest,
    client: StorageClient = Depends(get_storage_client)  # Dependency injection
) -> LearnResponse:
    """Learn endpoint - thin gRPC proxy."""
    try:
        seq = client.learn_concept(
            concept_id=request.id,
            content=request.content,
            strength=request.strength
        )
        return LearnResponse(concept_id=request.id, sequence=seq)
    except grpc.RpcError as e:
        raise HTTPException(status_code=503, detail=f"Storage error: {e}")
```

## Key Files & Their Purposes

### Storage Layer
- `packages/sutra-storage/src/concurrent_memory.rs` - Lock-free storage with dual-plane architecture
- `packages/sutra-storage/proto/storage.proto` - gRPC contract (source of truth)
- `packages/sutra-storage-client/sutra_storage_client/client.py` - Python gRPC client

### Reasoning Layer
- `packages/sutra-core/sutra_core/reasoning/engine.py` - Main reasoning orchestrator
- `packages/sutra-core/sutra_core/reasoning/paths.py` - PathFinder (BFS, best-first search)
- `packages/sutra-core/sutra_core/reasoning/mppa.py` - Multi-Path Plan Aggregation (consensus)

### API Layer
- `packages/sutra-api/sutra_api/main.py` - FastAPI app (thin proxy)
- `packages/sutra-api/sutra_api/dependencies.py` - DI for StorageClient
- `packages/sutra-hybrid/sutra_hybrid/api.py` - OpenAI-compatible API

### Frontend
- `packages/sutra-client/src/` - React SPA (Vite + TypeScript)
- `packages/sutra-control/` - Admin dashboard (React + FastAPI backend)

## Common Pitfalls

### 1. Bloated Docker Images
**Problem**: Adding unnecessary dependencies to `setup.py`
```python
# ❌ BAD - sutra-api should NOT depend on these
install_requires=[
    "sutra-core>=1.0.0",      # ❌ Has reasoning engine we don't need
    "sutra-hybrid>=1.0.0",    # ❌ Has ML libs we don't need
]

# ✅ GOOD - Only what's needed for gRPC proxy
install_requires=[
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.0.0",
    "sutra-storage-client",   # Only this!
]
```

### 2. Direct Storage Access
**Problem**: Bypassing gRPC and using in-process storage
```python
# ❌ BAD - Creates separate instance, no shared state
from sutra_storage import ConcurrentStorage
storage = ConcurrentStorage("./knowledge")

# ✅ GOOD - Uses centralized server via gRPC
from sutra_storage_client import StorageClient
client = StorageClient("storage-server:50051")
```

### 3. Incorrect Build Context
```bash
# ❌ BAD - Missing sutra-core dependency
docker build -t sutra-api -f packages/sutra-api/Dockerfile packages/sutra-api/

# ✅ GOOD - Monorepo root includes all packages
docker build -t sutra-api -f packages/sutra-api/Dockerfile .
```

### 4. Missing Environment Variables
Required for services:
```bash
# API
SUTRA_STORAGE_SERVER=storage-server:50051  # gRPC server address
SUTRA_STORAGE_MODE=server                  # Use gRPC (not in-process)

# Storage Server
STORAGE_PATH=/data                         # Persistent storage location
STORAGE_PORT=50051                         # gRPC port
```

## Integration Points

### Storage Server ↔ All Services
- **Protocol**: gRPC (defined in `proto/storage.proto`)
- **Port**: 50051
- **Operations**: learn_concept, learn_association, query_concept, find_paths, vector_search

### API ↔ Client
- **Protocol**: REST (OpenAPI spec at `/docs`)
- **Port**: 8000 (API), 3000 (Client dev), 8080 (Client prod)
- **Auth**: None yet (TODO: add auth middleware)

### Hybrid ↔ Embeddings
- **Embeddings**: Generated using Gemma models
- **Storage**: Embeddings sent to storage server, HNSW index built there

## Performance Targets

When optimizing, keep these benchmarks in mind:
- **Storage write**: 0.02ms per concept (57K/sec)
- **Storage read**: <0.01ms (memory-mapped)
- **Path finding**: ~1ms for 3-hop BFS
- **API latency**: <50ms end-to-end (including gRPC)
- **Image size**: API <150MB, Hybrid <400MB, Storage 24MB

## Documentation Structure

- `ARCHITECTURE.md` - System overview, data flow
- `GRPC_ARCHITECTURE.md` - gRPC migration guide, thin proxy pattern
- `DEPLOYMENT_PLAN.md` - K8s deployment, resource allocation
- `packages/sutra-storage/ARCHITECTURE.md` - Rust storage internals
- `packages/*/README.md` - Package-specific docs

## When Making Changes

### Adding an API Endpoint
1. Define Pydantic models in `sutra_api/models.py`
2. Add endpoint in `sutra_api/endpoints/`
3. Register router in `main.py`
4. Call `StorageClient` methods, NOT local reasoning
5. Add integration test in `tests/`

### Modifying Storage Schema
1. Update `proto/storage.proto`
2. Regenerate Python bindings: `cd packages/sutra-storage && ./build_protos.sh`
3. Update `StorageClient` in `sutra-storage-client/`
4. Update Rust implementation in `src/`
5. Update API models to reflect schema changes

### Adding a Package
1. Create in `packages/<name>/`
2. Add `pyproject.toml` or `setup.py`
3. Update root `pyproject.toml` workspace
4. Add to `build-images.sh` if needs Docker image
5. Update `docker-compose.yml` if it's a service

---

**Quick Reference Commands**:
- `npm run dev` - Start API + Client
- `docker compose up -d` - Full stack
- `./build-images.sh` - Build all Docker images
- `make test-core` - Run core tests
- `python test_direct_workflow.py` - E2E test
