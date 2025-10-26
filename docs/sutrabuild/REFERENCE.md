# Sutra AI Build System - Complete Reference

**Comprehensive command reference and configuration options**

## 🎯 Master Build Script

### Syntax
```bash
./sutrabuild/scripts/build-all.sh [OPTIONS]
```

### Required Options

| Option | Values | Description |
|--------|--------|-------------|
| `--profile` | `simple`\|`community`\|`enterprise` | Build profile determining which services to include |

### Optional Parameters

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--version` | `<tag>` | `latest` | Docker image tag for all built services |
| `--parallel` | `true`\|`false` | `false` | Build services concurrently (requires 4+ cores) |
| `--verbose` | N/A | `false` | Show detailed Docker build output |
| `--clean` | N/A | `false` | Force rebuild of base images |
| `--help` | N/A | N/A | Display usage information and exit |

## 📋 Build Profiles

### Simple Profile (`--profile simple`)
**Target**: Local development, demos, minimal deployment
**Services**: 4 core services
**Build Time**: ~3 minutes
**Resource Requirements**: 4GB RAM, 8GB disk

```bash
Services Built:
├── sutra-storage (Rust binary - 167MB)
├── sutra-api (Python FastAPI - 624MB)  
├── sutra-hybrid (Python ML - 624MB)
└── sutra-embedding-service (PyTorch - 624MB)

Base Images:
├── sutra-python-base:latest (624MB)
└── sutra-rust-base:latest (158MB)
```

### Community Profile (`--profile community`)
**Target**: Team development, staging environments
**Services**: 6 services (Simple + enhancements)
**Build Time**: ~4 minutes
**Resource Requirements**: 6GB RAM, 12GB disk

```bash
Additional Services:
├── sutra-user-storage (Authentication)
└── sutra-nlg (Natural Language Generation)
```

### Enterprise Profile (`--profile enterprise`)
**Target**: Production deployment, full feature set
**Services**: 12+ services (Community + grid services)
**Build Time**: ~8 minutes  
**Resource Requirements**: 12GB RAM, 20GB disk

```bash
Additional Services:
├── sutra-grid-master (Distributed coordination)
├── sutra-grid-agent (Compute nodes)
├── sutra-bulk-ingester (High-throughput data)
├── sutra-monitoring (Observability)
└── sutra-gateway (API gateway)
```

## 🔧 Command Examples

### Basic Operations
```bash
# Minimal build for development
./sutrabuild/scripts/build-all.sh --profile simple

# Production build with version tag
./sutrabuild/scripts/build-all.sh --profile community --version v2.1.0

# Enterprise build with parallel execution
./sutrabuild/scripts/build-all.sh --profile enterprise --parallel
```

### Advanced Operations
```bash
# Force clean rebuild (ignores cache)
./sutrabuild/scripts/build-all.sh --profile simple --clean

# Verbose output for debugging
./sutrabuild/scripts/build-all.sh --profile simple --verbose

# Tagged parallel build
./sutrabuild/scripts/build-all.sh --profile enterprise --version v2.1.0 --parallel --verbose
```

### Development Workflows
```bash
# Initial setup
./sutrabuild/scripts/build-all.sh --profile simple

# Incremental rebuild after code changes
./sutrabuild/scripts/build-all.sh --profile simple

# Test different profile
./sutrabuild/scripts/build-all.sh --profile community
```

## 🏥 Health Check Utility

### Syntax
```bash
./sutrabuild/scripts/health-check.sh <url> [timeout] [retries]
```

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `url` | Yes | N/A | HTTP endpoint to check |
| `timeout` | No | `3` | Timeout in seconds |
| `retries` | No | `1` | Number of retry attempts |

### Examples
```bash
# Basic health check
./sutrabuild/scripts/health-check.sh http://localhost:8000/health

# With custom timeout and retries
./sutrabuild/scripts/health-check.sh http://localhost:8000/health 5 3

# Check multiple services
./sutrabuild/scripts/health-check.sh http://localhost:8000/health    # API
./sutrabuild/scripts/health-check.sh http://localhost:8001/health    # Hybrid
./sutrabuild/scripts/health-check.sh http://localhost:8889/health    # Embedding
```

### Return Codes
- `0`: Health check successful
- `1`: Health check failed after all retries

## 🐳 Docker Compose Integration

### Unified Compose File
**Location**: `sutrabuild/compose/docker-compose.yml`

### Profile Usage
```bash
# Start services for specific profile
docker-compose -f sutrabuild/compose/docker-compose.yml --profile simple up -d

# Scale services
docker-compose -f sutrabuild/compose/docker-compose.yml --profile simple up -d --scale sutra-api=2

# View logs
docker-compose -f sutrabuild/compose/docker-compose.yml --profile simple logs -f

