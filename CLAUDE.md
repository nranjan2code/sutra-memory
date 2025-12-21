# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Critical Context

**Sutra AI** is a production-grade, domain-specific explainable AI platform with TWO deployment modes:
1. **Desktop Edition** - Pure Rust native macOS app (no Docker required)
2. **Server Edition** - Distributed 15-service production system

**Key Architecture:** Multi-language workspace (Rust + Python + React) with custom TCP binary protocol (NOT gRPC/SQL/GraphQL).

## Important Note on Image Naming

This deployment uses the `sutra-works-` prefix for all Docker images to avoid conflicts with other Sutra deployments. See `docs/deployment/IMAGE_NAMING.md` for details. All `./sutra` CLI commands automatically use the correct image naming.

## Project Overview

Sutra AI is a **production-grade, domain-specific explainable AI platform** providing semantic reasoning over private knowledge graphs. Unlike general-purpose LLMs, Sutra starts empty and learns exclusively from your proprietary data with complete audit trails and millisecond-level query responses.

**Core Value:** 1000× smaller models, 100× lower cost, 100% explainable reasoning paths for regulated industries (healthcare, finance, legal) and knowledge-intensive domains (DevOps observability, enterprise knowledge management).

## Build & Test Commands

### Build System

```bash
# Build all services (unified entry point)
sutra build                         # Builds all services for current SUTRA_EDITION
SUTRA_EDITION=enterprise sutra build  # Build all enterprise services (10 services)

# Build specific services
sutra build storage api             # Build only storage and api

# Check build status
sutra status                        # Show running containers and built images

# Validate built images
sutra validate                      # Verify all essential images exist
```

### Testing

```bash
# E2E tests (web-based UI automation using Playwright - 3 continuous learning tests)
npm run test:e2e                # Run continuous learning tests (~3.3 minutes)
npm run test:e2e:all            # Run all browser tests (chromium, firefox, webkit)
npm run test:e2e:ui             # Interactive UI mode
npm run test:e2e:debug          # Debug mode with breakpoints
npm run test:e2e:report         # View HTML report
# Tests located in: tests/e2e/continuous-learning-fixed.spec.ts
# Configuration: playwright.config.ts

# Python unit tests (pytest with coverage requirements)
PYTHONPATH=packages/sutra-core python -m pytest tests/ -v
pytest --cov=packages/sutra-core --cov=packages/sutra-api --cov=packages/sutra-hybrid
# Coverage requirement: 70% minimum (enforced by pytest.ini)

# Run specific test markers
pytest -v -m unit                   # Fast unit tests only
pytest -v -m integration            # Integration tests (requires services running)
pytest -v -m slow                   # Resource-intensive tests

# Rust tests (storage engine, WAL recovery, 2PC transactions)
cd packages/sutra-storage && cargo test
cargo test --workspace              # Test entire Rust workspace
cargo test test_wal_recovery       # Specific test

# Desktop Edition tests (Rust native app)
cd desktop && cargo test

# Production smoke tests (validates embedding services and HTTP health endpoints)
sutra test smoke

# Integration tests (validates Docker deployment)
sutra test integration

# Scripts-based testing
./scripts/smoke-test-embeddings.sh  # Comprehensive embedding service validation
./scripts/integration-test.sh       # End-to-end workflow testing
```

### Rust Development

```bash
# Rust workspace structure (24 members - see Cargo.toml)
# Core packages: sutra-storage, sutra-protocol, sutra-grid-*, sutra-bulk-ingester
# Desktop: desktop (native macOS app)
# Vendored AI: sutra-embedder, sutraworks-model (with 11 sub-crates)

# Build storage engine
cd packages/sutra-storage
cargo build --release               # Production build (optimized)
cargo build                         # Debug build (faster compilation)
cargo run --bin storage-server      # Run storage server binary

# Desktop Edition (Pure Rust native app)
cd desktop
cargo run -p sutra-desktop          # Build and run desktop app
cargo build -p sutra-desktop --release  # Production build
./scripts/build-macos.sh            # Create macOS app bundle

# Workspace-level commands (run from repository root)
cargo check --workspace             # Check all workspace packages
cargo clippy --workspace            # Linting across workspace
cargo test --workspace              # Test all workspace packages
cargo build --release --workspace   # Build all packages

# Run specific test
cargo test test_wal_recovery        # In specific package
```

### Deployment

