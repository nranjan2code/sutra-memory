# Sutra Documentation Hub

**Production-Ready Domain-Specific Reasoning Engine**

**Version:** 3.0.1 | **Grade:** A+ (98/100) | **Status:** Production-Ready

---

## 🎉 Production Readiness Complete (November 2025)

**NEW: Clean Architecture (v3.0.1) - November 9, 2025**
- **Simplified Architecture**: Single TCP backend (removed RustStorageAdapter, GrpcStorageAdapter)
- **1000+ LOC Removed**: Eliminated dead code and over-engineered patterns
- **27MB Lighter**: Made sklearn/sqlalchemy/hnswlib optional
- **Cleaner Codebase**: Single initialization path, no mode switching
- **Exclusive Product**: No pluggable backends - integrated solution

[**Architecture Changes →**](architecture/CLEAN_ARCHITECTURE_IMPLEMENTATION.md)

**Performance Optimization (v3.0.0) - November 8, 2025**
- **50-70× Throughput Improvements**: 0.13 → 9.06 req/sec (Sequential)
- **100% Async Success**: Fixed dimension mismatch causing 0% success rate
- **Config-Driven Dimensions**: Matryoshka 256-dim support without hardcoded validation
- **TCP Connection Resilience**: Eliminated connection crashes and retry penalties
- **Production Monitoring**: Request tracking and slow query detection

