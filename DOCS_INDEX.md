# Sutra AI - Documentation Index

**Single source of truth for all documentation.**

## 🎯 Start Here

### New Users
1. **[README.md](README.md)** - Project overview and quick start
2. **[BUILD_AND_DEPLOY.md](BUILD_AND_DEPLOY.md)** - ⭐ **Build and deployment guide** (MANDATORY)
3. **[docs/PRODUCTION_GUIDE.md](docs/PRODUCTION_GUIDE.md)** - Complete production documentation

### Developers
1. **[WARP.md](WARP.md)** - ⭐ **AI assistant guidance** (comprehensive technical reference)
2. **[BUILD_AND_DEPLOY.md](BUILD_AND_DEPLOY.md)** - Build system and deployment
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture

### Operations
1. **[BUILD_AND_DEPLOY.md](BUILD_AND_DEPLOY.md)** - Deployment procedures
2. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Issue resolution
3. **[docs/PRODUCTION_GUIDE.md](docs/PRODUCTION_GUIDE.md)** - Production operations

## 📚 Core Documentation

### Build & Deploy (⭐ CRITICAL)
- **[BUILD_AND_DEPLOY.md](BUILD_AND_DEPLOY.md)** - **SINGLE SOURCE OF TRUTH** for building and deploying
  - All 9 services (ZERO failures accepted)
  - Official Docker images (rust:1.82-slim, python:3.11-slim, node:18-slim)
  - Complete troubleshooting
  - Development workflow
  - Production requirements

### Architecture & Design
- **[WARP.md](WARP.md)** - Comprehensive technical reference for AI assistants
  - Embedding system requirements (CRITICAL)
  - Unified learning architecture
  - TCP binary protocol
  - Package structure
  - Development commands
  - Common errors and fixes
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture overview
- **[docs/grid/architecture/GRID_ARCHITECTURE.md](docs/grid/architecture/GRID_ARCHITECTURE.md)** - Sutra Grid distributed system

### Production Operations
- **[docs/PRODUCTION_GUIDE.md](docs/PRODUCTION_GUIDE.md)** - Complete production guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment documentation
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Troubleshooting guide
- **[PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)** - Pre-deployment verification

### Specific Features
- **[EMBEDDING_SERVICE_MIGRATION.md](EMBEDDING_SERVICE_MIGRATION.md)** - Embedding service details
- **[EMBEDDING_SERVICE.md](EMBEDDING_SERVICE.md)** - Embedding configuration
- **[docs/EMBEDDING_TROUBLESHOOTING.md](docs/EMBEDDING_TROUBLESHOOTING.md)** - Embedding fixes
- **[BULK_INGESTER_INTEGRATION.md](BULK_INGESTER_INTEGRATION.md)** - Bulk data ingestion

### Development
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md)** - Performance optimizations

## 🔧 Scripts Reference

### Build Scripts
- **`build-all.sh`** - Build all 9 Docker services (REQUIRED)
- **`verify-build.sh`** - Verify all services built successfully
- **`clean-and-rebuild.sh`** - Complete fresh install

### Deployment Scripts
- **`sutra-deploy.sh`** - Main deployment script
  - `up` - Start all services
  - `down` - Stop all services
  - `status` - Check health
  - `logs` - View logs
  - `validate` - Run health checks
  - `clean` - Remove all data

### Testing Scripts
- **`test_direct_workflow.py`** - End-to-end test
- **`scripts/smoke-test-embeddings.sh`** - Embedding validation

## 🎓 Learning Path

### 1. First Time Setup
1. Read [README.md](README.md) - Understand what Sutra AI is
2. Read [BUILD_AND_DEPLOY.md](BUILD_AND_DEPLOY.md) - Learn build process
3. Run `./build-all.sh` - Build all services
4. Run `./verify-build.sh` - Verify build
5. Run `./sutra-deploy.sh up` - Deploy system
6. Read [docs/PRODUCTION_GUIDE.md](docs/PRODUCTION_GUIDE.md) - Learn operations