```bash
# Build nginx proxy (required for all deployments)
cd .sutra/compose
docker build -t sutra-works-nginx-proxy:latest -f nginx/Dockerfile nginx/
cd ../..

# Deploy by edition (profile-based Docker Compose)
export SUTRA_EDITION=simple    # or community, enterprise
export SUTRA_VERSION=latest
docker-compose -f .sutra/compose/production.yml --profile simple up -d

# Production deployment with security
export SUTRA_SECURE_MODE=true
export SUTRA_EDITION=enterprise
export SUTRA_SSL_CERT_PATH=/path/to/cert.pem
export SUTRA_SSL_KEY_PATH=/path/to/key.pem
docker-compose -f .sutra/compose/production.yml --profile enterprise up -d

# Stop services
docker-compose -f .sutra/compose/production.yml down

# View logs (note: all containers use sutra-works- prefix)
docker logs sutra-works-storage         # Storage server logs
docker logs sutra-works-api             # API service logs
docker logs sutra-works-nginx-proxy     # Nginx proxy logs

# Access services through nginx proxy
curl http://localhost:8080/api/health       # API via proxy
curl http://localhost:8080/sutra/health     # Hybrid service via proxy
open http://localhost:8080/                 # Main UI via proxy
```

## Architecture Overview

### Multi-Language Workspace

- **Rust Workspace** (packages/sutra-storage, sutra-protocol, sutra-grid-*, sutra-bulk-ingester)
  - Storage engine: Log-structured, HNSW vector indexing, WAL for durability
  - TCP binary protocol: Custom MessagePack-based (NOT gRPC)
  - Grid infrastructure: Distributed orchestration and sharding
  - Bulk ingestion: High-throughput data loading

- **Python Packages** (packages/sutra-core, sutra-api, sutra-hybrid, sutra-client, sutra-control)
  - Reasoning engine: Multi-Path Plan Aggregation (MPPA), graph traversal
  - REST APIs: FastAPI-based services
  - ML orchestration: Embedding and NLG service coordination
  - Web UIs: Streamlit client, React control center

### Core Components

**Storage Server (Rust)** - Port 50051 TCP
- **ConcurrentMemory**: Lock-free write log + immutable read views
- **Write-Ahead Log (WAL)**: Zero data loss, automatic crash recovery
- **Unified Learning Pipeline**: Server owns complete learning process:
  1. Embedding generation (calls HA service at :8888)
  2. Semantic analysis (rule-based + pattern matching)
  3. Association extraction (NLP + ML-based relationship discovery)
  4. Atomic storage (2PC for cross-shard writes)
- **HNSW Vector Index**: USearch with mmap persistence (94× faster startup vs rebuild)
- **Sharded Storage**: 4-16 shards for 10M+ concepts with 2PC transactions

**Reasoning Engine (Python)**
- `sutra-core`: Graph traversal, MPPA consensus reasoning, query processing
- Real-time learning without retraining
- Quality gates: "I don't know" responses when confidence < threshold

**ML Foundation Services**
- **Embedding Service** (:8888 HAProxy → :8889-8891 replicas)
  - Model: nomic-embed-text-v1.5 (768-dimensional vectors)
  - HA architecture: 3 replicas + load balancer
- **NLG Service** (:8890)
  - Grounded text generation with strict/balanced/creative modes
  - Edition-aware scaling (Simple/Community/Enterprise)

**API Layer**
- `sutra-api` (:8000): Primary REST API (FastAPI)
- `sutra-hybrid` (:8001): Semantic orchestration service
- `sutra-bulk-ingester` (:8005): High-throughput Rust-based ingestion

**Web Interfaces**
- `sutra-control` (:9000): React + Material UI control center
- `sutra-client` (:8080): Streamlit interactive query interface
- `sutra-explorer` (:8100): React + D3.js storage visualization

### Data Flow Pattern: Unified Learning

**CRITICAL**: All learning MUST route through the storage server's TCP `learn_concept()` method. Never bypass this pipeline.

```rust
// packages/sutra-storage/src/learning_pipeline.rs
pub async fn learn_concept(&mut self, content: String) -> Result<ConceptId> {
    // 1. Generate embedding via HA service
    let embedding = self.embedding_client.generate(content).await?;

    // 2. Extract associations (semantic extractor)
    let associations = self.semantic_extractor.extract(&content)?;

    // 3. Store atomically (2PC if sharded)
    self.store_atomically(content, embedding, associations).await
}
```

