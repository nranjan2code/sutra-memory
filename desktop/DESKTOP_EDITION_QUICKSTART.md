# Sutra Desktop Edition - Quick Start Guide

**Version:** 1.0.0  
**Updated:** January 21, 2025

## Overview

Sutra Desktop Edition is a Docker-based deployment that provides a complete AI knowledge management system with a modern web interface. Unlike traditional desktop apps, this edition runs as Docker containers for easy distribution and cross-platform compatibility.

## What You Get

- 🚀 **Modern Web UI** - Beautiful React-based interface accessible in your browser
- 🧠 **AI-Powered Learning** - Semantic understanding with embeddings
- 📦 **Simple Deployment** - One script builds and deploys everything
- 🔒 **Localhost Only** - All services run on your machine, no external dependencies
- 💾 **Persistent Storage** - Data survives container restarts

## Architecture

```
┌──────────────────────────────────────────────┐
│           http://localhost:3000              │
│          Sutra Web Interface (React)         │
└─────────────────────┬────────────────────────┘
                      │
         ┌────────────┴───────────┐
         │                        │
    ┌────▼────┐            ┌──────▼─────┐
    │ API     │            │ Storage    │
    │ Server  │────────────│ Server     │
    │ (8000)  │            │ (50051)    │
    └────┬────┘            └────────────┘
         │
    ┌────▼────────┐
    │ Embedding   │
    │ Service     │
    │ (8888)      │
    └─────────────┘
```

## Prerequisites

- **Docker Desktop** (version 20.10 or higher)
- **Node.js** (version 18 or higher)
- **npm** (version 9 or higher)
- **8GB RAM** minimum
- **10GB disk space** for Docker images

## Quick Start

### 1. Build Everything

```bash
cd /path/to/sutra-memory
./desktop/build-desktop-edition.sh
```

This script will:
- ✅ Check prerequisites
- ✅ Clean previous builds
- ✅ Install web client dependencies
- ✅ Validate TypeScript code
- ✅ Build React app
- ✅ Build 4 Docker images
- ✅ Deploy services with Docker Compose
- ✅ Run health checks

**Expected build time:** 5-10 minutes (first time)

### 2. Access the Application

Once build completes:
1. Open your browser
2. Navigate to **http://localhost:3000**
3. You'll see the Sutra Desktop interface

### 3. Start Learning

Try these commands in the chat interface:

```
/learn The sky is blue
/learn Paris is the capital of France
/learn Python is a programming language
/search What is the capital of France?
/stats
```

## Services

### Web Client (Port 3000)
- **Image:** `sutra-desktop-web:latest`
- **Tech:** React 18 + TypeScript + Vite + Tailwind CSS
- **Size:** ~50MB
- **Access:** http://localhost:3000

### API Server (Port 8000 - Internal)
- **Image:** `sutra-api:latest`
- **Tech:** Python FastAPI
- **Size:** ~150MB
- **Endpoints:** /learn, /search, /concepts, /stats

### Storage Server (Port 50051 - Internal)
- **Image:** `sutra-storage:latest`
- **Tech:** Rust binary
- **Size:** ~20MB
- **Features:** Graph database, vector search, WAL persistence

### Embedding Service (Port 8888 - Internal)
- **Image:** `sutra-embedding-simple:latest`
- **Tech:** Python + sentence-transformers
- **Size:** ~1.2GB (includes PyTorch + models)
- **Model:** all-mpnet-base-v2 (768 dimensions)

## Management Commands

### Start Services
```bash
cd /path/to/sutra-memory
docker compose -f .sutra/compose/desktop.yml up -d
```

### Stop Services
```bash
docker compose -f .sutra/compose/desktop.yml down
```

### View Logs
```bash
# All services
docker compose -f .sutra/compose/desktop.yml logs -f

# Specific service
docker logs -f sutra-desktop-web
docker logs -f sutra-desktop-api
docker logs -f sutra-desktop-storage
docker logs -f sutra-desktop-embedding
```

### Check Status
```bash
docker compose -f .sutra/compose/desktop.yml ps
```

### Restart Single Service
```bash
docker restart sutra-desktop-web
docker restart sutra-desktop-api
docker restart sutra-desktop-storage
docker restart sutra-desktop-embedding
```

