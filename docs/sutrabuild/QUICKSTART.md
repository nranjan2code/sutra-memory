# Sutra AI Build System - Quick Start Guide

**Get building immediately with the consolidated build system**

## 🚀 Immediate Start

### One-Command Build
```bash
# Build all services for simple edition (most common)
./sutrabuild/scripts/build-all.sh --profile simple
```

**Expected output**:
```
╔═══════════════════════════════════════════════════════════════╗
║              Sutra AI - Master Build System v3.0             ║
║                    🏗️  BUILD CONSOLIDATION                   ║
╚═══════════════════════════════════════════════════════════════╝

ℹ Profile: simple
ℹ Building shared base images...
✓ Base images built successfully
ℹ Building service images for profile: simple...
✓ All service images built for profile: simple
✓ BUILD COMPLETE: Sutra AI simple Edition
```

## 📋 Prerequisites

- **Docker**: Version 20.0+ with BuildKit enabled
- **System Resources**: 4GB RAM, 10GB disk space for builds
- **Network**: Internet access for base image downloads and dependencies

**Quick verification**:
```bash
docker --version          # Should show Docker 20.0+
docker buildx version     # Should show BuildKit support
df -h                     # Check available disk space
```

## 🎯 Common Build Scenarios

### 1. Development Build (Most Common)
```bash
# Clean build for development
./sutrabuild/scripts/build-all.sh --profile simple

# Faster parallel build (if you have multiple cores)
./sutrabuild/scripts/build-all.sh --profile simple --parallel
```

### 2. Production Build
```bash
# Build with specific version tag
./sutrabuild/scripts/build-all.sh --profile community --version v2.1.0

# Enterprise edition with all services
./sutrabuild/scripts/build-all.sh --profile enterprise
```

### 3. Incremental Development
```bash
# Build only after code changes (base images cached)
./sutrabuild/scripts/build-all.sh --profile simple

# Force rebuild of base images (if dependencies changed)
./sutrabuild/scripts/build-all.sh --profile simple --clean
```

## 🔧 Build Profiles Explained

| Profile | Services | Use Case | Build Time |
|---------|----------|----------|------------|
| **simple** | 4 core services | Local development, demos | ~3 minutes |
| **community** | 6 services | Team development, staging | ~4 minutes |
| **enterprise** | 12+ services | Production, full features | ~8 minutes |

### Simple Profile Services
- `sutra-storage` - Core knowledge storage (Rust)
- `sutra-api` - REST API service (Python)
- `sutra-hybrid` - AI reasoning engine (Python + ML)
- `sutra-embedding-service` - Vector embeddings (PyTorch)

## 🏃‍♂️ Quick Workflows

### Development Cycle
```bash
# 1. Initial setup
./sutrabuild/scripts/build-all.sh --profile simple

# 2. Start services  
docker-compose -f sutrabuild/compose/docker-compose.yml --profile simple up -d

# 3. Verify health
./sutrabuild/scripts/health-check.sh http://localhost:8000/health
./sutrabuild/scripts/health-check.sh http://localhost:8001/health

# 4. Make code changes...

# 5. Rebuild (incremental - fast!)
./sutrabuild/scripts/build-all.sh --profile simple

# 6. Restart services
docker-compose -f sutrabuild/compose/docker-compose.yml --profile simple restart
```

### Clean Environment
```bash
# Stop all services
docker-compose -f sutrabuild/compose/docker-compose.yml down

# Clean all images and start fresh
docker system prune -af --volumes

# Rebuild everything
./sutrabuild/scripts/build-all.sh --profile simple
```

## 🎛️ Command Options

### Basic Syntax
```bash
./sutrabuild/scripts/build-all.sh [OPTIONS]
```

### Essential Options
```bash
--profile PROFILE    # simple|community|enterprise (required)
--version VERSION    # Image tag (default: latest)  
--parallel          # Build services in parallel (faster)
--verbose           # Detailed build output
--help              # Show all options
```

### Examples
```bash
# Basic build
./sutrabuild/scripts/build-all.sh --profile simple

# Parallel build with version tag
./sutrabuild/scripts/build-all.sh --profile community --version v2.1.0 --parallel

# Verbose output for debugging
./sutrabuild/scripts/build-all.sh --profile simple --verbose
```

## 🔍 Health Checks

### Verify Build Success
```bash
# Check if images were built
docker images | grep sutra

# Test health endpoints
./sutrabuild/scripts/health-check.sh http://localhost:8000/health    # API
./sutrabuild/scripts/health-check.sh http://localhost:8001/health    # Hybrid  
./sutrabuild/scripts/health-check.sh http://localhost:8889/health    # Embedding
```

### Expected Image Sizes
```bash
REPOSITORY                SIZE
sutra-embedding-service   624MB
sutra-hybrid              624MB  
sutra-api                 624MB
sutra-storage             167MB
sutra-rust-base           158MB
sutra-python-base         624MB
```

## ⚡ Performance Tips

### Faster Builds
1. **Use Parallel Builds**: Add `--parallel` flag (requires 4+ CPU cores)
2. **Keep Base Images**: Don't run `docker system prune` unless necessary
3. **Incremental Changes**: Only changed services will rebuild
4. **SSD Storage**: Use SSD for Docker storage directory

### Build Optimization
```bash
# Check Docker build cache usage
docker system df

# Optimize build context (if builds are slow)
echo "node_modules" >> .dockerignore
echo "*.pyc" >> .dockerignore
echo ".git" >> .dockerignore
```

## 🆘 Common Issues & Solutions

### Build Failures

**Issue**: "Permission denied" errors
```bash
# Solution: Check Docker permissions
sudo usermod -aG docker $USER
newgrp docker  # Or logout/login
```

**Issue**: "No space left on device"  
```bash
# Solution: Clean Docker cache
docker system prune -f
docker volume prune -f
```

**Issue**: Base image build fails
```bash
# Solution: Clear cache and retry
docker builder prune -f
./sutrabuild/scripts/build-all.sh --profile simple
```

### Network Issues

**Issue**: Download timeouts during build
```bash
# Solution: Check network and retry
ping google.com
./sutrabuild/scripts/build-all.sh --profile simple --verbose
```

### Performance Issues

**Issue**: Builds are very slow
```bash
# Check available resources
docker stats
df -h

# Use parallel builds if you have resources
./sutrabuild/scripts/build-all.sh --profile simple --parallel
```

## 📈 Next Steps

### After Successful Build
1. **Deploy Services**: Follow [deployment documentation](../QUICKSTART.md)
2. **Configure Profiles**: Customize for your environment needs
3. **Set Up Monitoring**: Enable health checks and metrics
4. **Optimize Performance**: Tune based on your hardware

### Advanced Usage
- **Custom Profiles**: Create environment-specific build configurations
- **CI/CD Integration**: Automate builds in your pipeline
- **Multi-Architecture**: Build for ARM64 and AMD64
- **Registry Integration**: Push/pull from container registries

---

> **Need Help?** Check [MAINTENANCE.md](MAINTENANCE.md) for troubleshooting or [REFERENCE.md](REFERENCE.md) for complete command documentation.