**Why this matters:**
- Single source of truth for learning
- Automatic embeddings for ALL ingestion paths
- Zero code duplication across clients
- Guaranteed consistency with ACID semantics

### TCP Binary Protocol (NOT gRPC)

Sutra uses a custom MessagePack-based binary protocol for 10-50× better performance than gRPC/REST.

**Architectural Policy**: Sutra will NEVER support SQL, Cypher, or GraphQL. See `docs/architecture/NO_SQL_POLICY.md` for rationale.

```rust
// packages/sutra-protocol/src/messages.rs
#[derive(Serialize, Deserialize)]
pub enum StorageRequest {
    LearnConcept { content: String, metadata: Option<ConceptMetadata> },
    QueryGraph { query: String, max_paths: u32 },
    GetConcept { concept_id: ConceptId },
}
```

### Security Modes

**Development (default)**: NO authentication, NO encryption - localhost only
```bash
sutra deploy  # Unsafe for production
```

**Production**: TLS 1.3, HMAC-SHA256, RBAC, network isolation
```bash
SUTRA_SECURE_MODE=true sutra deploy
docker logs sutra-storage | grep "Authentication: ENABLED"  # Verify
```

Security is **fully integrated** as of October 2025. See `docs/security/PRODUCTION_SECURITY_SETUP.md`.

### Grid Event Ingestion (Self-Monitoring)

Sutra Grid uses **its own storage** for observability - storing operational events as concepts for natural language querying.

**Enable Grid Events**:
```bash
# Start storage server
cd packages/sutra-storage
STORAGE_PATH=/tmp/sutra-data/storage.dat cargo run --bin storage-server

# Start Grid Master with event storage
cd packages/sutra-grid-master
EVENT_STORAGE=localhost:50051 cargo run

# Events are now automatically stored as concepts
# Query via Control Center: "Show me all agents that went offline today"
```

**7 Event Types Emitted**:
- AgentRegistered, AgentHeartbeat, AgentRecovered
- AgentDegraded, AgentOffline, AgentUnregistered
- Background health monitoring (every 30s)

**Architecture**: Grid Master → EventEmitter → TCP Storage → Control Center Queries

See `GRID_EVENT_INGESTION_GUIDE.md` for complete deployment guide.

### Environment Variable Contracts

**Bulk Ingester** (Fail-Fast Philosophy):
```bash
# Production (default): Fail loudly if storage unavailable
cargo run --bin bulk-ingester  # Connection failure = FATAL error

# Testing ONLY: Enable mock mode
SUTRA_ALLOW_MOCK_MODE=1 cargo run --bin bulk-ingester
# ⚠️  Mock mode DISCARDS all data - never use in production!
```

**Grid Master** (Event Ingestion):
```bash
# Enable event storage
EVENT_STORAGE=localhost:50051 cargo run

# Disable event storage (events not persisted)
cargo run  # "Event emission disabled (no EVENT_STORAGE configured)"
```

**Storage Server**:
```bash
STORAGE_PATH=/tmp/sutra-data/storage.dat  # Data file location (required)
SUTRA_SECURE_MODE=true                     # Enable authentication/TLS
```

### Control Center (Zero Mocks)

Control Center has **zero mocks** - all connections are real or gracefully degrade:

**Real Connections**:
- Storage Server (TCP): Real metrics, real queries
- Grid Events: Real semantic search against knowledge graph
- Natural Language Queries: Real StorageClient semantic search

**Graceful Degradation**:
```python
# If storage unavailable, show "Storage Unavailable" instead of crashing
storage = await get_storage_client()
if storage:
    return real_metrics_from_storage()
else:
    return empty_metrics_with_timestamp()  # UI shows "unavailable" state
```

**vs. Bulk Ingester Fail-Fast**:
- Control Center: Monitoring UI - should show unavailable, not crash
- Bulk Ingester: Data ingestion - failure is unacceptable, fail loudly

## Key Architectural Patterns

### Edition System

```bash
export SUTRA_EDITION=simple|community|enterprise
```

**Impact:**
- **Simple**: 8 services, single storage instance, lower rate limits (FREE)
- **Community**: 8 services, HA embedding (3 replicas), 10× higher limits ($99/mo)
- **Enterprise**: 10 services (+ grid-master, grid-agent), 16 shards, 100× limits ($999/mo)

Edition affects: service count, shard configuration, embedding model selection, rate limits, resource allocation.

### Cargo Workspace Structure