[**Performance Guide →**](architecture/PERFORMANCE_OPTIMIZATION.md) | [**Troubleshooting →**](guides/troubleshooting.md#1-performance-issues-november-2025-)

**Production Validation & Quality Assurance (v2.0.1)**
- **100% Dependency Pinning**: All Python (`==`) and JavaScript (exact) versions locked
- **Automated Testing**: Smoke tests + integration tests + 70% coverage minimum
- **React 18.2.0 Standardized**: Eliminated version conflicts across all packages
- **Reproducible Builds**: "Works on my machine" issues eliminated
- **Production Documentation**: Complete deployment checklists and validation guides

**Production Score: 95/100 → 98/100 (A+ Grade)**

[**Production Fixes Documentation →**](PRODUCTION_FIXES.md) | [**Production Readiness Report →**](PRODUCTION_READINESS_COMPLETE.md)

---

## 🎉 Major Architecture Update (v2.0.0)

**ML-Base Service Architecture**
- **65% Storage Reduction**: From 2.77GB to 1.6GB total
- **Unlimited Horizontal Scaling**: Lightweight clients (50MB each) + centralized inference
- **92% Memory Reduction**: Per client memory usage drops from 1.5GB to 128MB
- **Full API Compatibility**: Existing integrations continue working unchanged

[**Learn More →**](ml-foundation/ML_BASE_SERVICE.md)

## 🚀 Quick Navigation

### Getting Started
**New to Sutra? Start here!**
- [**Quickstart Guide**](getting-started/quickstart.md) - Get running in 5 minutes
- [Editions Overview](getting-started/editions.md) - Choose your edition
- [Tutorial](getting-started/tutorial.md) - Learn Sutra's capabilities

### Build & Deploy
**Ready to build and deploy?**
- [**Build Guide**](build/README.md) - Build Docker images
- [**Deployment Guide**](deployment/README.md) - Deploy all editions
- [Release Management](release/README.md) - Version control and releases

### Core Documentation
- [**Architecture**](architecture/system-overview.md) - System design and components
- [**ML-Base Service**](ml-foundation/ML_BASE_SERVICE.md) - Revolutionary ML architecture (v2.0)
- [**User Guides**](guides/README.md) - Usage guides and best practices
- [**API Reference**](api/README.md) - REST API documentation
- [**Development**](development/README.md) - Developer setup and workflows

## 📚 Documentation Structure

```
docs/
├── getting-started/      # User onboarding (quickstart, tutorials)
├── build/                # Building services & Docker images
├── deployment/           # Deployment guides (simple, community, enterprise)
├── release/              # Version management & release process
├── architecture/         # System architecture & design
├── security/             # Security implementation (httpOnly cookies, TLS, OWASP)
├── guides/               # User & admin guides
├── reference/            # API & CLI reference
└── development/          # Developer documentation (quality gates, pre-commit)
```

## 🎯 Common Tasks

### First Time Setup
```bash
# 1. Clone repository
git clone https://github.com/nranjan2code/sutra-memory
cd sutra-memory

# 2. Build services
SUTRA_EDITION=simple ./sutra-optimize.sh build-all

# 3. Deploy
SUTRA_EDITION=simple ./sutra deploy

# 4. Verify deployment (NEW v2.0.1)
./scripts/smoke-test-embeddings.sh     # Smoke tests (7 services)
./scripts/integration-test.sh          # Integration tests
pytest                                  # Unit tests with coverage

# 5. Check status
./sutra status
```

→ [Full Quickstart Guide](getting-started/quickstart.md) | [Production Validation Guide](PRODUCTION_FIXES.md)

### Build & Deploy Workflow
```bash
# Build all services
./sutra-optimize.sh build-all

# Check build status
./sutra-optimize.sh sizes

# Deploy specific edition
SUTRA_EDITION=simple ./sutra deploy

# Validate deployment
./sutra validate
```

→ [Build Documentation](build/README.md) | [Deployment Guide](deployment/README.md)

### Release Management
```bash
# Check current version
./sutra-deploy.sh version

# Create new release
./sutra-deploy.sh release patch|minor|major

# Push and trigger automated builds
git push origin main --tags
```

→ [Release Management](release/README.md)

## 🏗️ System Architecture

Sutra is a **12-service distributed system** for explainable reasoning:

**Core Components:**
- **Storage Layer** (Rust): High-performance graph storage with HNSW vector indexing
- **Reasoning Engine** (Python): Graph traversal with confidence scoring
- **ML Foundation**: Embedding & NLG services
- **API Layer**: REST APIs and hybrid orchestration
- **Grid Layer** (Enterprise): Distributed coordination and sharding

→ [Architecture Overview](architecture/system-overview.md)

## 📖 Key Topics

### For Users
- [Getting Started](getting-started/README.md) - Installation and first steps
- [Editions Guide](getting-started/editions.md) - Simple vs Community vs Enterprise
- [User Guide](guides/user-guide.md) - Using Sutra's features
- [Troubleshooting](guides/troubleshooting.md) - Common issues and solutions

### For Operators
- [Deployment Guide](deployment/README.md) - Deploy all editions
- [Production Guide](deployment/production.md) - Production best practices
- [Validation](deployment/validation.md) - Healthchecks and monitoring
- [Infrastructure](deployment/infrastructure.md) - System requirements

### For Developers
- [Build Guide](build/README.md) - Building from source
- [Development Setup](development/README.md) - Dev environment setup
- [Contributing](guides/contributing.md) - Contribution guidelines
- [API Reference](api/README.md) - API documentation

### For Release Managers
- [Release Process](release/RELEASE_PROCESS.md) - Step-by-step workflow
- [Versioning Strategy](release/VERSIONING_STRATEGY.md) - Version bumping rules
- [Changelog](release/changelog.md) - Version history

## 🔍 What Makes Sutra Different?

Unlike general LLMs, Sutra:

1. **Domain-Specific**: Starts empty, learns from YOUR proprietary data
2. **Explainable**: Complete audit trails with confidence scores
3. **Compliant**: Built for regulated industries (medical, legal, financial)
4. **Real-time Learning**: No retraining required - learns incrementally
5. **Self-Contained**: Your data never leaves your infrastructure
6. **Production-Grade Security**: httpOnly cookies (XSS immune), 8-layer OWASP headers, TLS 1.3
7. **Quality Enforced**: Automated pre-commit hooks, CI validation, bundle size limits

## 📊 Performance

- **Learning**: 57K concepts/second
- **Query**: <0.01ms (zero-copy mmap)
- **Startup**: 3.5ms for 1M vectors
- **Scale**: 10M+ concepts across 16 shards
- **Memory**: Efficient per-concept storage

→ [Performance Details](architecture/runtime.md)

## 🏢 Editions

### Simple Edition (8 services)
- Single-node deployment
- All core functionality
- **Size**: 4.4GB
- **Use**: Development, small deployments

### Community Edition (13 containers)
- High-availability ML services
- 3x embedding replicas + HAProxy
- Automatic failover
- **Size**: ~6GB
- **Use**: Production HA deployments

### Enterprise Edition (10 services)
- Distributed grid infrastructure
- Multi-shard storage with 2PC
- Grid coordinator + workers
- **Size**: 4.76GB
- **Use**: High-scale, multi-tenant

→ [Editions Comparison](getting-started/editions.md) | [Pricing](PRICING.md)

## 🛠️ System Requirements

**Minimum:**
- Docker 20.10+
- 8GB RAM
- 20GB disk
- 4 CPU cores

**Recommended:**
- Docker Latest
- 16GB RAM
- 50GB SSD
- 8 CPU cores

→ [Full Requirements](deployment/infrastructure.md)

## 📞 Support & Community

- **Issues**: [GitHub Issues](https://github.com/nranjan2code/sutra-memory/issues)
- **Discussions**: [GitHub Discussions](https://github.com/nranjan2code/sutra-memory/discussions)
- **Contributing**: [Contribution Guide](guides/contributing.md)

## 📝 License

See [LICENSE](../LICENSE) for details.

---

**Version**: 2.0.0 | **Updated**: October 2025
