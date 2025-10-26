# Release Process - Sutra AI

**Simple release management for small teams ready to onboard customers**

This document describes the complete release process for Sutra AI, designed for small companies that need professional release management without excessive complexity.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Version Management](#version-management)
3. [Release Workflow](#release-workflow)
4. [Commands Reference](#commands-reference)
5. [GitHub Actions](#github-actions)
6. [Customer Deployments](#customer-deployments)
7. [Troubleshooting](#troubleshooting)

---

## Overview

### Release Philosophy

As a small company onboarding customers, we need:
- ✅ **Predictable releases** - Customers can rely on stable versions
- ✅ **Easy rollbacks** - Quick revert if issues arise
- ✅ **Clear versioning** - Semantic versioning (MAJOR.MINOR.PATCH)
- ✅ **Automated builds** - Consistent Docker images per release
- ✅ **Simple workflow** - 3 commands to create a release

### Key Components

1. **VERSION file** - Single source of truth for current version
2. **sutra-deploy.sh** - Release commands (`version`, `release`, `deploy`)
3. **GitHub Actions** - Automated Docker builds and releases
4. **Docker image tags** - Every service tagged with version number

---

## Version Management

### Semantic Versioning

We follow [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH

Example: 2.1.3
         │ │ │
         │ │ └─ Patch: Bug fixes (backward compatible)
         │ └─── Minor: New features (backward compatible)
         └───── Major: Breaking changes
```

**Version Bumping Rules:**

- **Patch** (2.0.0 → 2.0.1): Bug fixes, security patches, minor improvements
- **Minor** (2.0.0 → 2.1.0): New features, API additions (no breaking changes)
- **Major** (2.0.0 → 3.0.0): Breaking API changes, major architecture changes

### VERSION File

Located at repo root: `/VERSION`

```bash
# Check current version
cat VERSION
# Output: 2.0.0
```

This single file controls:
- Docker image tags (e.g., `sutra-api:2.0.0`)
- README badge
- Git tags (e.g., `v2.0.0`)

---

## Release Workflow

### Step-by-Step Release Process

#### 1. Check Current Version

```bash
./sutra-deploy.sh version
```

**Output:**
```
ℹ Current version: v2.0.0
```

#### 2. Create Release

```bash
# For bug fixes
./sutra-deploy.sh release patch

# For new features
./sutra-deploy.sh release minor

# For breaking changes
./sutra-deploy.sh release major
```

**Example: Patch Release (2.0.0 → 2.0.1)**

```bash
$ ./sutra-deploy.sh release patch

ℹ Current version: v2.0.0
▶ Bumping PATCH version (bug fixes)

⚠ Release Summary:
  Current: v2.0.0
  New:     v2.0.1
  Type:    patch

Proceed with release v2.0.1? (y/N) y

✓ Updated VERSION file to v2.0.1
✓ Updated README.md version badge
✓ Created git tag v2.0.1

🎉 Release v2.0.1 ready!

Next steps:
  1. Review changes: git show v2.0.1
  2. Push to GitHub: git push origin main --tags
  3. GitHub Actions will automatically:
     - Build Docker images with tag v2.0.1
     - Create GitHub release
     - Generate release notes

To deploy this version:
  ./sutra-deploy.sh deploy v2.0.1
```

#### 3. Push to GitHub

```bash
# Push commits and tags
git push origin main --tags
```

This triggers **GitHub Actions** which will:
1. Build all Docker images with version tag
2. Push images to GitHub Container Registry
3. Create GitHub Release with auto-generated notes
4. Validate images are accessible

#### 4. Wait for GitHub Actions

Monitor build at: `https://github.com/YOUR_ORG/sutra-models/actions`

Typically takes 10-15 minutes to:
- Build 10+ Docker images
- Run multi-arch builds (amd64 + arm64)
- Push to registry
- Create release

#### 5. Verify Release

**Check Docker Images:**
```bash
# List available versions
docker search ghcr.io/YOUR_ORG/sutra-api --limit 5

# Pull specific version
docker pull ghcr.io/YOUR_ORG/sutra-api:2.0.1
```

**Check GitHub Release:**
Visit: `https://github.com/YOUR_ORG/sutra-models/releases/latest`

---

## Commands Reference

### Version Commands

#### Show Current Version
```bash
./sutra-deploy.sh version
```

Shows version from `VERSION` file.

#### Create Release

```bash
./sutra-deploy.sh release <type>
```

**Arguments:**
- `patch` - Bug fixes (2.0.0 → 2.0.1)
- `minor` - New features (2.0.0 → 2.1.0)
- `major` - Breaking changes (2.0.0 → 3.0.0)

**What it does:**
1. Reads current version from `VERSION` file
2. Bumps version according to type
3. Updates `VERSION` file
4. Updates README.md badge
5. Creates git commit
6. Creates git tag (e.g., `v2.0.1`)
7. Prompts to push to GitHub

**Example:**
```bash
./sutra-deploy.sh release minor
# Creates v2.1.0 from v2.0.0
```

#### Deploy Specific Version

```bash
./sutra-deploy.sh deploy <version>
```

**Arguments:**
- `<version>` - Version tag (e.g., `v2.0.1`) or `latest`

**What it does:**
1. Exports `SUTRA_VERSION` environment variable
2. Pulls Docker images for specified version
3. Starts services with that version
4. Shows service status

**Example:**
```bash
# Deploy specific version
./sutra-deploy.sh deploy v2.0.1

# Deploy latest
./sutra-deploy.sh deploy latest
```

---

## GitHub Actions

### Automatic Release Pipeline

File: `.github/workflows/release.yml`

**Triggers:**
- Push of version tags (e.g., `v2.0.1`, `v2.1.0`)

**Jobs:**

#### 1. Build & Push Docker Images
- Builds all services in parallel (10+ images)
- Multi-architecture: `linux/amd64`, `linux/arm64`
- Tags images:
  - `ghcr.io/YOUR_ORG/sutra-api:2.0.1` (version-specific)
  - `ghcr.io/YOUR_ORG/sutra-api:latest` (latest tag)
- Uses build cache for faster builds

**Services built:**
- `storage-server`
- `grid-master`
- `grid-agent`
- `api`
- `hybrid`
- `embedding-service`
- `nlg-service`
- `control`
- `client`
- `bulk-ingester`

#### 2. Create GitHub Release
- Generates release notes from commits
- Creates downloadable release assets
- Links to Docker images
- Includes deployment instructions

#### 3. Validate Release
- Pulls key images to verify accessibility
- Reports validation status

**Monitoring:**

View builds: `https://github.com/YOUR_ORG/sutra-models/actions`

**Build times:**
- ~10-15 minutes for full release
- Parallel builds for all services

---

## Customer Deployments

### Deploying to Customer Environments

#### Option 1: Deploy Specific Version (Recommended)

**Customer setup:**
```bash
# Clone repository
git clone https://github.com/YOUR_ORG/sutra-models.git
cd sutra-models

# Checkout specific version
git checkout v2.0.1

# Configure edition
export SUTRA_EDITION=community
export SUTRA_LICENSE_KEY=customer-license-key

# Deploy that version
export SUTRA_VERSION=2.0.1
./sutra-deploy.sh install
```

#### Option 2: Deploy Latest

**For customers who want automatic updates:**
```bash
export SUTRA_EDITION=community
export SUTRA_LICENSE_KEY=customer-license-key
./sutra-deploy.sh install
```

This uses `:latest` tags, which get updated with each release.

#### Option 3: Use Pre-built Images

**For air-gapped or restricted environments:**

```bash
# Pull specific version
docker pull ghcr.io/YOUR_ORG/sutra-storage-server:2.0.1
docker pull ghcr.io/YOUR_ORG/sutra-api:2.0.1
# ... etc for all services

# Save images
docker save -o sutra-2.0.1.tar \
  ghcr.io/YOUR_ORG/sutra-storage-server:2.0.1 \
  ghcr.io/YOUR_ORG/sutra-api:2.0.1

# Transfer to customer environment
# Load on customer side
docker load -i sutra-2.0.1.tar

# Deploy
export SUTRA_VERSION=2.0.1
./sutra-deploy.sh deploy v2.0.1
```

### Version Pinning for Customers

**Create customer-specific deployment script:**

```bash
# deploy-customer-acme.sh
#!/bin/bash
set -e

# Pin to tested version
export SUTRA_VERSION=2.0.1
export SUTRA_EDITION=enterprise
export SUTRA_LICENSE_KEY=${ACME_LICENSE_KEY}

# Deploy
./sutra-deploy.sh install

echo "Deployed Sutra AI v2.0.1 for ACME Corp"
```

This ensures customers don't accidentally upgrade to untested versions.

---

## Troubleshooting

### Common Issues

#### 1. "VERSION file not found"

**Solution:**
```bash
# Create VERSION file
echo "2.0.0" > VERSION
```

#### 2. "Failed to create git tag"

**Cause:** Tag already exists

**Solution:**
```bash
# Delete existing tag
git tag -d v2.0.1

# Try release again
./sutra-deploy.sh release patch
```

#### 3. GitHub Actions build fails

**Check:**
1. Dockerfiles are valid
2. No syntax errors in workflow file
3. GitHub Container Registry is accessible

**View logs:**
```bash
# Go to Actions tab on GitHub
https://github.com/YOUR_ORG/sutra-models/actions
```

#### 4. Images not pulling

**Verify registry access:**
```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Try pulling
docker pull ghcr.io/YOUR_ORG/sutra-api:2.0.1
```

#### 5. Version mismatch after deployment

**Check VERSION file:**
```bash
cat VERSION
```

**Check deployed containers:**
```bash
docker ps --format "{{.Names}}: {{.Image}}"
```

**Fix:**
```bash
# Redeploy with correct version
export SUTRA_VERSION=2.0.1
./sutra-deploy.sh deploy v2.0.1
```

---

## Release Checklist

Before each release, verify:

### Pre-Release
- [ ] All tests passing (`pytest -v`)
- [ ] CHANGELOG.md updated with changes
- [ ] No uncommitted changes (`git status`)
- [ ] On correct branch (usually `main`)
- [ ] Version bump makes sense (patch/minor/major)

### During Release
- [ ] `./sutra-deploy.sh version` shows correct current version
- [ ] `./sutra-deploy.sh release <type>` completes successfully
- [ ] Git tag created (`git tag -l`)
- [ ] Pushed to GitHub (`git push origin main --tags`)

### Post-Release
- [ ] GitHub Actions workflow completed successfully
- [ ] Docker images available on registry
- [ ] GitHub release created with notes
- [ ] Can pull and deploy new version
- [ ] Update internal documentation with release notes

---

## Release Schedule (Recommended)

For small teams with customers:

**Patch Releases (Bug Fixes):**
- **Frequency:** As needed (hotfixes)
- **Testing:** Focused on bug fix area
- **Example:** 2.0.0 → 2.0.1

**Minor Releases (Features):**
- **Frequency:** Every 2-4 weeks
- **Testing:** Full regression testing
- **Example:** 2.0.0 → 2.1.0

**Major Releases (Breaking Changes):**
- **Frequency:** Every 3-6 months
- **Testing:** Comprehensive testing + customer beta
- **Example:** 2.0.0 → 3.0.0
- **Communication:** Advance notice to customers (30+ days)

---

## Customer Communication

### Release Announcement Template

```markdown
Subject: Sutra AI v2.1.0 Released - New Features & Improvements

Dear Valued Customer,

We're excited to announce Sutra AI v2.1.0 is now available!

**What's New:**
- Feature X: [Brief description]
- Feature Y: [Brief description]
- Performance improvements: [Brief description]

**Upgrade Instructions:**
https://github.com/YOUR_ORG/sutra-models/releases/tag/v2.1.0

**Breaking Changes:**
None - this is a backward-compatible release.

**Support:**
Contact us at support@sutra-ai.com with any questions.

Best regards,
The Sutra AI Team
```

### For Major Releases (Breaking Changes)

**30 days before:**
- Send advance notice
- Provide migration guide
- Offer beta testing opportunity

**On release day:**
- Send detailed upgrade instructions
- Schedule customer support calls
- Monitor for issues

---

## Quick Reference

### One-Page Cheat Sheet

```bash
# 1. Check version
./sutra-deploy.sh version

# 2. Create release
./sutra-deploy.sh release patch    # Bug fixes
./sutra-deploy.sh release minor    # New features
./sutra-deploy.sh release major    # Breaking changes

# 3. Push to GitHub
git push origin main --tags

# 4. Deploy version
./sutra-deploy.sh deploy v2.0.1

# 5. Check status
./sutra-deploy.sh status
```

**Image naming:**
```
ghcr.io/YOUR_ORG/sutra-<service>:<version>

Examples:
ghcr.io/YOUR_ORG/sutra-api:2.0.1
ghcr.io/YOUR_ORG/sutra-storage-server:2.0.1
```

---

## Support

**Questions about releases?**
- GitHub Issues: https://github.com/YOUR_ORG/sutra-models/issues
- Email: support@sutra-ai.com
- Docs: See this file and WARP.md

**Emergency hotfix needed?**
```bash
# Quick patch release
./sutra-deploy.sh release patch
git push origin main --tags
# Wait for build (~15 min)
# Deploy to affected customers
```

---

**Last Updated:** October 26, 2025  
**Version:** 1.0
