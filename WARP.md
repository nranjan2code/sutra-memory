# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Sutra AI is an explainable graph-based AI system that learns in real-time without retraining. It provides complete reasoning paths for every decision, making it a transparent alternative to black-box LLMs.

**Core Value Proposition:**
- Shows reasoning for every answer
- Learns incrementally from new information  
- Provides audit trails for compliance
- Works without GPUs or massive compute
- 100% explainable reasoning paths

## Architecture

gRPC-first microservices architecture with containerized deployment. All services communicate via gRPC with a secure React-based control center for monitoring.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            Docker Network (sutra-network)                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────────┐  │
│  │  sutra-control  │    │   sutra-client  │    │      sutra-markdown-web     │  │
│  │  (React + Fast  │    │   (Streamlit)   │    │       (Markdown API)       │  │
│  │   API Gateway)  │    │    UI Client    │    │        UI Client           │  │
│  │   Port: 9000    │    │   Port: 8080    │    │       Port: 8002           │  │
│  └─────────┬───────┘    └─────────┬───────┘    └─────────────┬───────────────┘  │
│            │                      │                          │                   │
│            └──────────────────────┼──────────────────────────┘                   │
│                                   │                                              │
│  ┌─────────────────┐              │gRPC       ┌─────────────────────────────┐  │
│  │   sutra-api     │◀─────────────┼──────────▶│      storage-server         │  │
│  │   (FastAPI)     │              │           │       (Rust gRPC)           │  │
│  │   Port: 8000    │              │           │      Port: 50051            │  │
│  └─────────┬───────┘              │           └──────────────┬──────────────┘  │
│            │                      │                          │                   │
│            └──────────────────────┼──────────────────────────┘                   │
│                                   │                                              │
│  ┌─────────────────┐              │           ┌─────────────────────────────┐  │
│  │  sutra-hybrid   │◀─────────────┼──────────▶│        sutra-ollama         │  │
│  │ (Embeddings +   │              │           │     (Local LLM Server)      │  │
│  │ Orchestration)  │              │           │      Port: 11434            │  │
│  │   Port: 8001    │              │           └─────────────────────────────┘  │
│  └─────────────────┘              │                                              │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Key Architectural Principles:**
- All graph/vector ops run in storage-server; no in-process storage in API/Hybrid
- Rust storage provides zero-copy memory-mapped files and lock-free concurrency
- Optional semantic embeddings enhance reasoning but remain transparent
- Temporal log-structured storage for time-travel queries

### Package Structure

- **sutra-core**: Core graph reasoning engine with concepts, associations, and multi-path plan aggregation (MPPA)
- **sutra-storage**: Production-ready Rust storage with ConcurrentStorage (57K writes/sec, <0.01ms reads), single-file architecture, and lock-free concurrency  
- **sutra-hybrid**: Semantic embeddings integration (SutraAI class) that combines graph reasoning with optional similarity matching
- **sutra-api**: Production REST API with FastAPI, rate limiting, and comprehensive endpoints
- **sutra-control**: Modern React-based control center with secure FastAPI gateway for system monitoring and management
- **sutra-client**: Streamlit-based web interface for interactive AI queries and knowledge exploration
- **sutra-markdown-web**: Markdown API service for document processing and content management
- **sutra-cli**: Command-line interface (placeholder)

#### Sutra Grid (Distributed Infrastructure)
- **sutra-grid-master**: Rust-based orchestration service managing agents and storage nodes (port 7000)
- **sutra-grid-agent**: Rust-based agent with gRPC server for storage node lifecycle management (port 8001+)
- **sutra-grid-events**: Event emission library with 17 structured event types, async background worker
- **sutra-grid-cli**: Command-line tool for cluster management (`list-agents`, `status`, `spawn`, `stop`)

**Grid Status**: Production-Ready ✅  
- Master: 11 events emitted (agent lifecycle, node operations)
- Agent: 2 events emitted (node crash, restart)
- Reserved Storage: Port 50052 for Grid events
- Testing: End-to-end verified with `test-integration.sh`
- Documentation: See `docs/grid/architecture/GRID_ARCHITECTURE.md` for complete details