```
Cargo.toml (workspace root - 24 members)
├── packages/sutra-storage/        # Core storage engine + binary
├── packages/sutra-protocol/       # TCP protocol definitions
├── packages/sutra-grid-master/    # Grid orchestration
├── packages/sutra-grid-agent/     # Node management
├── packages/sutra-grid-events/    # Event library (26 event types)
├── packages/sutra-bulk-ingester/  # High-throughput ingestion
├── packages/sutra-embedder/       # Vendored ONNX embedding library (4x faster)
├── packages/sutraworks-model/     # Vendored NLG/text generation (RWKV support)
│   ├── crates/sutra-core/        # Core ML framework
│   ├── crates/sutra-rwkv/        # RWKV model implementation
│   ├── crates/sutra-mamba/       # Mamba model implementation
│   └── ... (11 sub-crates total)
└── desktop/                       # Pure Rust native macOS application
```

**Key Points:**
- Shared dependencies in `[workspace.dependencies]` for consistency
- Vendored AI packages (sutra-embedder, sutraworks-model) for zero external dependencies
- Desktop edition reuses `sutra-storage` crate (no code duplication)

### Python Package Structure

**Core Packages:**
- `packages/sutra-core/` - Graph reasoning engine (42 modules, MPPA algorithm)
- `packages/sutra-api/` - FastAPI REST API service
- `packages/sutra-hybrid/` - Semantic orchestration service
- `packages/sutra-client/` - Streamlit interactive UI
- `packages/sutra-control/` - React control center

**Installation Modes:**
```bash
# Production (minimal - TCP client only)
pip install sutra-core[server]      # 20MB (no sklearn/sqlalchemy/hnswlib)
pip install sutra-hybrid             # 103MB (no sklearn)

# Development (with local storage - NOT RECOMMENDED)
pip install sutra-core[local]        # 30MB (includes sqlalchemy/hnswlib)
pip install sutra-hybrid[tfidf]      # 115MB (includes sklearn)
```

**Critical Architecture Decision (v3.0.1):**
- **ONLY ONE BACKEND**: TCP Binary Protocol (RustStorageAdapter and GrpcStorageAdapter removed)
- **1000+ LOC deleted**: connection.py, embedded mode, gRPC mode all removed
- See: `docs/architecture/CLEAN_ARCHITECTURE_IMPLEMENTATION.md`

### NPM/PNPM Workspace

**Root workspace** (pnpm-workspace.yaml):
- `packages/sutra-client` - React/Vite frontend
- `packages/sutra-control` - React control center
- `packages/sutra-explorer/frontend` - React visualization tool
- `packages/sutra-ui-framework` - Shared UI components

**Key npm scripts** (from package.json):
```bash
npm run test:e2e              # Playwright E2E tests
npm run test:e2e:ui           # Interactive UI mode
npm run dev                   # Concurrent API + client development
```

### Version Management

**Single source of truth**: `VERSION` file (currently 3.3.0)

```bash
# Check version
sutra version                     # Show current version
cat VERSION                       # Direct file access (e.g., 3.0.0)

# Create releases (manual VERSION file update)
echo "3.0.1" > VERSION           # Bug fix: 3.0.0 → 3.0.1
echo "3.1.0" > VERSION           # Feature: 3.0.0 → 3.1.0
echo "4.0.0" > VERSION           # Breaking: 3.0.0 → 4.0.0

# Commit, tag, and push to trigger automated builds
git add VERSION
git commit -m "Release v3.0.1"
git tag -a v3.0.1 -m "Release version 3.0.1"
git push origin main --tags
```

See `docs/release/` for complete release management documentation.

### Self-Monitoring Architecture (Revolutionary)

Sutra monitors itself using its own reasoning engine - NO external tools (Prometheus, Grafana, Datadog).

**26 Production Event Types** (`packages/sutra-grid-events/src/events.rs`):
- Agent lifecycle: Registered, Heartbeat, Degraded, Offline, Recovered, Unregistered
- Node lifecycle: SpawnRequested/Succeeded/Failed, StopRequested/Succeeded/Failed, Crashed, Restarted
- Performance: StorageMetrics, QueryPerformance, EmbeddingLatency, HnswIndexBuilt, PathfindingMetrics

**Natural Language Operational Queries:**
```python
"Show cluster status"
"What caused the 2am crash?"  # Returns complete causal chain in ~30ms
"Which agents went offline this week?"
"Why did node-abc123 crash?"  # Automatic root cause analysis
"Which storage node is slowest?"
```