## Data Persistence

Your knowledge data is stored in Docker volumes:
- `desktop-storage-data` - Graph database
- `desktop-user-data` - User settings

To **backup your data:**
```bash
docker volume inspect desktop-storage-data
# Copy from: /var/lib/docker/volumes/desktop-storage-data/_data
```

To **reset everything:**
```bash
docker compose -f .sutra/compose/desktop.yml down -v
```
⚠️ This deletes all learned knowledge!

## Troubleshooting

### Services Won't Start

Check Docker Desktop is running:
```bash
docker info
```

Check port availability:
```bash
lsof -i :3000  # Web client
lsof -i :8000  # API
```

### Web UI Not Loading

1. Check web service is running:
```bash
docker ps | grep sutra-desktop-web
```

2. Check logs for errors:
```bash
docker logs sutra-desktop-web
```

3. Try rebuilding:
```bash
docker-compose -f .sutra/compose/desktop.yml up -d --build sutra-desktop-web
```

### Embedding Service Slow

First time the embedding service starts, it downloads the AI model (~420MB). This can take 2-5 minutes depending on your internet connection.

Check download progress:
```bash
docker logs -f sutra-desktop-embedding
```

### API Errors

Check storage server is healthy:
```bash
docker exec sutra-desktop-storage storage-server --version
```

Check connectivity:
```bash
docker exec sutra-desktop-api curl http://storage-server:50051/health
```

### Clean Rebuild

If things are broken, try a clean rebuild:
```bash
# Stop everything
docker compose -f .sutra/compose/desktop.yml down

# Remove images
docker rmi sutra-desktop-web sutra-api sutra-storage sutra-embedding-simple

# Rebuild
./desktop/build-desktop-edition.sh
```

## Development

### Modify Web Client

Edit files in `desktop/web-client/src/`

Rebuild:
```bash
cd desktop/web-client
npm run build
docker build -t sutra-desktop-web:latest .
docker restart sutra-desktop-web
```

### Modify API

Edit files in `packages/sutra-api/sutra_api/`

Rebuild:
```bash
docker build -t sutra-api:latest -f packages/sutra-api/Dockerfile .
docker restart sutra-desktop-api
```

### Hot Reload (Development Mode)

Run web client in dev mode:
```bash
cd desktop/web-client
npm run dev
# Access at http://localhost:5173
```

## System Requirements

### Minimum
- CPU: 2 cores
- RAM: 8GB
- Disk: 10GB free
- OS: macOS 11+, Windows 10+, Linux (kernel 4.x+)

### Recommended
- CPU: 4 cores
- RAM: 16GB
- Disk: 20GB free (for caching)
- SSD storage

## Performance Tips

1. **Increase Docker resources:**  
   Docker Desktop → Settings → Resources  
   - CPUs: 4  
   - Memory: 8GB  
   - Swap: 2GB

2. **Enable BuildKit:**  
   ```bash
   export DOCKER_BUILDKIT=1
   ```

3. **Prune old images:**  
   ```bash
   docker system prune -a
   ```

## Production Deployment

⚠️ **Desktop Edition is NOT for production!**

For production deployments, use:
- **Server Edition** (15 services, HA setup)
- **Enterprise Edition** (advanced features, multi-tenancy)

See `docs/deployment/README.md` for production guides.

## Getting Help

- **Documentation:** `docs/desktop/`
- **Architecture:** `docs/desktop/ARCHITECTURE.md`
- **Build Guide:** `docs/desktop/BUILDING.md`
- **UI Components:** `docs/desktop/UI_COMPONENTS.md`
- **Issue Tracker:** GitHub Issues
- **Community:** Discord (link in README.md)

## Next Steps

1. ✅ Complete Quick Start above
2. 📖 Read [Desktop Architecture](../docs/desktop/ARCHITECTURE.md)
3. 🎨 Explore [UI Components](../docs/desktop/UI_COMPONENTS.md)
4. 🔧 Try [Building from Source](../docs/desktop/BUILDING.md)
5. 🚀 Deploy to production with [Server Edition](../docs/deployment/README.md)

## License

See LICENSE file in project root.

---

**Questions?** Check our documentation or open an issue on GitHub.