## Development Commands

### Environment Setup
```bash
# One-command setup (creates venv, installs packages)
make setup

# Manual setup (alternative)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e packages/sutra-core/
pip install -r requirements-dev.txt
```

### Testing
```bash
# Core package tests
make test-core

# Storage tests (Rust - includes WAL crash recovery tests)
cd packages/sutra-storage
cargo test
cargo test test_wal  # Specific WAL durability tests

# End-to-end demos
python demo_simple.py
python demo_end_to_end.py
python demo_mass_learning.py
python demo_wikipedia_learning.py

# Integration tests (root tests directory)
python -m pytest tests/ -v

# Verify storage performance
python verify_concurrent_storage.py

# Grid integration tests
cd packages/sutra-grid-master
./test-integration.sh  # Automated end-to-end (5 tests)

# Manual Grid testing (3 terminals required)
# Terminal 1: Reserved storage for events
cd packages/sutra-storage
./bootstrap-grid-events.sh

# Terminal 2: Grid Master
cd packages/sutra-grid-master
EVENT_STORAGE=http://localhost:50052 cargo run --release

# Terminal 3: Grid Agent
cd packages/sutra-grid-agent
EVENT_STORAGE=http://localhost:50052 cargo run --release

# Terminal 4: CLI commands
cd packages/sutra-grid-master
cargo build --release
./target/release/sutra-grid-cli --master http://localhost:7000 list-agents
./target/release/sutra-grid-cli status
./target/release/sutra-grid-cli spawn --agent agent-001 --port 50053 --storage-path /tmp/node1 --memory 512
```

### Code Quality
```bash
# Format code (black + isort)
make format

# Lint core package
make lint

# Full quality check
make check  # Runs format, lint, and test
```

### Deployment
```bash
# Full containerized stack (recommended)
docker compose up -d

# Development with local optimizations
DEPLOY=local VERSION=v2 bash deploy-optimized.sh

# Individual service development (requires storage server)
export SUTRA_STORAGE_SERVER=localhost:50051
uvicorn sutra_api.main:app --host 0.0.0.0 --port 8000

# Control center development (with Grid integration)
cd packages/sutra-control
npm install
python3 -m venv venv && source venv/bin/activate
pip install fastapi uvicorn pydantic grpcio
npm run build  # Build React app
# Start with Grid support:
SUTRA_GRID_MASTER=localhost:7000 python3 backend/main.py
```

### Build and Distribution
```bash
# Build all packages
make build

# Clean build artifacts
make clean
```

## Key Components

### ReasoningEngine (sutra-core)
The main AI interface that orchestrates reasoning components:
- Natural language query processing
- Real-time learning without retraining
- Query result caching for performance  
- Multi-path plan aggregation (MPPA) for consensus
- Complete audit trails

### PathFinder (sutra-core/reasoning)
Advanced graph traversal with multiple search strategies:
- **Best-first**: Confidence-optimized with heuristics
- **Breadth-first**: Shortest path exploration
- **Bidirectional**: Optimal path finding from both ends
- Confidence decay (0.85 default) for realistic propagation
- Cycle detection and path diversification

### MultiPathAggregator (MPPA) (sutra-core/reasoning)
Consensus-based reasoning that prevents single-path derailment:
- Path clustering by answer similarity (0.8 threshold)
- Majority voting with configurable thresholds
- Diversity bonus for varied reasoning approaches
- Robustness analysis with multiple metrics

### SutraAI (sutra-hybrid)
High-level interface combining graph reasoning with semantic embeddings:
- Optional semantic similarity matching
- Multi-strategy comparison (graph-only vs semantic-enhanced)
- Agreement scoring between strategies
- Knowledge persistence and audit trails

