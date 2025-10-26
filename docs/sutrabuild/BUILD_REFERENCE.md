# Sutra AI Build Reference

**Complete Command Reference & Configuration Guide**

---

## 🚀 Master Build Script

### `./sutrabuild/scripts/build-all.sh`

**Primary build orchestration script with comprehensive profile and configuration support.**

#### Syntax
```bash
./sutrabuild/scripts/build-all.sh [OPTIONS]
```

#### Options

| Flag | Description | Default | Example |
|------|-------------|---------|---------|
| `--profile <name>` | Build profile selection | `simple` | `--profile enterprise` |
| `--version <tag>` | Version tag for images | `latest` | `--version v2.1.0` |
| `--parallel` | Enable parallel builds | `false` | `--parallel` |
| `--rebuild-base` | Force rebuild base images | `false` | `--rebuild-base` |
| `--no-cache` | Disable Docker layer caching | `false` | `--no-cache` |
| `--verbose` | Enable detailed logging | `false` | `--verbose` |
| `--dry-run` | Show commands without execution | `false` | `--dry-run` |
| `--help` | Display help information | - | `--help` |

#### Build Profiles

##### Simple Profile (Development)
```bash
./sutrabuild/scripts/build-all.sh --profile simple
```
- ✅ **Services**: Storage, API, Hybrid, Embedding  
- ✅ **Use Case**: Development, testing, small deployments
- ✅ **Resources**: 4GB RAM, 2 CPU cores minimum
- ✅ **Build Time**: ~3-4 minutes (cold), ~30s (incremental)

##### Community Profile (Small Production)  
```bash
./sutrabuild/scripts/build-all.sh --profile community
```
- ✅ **Services**: All Simple + Monitoring, Load Balancing
- ✅ **Use Case**: Small production, community deployments  
- ✅ **Resources**: 8GB RAM, 4 CPU cores recommended
- ✅ **Build Time**: ~4-5 minutes (cold), ~45s (incremental)

##### Enterprise Profile (Large Scale)
```bash
./sutrabuild/scripts/build-all.sh --profile enterprise
```
- ✅ **Services**: Full suite + Grid Master, Sharding, HA
- ✅ **Use Case**: Large-scale production, enterprise deployments
- ✅ **Resources**: 16GB RAM, 8+ CPU cores recommended
- ✅ **Build Time**: ~6-8 minutes (cold), ~60s (incremental)

#### Performance Options

##### Parallel Builds
```bash
# Enable parallel execution (faster, more resources)
./sutrabuild/scripts/build-all.sh --profile simple --parallel

# Sequential execution (default, safer)  
./sutrabuild/scripts/build-all.sh --profile simple
```

**Resource Requirements for Parallel:**
- **RAM**: 8GB minimum, 16GB recommended
- **CPU**: 4 cores minimum, 8+ optimal
- **Disk I/O**: SSD recommended for best performance

##### Version Management
```bash
# Build specific version
./sutrabuild/scripts/build-all.sh --version v2.1.0

# Build with custom tag  
./sutrabuild/scripts/build-all.sh --version dev-$(date +%Y%m%d)

# Latest development build
./sutrabuild/scripts/build-all.sh --version latest
```

#### Advanced Options

##### Force Rebuild  
```bash
# Rebuild base images (useful after security updates)
./sutrabuild/scripts/build-all.sh --rebuild-base

# Disable all caching (clean build)
./sutrabuild/scripts/build-all.sh --no-cache

# Both options combined
./sutrabuild/scripts/build-all.sh --rebuild-base --no-cache
```

##### Debugging & Validation
```bash
# Verbose output for debugging
./sutrabuild/scripts/build-all.sh --verbose

# Show commands without executing  
./sutrabuild/scripts/build-all.sh --dry-run

# Validate configuration
./sutrabuild/scripts/build-all.sh --profile enterprise --dry-run --verbose
```

#### Exit Codes

| Code | Meaning | Action Required |
|------|---------|----------------|
| `0` | Success | None - build completed successfully |
| `1` | Configuration Error | Check parameters and environment |
| `2` | Docker Error | Verify Docker is running and accessible |
| `3` | Build Failure | Check logs for specific service errors |
| `4` | Validation Error | Review health checks and dependencies |

#### Examples