# Stop services  
docker-compose -f sutrabuild/compose/docker-compose.yml --profile simple down
```

## 🏗️ Dockerfile Locations

### Base Images
```bash
sutrabuild/docker/base/
├── python-base.dockerfile    # Python 3.11 + common dependencies
└── rust-base.dockerfile      # Rust 1.82 + runtime essentials
```

### Service Images
```bash
sutrabuild/docker/services/
├── sutra-api.dockerfile
├── sutra-hybrid.dockerfile
├── sutra-storage.dockerfile
├── sutra-embedding-service.dockerfile
├── sutra-user-storage.dockerfile         # Community+
├── sutra-nlg.dockerfile                  # Community+
├── sutra-grid-master.dockerfile          # Enterprise
├── sutra-grid-agent.dockerfile           # Enterprise
└── sutra-bulk-ingester.dockerfile        # Enterprise
```

## 🔄 Environment Variables

### Build-Time Variables
```bash
# Version control
export SUTRA_VERSION=v2.1.0
export DOCKER_BUILDKIT=1

# Performance tuning
export DOCKER_CLI_EXPERIMENTAL=enabled
export BUILDKIT_PROGRESS=plain
```

### Runtime Variables
```bash
# Profile selection
export SUTRA_EDITION=simple        # simple|community|enterprise
export SUTRA_ENVIRONMENT=dev       # dev|staging|production

# Resource limits
export SUTRA_API_MEMORY=1g
export SUTRA_STORAGE_MEMORY=2g
```

## 📊 Build Output Reference

### Successful Build Output
```bash
╔═══════════════════════════════════════════════════════════════╗
║              Sutra AI - Master Build System v3.0             ║
║                    🏗️  BUILD CONSOLIDATION                   ║
╚═══════════════════════════════════════════════════════════════╝

ℹ Profile: simple
ℹ Version: latest
ℹ Parallel: false

ℹ Building shared base images...
ℹ Building sutra-python-base...
✓ Base images built successfully

ℹ Building service images for profile: simple...
ℹ Building sutra-storage...
✓ Built sutra-storage
ℹ Building sutra-api...
✓ Built sutra-api
ℹ Building sutra-hybrid...
✓ Built sutra-hybrid
ℹ Building sutra-embedding-service...
✓ Built sutra-embedding-service

✓ All service images built for profile: simple
ℹ Verifying built images...
✓ All images verified successfully

✓ ═══════════════════════════════════════════════════
✓   BUILD COMPLETE: Sutra AI simple Edition
✓ ═══════════════════════════════════════════════════

ℹ Built images:
REPOSITORY                TAG               SIZE
sutra-embedding-service   latest            624MB
sutra-hybrid              latest            624MB
sutra-api                 latest            624MB
sutra-storage             latest            167MB
sutra-rust-base           latest            158MB
sutra-python-base         latest            624MB
```

### Error Output Patterns
```bash
# Build failure
❌ Failed to build sutra-api
Error: [Dockerfile syntax error or dependency issue]

# Missing Docker
❌ Docker not found. Please install Docker and try again.

# Insufficient resources
❌ Build failed: No space left on device
```

## 🔧 Customization Options

### Custom Build Variants
```bash
# Create custom profile by modifying build script
cp sutrabuild/scripts/build-all.sh sutrabuild/scripts/build-custom.sh

# Add custom services to profile
case "$PROFILE" in
    custom)
        services+=(
            "my-custom-service:sutrabuild/docker/services/my-service.dockerfile"
        )
        ;;
esac
```

### Build Arguments
```bash
# Pass build arguments to Docker
export DOCKER_BUILDKIT=1
./sutrabuild/scripts/build-all.sh --profile simple
```

### Registry Integration
```bash
# Tag for registry push
docker tag sutra-api:latest registry.company.com/sutra-api:v2.1.0

# Push to registry
docker push registry.company.com/sutra-api:v2.1.0
```

## 📈 Performance Tuning

### Build Cache Optimization
```bash
# Check cache usage
docker system df

# Prune old cache (if needed)
docker builder prune --filter until=24h

# Configure cache size (in Docker Desktop)
# Settings > Resources > Advanced > Disk image size
```

### Parallel Build Requirements
```bash
# Minimum system requirements for --parallel
CPU: 4+ cores
RAM: 8GB+  
Disk: SSD recommended
Network: Stable internet connection

# Monitor resource usage during parallel builds
htop  # or docker stats
```

### Build Time Optimization
```bash
# Use .dockerignore to reduce build context
echo "*.log" >> .dockerignore
echo "node_modules" >> .dockerignore  
echo ".git" >> .dockerignore

# Keep base images to leverage caching
# Only run 'docker system prune' when necessary
```

## 🔍 Debugging

### Verbose Build Output
```bash
# Enable detailed logging
./sutrabuild/scripts/build-all.sh --profile simple --verbose

# Docker BuildKit progress
export BUILDKIT_PROGRESS=plain
./sutrabuild/scripts/build-all.sh --profile simple
```

### Build Context Analysis
```bash
# Check what's being sent to Docker daemon
docker build --progress=plain --no-cache -f sutrabuild/docker/base/python-base.dockerfile .
```

### Image Inspection
```bash
# Analyze built images
docker images sutra-*
docker history sutra-api:latest
docker inspect sutra-api:latest
```

---

> **Complete Documentation**: See [ARCHITECTURE.md](ARCHITECTURE.md) for technical deep-dive, [QUICKSTART.md](QUICKSTART.md) for immediate productivity, and [MAINTENANCE.md](MAINTENANCE.md) for ongoing operations.