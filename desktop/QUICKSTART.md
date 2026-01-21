# Sutra Desktop Edition - Quick Start Guide

**Time to get started: 5 minutes**

This guide will take you from zero to a running Sutra Desktop Edition.

## Prerequisites

Before you begin, make sure you have:

1. **Docker Desktop** installed and running
   - Download: https://www.docker.com/products/docker-desktop/
   - Version: 4.0 or higher
   - Memory: 4GB allocated to Docker (recommended)

2. **Git** (to clone the repository)
   - macOS: `xcode-select --install`
   - Windows: https://git-scm.com/download/win
   - Linux: `sudo apt install git` or `sudo yum install git`

3. **Node.js 18+** and **npm** (for web client)
   - Download: https://nodejs.org/
   - Check: `node --version` and `npm --version`

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/sutra-ai/sutra.git
cd sutra
```

### 2. Run the Build Script

This single command builds everything and starts all services:

```bash
./desktop/build-desktop-edition.sh
```

**What this does:**
- ✅ Checks prerequisites (Docker, Node.js)
- ✅ Installs web client dependencies
- ✅ Validates TypeScript code
- ✅ Builds React web application
- ✅ Builds 3 Docker images (Storage, API, Web)
- ✅ Starts all containers
- ✅ Runs end-to-end validation tests
- ✅ Shows you the access URLs

**Expected time:** 3-5 minutes (first run)

### 3. Access the Application

Once the build completes, open your browser:

```
http://localhost:3000
```

You'll see the Sutra Desktop Edition web interface!

## First Steps

### Chat with Sutra

1. Click **Chat** in the sidebar
2. Try asking: "What can you do?"
3. Teach something: `/learn The Earth orbits the Sun`
4. Ask about it: "Tell me about Earth"

### Browse Knowledge

1. Click **Knowledge** in the sidebar
2. See all concepts you've taught
3. Search, filter, or delete concepts
4. Add new concepts with the "+ Add Concept" button

### View Analytics

1. Click **Analytics** in the sidebar
2. See real-time metrics:
   - Total concepts
   - Total edges (relationships)
   - Average query time
   - System health

## Management Commands

### Check Status
```bash
./desktop/scripts/docker-start.sh status
```

### View Logs
```bash
./desktop/scripts/docker-start.sh logs
```

### Stop Services
```bash
./desktop/scripts/docker-start.sh stop
```

### Restart Services
```bash
./desktop/scripts/docker-start.sh start
```

### Clean Everything (⚠️ Deletes all data)
```bash
./desktop/scripts/docker-start.sh clean
```

## Validation

To verify everything is working correctly:

```bash
./desktop/validate-desktop.sh
```

This runs automated tests on all endpoints.

## Troubleshooting

### "Docker daemon not running"

**Solution:** Start Docker Desktop application

### "Port 3000 already in use"

**Solution:** Kill the process using port 3000
```bash
# Find process
lsof -ti:3000

# Kill it
kill -9 $(lsof -ti:3000)

# Or change the port in .sutra/compose/desktop.yml
```

### "Build failed: npm install error"

**Solution:** Clear npm cache and retry
```bash
cd desktop/web-client
rm -rf node_modules package-lock.json
npm cache clean --force
npm install --legacy-peer-deps
```

### "Container won't start"

**Solution:** Check logs
```bash
# See which container is failing
docker compose -f .sutra/compose/desktop.yml ps

# Check its logs
docker compose -f .sutra/compose/desktop.yml logs <container-name>
```

### "Web page won't load"

1. Check containers are running: `docker ps | grep sutra-desktop`
2. Check API health: `curl http://localhost:8000/health`
3. Check web health: `curl http://localhost:3000/health`
4. Clear browser cache and retry

### "Can't connect to API"

**Solution:** Restart API container
```bash
docker restart sutra-desktop-api
```

## Data Location

Your knowledge data is stored in Docker volumes:

```bash
# List volumes
docker volume ls | grep sutra-desktop

# Backup data
docker run --rm -v sutra-desktop-storage-data:/data \
  -v $(pwd):/backup alpine \
  tar czf /backup/sutra-backup.tar.gz -C /data .
```

## Updating

To get the latest version:

```bash
# Stop services
./desktop/scripts/docker-start.sh stop

# Pull latest code
git pull origin main

# Rebuild everything
./desktop/build-desktop-edition.sh
```

Your data is preserved in Docker volumes.

## Next Steps

- **Read the full guide**: `desktop/DESKTOP_EDITION.md`
- **Learn about architecture**: `DESKTOP_EDITION_IMPLEMENTATION.md`
- **Check the release checklist**: `desktop/RELEASE_CHECKLIST.md`
- **Explore the API**: http://localhost:8000/docs

## Getting Help

- **Documentation**: `docs/` directory
- **Issues**: https://github.com/sutra-ai/sutra/issues
- **Discussions**: https://github.com/sutra-ai/sutra/discussions

## Performance Tips

- **Allocate more memory to Docker**: Settings → Resources → Memory (4GB+)
- **Use SSD storage**: Docker Desktop → Settings → Resources → Disk image location
- **Close unused apps**: Free up system resources for better performance

## Security Notes

⚠️ **Desktop Edition is for personal use only**

- All ports are bound to `127.0.0.1` (localhost only)
- No authentication or encryption by default
- **Do NOT expose to the internet**
- For production use, see **Server Edition** instead

## What's Running

When you start Desktop Edition, you get:

1. **Storage Server** (Rust)
   - Port: 50051 (internal)
   - Purpose: High-performance graph storage

2. **Embedding Service** (ONNX)
   - Port: 8888 (internal)
   - Purpose: Semantic embeddings (768D vectors)

3. **API Server** (Python/FastAPI)
   - Port: 8000 (localhost only)
   - Purpose: REST API backend

4. **Web Client** (React/TypeScript)
   - Port: 3000 (localhost only)
   - Purpose: Beautiful web interface

## Resource Usage

Expected resource consumption:

- **Memory**: ~500MB total
- **CPU**: <5% idle, 20-40% during queries
- **Disk**: ~200MB images + your data
- **Network**: Localhost only (no external traffic)

## Success Checklist

After installation, verify:

- [ ] `docker ps` shows 4 running containers
- [ ] http://localhost:3000 loads the web interface
- [ ] http://localhost:8000/health returns "healthy"
- [ ] Can chat and use `/learn` command
- [ ] Knowledge browser shows concepts
- [ ] Analytics dashboard displays metrics

## Ready to Go!

You now have a fully functional Sutra Desktop Edition. Start teaching it knowledge and exploring semantic reasoning!

**Access**: http://localhost:3000

**Enjoy!** 🚀