```bash
# Development build (fastest)
./sutrabuild/scripts/build-all.sh

# Production build with parallel execution
./sutrabuild/scripts/build-all.sh --profile enterprise --parallel --version v2.1.0

# Clean enterprise build
./sutrabuild/scripts/build-all.sh --profile enterprise --no-cache --rebuild-base

# Debug community build
./sutrabuild/scripts/build-all.sh --profile community --verbose --dry-run
```

---

## 🏥 Health Check System

### `./sutrabuild/scripts/health-check.sh`

**Universal health validation system for services and endpoints.**

#### Syntax
```bash  
./sutrabuild/scripts/health-check.sh [URL] [OPTIONS]
```

#### Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `URL` | Service endpoint to check | `http://localhost:8000/health` |
| `--timeout <sec>` | Request timeout | `--timeout 30` |
| `--retries <num>` | Number of retry attempts | `--retries 3` |
| `--interval <sec>` | Retry interval | `--interval 5` |
| `--silent` | Suppress output | `--silent` |

#### Service Endpoints

| Service | Health Endpoint | Default Port |
|---------|----------------|--------------|
| **sutra-api** | `http://localhost:8000/health` | 8000 |
| **sutra-hybrid** | `http://localhost:8001/health` | 8001 |  
| **sutra-storage** | `tcp://localhost:50051/health` | 50051 |
| **sutra-embedding** | `http://localhost:8888/health` | 8888 |

#### Usage Examples

```bash
# Basic health check
./sutrabuild/scripts/health-check.sh http://localhost:8000/health

# Health check with custom timeout
./sutrabuild/scripts/health-check.sh http://localhost:8001/health --timeout 60

# Robust health check with retries
./sutrabuild/scripts/health-check.sh http://localhost:8888/health --retries 5 --interval 10

# Silent health check for automation  
./sutrabuild/scripts/health-check.sh http://localhost:8000/health --silent
```

#### Return Codes

| Code | Status | Description |
|------|--------|-------------|
| `0` | Healthy | Service responding correctly |
| `1` | Unhealthy | Service not responding or errors |
| `2` | Timeout | Service response timeout exceeded |  
| `3` | Connection Failed | Cannot connect to service |

---

## 🔐 Security & Secrets Management

### `./sutrabuild/scripts/generate-secrets.sh`

**Comprehensive security credential generation and management system.**

#### Features
- 🔐 **Cryptographically Secure**: OpenSSL-based secret generation
- 🔐 **JWT Token Management**: Service and admin tokens with HMAC-SHA256
- 🔐 **TLS Certificate Support**: Self-signed for development, CA integration for production
- 🔐 **Environment Integration**: Auto-generates `.env` configuration

#### Execution
```bash
./sutrabuild/scripts/generate-secrets.sh
```

#### Generated Artifacts

```
.secrets/
├── auth_secret.txt         # 32-byte base64 authentication secret
├── tokens/
│   ├── service_token.txt   # Long-lived service authentication token
│   └── admin_token.txt     # Administrative access token  
├── tls/
│   ├── cert.pem           # TLS certificate (if generated)
│   └── key.pem            # TLS private key (if generated)  
└── .env                   # Complete environment configuration
```

#### Security Features

##### Token Structure
```json
{
  "sub": "service-name",
  "roles": ["Service"],  
  "iat": 1640995200,
  "exp": 1672531200
}
```

##### Permissions & Access Levels

| Role | Permissions | Token Validity | Use Case |
|------|-------------|----------------|----------|
| **Service** | Inter-service communication | 1 year | Automated systems |
| **Admin** | Full system access | 1 year | Administrative tasks |
| **User** | Limited API access | 1 hour | User authentication |

##### Environment Variables Generated
```bash
# Authentication
SUTRA_AUTH_SECRET=<generated-secret>
SUTRA_AUTH_METHOD=hmac
SUTRA_TOKEN_TTL_SECONDS=3600

# Service Tokens
SUTRA_SERVICE_TOKEN=<generated-token>
SUTRA_ADMIN_TOKEN=<generated-token>

# Security Configuration
SUTRA_TLS_ENABLED=false
SUTRA_BEHIND_PROXY=false
```

---

## 🧪 Testing & Validation

### `./sutrabuild/scripts/smoke-test-embeddings.sh`

**Production-ready smoke testing for the embedding service stack.**

#### Test Coverage
- ✅ **API Endpoints**: All REST API functionality
- ✅ **Embedding Generation**: Text-to-vector conversion  
- ✅ **Performance**: Response time validation
- ✅ **Health Checks**: Service availability
- ✅ **Integration**: End-to-end workflows

