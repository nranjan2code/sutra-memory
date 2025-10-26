# Release Management Documentation

**Professional release management for Sutra AI**

This directory contains complete documentation for managing releases, deployments, and customer version control.

---

## 📚 Documentation Structure

### Getting Started
- **[RELEASE_PROCESS.md](RELEASE_PROCESS.md)** - Complete release workflow guide
  - Version management
  - Release commands
  - GitHub Actions pipeline
  - Customer deployments
  - Troubleshooting

### Setup & Configuration
- **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** - Implementation summary
  - What was created
  - System architecture
  - Next steps
  - Testing guide

### Quick References
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command cheat sheet
  - Common commands
  - Examples
  - One-page reference

### Version History
- **[VERSIONING_STRATEGY.md](VERSIONING_STRATEGY.md)** - Semantic versioning guide
  - When to bump versions
  - Version number meanings
  - Release schedules

---

## 🚀 Quick Start

### Check Current Version
```bash
./sutra-deploy.sh version
```

### Create a Release
```bash
# Bug fixes
./sutra-deploy.sh release patch

# New features  
./sutra-deploy.sh release minor

# Breaking changes
./sutra-deploy.sh release major

# Push to trigger automated builds
git push origin main --tags
```

### Deploy Specific Version
```bash
./sutra-deploy.sh deploy v2.0.1
```

---

## 🎯 Core Concepts

### 1. Centralized Version Control
- Single `VERSION` file at repo root
- All packages use this version
- Docker images tagged with version

### 2. Semantic Versioning
```
MAJOR.MINOR.PATCH
  │     │     │
  │     │     └─ Bug fixes (2.0.0 → 2.0.1)
  │     └─────── New features (2.0.0 → 2.1.0)
  └───────────── Breaking changes (2.0.0 → 3.0.0)
```

### 3. Automated Pipeline
- Push tag → GitHub Actions builds everything
- Multi-arch Docker images (amd64 + arm64)
- Automatic GitHub releases
- ~15 minute build time

### 4. Customer Deployments
- Pin to specific versions
- Easy rollbacks
- Clear upgrade paths

---

## 📋 Release Workflow

```mermaid
graph LR
    A[Edit Code] --> B[Test]
    B --> C[Update CHANGELOG]
    C --> D[Create Release]
    D --> E[Push Tags]
    E --> F[GitHub Actions Build]
    F --> G[Docker Images Published]
    G --> H[GitHub Release Created]
    H --> I[Customers Deploy]
```

**Detailed steps:**
1. **Development** - Make changes, test locally
2. **Documentation** - Update CHANGELOG.md with changes
3. **Release** - Run `./sutra-deploy.sh release <type>`
4. **Publish** - Run `git push origin main --tags`
5. **Automated** - GitHub Actions builds & publishes
6. **Deploy** - Customers use tagged versions

---

## 🔧 Key Files

### Repository Files
```
/VERSION                           # Current version (2.0.0)
/RELEASE.md                        # Quick reference
/sutra-deploy.sh                   # Release commands
/docker-compose-grid.yml           # Version-tagged services
/.github/workflows/release.yml     # Automated builds
```

### Documentation Files
```
docs/release/
├── README.md                      # This file
├── RELEASE_PROCESS.md             # Complete guide
├── SETUP_COMPLETE.md              # Setup summary
├── QUICK_REFERENCE.md             # Command cheat sheet
└── VERSIONING_STRATEGY.md         # Version guidelines
```

---

## 🎨 Docker Image Registry

### Image Naming Convention
```
ghcr.io/{YOUR_ORG}/sutra-{service}:{version}
```

### Available Services
- `sutra-storage-server`
- `sutra-api`
- `sutra-hybrid`
- `sutra-grid-master`
- `sutra-grid-agent`
- `sutra-embedding-service`
- `sutra-nlg-service`
- `sutra-control`
- `sutra-client`
- `sutra-bulk-ingester`

### Example Usage
```bash
# Pull specific version
docker pull ghcr.io/YOUR_ORG/sutra-api:2.0.1

# Pull latest
docker pull ghcr.io/YOUR_ORG/sutra-api:latest
```

---

## 👥 For Team Members

### Developers
- **Before committing:** Update CHANGELOG.md
- **Testing:** Use `./sutra-deploy.sh build` locally
- **Releasing:** Only team lead creates releases

