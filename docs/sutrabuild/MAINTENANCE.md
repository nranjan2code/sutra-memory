# Sutra AI Build System - Maintenance Guide

**System maintenance, troubleshooting, and optimization for production operations**

## 🔧 Routine Maintenance

### Daily Operations

#### Health Monitoring
```bash
# Check all service health
./sutrabuild/scripts/health-check.sh http://localhost:8000/health    # API
./sutrabuild/scripts/health-check.sh http://localhost:8001/health    # Hybrid
./sutrabuild/scripts/health-check.sh http://localhost:8889/health    # Embedding

# Automated health check script
#!/bin/bash
endpoints=("8000" "8001" "8889")
for port in "${endpoints[@]}"; do
    if ./sutrabuild/scripts/health-check.sh "http://localhost:$port/health"; then
        echo "✓ Port $port healthy"
    else
        echo "❌ Port $port unhealthy"
    fi
done
```

#### Build Cache Management
```bash
# Check Docker system usage
docker system df

# Clean old images (keep base images)
docker image prune -f

# Check build cache size
docker builder df
```

### Weekly Maintenance

#### Base Image Updates
```bash
# Rebuild base images with latest security patches
./sutrabuild/scripts/build-all.sh --profile simple --clean

# Verify no vulnerabilities
docker scan sutra-python-base:latest  # If Docker scan is available
```

#### Performance Monitoring
```bash
# Check build performance trends
time ./sutrabuild/scripts/build-all.sh --profile simple

# Monitor disk usage
du -sh /var/lib/docker/
df -h
```

### Monthly Maintenance

#### Full System Refresh
```bash
# Complete cleanup and rebuild
docker system prune -af --volumes
./sutrabuild/scripts/build-all.sh --profile enterprise --clean

# Update documentation
git pull origin main
# Review docs/build/ for any updates
```

## 🚨 Troubleshooting

### Build Failures

#### Common Build Errors

**Error: "No space left on device"**
```bash
# Check available space
df -h

# Clean Docker cache
docker system prune -f
docker volume prune -f

# If still insufficient, clean everything
docker system prune -af --volumes
```

**Error: "Failed to build base image"**
```bash
# Check network connectivity
ping google.com

# Retry with verbose output
export BUILDKIT_PROGRESS=plain
./sutrabuild/scripts/build-all.sh --profile simple --verbose

# Check Docker BuildKit
docker buildx version
```

**Error: "Cannot connect to Docker daemon"**
```bash
# Check Docker service
sudo systemctl status docker      # Linux
brew services list | grep docker  # macOS

# Restart Docker service
sudo systemctl restart docker     # Linux
# Or restart Docker Desktop       # macOS/Windows

# Check permissions
sudo usermod -aG docker $USER
newgrp docker
```

#### Service-Specific Issues

**Python Service Build Failures:**
```bash
# Check Python base image
docker images sutra-python-base:latest

# Rebuild base if missing
docker build -f sutrabuild/docker/base/python-base.dockerfile -t sutra-python-base:latest .

# Check for dependency conflicts
docker build --no-cache -f sutrabuild/docker/services/sutra-api.dockerfile -t sutra-api:test .
```

**Rust Service Build Failures:**
```bash
# Check Rust base image
docker images sutra-rust-base:latest

# Clear Rust cache if corrupted
docker builder prune --filter type=exec.cachemount

# Rebuild with fresh cache
./sutrabuild/scripts/build-all.sh --profile simple --clean
```

### Runtime Issues

#### Service Won't Start
```bash
# Check service logs
docker-compose -f sutrabuild/compose/docker-compose.yml --profile simple logs sutra-api

# Check resource usage
docker stats

# Verify health endpoints
curl -f http://localhost:8000/health || echo "API unhealthy"
```

#### Performance Problems
```bash
# Monitor resource usage during builds
htop  # CPU/Memory usage
iotop # Disk I/O usage

# Check Docker resource limits
docker info | grep -i memory
docker info | grep -i cpu
```

### Network Issues

#### Port Conflicts
```bash
# Check what's using ports
netstat -tulpn | grep :8000
lsof -i :8000

# Kill conflicting processes
sudo kill -9 $(lsof -ti:8000)
```

#### Container Communication
```bash
# Test container networking
docker network ls
docker network inspect sutra-models_default

# Test inter-service communication
docker exec sutra-api curl http://sutra-storage:50051/health
```

## 🎛️ Performance Optimization

### Build Performance

#### Cache Optimization
```bash
# Monitor cache hit rates
docker builder du

# Optimize .dockerignore
echo "*.log" >> .dockerignore
echo "node_modules" >> .dockerignore
echo ".git" >> .dockerignore
echo "*.pyc" >> .dockerignore

# Use parallel builds (if you have 4+ cores)
./sutrabuild/scripts/build-all.sh --profile simple --parallel
```

#### Storage Optimization
```bash
# Use SSD for Docker storage (Docker Desktop)
# Settings > Resources > Advanced > Disk image location

# Configure build cache size
# Docker Desktop: Settings > Docker Engine
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "10GB"
    }
  }
}
```

### Runtime Optimization