### ConcurrentStorage (sutra-storage - Rust)
Production-ready storage architecture with enterprise-grade durability:
- **57,412 writes/sec** (25,000× faster than JSON baseline)
- **<0.01ms read latency** (zero-copy memory-mapped files)
- **Zero data loss** with Write-Ahead Log (WAL) integration
- Lock-free write log with background reconciliation
- Single-file storage (`storage.dat`) with 512MB initial size
- Immutable read snapshots for burst-tolerant performance
- Path finding and graph traversal (BFS)
- Crash recovery with automatic WAL replay
- 100% test pass rate with verified accuracy

**Durability Guarantees:**
- Every write logged to WAL before in-memory structures
- Automatic crash recovery on startup
- WAL checkpoint on flush (safe truncation)
- RPO (Recovery Point Objective): 0 (zero data loss)
- Tested with comprehensive crash simulation tests

### Sutra Control Center (sutra-control)
Modern React-based monitoring and management interface with **Grid Management Integration**:
- **Frontend**: React 18 with Material Design 3, TypeScript, and Vite
- **Backend**: Secure FastAPI gateway that abstracts internal gRPC communication
- **Real-time Updates**: WebSocket connection for live system metrics
- **Grid Management**: Complete web UI for Grid agents and storage nodes ✅
- **Grid API**: REST endpoints for spawn/stop operations, status monitoring ✅
- **Features**: System health monitoring, performance metrics, knowledge graph visualization, Grid cluster management
- **Architecture**: Multi-stage Docker build combining React SPA with Python gateway
- **Access**: http://localhost:9000 (containerized deployment)
- **Grid UI**: Accessible at http://localhost:9000/grid with real-time monitoring
### Configuration

### Environment Variables
```bash
# Storage server address (all services)
export SUTRA_STORAGE_SERVER="storage-server:50051"

# Grid Master address (for Control Center integration)
export SUTRA_GRID_MASTER="localhost:7000"

# Service ports
export SUTRA_API_PORT="8000"
export SUTRA_HYBRID_PORT="8001"
export SUTRA_CLIENT_PORT="8080"
export SUTRA_CONTROL_PORT="9000"
export SUTRA_MARKDOWN_PORT="8002"
export SUTRA_OLLAMA_PORT="11434"
export SUTRA_STORAGE_PORT="50051"

# Rate limits
export SUTRA_RATE_LIMIT_LEARN="30"
export SUTRA_RATE_LIMIT_REASON="60"

# Production settings
export ENVIRONMENT="production"
export PYTHONPATH=/app:$PYTHONPATH
```

### Reasoning Configuration
- **Confidence decay**: 0.85 per reasoning step
- **Max reasoning depth**: 6 hops
- **Consensus threshold**: 50% agreement for multi-path aggregation
- **Path similarity threshold**: 0.7 maximum overlap for diversification

## Performance Characteristics

Based on production testing with ConcurrentStorage:
- **Learning**: **0.02ms per concept** (57,412 concepts/sec) — 25,000× faster than old system
- **Query**: **<0.01ms** with zero-copy memory-mapped access
- **Path finding**: ~1ms for 3-hop BFS traversal
- **Memory**: ~0.1KB per concept (excluding embeddings)
- **Storage**: Single `storage.dat` file (512MB for 1K concepts)
- **Vector search**: Product quantization for 4× compression (in development)
- **Accuracy**: 100% verified with comprehensive test suite

## Testing Strategy

The system has comprehensive testing at multiple levels:

1. **Integration tests**: `tests/` directory with cross-package functionality
2. **End-to-end demos**: `demo_simple.py`, `demo_end_to_end.py`, `demo_mass_learning.py`
3. **API tests**: `packages/sutra-api/tests/` and `packages/sutra-hybrid/tests/`
4. **Performance verification**: `verify_concurrent_storage.py` (production benchmarks)
5. **Storage tests**: Rust unit and integration tests in `packages/sutra-storage/`

### Test Locations
- **Root `tests/`**: Integration tests and query processor tests
- **`demo_*.py`**: End-to-end workflow demonstrations
- **`verify_concurrent_storage.py`**: Performance benchmarking (57K writes/sec verified)
- **Package-specific tests**: In respective `packages/*/tests/` directories