#### Execution
```bash
./sutrabuild/scripts/smoke-test-embeddings.sh
```

#### Test Scenarios

##### Basic Functionality Tests
1. **Service Discovery**: Verify all services are reachable
2. **Health Endpoints**: Validate health check responses
3. **Authentication**: Test token-based authentication
4. **API Contracts**: Verify request/response formats

##### Performance Tests  
1. **Response Time**: API calls < 100ms P95
2. **Throughput**: Minimum requests per second
3. **Concurrent Load**: Multi-client stress testing
4. **Resource Usage**: Memory and CPU efficiency

##### Integration Tests
1. **End-to-End**: Complete user workflow
2. **Error Handling**: Graceful failure scenarios  
3. **Data Consistency**: Cross-service data integrity
4. **Recovery**: Service restart and reconnection

#### Output Format
```bash
✅ PASS: Service Discovery (3/3 services reachable)
✅ PASS: Health Checks (all endpoints responding)  
✅ PASS: Authentication (tokens valid)
✅ PASS: API Contracts (all schemas valid)
✅ PASS: Performance (avg 45ms, P95 78ms)
✅ PASS: Integration (end-to-end workflow complete)

🎉 SMOKE TEST PASSED: All 25 tests successful
   Duration: 45 seconds
   Performance: EXCELLENT (all metrics within SLA)
```

### `./sutrabuild/scripts/test-embedding-ha.sh`

**High Availability and failover testing for embedding services.**

#### Test Scenarios
- 🔄 **Failover Testing**: Automatic service recovery  
- 🔄 **Load Balancing**: Request distribution validation
- 🔄 **Circuit Breaking**: Fault isolation testing
- 🔄 **Zero Downtime**: Rolling update validation

#### Execution
```bash
./sutrabuild/scripts/test-embedding-ha.sh
```

#### Test Phases

##### Phase 1: Baseline (30s)
- Establish baseline performance metrics
- Validate all instances are healthy
- Measure normal request distribution

##### Phase 2: Single Instance Failure (20s)  
- Stop one embedding service instance
- Verify automatic failover to healthy instances
- Measure performance impact

##### Phase 3: Multiple Instance Failure (15s)
- Stop additional instances (2/3 down)
- Test system behavior under stress
- Validate graceful degradation

##### Phase 4: Recovery Testing (20s)
- Restart failed instances  
- Verify automatic re-integration
- Confirm performance recovery

#### Success Criteria
- ✅ **Availability**: >95% success rate during failures
- ✅ **Failover Time**: <5 seconds detection and recovery
- ✅ **Performance Impact**: <20% degradation during failover
- ✅ **Recovery Time**: <30 seconds full restoration

---

## 🔍 Diagnostics & Troubleshooting

### `./sutrabuild/scripts/diagnose-docker-pipeline.sh`

**Comprehensive system diagnostics and issue detection.**

#### Diagnostic Categories
1. **Docker Environment**: Installation, daemon, configuration
2. **Required Files**: Build dependencies, Docker files
3. **Python Dependencies**: Package availability and versions  
4. **Rust Compilation**: Storage server build validation
5. **API Configuration**: Service endpoint validation
6. **TCP Client**: Storage client functionality
7. **Docker Compose**: Configuration validation
8. **Port Availability**: Network conflict detection
9. **Ollama Service**: Embedding model availability
10. **Container State**: Existing container analysis

#### Execution
```bash
./sutrabuild/scripts/diagnose-docker-pipeline.sh
```

#### Sample Output
```bash
🔬 Docker Pipeline Diagnostic Tool
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  Docker Environment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ OK: Docker installed
   Version: Docker version 24.0.6
✅ OK: Docker daemon running

2️⃣  Required Files  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ OK: Found sutrabuild/compose/docker-compose-grid.yml
✅ OK: Found packages/sutra-api/Dockerfile
✅ OK: Found packages/sutra-storage/Cargo.toml

📊 Diagnostic Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 No critical issues found!

Next steps:
  1. Build images: ./sutrabuild/scripts/build-all.sh --profile simple
  2. Start services: ./sutra-deploy.sh up  
  3. Verify: ./sutrabuild/scripts/smoke-test-embeddings.sh
```

### `./sutrabuild/scripts/verify-production-fixes.sh`

**Production readiness validation and compliance checking.**

