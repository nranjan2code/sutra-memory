# Sutra Desktop Edition

**The Simplest Way to Run Sutra AI - Local Docker + World-Class Web Interface**

Sutra Desktop Edition combines the power of enterprise-grade semantic reasoning with the simplicity of local Docker deployment. No installation complexity, no native builds - just start Docker and open your browser.

## Quick Start (3 Steps)

```bash
# 1. Start Docker services (first time takes 2-3 minutes)
./desktop/scripts/docker-start.sh start

# 2. Open in your browser
open http://localhost:3000

# 3. Start learning and querying!
```

That's it! No Rust installation, no cargo builds, no platform-specific issues.

## What You Get

### 🌐 World-Class Web Interface
- **Modern Design**: Beautiful dark theme with smooth animations
- **Chat Interface**: Natural language `/learn` commands
- **Knowledge Browser**: Visual grid to browse all concepts  
- **Analytics Dashboard**: Real-time performance metrics
- **Cross-Platform**: Works on any device with a browser

### 🐳 Simple Docker Deployment
- **3 Services**: Storage + Embedding + API (auto-configured)
- **Single Command**: `./desktop/scripts/docker-start.sh start`
- **Auto-Healing**: Containers restart automatically on failure
- **Local Only**: All ports bound to 127.0.0.1 (secure by default)

### 🚀 Production-Grade Backend
- **Storage Server**: Rust-based high-performance graph storage
- **Embedding Service**: Fast semantic embeddings (768D)
- **REST API**: Full-featured API for all operations

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Browser (localhost:3000)                      │
│              React + TypeScript + TailwindCSS                    │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────────────┐
│                   API Server (localhost:8000)                    │
│                    Python FastAPI Backend                        │
└──────────────────────┬──────────────────────────────────────────┘
                       │ TCP Binary Protocol
┌──────────────────────▼──────────────────────────────────────────┐
│               Storage Server (localhost:50051)                   │
│                 Rust High-Performance Engine                     │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP
┌──────────────────────▼──────────────────────────────────────────┐
│          Embedding Service (Docker internal:8888)                │
│             ONNX Neural Networks (768D vectors)                  │
└─────────────────────────────────────────────────────────────────┘
```

## Management Commands

```bash
# Start all services
./desktop/scripts/docker-start.sh start

# Check status
./desktop/scripts/docker-start.sh status

# View logs
./desktop/scripts/docker-start.sh logs

# Stop services
./desktop/scripts/docker-start.sh stop

# Clean all data (WARNING: deletes everything!)
./desktop/scripts/docker-start.sh clean
```

## Features

### Chat Interface
- Ask questions in natural language
- Use `/learn` command to teach new facts
- Automatic semantic understanding and reasoning

### Knowledge Browser
- Visual grid showing all concepts
- Real-time search and filtering
- One-click concept deletion
- Add new concepts with modal dialog

### Analytics Dashboard
- Total concepts and edges
- Average query latency
- Storage size and efficiency
- System health monitoring

## Data Storage

All data is stored in Docker volumes:

```
Docker Volumes:
├── sutra-desktop-storage-data  # Concept and edge storage
└── (managed automatically by Docker)
```

To back up your data:
```bash
docker run --rm -v sutra-desktop-storage-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/sutra-backup.tar.gz -C /data .
```

To restore:
```bash
docker run --rm -v sutra-desktop-storage-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/sutra-backup.tar.gz -C /data
```

## Requirements

- **Docker Desktop**: Install from [docker.com](https://www.docker.com/products/docker-desktop/)
  - macOS: Docker Desktop 4.0+
  - Windows: Docker Desktop 4.0+ (WSL2 backend)
  - Linux: Docker Engine 20.10+
- **Modern Browser**: Chrome, Firefox, Safari, or Edge
- **RAM**: 2GB free (4GB recommended)
- **Disk**: 1GB for Docker images + your data

## First Launch

The first time you run `docker-start.sh start`:

1. Downloads Docker images (~500MB total)
2. Builds the web client container
3. Starts 3 services (Storage, Embedding, API, Web)
4. Waits for services to be healthy
5. Ready in 2-3 minutes!

Subsequent starts take only 5-10 seconds.

## Ports

All services run on localhost only (secure by default):

- **3000**: Web interface (main access point)
- **8000**: REST API (accessed by web client)
- **50051**: Storage server (internal TCP)
- **8888**: Embedding service (Docker internal only)

## Troubleshooting

### Docker not running
```
Error: Docker daemon not running
Solution: Start Docker Desktop application
```

### Port already in use
```bash
# Check what's using port 3000
lsof -i :3000

# Kill the process or change the port in docker-compose
```

### Services won't start
```bash
# Check logs
./desktop/scripts/docker-start.sh logs

# Clean and restart
./desktop/scripts/docker-start.sh stop
./desktop/scripts/docker-start.sh start
```

### Can't connect to web interface
1. Verify services are running: `docker ps | grep sutra-desktop`
2. Check API health: `curl http://localhost:8000/health`
3. Check web health: `curl http://localhost:3000/health`

## Comparison with Other Editions

| Feature | Desktop Edition | Server Edition |
|---------|----------------|----------------|
| **Deployment** | Docker Compose | Kubernetes/Docker |
| **Interface** | Web Browser | Web + APIs |
| **Setup Time** | 2-3 minutes | 15-30 minutes |
| **Users** | Single user | Multi-tenant |
| **Authentication** | None | JWT + RBAC |
| **Scalability** | Single node | Distributed grid |
| **Best For** | Personal use, development | Production, teams |

## Development

Want to customize the web interface?

```bash
cd desktop/web-client

# Install dependencies
npm install

# Start dev server (with HMR)
npm run dev

# Build for production
npm run build
```

## Performance

Expected performance on modern hardware:

- **Startup**: 5-10 seconds (after first run)
- **Query Latency**: <50ms average
- **Learning**: <200ms per concept
- **Memory**: ~500MB total (all services)
- **Storage**: ~1MB per 1000 concepts

## Security

Desktop Edition is designed for local, single-user use:

- ✅ All ports bound to 127.0.0.1 (localhost only)
- ✅ No external network access required
- ✅ No authentication (assumes trusted environment)
- ⚠️ **Do NOT expose to internet without adding authentication**
- ⚠️ **Not suitable for multi-user production environments**

For production deployment with authentication and multi-tenancy, use Sutra Server Edition instead.

## Upgrading

```bash
# Stop services
./desktop/scripts/docker-start.sh stop

# Pull latest code
git pull origin main

# Rebuild images
cd /path/to/sutra-memory
SUTRA_EDITION=simple ./sutra build

# Restart
./desktop/scripts/docker-start.sh start
```

Your data is preserved in Docker volumes across upgrades.

## Uninstall

```bash
# Stop and remove all data
./desktop/scripts/docker-start.sh clean

# Remove Docker images (optional)
docker rmi sutra-storage:latest
docker rmi sutra-api:latest
docker rmi sutra-desktop-web:latest
docker rmi ghcr.io/nranjan2code/sutra-embedder:v1.0.1
```

## Support

- **Documentation**: `docs/desktop/`
- **Issues**: [GitHub Issues](https://github.com/sutra-ai/sutra/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sutra-ai/sutra/discussions)

## License

Sutra Desktop Edition is part of the Sutra AI project.
See [LICENSE](../LICENSE) for details.

---

**Made with ❤️ by the Sutra AI team**

*Semantic reasoning for everyone, everywhere.*