#### Resource Limits
```yaml
# In sutrabuild/compose/docker-compose.yml
services:
  sutra-api:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

#### Health Check Tuning
```yaml
services:
  sutra-api:
    healthcheck:
      test: ["CMD", "health-check", "http://localhost:8000/health"]
      interval: 30s      # Increase for less overhead
      timeout: 10s       # Increase for slow responses
      retries: 3         # Adjust based on reliability needs
      start_period: 40s  # Increase for slow-starting services
```

## 📊 Monitoring & Metrics

### Build Metrics

#### Performance Tracking
```bash
# Create build performance log
#!/bin/bash
echo "$(date): Starting build" >> build-performance.log
start_time=$(date +%s)

./sutrabuild/scripts/build-all.sh --profile simple

end_time=$(date +%s)
duration=$((end_time - start_time))
echo "$(date): Build completed in ${duration}s" >> build-performance.log
```

#### Cache Efficiency
```bash
# Monitor cache usage over time
docker system events --filter type=image --format '{{.Time}} {{.Action}} {{.Actor.Attributes.name}}'

# Analyze build cache hits
docker builder du | awk 'NR>1 {shared+=$3; total+=$2} END {print "Cache efficiency:", (shared/total)*100"%"}'
```

### Service Metrics

#### Health Monitoring
```bash
# Automated health dashboard
#!/bin/bash
services=("api:8000" "hybrid:8001" "embedding:8889" "storage:50051")

for service in "${services[@]}"; do
    name=${service%:*}
    port=${service#*:}
    
    if ./sutrabuild/scripts/health-check.sh "http://localhost:$port/health"; then
        echo "✅ $name (port $port) - Healthy"
    else
        echo "❌ $name (port $port) - Unhealthy"
    fi
done
```

#### Resource Monitoring
```bash
# Container resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Service-specific monitoring
#!/bin/bash
while true; do
    echo "=== $(date) ==="
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    sleep 60
done >> monitoring.log
```

## 🔧 Advanced Maintenance

### Build System Updates

#### Updating Base Images
```bash
# Update Python base
docker pull python:3.11-slim
./sutrabuild/scripts/build-all.sh --profile simple --clean

# Update Rust base  
docker pull rust:1.82-slim
./sutrabuild/scripts/build-all.sh --profile simple --clean
```

#### Dockerfile Optimization
```dockerfile
# Optimize layer ordering (most stable → most volatile)
FROM sutra-python-base:latest

# 1. System packages (rarely change)
USER root
RUN apt-get update && apt-get install -y package-name

# 2. Application dependencies (change occasionally)
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# 3. Application code (changes frequently)
COPY src/ /app/src/

USER sutra
```

### Security Maintenance

#### Vulnerability Scanning
```bash
# Scan base images
docker scout cves sutra-python-base:latest  # If Docker Scout available
docker scout cves sutra-rust-base:latest

# Update base images on security patches
# Check security advisories monthly
```

#### Access Control
```bash
# Verify non-root execution
docker inspect sutra-api:latest | jq '.[0].Config.User'  # Should be "sutra"

# Check file permissions
docker run --rm sutra-api:latest ls -la /app
```

## 🚨 Emergency Procedures

### Complete System Recovery

#### Full Reset
```bash
# Stop all services
docker-compose -f sutrabuild/compose/docker-compose.yml down

# Clean everything
docker system prune -af --volumes

# Rebuild from scratch
./sutrabuild/scripts/build-all.sh --profile simple

# Restart services
docker-compose -f sutrabuild/compose/docker-compose.yml --profile simple up -d
```

#### Backup and Restore
```bash
# Backup important images
docker save sutra-python-base:latest | gzip > sutra-python-base-backup.tar.gz
docker save sutra-rust-base:latest | gzip > sutra-rust-base-backup.tar.gz

# Restore from backup
gunzip -c sutra-python-base-backup.tar.gz | docker load
gunzip -c sutra-rust-base-backup.tar.gz | docker load
```

### Rollback Procedures

#### Version Rollback
```bash
# Build previous version
./sutrabuild/scripts/build-all.sh --profile simple --version v2.0.0

# Update compose to use specific version
export SUTRA_VERSION=v2.0.0
docker-compose -f sutrabuild/compose/docker-compose.yml --profile simple up -d
```

## 📋 Maintenance Checklist

### Daily Checklist
- [ ] Check service health endpoints
- [ ] Monitor Docker disk usage (`docker system df`)
- [ ] Review container logs for errors
- [ ] Verify all services responding

### Weekly Checklist  
- [ ] Update base images with security patches
- [ ] Clean unused Docker images (`docker image prune -f`)
- [ ] Monitor build performance trends
- [ ] Check for Docker engine updates

### Monthly Checklist
- [ ] Full system cleanup and rebuild
- [ ] Review and update documentation  
- [ ] Security vulnerability scan
- [ ] Performance optimization review
- [ ] Backup critical images and configurations

---

> **Quick References:** [ARCHITECTURE.md](ARCHITECTURE.md) for technical details, [QUICKSTART.md](QUICKSTART.md) for immediate help, [REFERENCE.md](REFERENCE.md) for complete commands.