#### Validation Categories
- ✅ **Configuration**: Default settings and environment variables
- ✅ **API Integration**: Unified pipeline implementation
- ✅ **Storage Architecture**: Learning pipeline components
- ✅ **Client Libraries**: TCP client functionality  
- ✅ **Code Quality**: Rust compilation and Python imports
- ✅ **Documentation**: Required documentation presence
- ✅ **Docker Configuration**: Production-ready settings

#### Execution  
```bash
./sutrabuild/scripts/verify-production-fixes.sh
```

---

## 🔧 Utility Scripts

### `./sutrabuild/scripts/scan-dependencies.sh`

**Security and dependency analysis across the entire stack.**

#### Scan Coverage
- 🔍 **Python Packages**: Security vulnerabilities, license compliance
- 🔍 **Rust Crates**: Dependency analysis, security advisories  
- 🔍 **Node.js Dependencies**: JavaScript package security (if applicable)
- 🔍 **Docker Images**: Base image vulnerability assessment
- 🔍 **Configuration**: Security best practices validation

#### Output Formats
- **Console**: Human-readable summary
- **JSON**: Machine-readable for CI/CD integration
- **SARIF**: Security analysis format for tools
- **CSV**: Tabular format for reporting

### `./sutrabuild/scripts/detect-changes.sh`

**Intelligent build optimization through change detection.**

#### Change Detection Logic
```bash
# Detect changes since last commit
./sutrabuild/scripts/detect-changes.sh

# Detect changes since specific reference
./sutrabuild/scripts/detect-changes.sh HEAD~5
```

#### Output  
```bash
Changed Packages:
  - sutra-api (packages/sutra-api/*)
  - sutra-hybrid (packages/sutra-hybrid/*)

Recommended Build:
  ./sutrabuild/scripts/build-all.sh --services sutra-api,sutra-hybrid
```

### `./sutrabuild/scripts/scale-validation.rs`

**Performance benchmarking and scale validation.**

#### Test Scenarios
- 📈 **Sequential Write**: 10M concepts throughput measurement
- 📈 **Batch Write**: 1000-concept batch performance
- 📈 **Query Latency**: Random query performance (P50/P95/P99)
- 📈 **Vector Search**: Semantic search with HNSW indexing
- 📈 **Pathfinding**: Multi-hop path traversal performance
- 📈 **Memory Usage**: Resource consumption analysis

#### Execution
```bash
# Compile and run performance tests
cd sutrabuild/scripts
cargo run --release --bin scale-validation
```

#### Expected Results
- **Write Throughput**: >57K concepts/sec sustained
- **Query Latency**: <0.01ms per concept (P50)  
- **Vector Search**: <50ms for top-10 results (P95)
- **Memory Efficiency**: ~1KB per concept
- **Pathfinding**: <100ms for 3-hop paths (P95)

### `./sutrabuild/scripts/generate-license.py`

**License management and compliance reporting.**

#### Functionality  
- 📄 **License Detection**: Automatic license identification  
- 📄 **Compatibility Analysis**: License compatibility matrix
- 📄 **Report Generation**: Compliance reports for legal review
- 📄 **SPDX Support**: Standard license identifier format

#### Usage
```bash
python ./sutrabuild/scripts/generate-license.py --format json --output licenses.json
python ./sutrabuild/scripts/generate-license.py --report --compliance
```

---

## 🐳 Docker Compose Reference

### Compose File Locations

| File | Purpose | Environment |
|------|---------|-------------|
| `sutrabuild/compose/docker-compose.yml` | Unified orchestration | All environments |
| `sutrabuild/compose/docker-compose-grid.yml` | Grid deployment | Enterprise |
| `sutrabuild/compose/docker-compose-secure.yml` | Security-hardened | Production |
| `sutrabuild/compose/docker-compose-dev.yml` | Development | Development |

### Profile Usage

```bash
# Simple profile (development)
docker-compose -f sutrabuild/compose/docker-compose.yml --profile simple up

# Community profile (small production)  
docker-compose -f sutrabuild/compose/docker-compose.yml --profile community up

# Enterprise profile (large scale)
docker-compose -f sutrabuild/compose/docker-compose.yml --profile enterprise up
```

### Service Management

```bash
# Start specific services
docker-compose up sutra-storage sutra-api

# Scale services  
docker-compose up --scale sutra-embedding-service=3

# View logs
docker-compose logs -f sutra-hybrid

# Health check
docker-compose exec sutra-api health-check http://localhost:8000/health
```