### 2. Development
1. Read [WARP.md](WARP.md) - Technical reference
2. Read [ARCHITECTURE.md](ARCHITECTURE.md) - System design
3. Read [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
4. Start building!

### 3. Production Deployment
1. Read [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) - Pre-deployment
2. Run `./scripts/smoke-test-embeddings.sh` - Validate embedding config
3. Follow [BUILD_AND_DEPLOY.md](BUILD_AND_DEPLOY.md) - Deploy
4. Read [docs/PRODUCTION_GUIDE.md](docs/PRODUCTION_GUIDE.md) - Operations
5. Keep [TROUBLESHOOTING.md](TROUBLESHOOTING.md) handy

## 🚨 Critical Requirements

**Before any deployment, you MUST:**
1. ✅ Build all 9 services successfully (run `./verify-build.sh`)
2. ✅ Use official Docker images (rust:1.82-slim, python:3.11-slim, node:18-slim)
3. ✅ Configure embedding service correctly (see [WARP.md](WARP.md))
4. ✅ Validate with `./scripts/smoke-test-embeddings.sh`

**Zero failures accepted. All services are required.**

## 📊 Documentation Status

| Document | Status | Purpose | Audience |
|----------|--------|---------|----------|
| [BUILD_AND_DEPLOY.md](BUILD_AND_DEPLOY.md) | ⭐ **CRITICAL** | Build & deploy guide | All |
| [WARP.md](WARP.md) | ⭐ **CRITICAL** | Technical reference | AI/Devs |
| [README.md](README.md) | ✅ Current | Project overview | All |
| [docs/PRODUCTION_GUIDE.md](docs/PRODUCTION_GUIDE.md) | ✅ Current | Production ops | Ops |
| [ARCHITECTURE.md](ARCHITECTURE.md) | ✅ Current | System design | Devs |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | ✅ Current | Issue resolution | Ops |
| [DEPLOYMENT.md](DEPLOYMENT.md) | ⚠️ Outdated | See BUILD_AND_DEPLOY.md | - |

## 🔄 Document Relationships

```
README.md
  ├─→ BUILD_AND_DEPLOY.md (build & deploy)
  ├─→ docs/PRODUCTION_GUIDE.md (operations)
  └─→ ARCHITECTURE.md (design)

WARP.md (AI assistant reference)
  ├─→ BUILD_AND_DEPLOY.md (build process)
  ├─→ EMBEDDING_SERVICE_MIGRATION.md (embedding details)
  └─→ docs/grid/architecture/GRID_ARCHITECTURE.md (Grid details)

BUILD_AND_DEPLOY.md (SINGLE SOURCE OF TRUTH)
  ├─→ TROUBLESHOOTING.md (issues)
  ├─→ OPTIMIZATION_SUMMARY.md (optimizations)
  └─→ QUICK_START_OPTIMIZATION.md (quick ref)
```

## 🆘 Need Help?

1. **Build failing?** → [BUILD_AND_DEPLOY.md](BUILD_AND_DEPLOY.md) Troubleshooting section
2. **Deployment issues?** → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. **Embedding errors?** → [docs/EMBEDDING_TROUBLESHOOTING.md](docs/EMBEDDING_TROUBLESHOOTING.md)
4. **General questions?** → [docs/PRODUCTION_GUIDE.md](docs/PRODUCTION_GUIDE.md)

## 📝 Update Guidelines

**When updating documentation:**
1. ✅ Update [BUILD_AND_DEPLOY.md](BUILD_AND_DEPLOY.md) for build/deploy changes
2. ✅ Update [WARP.md](WARP.md) for technical changes
3. ✅ Update [README.md](README.md) for major features
4. ✅ Update this index if adding/removing docs
5. ✅ Update [CHANGELOG.md](CHANGELOG.md) for version changes

**Keep documentation DRY:**
- One source of truth per topic
- Cross-reference instead of duplicating
- Update this index when restructuring
