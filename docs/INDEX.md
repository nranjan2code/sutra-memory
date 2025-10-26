# Sutra AI Documentation Index

**Complete technical documentation for the Sutra AI distributed reasoning system**

---

## 🚀 Getting Started

New to Sutra AI? Start here:

1. **[Quick Start Guide](QUICKSTART.md)** - Get running in 5 minutes
2. **[System Overview](SYSTEM_OVERVIEW.md)** - Understand the architecture
3. **[Tutorial](TUTORIAL.md)** - Build your first knowledge graph

---

## � Release Management (NEW)

**Professional release management for production deployments:**

### Essential Docs
- **[Release Overview](release/README.md)** - Complete release system documentation
- **[Release Process](release/RELEASE_PROCESS.md)** - Step-by-step release workflow
- **[Quick Reference](release/QUICK_REFERENCE.md)** - Command cheat sheet
- **[Versioning Strategy](release/VERSIONING_STRATEGY.md)** - When to bump versions

### Quick Commands
```bash
./sutra-deploy.sh version          # Check current version
./sutra-deploy.sh release patch    # Create bug fix release
./sutra-deploy.sh deploy v2.0.1    # Deploy specific version
```

**Use for:** Creating releases, deploying to customers, version management

---

## Package Documentation

### Core Packages
- [sutra-storage](../packages/sutra-storage/README.md) - Storage engine (Rust)
- [sutra-core](../packages/sutra-core/README.md) - Reasoning engine (Python)
- [sutra-hybrid](../packages/sutra-hybrid/README.md) - Semantic orchestration
- [sutra-api](../packages/sutra-api/README.md) - REST API

### Support Packages
- [sutra-nlg](../packages/sutra-nlg/README.md) - Natural language generation
- [sutra-storage-client-tcp](../packages/sutra-storage-client-tcp/README.md) - TCP client

### Grid Infrastructure
- [sutra-grid-master](../packages/sutra-grid-master/README.md) - Orchestration
- [sutra-grid-agent](../packages/sutra-grid-agent/README.md) - Node management
- [sutra-grid-events](../packages/sutra-grid-events/README.md) - Event system

### UI & Tools
- [sutra-control](../packages/sutra-control/README.md) - Control center
- [sutra-client](../packages/sutra-client/README.md) - Web UI
- [sutra-explorer](../packages/sutra-explorer/README.md) - Storage explorer

---

## Architecture

- [System Architecture](ARCHITECTURE.md) - High-level design
- [Storage Architecture](storage/ARCHITECTURE.md) - Storage engine
- [TCP Protocol](TCP_PROTOCOL_ARCHITECTURE.md) - Binary protocol

---

## Operations

- [Deployment](operations/DEPLOYMENT.md) - Production deployment
- [Monitoring](operations/MONITORING.md) - Observability
- [Production Requirements](operations/PRODUCTION_REQUIREMENTS.md) - Critical config
- [Troubleshooting](./TROUBLESHOOTING.md) - Common issues

---

## Development

- [Development Guide](guides/DEVELOPMENT.md) - Setup
- **[Fast Development Workflow](../FAST_DEVELOPMENT.md)** - **NEW: Single-service updates**
- **[Simple Deployment Solution](../SIMPLE_DEPLOYMENT_SOLUTION.md)** - **NEW: What we built**
- [Contributing](./CONTRIBUTING.md) - How to contribute
- [Testing](development/testing.md) - Test procedures

---

## Security & Compliance

### Dependency Management
- [Quick Start](dependency-management/QUICK_START.md) - Get started in 5 minutes
- [Architecture](dependency-management/ARCHITECTURE.md) - System design
- [Design](dependency-management/DESIGN.md) - Design principles
- [Documentation Index](dependency-management/README.md) - All dependency docs

### Security
- [Security Overview](security/README.md) - Security documentation
- [Production Security](security/PRODUCTION_SECURITY_SETUP.md) - Production setup
- [Security Audit](security/SECURITY_AUDIT_REPORT.md) - Vulnerability analysis

---

## Reference

- [Documentation Audit](DOCUMENTATION_AUDIT_2025.md) - Complete analysis
- [Completion Summary](DOCUMENTATION_COMPLETION_SUMMARY.md) - Roadmap

---

**Last Updated**: October 25, 2025