See `docs/sutra-platform-review/DEVOPS_SELF_MONITORING.md` for complete case study.

## Testing Considerations

### Test Markers

```python
@pytest.mark.unit           # Fast unit tests
@pytest.mark.integration    # Requires services running
@pytest.mark.slow           # Resource-intensive tests
```

### Coverage Requirements

- Minimum coverage: 70% (enforced by pytest.ini)
- Reports: HTML (htmlcov/), XML (coverage.xml), terminal
- Coverage command: `pytest --cov=packages/sutra-core --cov=packages/sutra-api`

### WAL Testing (Rust)

Storage engine tests include crash recovery scenarios:
```bash
cd packages/sutra-storage
cargo test test_wal_recovery       # Tests write-ahead log replay
cargo test test_2pc_transaction    # Tests cross-shard atomicity
```

## Important File Locations

**Build & Deploy:**
- `./sutra` - Unified Python CLI (single entry point for all operations)
- `./sutra-optimize.sh` - Backend build orchestration (called by ./sutra)
- `.sutra/compose/production.yml` - Docker Compose file with edition profiles
- `VERSION` - Single source of truth for versioning (currently 3.3.0)
- `Cargo.toml` - Rust workspace configuration (24 members)
- `package.json` - Root npm/pnpm workspace configuration
- `pytest.ini` - Python test configuration (70% coverage requirement)
- `playwright.config.ts` - E2E test configuration

**Storage Engine (Rust):**
- `packages/sutra-storage/src/lib.rs` - Module exports and definitions
- `packages/sutra-storage/src/concurrent_memory.rs` - Lock-free core
- `packages/sutra-storage/src/learning_pipeline.rs` - Unified learning pipeline
- `packages/sutra-storage/src/wal.rs` - Write-Ahead Log
- `packages/sutra-storage/src/transaction.rs` - 2PC coordinator
- `packages/sutra-storage/src/bin/storage_server.rs` - TCP server binary

**Desktop Edition (Rust):**
- `desktop/src/main.rs` - Entry point, window setup
- `desktop/src/app.rs` - Main app controller (uses sutra-storage directly)
- `desktop/src/local_embedding.rs` - Integration with sutra-embedder
- `desktop/src/local_nlg.rs` - Integration with sutraworks-model
- `desktop/src/ui/` - UI components (sidebar, chat, knowledge, settings)
- `desktop/src/theme.rs` - Color palette and styling
- `desktop/scripts/build-macos.sh` - macOS app bundle builder

**Vendored AI Packages (Rust):**
- `packages/sutra-embedder/` - ONNX embedding with all-mpnet-base-v2 (768D vectors)
- `packages/sutraworks-model/` - NLG/text generation with RWKV/Mamba support
- `packages/sutraworks-model/src/lib.rs` - Public API facade for external consumers

**Reasoning Engine (Python):**
- `packages/sutra-core/sutra_core/` - 42 Python modules
- `packages/sutra-core/sutra_core/reasoning.py` - MPPA algorithm
- `packages/sutra-core/sutra_core/graph.py` - Concept/Association data structures
- `packages/sutra-core/sutra_core/storage/tcp_adapter.py` - ONLY storage adapter (TCP binary protocol)

**Web UIs (React/Streamlit):**
- `packages/sutra-client/` - Streamlit interactive query interface
- `packages/sutra-control/` - React + Material UI control center
- `packages/sutra-explorer/` - React + D3.js storage visualization

**Documentation Hub:**
- `docs/README.md` - Main navigation with user journeys
- `docs/architecture/SYSTEM_ARCHITECTURE.md` - Complete technical architecture
- `docs/desktop/` - Desktop edition documentation (README, ARCHITECTURE, BUILDING, UI_COMPONENTS)
- `docs/getting-started/quickstart.md` - 5-minute setup guide
- `docs/deployment/README.md` - Deployment guide
- `docs/release/README.md` - Release management
- `.github/copilot-instructions.md` - Detailed AI assistant guidance (updated November 2025)