### Release Manager
- **Weekly:** Review pending changes for release
- **Release day:** Follow RELEASE_PROCESS.md
- **Post-release:** Monitor GitHub Actions build
- **Communication:** Send customer release notes

### Support Team
- **Know current version:** `./sutra-deploy.sh version`
- **Deployment help:** See RELEASE_PROCESS.md customer section
- **Troubleshooting:** Check RELEASE_PROCESS.md troubleshooting

---

## 📊 Release Schedule (Recommended)

| Release Type | Frequency | Use Case | Example |
|-------------|-----------|----------|---------|
| **Patch** | As needed | Bug fixes, security patches | 2.0.0 → 2.0.1 |
| **Minor** | 2-4 weeks | New features, improvements | 2.0.0 → 2.1.0 |
| **Major** | 3-6 months | Breaking changes, major features | 2.0.0 → 3.0.0 |

---

## ✅ Pre-Release Checklist

Before creating any release:

- [ ] All tests passing (`pytest -v`)
- [ ] CHANGELOG.md updated with changes
- [ ] No uncommitted changes (`git status`)
- [ ] On correct branch (usually `main`)
- [ ] Version bump type makes sense
- [ ] Documentation updated if needed
- [ ] Team aware of release timing

---

## 🆘 Need Help?

### Common Questions
1. **"How do I create a release?"** → See [RELEASE_PROCESS.md](RELEASE_PROCESS.md)
2. **"What version should I use?"** → See [VERSIONING_STRATEGY.md](VERSIONING_STRATEGY.md)
3. **"How do customers deploy?"** → See [RELEASE_PROCESS.md](RELEASE_PROCESS.md#customer-deployments)
4. **"Build failed, what now?"** → See [RELEASE_PROCESS.md](RELEASE_PROCESS.md#troubleshooting)

### Quick Commands
```bash
# Show help
./sutra-deploy.sh help

# Check version
./sutra-deploy.sh version

# Test release (don't push)
./sutra-deploy.sh release patch
git reset --hard HEAD~1  # Undo if testing
git tag -d v2.0.1        # Remove tag
```

### Support Channels
- GitHub Issues: Technical problems
- Team Chat: Quick questions
- Email: Customer-facing issues

---

## 🔗 Related Documentation

### Core System Docs
- [System Overview](../SYSTEM_OVERVIEW.md)
- [Architecture](../ARCHITECTURE.md)
- [Quick Start](../QUICKSTART.md)
- [Production Guide](../PRODUCTION_GUIDE.md)

### Deployment Docs
- [Deployment Guide](../deployment/DEPLOYMENT.md)
- [Docker Compose](../../docker-compose-grid.yml)
- [Fast Development](../../FAST_DEVELOPMENT.md)

### Development Docs
- [Contributing](../CONTRIBUTING.md)
- [Development Guide](../development/)
- [Testing Guide](../../tests/README.md)

---

## 📈 Metrics & Monitoring

### Release Metrics to Track
- **Time to release:** Target < 20 minutes (from tag to published)
- **Build success rate:** Target > 95%
- **Customer deployment success:** Track customer feedback
- **Rollback frequency:** Should be rare

### Monitoring Release Health
```bash
# Check GitHub Actions status
# Visit: https://github.com/YOUR_ORG/sutra-models/actions

# Verify images published
docker pull ghcr.io/YOUR_ORG/sutra-api:latest

# Check release page
# Visit: https://github.com/YOUR_ORG/sutra-models/releases
```

---

## 🎯 Future Enhancements

### Planned Improvements
- [ ] Automated CHANGELOG generation from commits
- [ ] Release candidate (RC) process
- [ ] Beta channel for early adopters
- [ ] Automated security scanning in pipeline
- [ ] Multi-region Docker registry mirrors
- [ ] Release rollback automation

### Under Consideration
- [ ] Homebrew formula for CLI tools
- [ ] PyPI packages for Python libraries
- [ ] NPM packages for JavaScript clients
- [ ] Helm charts for Kubernetes

---

## 📝 Changelog

### v1.0.0 (October 26, 2025)
- Initial release management system
- Centralized VERSION file
- Release commands in sutra-deploy.sh
- GitHub Actions pipeline
- Complete documentation

---

**Last Updated:** October 26, 2025  
**Maintained By:** Sutra AI Team  
**Questions:** Open an issue or see [RELEASE_PROCESS.md](RELEASE_PROCESS.md#support)