## Common Development Tasks

### Adding New Reasoning Strategies
1. Implement in `sutra_core/reasoning/paths.py`
2. Add to PathFinder class
3. Update QueryProcessor to support new strategy
4. Add comprehensive tests

### Extending Storage Format
1. Update Rust structures in `packages/sutra-storage/src/`
2. Modify Python bindings via PyO3 in `lib.rs`
3. Update memory layout documentation in `docs/sutra-storage/`
4. Run `cargo build --release` and verify with `verify_concurrent_storage.py`
5. Ensure single-file `storage.dat` format compatibility

### Adding API Endpoints
1. Define request/response models in `sutra_api/models.py`
2. Implement endpoint in `sutra_api/main.py`
3. Add rate limiting configuration
4. Update OpenAPI documentation

### Extending Control Center
1. **Frontend Changes**: Edit React components in `packages/sutra-control/src/`
2. **Backend Changes**: Update FastAPI gateway in `packages/sutra-control/backend/main.py`
3. **Build Process**: Run `npm run build` to create production build
4. **Docker**: Rebuild container with `docker build -t sutra-control:latest .`
5. **Testing**: Access at http://localhost:9000 after `docker compose up -d`

### Extending Sutra Grid
1. **Adding New Event Types**: Update `packages/sutra-grid-events/src/types.rs` with new event variants
2. **Master Changes**: Edit orchestration logic in `packages/sutra-grid-master/src/master.rs`
3. **Agent Changes**: Edit node management in `packages/sutra-grid-agent/src/agent.rs`
4. **Protocol Updates**: Modify `.proto` files and regenerate with `cargo build`
5. **Testing**: Run `./test-integration.sh` and check event storage with `grpcurl`

**Grid Event Flow**: Master/Agent → EventEmitter → Async Worker → Storage gRPC → Sutra Storage (port 50052)

**Grid Control Center Integration**: ✅ **COMPLETED**
- ✅ React Grid dashboard with agent/node topology view
- ✅ REST API endpoints for all Grid operations  
- ✅ Real-time monitoring and status updates
- ✅ Interactive spawn/stop operations via web UI
- ✅ Comprehensive documentation and troubleshooting guides

**Future Enhancements**:
- Natural language queries for events ("Show me all crashed nodes today")
- Advanced visualizations and network topology diagrams
- Automated operations and auto-scaling capabilities

## Troubleshooting

### Import Errors
```bash
# Solution: Set PYTHONPATH for core tests
PYTHONPATH=packages/sutra-core python -m pytest tests/ -v

# Or run integration tests from root
python -m pytest tests/ -v
```

### Virtual Environment Issues
```bash
# Recreate environment
python3 -m venv venv
source venv/bin/activate
pip install -e packages/sutra-core/
pip install -r requirements-dev.txt
```

### Storage/Persistence Issues
- **ConcurrentStorage**: Data written to single `storage.dat` file
- **WAL (Write-Ahead Log)**: All writes logged to `wal.log` for durability
- Check storage path permissions (default: `./knowledge/storage.dat`)
- Call `storage.flush()` manually before shutdown
- Auto-flush triggers at 50K concepts (configurable)
- Verify performance with `verify_concurrent_storage.py`
- Monitor stats: `storage.stats()` shows writes, drops, concepts, edges
- WAL automatically replays on startup for crash recovery
- WAL is checkpointed (truncated) after successful flush

## Code Style

- **Line length**: 88 characters (black default)
- **Import order**: stdlib, third-party, local (isort with black profile)
- **Type hints**: Required for all public functions
- **Docstrings**: Google style for all public classes and methods
- **Testing**: pytest with descriptive test names and docstrings

## Research Foundation

Built on published research:
- **Adaptive Focus Learning**: "LLM-Oriented Token-Adaptive Knowledge Distillation" (Oct 2024)
- **Multi-Path Plan Aggregation (MPPA)**: Consensus-based reasoning
- **Graph-based reasoning**: Decades of knowledge representation research

No proprietary techniques - all methods are from published work.