**Technical Excellence Reports (December 2025):**
- `TECHNICAL_EXCELLENCE_ACHIEVED.md` - Phase 1: Storage engine excellence (137/137 tests passing, zero debt)
- `EXCELLENCE_COMPLETION_PLAN.md` - Strategic roadmap for remaining work
- `CORE_CHANGES_IMPACT_ANALYSIS.md` - Dependency impact mapping
- `TECHNICAL_DEBT_ELIMINATION_REPORT.md` - 350+ line comprehensive audit (541 TODOs across 153 files)
- `CONTROL_CENTER_EXCELLENCE.md` - Phase 5: All 12 mocks eliminated, real connections
- `GRID_EVENT_INGESTION_GUIDE.md` - Phase 6: Complete deployment guide (650+ lines)
- `GRID_EVENT_INGESTION_COMPLETE.md` - Phase 6 completion summary

**Testing:**
- `tests/e2e/` - Playwright E2E tests (3 continuous learning tests)
- `tests/e2e/README.md` - Complete test documentation
- `e2e/page-objects.ts` - Page object models (LoginPage, ChatPage)

**Scripts:**
- `scripts/smoke-test-embeddings.sh` - Production smoke tests
- `scripts/integration-test.sh` - End-to-end integration tests
- `scripts/ci-validate.sh` - CI validation
- `scripts/stress_test.py` - Performance benchmarking (expects 9+ req/sec, 100% success)

## Common Anti-Patterns to Avoid

❌ **Don't bypass unified learning**: All ingestion MUST go through storage server TCP `learn_concept()`
❌ **Don't ignore editions**: Features/performance vary significantly by `SUTRA_EDITION`
❌ **Don't assume security**: Default mode has NO authentication (development only)
❌ **Don't skip semantic versioning**: Update VERSION file, commit, and tag properly (see Version Management section)
❌ **Don't use non-existent scripts**: Use `sutra` command as the single entry point
❌ **Don't use mock mode in production**: `SUTRA_ALLOW_MOCK_MODE=1` is for testing ONLY - data is discarded
❌ **Don't bypass fail-fast**: Bulk ingester fails loudly on connection errors by design (prevents silent data loss)
❌ **Don't add new mocks**: Control Center and Bulk Ingester have zero mocks - keep it that way
❌ **Don't forget EVENT_STORAGE**: Grid Master needs `EVENT_STORAGE=localhost:50051` to enable event ingestion
❌ **Don't position as "regulated industries only"**: Market spans 20+ industries ($200B+ TAM)
❌ **Don't forget temporal/causal reasoning**: Core differentiator vs. vector databases
❌ **Don't use gRPC/SQL/GraphQL**: Sutra uses custom TCP binary protocol exclusively
❌ **Don't duplicate storage logic**: Desktop edition reuses `sutra-storage` crate, not separate implementation
❌ **Don't add external AI dependencies**: Use vendored packages (sutra-embedder, sutraworks-model) for zero external deps

## Development Workflow

### Single Service Updates (Fast Development)

```bash
# Rebuild and restart specific service (faster than full rebuild)
docker-compose -f .sutra/compose/production.yml up -d --build sutra-api
docker-compose -f .sutra/compose/production.yml up -d --build sutra-embedding-service

# Hot-reload development (Python/React changes apply instantly)
docker-compose -f docker-compose-grid.yml -f docker-compose.dev.yml up
```

### Code Quality

```bash
# Pre-commit hooks (9 checks: black, isort, flake8, bandit, etc.)
pre-commit run --all-files

# Manual formatting
black packages/
isort packages/

# Rust linting
cargo clippy --workspace -- -D warnings
```

## Documentation Structure

User journeys:
1. **New Users**: `docs/getting-started/` → quickstart.md → tutorial.md
2. **Developers**: `docs/build/` → `docs/deployment/` → `docs/architecture/`
3. **DevOps**: `docs/deployment/` → `docs/release/` → `docs/security/`
4. **Contributors**: `docs/guides/DEVELOPMENT.md` → `docs/CONTRIBUTING.md`

## References

- **Architecture**: `docs/architecture/SYSTEM_ARCHITECTURE.md` (100+ lines)
- **Platform Review**: `docs/sutra-platform-review/` (complete technical/market analysis)
- **Build System**: `docs/build/README.md`
- **Deployment**: `docs/deployment/README.md`
- **Release Process**: `docs/release/RELEASE_PROCESS.md`
- **Copilot Instructions**: `.github/copilot-instructions.md` (detailed AI assistant guidance)

## Scale & Performance Targets

- **Startup**: <50ms for 1M vectors (HNSW mmap persistence)
- **Write throughput**: 57K writes/sec
- **Read latency**: <10ms
- **Target scale**: 10M+ concepts across 16 shards
- **Memory efficiency**: <0.1% overhead for self-monitoring events
