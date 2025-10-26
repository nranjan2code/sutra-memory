# 🚀 Fast Development Guide - Sutra AI

**Stop wasting time on full rebuilds!** This guide shows you how to work on individual packages without rebuilding everything.

---

## ⚡ Quick Commands (The Only Ones You Need)

### Update Single Service (30 seconds instead of 5 minutes!)
```bash
# Changed API code? Update just the API:
./sutra-deploy.sh update sutra-api

# Changed frontend? Update just the client:
./sutra-deploy.sh update sutra-client

# Changed hybrid service?
./sutra-deploy.sh update sutra-hybrid
```

**That's it!** Other services keep running. No 5-minute rebuild wait.

---

## 🔥 Development Mode (Hot Reload - NO Rebuilds!)

Want **instant updates** without ANY rebuilds? Use development mode:

```bash
# Start development mode with hot reload
docker-compose -f docker-compose-grid.yml -f docker-compose.dev.yml up

# Now edit your code:
# - Python files (API/Hybrid): Changes apply instantly!
# - React files (Client): Browser auto-refreshes!
# - NO docker rebuild needed!
```

### What Gets Hot-Reloaded:
- ✅ **Python services** (`sutra-api`, `sutra-hybrid`) - Instant reload
- ✅ **React frontend** (`sutra-client`) - Hot Module Replacement (HMR)
- ❌ **Rust services** - Need rebuild (but with cache, only 30-60s)

---

## 📋 Common Workflows

### I Changed API Code
```bash
# Option 1: Development mode (instant changes)
docker-compose -f docker-compose-grid.yml -f docker-compose.dev.yml up sutra-api

# Option 2: Quick rebuild (30s)
./sutra-deploy.sh update sutra-api
```

### I Changed Multiple Services
```bash
# Update them one by one (each takes ~30s)
./sutra-deploy.sh update sutra-api
./sutra-deploy.sh update sutra-hybrid

# Or rebuild affected services
docker-compose -f docker-compose-grid.yml build sutra-api sutra-hybrid
docker-compose -f docker-compose-grid.yml up -d --no-deps sutra-api sutra-hybrid
```

### I Changed Storage Server (Rust)
```bash
# Storage is critical - be careful!
./sutra-deploy.sh update storage-server

# Or for faster Rust rebuilds with cache:
docker-compose -f docker-compose-grid.yml -f docker-compose.dev.yml build storage-server
docker-compose -f docker-compose-grid.yml up -d storage-server
```

### I Want to See What Changed
```bash
# Detect which packages changed
./scripts/detect-changes.sh

# Output shows only affected packages:
# Changed packages:
#   - sutra-api
#   - sutra-client
```

---

## 🎯 Best Practices

### For Daily Development
1. **Use development mode** for Python/JS work (no rebuilds!)
2. **Use `update` command** for quick one-off changes
3. **Only use full `build`** when you change dependencies

### Don't Do Full Rebuilds
```bash
# ❌ DON'T DO THIS (5-10 minutes):
./sutra-deploy.sh build
./sutra-deploy.sh restart

# ✅ DO THIS INSTEAD (30 seconds):
./sutra-deploy.sh update sutra-api
```

### Check Service Health
```bash
# Quick status check
./sutra-deploy.sh status

# Full validation
./sutra-deploy.sh validate

# Watch logs
./sutra-deploy.sh logs sutra-api
```

---

## 🐛 Troubleshooting

### "My changes aren't showing up!"

**For Python/JS in dev mode:**
```bash
# Make sure you're using dev compose file:
docker-compose -f docker-compose-grid.yml -f docker-compose.dev.yml up
```

**For production mode:**
```bash
# You need to update the service:
./sutra-deploy.sh update sutra-api
```

### "Update command failed"
```bash
# Check if service is running
docker ps | grep sutra-api

# Check logs
./sutra-deploy.sh logs sutra-api

# Try restarting
./sutra-deploy.sh restart
```

### "I want a clean slate"
```bash
# Full cleanup and rebuild (use rarely!)
./sutra-deploy.sh clean
./sutra-deploy.sh install
```

---

## 📊 Speed Comparison

| Task | Old Way | New Way | Time Saved |
|------|---------|---------|------------|
| **API code change** | 5-8 min | 30 sec | **10x faster** |
| **Frontend change** | 3-5 min | Instant (HMR) | **∞ faster** |
| **Multiple services** | 8-12 min | 2 min | **5x faster** |
| **Just config change** | 3 min | 10 sec | **18x faster** |

---

## 🎓 Advanced: CI/CD Integration

Want automatic smart builds in CI? The change detection works there too:

```yaml
# .github/workflows/smart-build.yml
- name: Detect changed packages
  run: ./scripts/detect-changes.sh > changed.txt
  
- name: Build only changed packages
  run: |
    for pkg in $(cat changed.txt | grep "- " | cut -d' ' -f4); do
      docker-compose build $pkg
    done
```

---

## 💡 Key Takeaways

1. **`./sutra-deploy.sh update <service>`** - Your new best friend
2. **Development mode** - Use for Python/JS development (instant changes)
3. **Never do full rebuilds** unless you changed core dependencies
4. **Check what changed** with `./scripts/detect-changes.sh`

Happy coding! 🚀