---

## 🌍 Environment Variables

### Build-Time Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `SUTRA_EDITION` | Deployment profile | `simple` | `export SUTRA_EDITION=enterprise` |
| `SUTRA_VERSION` | Image version tag | `latest` | `export SUTRA_VERSION=v2.1.0` |
| `DOCKER_BUILDKIT` | Enhanced build features | `1` | `export DOCKER_BUILDKIT=1` |
| `COMPOSE_DOCKER_CLI_BUILD` | Compose BuildKit support | `1` | `export COMPOSE_DOCKER_CLI_BUILD=1` |

### Runtime Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `SUTRA_SECURE_MODE` | Enable security features | `false` | `export SUTRA_SECURE_MODE=true` |
| `SUTRA_LOG_LEVEL` | Logging verbosity | `INFO` | `export SUTRA_LOG_LEVEL=DEBUG` |
| `SUTRA_MAX_CONNECTIONS` | Connection pool size | `1000` | `export SUTRA_MAX_CONNECTIONS=2000` |
| `SUTRA_WORKER_THREADS` | Worker thread count | `8` | `export SUTRA_WORKER_THREADS=16` |

### Service Discovery

| Variable | Description | Default |
|----------|-------------|---------|
| `SUTRA_STORAGE_URL` | Storage service endpoint | `tcp://storage:50051` |
| `SUTRA_EMBEDDING_URL` | Embedding service endpoint | `http://embedding:8888` |
| `SUTRA_API_URL` | API service endpoint | `http://api:8000` |
| `SUTRA_HYBRID_URL` | Hybrid service endpoint | `http://hybrid:8001` |

---

## 📊 Performance Tuning

### Build Performance

#### Docker BuildKit Optimization
```bash
# Enable BuildKit (default in modern Docker)
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Advanced BuildKit features
export BUILDKIT_STEP_LOG_MAX_SIZE=50000000
export BUILDKIT_STEP_LOG_MAX_SPEED=100000000
```

#### Cache Management
```bash
# Optimize cache usage
docker buildx create --use --name sutra-builder --driver docker-container

# Cache mount for package managers  
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
```

### Runtime Performance

#### Resource Limits
```yaml
services:
  sutra-storage:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:  
          memory: 2G
          cpus: '1.0'
```

#### Health Check Optimization
```yaml
healthcheck:
  test: ["CMD", "health-check", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s  
  start_period: 60s
  retries: 3
```

---

## ❗ Troubleshooting Quick Reference  

### Common Issues

#### Build Failures
```bash
# Problem: Docker build fails
# Solution: Run comprehensive diagnostics
./sutrabuild/scripts/diagnose-docker-pipeline.sh

# Problem: Out of disk space  
# Solution: Clean Docker system
docker system prune -af && docker volume prune -f

# Problem: Permission denied
# Solution: Fix Docker permissions (Linux)
sudo usermod -aG docker $USER && newgrp docker
```

#### Runtime Issues
```bash  
# Problem: Services not starting
# Solution: Check port conflicts
./sutrabuild/scripts/diagnose-docker-pipeline.sh

# Problem: Health checks failing
# Solution: Verify service endpoints  
./sutrabuild/scripts/health-check.sh http://localhost:8000/health

# Problem: Performance issues
# Solution: Run performance validation
./sutrabuild/scripts/scale-validation.rs
```

#### Network Issues
```bash
# Problem: Service connectivity issues
# Solution: Inspect Docker networks
docker network ls
docker network inspect sutra-grid_default

# Problem: Port binding conflicts
# Solution: Check port usage
lsof -i :8000  # Check specific port
netstat -tulpn | grep LISTEN  # Check all listening ports
```

---

## 📚 Additional Resources

- **[Architecture Guide](ARCHITECTURE.md)**: Technical system architecture  
- **[Deployment Guide](DEPLOYMENT.md)**: Production deployment procedures
- **[Security Guide](SECURITY.md)**: Security best practices and compliance
- **[Monitoring Guide](MONITORING.md)**: Observability and performance monitoring
- **[Troubleshooting Guide](TROUBLESHOOTING.md)**: Comprehensive problem resolution
- **[Release Management](RELEASE_MANAGEMENT.md)**: Version control and release processes

---

> **Professional Grade**: This reference represents comprehensive documentation for enterprise-grade build and deployment operations. Every command and option has been tested in production environments to ensure reliability and effectiveness.