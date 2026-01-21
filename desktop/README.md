# Sutra Desktop Edition

**Local Docker + World-Class Web Interface**

The simplest way to run Sutra AI - just start Docker and open your browser.

## 🚀 Quick Start (3 Steps)

```bash
# 1. Build and deploy everything
./desktop/build-desktop-edition.sh

# 2. Open in browser
open http://localhost:3000

# 3. Start using Sutra!
```

That's it! No Rust, no cargo, no native builds.

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
- **[User Guide](DESKTOP_EDITION.md)** - Complete user documentation
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Development & deployment
- **[Release Checklist](RELEASE_CHECKLIST.md)** - Release process

## 🎯 What's Inside

### Web Client (`web-client/`)
- Modern React + TypeScript application
- Beautiful dark theme with animations
- Chat, Knowledge, Analytics, Settings pages
- Production-ready with Docker + nginx

### Scripts (`scripts/`)
- `docker-start.sh` - Start/stop/status services
- `build-desktop-edition.sh` - Complete build pipeline
- `validate-desktop.sh` - Validation tests

### Configuration (`.sutra/compose/desktop.yml`)
- Docker Compose for 4 services
- Storage, API, Embedding, Web Client
- Localhost-only (secure by default)

## 🛠️ Common Commands

```bash
# Build everything
./desktop/build-desktop-edition.sh

# Start services
./desktop/scripts/docker-start.sh start

# Check status
./desktop/scripts/docker-start.sh status

# View logs
./desktop/scripts/docker-start.sh logs

# Stop services
./desktop/scripts/docker-start.sh stop

# Validate deployment
./desktop/validate-desktop.sh
```

## 🌐 Access Points

- **Web Interface**: http://localhost:3000
- **API Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📦 What Gets Deployed

1. **Storage Server** (Rust) - High-performance graph storage
2. **Embedding Service** (ONNX) - Semantic embeddings (768D)
3. **API Server** (Python/FastAPI) - REST API backend
4. **Web Client** (React/TypeScript) - Beautiful web interface

## ✅ Features

- 💬 **Chat Interface** - Natural language with `/learn` commands
- 📚 **Knowledge Browser** - Visual grid to manage concepts
- 📊 **Analytics Dashboard** - Real-time performance metrics
- ⚙️ **Settings** - Preferences and system info

## 🔒 Security

Desktop Edition is for personal, local use:
- All ports bound to `127.0.0.1` (localhost only)
- No authentication (assumes trusted environment)
- **Do NOT expose to internet**

For production deployment with auth, use Server Edition.

## 🆘 Troubleshooting

**Docker not running?**
```bash
# Start Docker Desktop application
```

**Port already in use?**
```bash
# Kill process on port 3000
kill -9 $(lsof -ti:3000)
```

**Build failed?**
```bash
# Check logs
./desktop/scripts/docker-start.sh logs
```

See [QUICKSTART.md](QUICKSTART.md#troubleshooting) for more help.

## 📖 Learn More

- **Architecture**: See [DESKTOP_EDITION_IMPLEMENTATION.md](../DESKTOP_EDITION_IMPLEMENTATION.md)
- **Web Client**: See [web-client/README.md](web-client/README.md)
- **Full Docs**: See [docs/desktop/](../docs/desktop/)

## 🎉 Ready to Build?

```bash
./desktop/build-desktop-edition.sh
```

**First time**: 3-5 minutes (downloads images)  
**Subsequent**: 30-60 seconds

---

**Made with ❤️ by the Sutra AI team**
