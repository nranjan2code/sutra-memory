# Release Commands - Quick Reference

**One-page cheat sheet for Sutra AI releases**

---

## 📦 Version Commands

### Check Current Version
```bash
./sutra-deploy.sh version
```
**Output:** `Current version: v2.0.0`

---

## 🚀 Creating Releases

### Bug Fix Release (Patch)
**Use for:** Bug fixes, security patches, minor improvements

```bash
./sutra-deploy.sh release patch
git push origin main --tags
```
**Result:** `2.0.0 → 2.0.1`

### Feature Release (Minor)
**Use for:** New features, enhancements (backward compatible)

```bash
./sutra-deploy.sh release minor
git push origin main --tags
```
**Result:** `2.0.0 → 2.1.0`

### Breaking Change Release (Major)
**Use for:** Breaking API changes, major architecture changes

```bash
./sutra-deploy.sh release major
git push origin main --tags
```
**Result:** `2.0.0 → 3.0.0`

---

## 🎯 Deployment Commands

### Deploy Specific Version
```bash
./sutra-deploy.sh deploy v2.0.1
```

### Deploy Latest Version
```bash
./sutra-deploy.sh deploy latest
```

### Check Service Status
```bash
./sutra-deploy.sh status
```

---

## 👥 Customer Deployment

### Standard Deployment
```bash
# 1. Clone repo
git clone https://github.com/YOUR_ORG/sutra-models.git
cd sutra-models

# 2. Checkout version
git checkout v2.0.1

# 3. Configure edition
export SUTRA_EDITION=community
export SUTRA_LICENSE_KEY=customer-license-key

# 4. Deploy
export SUTRA_VERSION=2.0.1
./sutra-deploy.sh install
```

### Quick Deployment (Latest)
```bash
export SUTRA_EDITION=community
export SUTRA_LICENSE_KEY=customer-license-key
./sutra-deploy.sh install
```

---

## 🔄 Rollback

### Rollback to Previous Version
```bash
./sutra-deploy.sh deploy v2.0.0
```

### Check What's Running
```bash
docker ps --format "{{.Names}}: {{.Image}}"
```

---

## 🐳 Docker Images

### Image Naming
```
ghcr.io/YOUR_ORG/sutra-{service}:{version}
```

### Pull Images
```bash
# Specific version
docker pull ghcr.io/YOUR_ORG/sutra-api:2.0.1

# Latest
docker pull ghcr.io/YOUR_ORG/sutra-api:latest
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

---

## 🔍 Troubleshooting

### Check Logs
```bash
./sutra-deploy.sh logs <service>
```

### Rebuild Service
```bash
./sutra-deploy.sh update <service>
```

### Full System Restart
```bash
./sutra-deploy.sh restart
```

### Clean & Rebuild
```bash
./sutra-deploy.sh clean
./sutra-deploy.sh install
```

---

## 📊 Semantic Versioning

```
MAJOR.MINOR.PATCH
  2  . 1  . 3

MAJOR: Breaking changes
MINOR: New features (backward compatible)
PATCH: Bug fixes
```

### Examples
- `2.0.0 → 2.0.1` - Fixed bug
- `2.0.1 → 2.1.0` - Added new feature
- `2.1.0 → 3.0.0` - Changed API (breaking)

---

## ✅ Pre-Release Checklist

- [ ] Tests pass: `pytest -v`
- [ ] Clean git: `git status`
- [ ] CHANGELOG updated
- [ ] On main branch
- [ ] Version bump makes sense

---

## 🔗 More Help

- **Full Guide:** [docs/release/RELEASE_PROCESS.md](RELEASE_PROCESS.md)
- **Setup Info:** [docs/release/SETUP_COMPLETE.md](SETUP_COMPLETE.md)
- **All Docs:** [docs/release/README.md](README.md)

---

## 🎯 Complete Release Workflow

```bash
# 1. Make changes & test
pytest -v

# 2. Update changelog
vim docs/CHANGELOG.md

# 3. Create release
./sutra-deploy.sh release patch

# 4. Push to GitHub (triggers CI)
git push origin main --tags

# 5. Monitor build (~15 min)
# Visit: https://github.com/YOUR_ORG/sutra-models/actions

# 6. Verify release
./sutra-deploy.sh deploy v2.0.1
./sutra-deploy.sh status
```

---

**Last Updated:** October 26, 2025
