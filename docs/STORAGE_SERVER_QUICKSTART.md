# Storage Server Quick Start

**Status:** ✅ Current Architecture (v3.0.1)  
**Last Updated:** November 9, 2025

## TL;DR

✅ All services connect to a standalone storage server over **TCP Binary Protocol**  
✅ No embedded/in-process storage in API/Hybrid  
✅ Python clients use `TcpStorageAdapter` (included in sutra-core)

## Architecture

**Production (v3.0.1+):**
```
Process 1 (API) ──┐
Process 2 (Hybrid)┼─→ Storage Server (TCP :50051) → storage.dat
Process 3 (Client)┘
```

**Note:** Embedded mode has been removed in v3.0.1. All deployments use the storage server.

## Quick Start

### 1) Build storage-server

```bash
cd packages/sutra-storage
cargo build --release
```

### 2) Python Client Usage

```python
# Production code (automatic via environment)
from sutra_core.storage import TcpStorageAdapter

# Initialize (reads SUTRA_STORAGE_SERVER env var)
storage = TcpStorageAdapter(
    server_address="storage-server:50051",
    vector_dimension=768,
)
```

**Note:** As of v3.0.1, `RustStorageAdapter` and `connection.py` have been removed. Only `TcpStorageAdapter` is available.

### 3) Build & Test

```bash
# Build server
cd packages/sutra-storage
cargo build --release

# Start server
./target/release/storage-server --storage ./knowledge

# Start services (connect automatically via env)
export SUTRA_STORAGE_SERVER=localhost:50051
uvicorn sutra_api.main:app --host 0.0.0.0 --port 8000
uvicorn sutra_hybrid.api.app:app --host 0.0.0.0 --port 8001
```

## Usage Examples

### Development
```bash
# Run via docker-compose (recommended)
DEPLOY=local VERSION=v2 bash deploy-optimized.sh
```

### Manual run
```bash
# Terminal 1: Start storage server
./packages/sutra-storage/bin/storage-server \
  --host 0.0.0.0 \
  --port 50051 \
  --storage /var/lib/sutra/knowledge

# Terminal 2: Start API (connects automatically)
# no SUTRA_STORAGE_MODE; gRPC is the only mode now
export SUTRA_STORAGE_SERVER=localhost:50051
cd packages/sutra-api
python -m sutra_api.main

# Terminal 3: Start another service (shares same storage!)
export SUTRA_STORAGE_MODE=server
python demo_mass_learning.py
```

### Docker Compose
```yaml
version: '3.8'
services:
  storage:
    build: ./packages/sutra-storage
    ports:
      - "50051:50051"
    volumes:
      - ./knowledge:/data
    command: storage-server --host 0.0.0.0 --storage /data

  api:
    build: ./packages/sutra-api
    ports:
      - "8000:8000"
    environment:
      - SUTRA_STORAGE_MODE=server
      - SUTRA_STORAGE_SERVER=storage:50051
    depends_on:
      - storage
```

## Verification Checklist

### ✅ Health checks
```bash
curl -f http://localhost:8000/health
curl -f http://localhost:8001/ping
```

### ✅ Stats
```bash
# Start server first
./bin/storage-server &

grpcurl -plaintext localhost:50051 list
```

### ✅ Multi-Client Shared State (via gRPC)
```bash
# Terminal 1
export SUTRA_STORAGE_SERVER=localhost:50051
python -c "
from sutra_core import ReasoningEngine
e = ReasoningEngine()
e.learn('Redis is an in-memory database')
"

# Terminal 2
export SUTRA_STORAGE_SERVER=localhost:50051
python -c "
from sutra_core import ReasoningEngine
e = ReasoningEngine()
result = e.query('What is Redis?')
print(result)
"
# Expected: Should return result about Redis from Terminal 1
```

## Troubleshooting

### Server won't start
```bash
# Check if port is in use
lsof -i :50051

# Check storage permissions
ls -la ./knowledge/

# Run with debug logging
RUST_LOG=debug ./bin/storage-server
```

### Client can't connect
```bash
# Verify server is running
nc -zv localhost 50051

# Check environment
echo $SUTRA_STORAGE_MODE
echo $SUTRA_STORAGE_SERVER

# Test with grpcurl
grpcurl -plaintext localhost:50051 list
```

### Still using embedded mode
```bash
# Make sure env vars are set
export SUTRA_STORAGE_MODE=server

# Verify in Python
python -c "
import os
print('Mode:', os.getenv('SUTRA_STORAGE_MODE'))
from sutra_core.storage.connection import get_storage_backend
backend = get_storage_backend('./knowledge')
print('Backend:', type(backend))
# Expected: <class 'sutra_storage_client.client.StorageClient'>
"
```

## Next Steps

1. **Phase 1 (Now):** Implement changes, build, test locally
2. **Phase 2 (Week 1):** Deploy to dev environment, collect metrics
3. **Phase 3 (Week 2):** Parallel testing (embedded + server)
4. **Phase 4 (Month 1):** Production deployment with monitoring
5. **Phase 5 (Month 2+):** Add HA, replication, distributed features

## Key Files Created

```
docs/
  STORAGE_SERVER.md              # Complete guide
  STORAGE_SERVER_COMPATIBILITY.md # Package analysis
  STORAGE_SERVER_QUICKSTART.md   # This file

packages/sutra-storage/
  proto/storage.proto            # gRPC service definition
  src/server.rs                  # Server implementation
  bin/storage-server             # Startup script

packages/sutra-storage-client/
  sutra_storage_client/
    client.py                    # Python gRPC client

packages/sutra-core/
  sutra_core/storage/
    connection.py                # Mode selector
```

## Performance Expectations

| Operation | Embedded | Server (Local) | Server (Remote) |
|-----------|----------|----------------|-----------------|
| Write | 0.02ms | ~0.1ms | ~1ms |
| Read | <0.01ms | ~0.05ms | ~1ms |
| Path Finding | ~1ms | ~1.1ms | ~2ms |

**Local server mode is ~5x slower but still excellent performance!**

## Documentation

- **Full Guide:** `docs/STORAGE_SERVER.md`
- **Compatibility:** `docs/STORAGE_SERVER_COMPATIBILITY.md`
- **This Quick Start:** `docs/STORAGE_SERVER_QUICKSTART.md`

## Questions?

- Architecture questions → See `STORAGE_SERVER.md`
- Package compatibility → See `STORAGE_SERVER_COMPATIBILITY.md`
- Implementation help → See this file
- Issues → Check Troubleshooting section above
