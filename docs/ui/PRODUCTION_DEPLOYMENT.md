# Sutra AI - Conversation-First UI Production Deployment Guide

**Version:** 2.0.0  
**Date:** October 26, 2025  
**Status:** Production Ready

---

## Overview

This guide covers deploying the complete Sutra AI system with the new conversation-first UI to production. The deployment uses Docker Compose with a single unified script (`sutra-deploy.sh`) that handles all services.

### Architecture

```
                    ┌─────────────────┐
                    │   sutra-client  │
                    │   (nginx:8080)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   API Gateway   │
                    │  (nginx proxy)  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
      ┌───────▼──────┐ ┌────▼────┐  ┌─────▼──────┐
      │  sutra-api   │ │ hybrid  │  │   storage  │
      │  :8000       │ │ :8001   │  │   :50051   │
      └──────┬───────┘ └─────────┘  └─────┬──────┘
             │                             │
      ┌──────▼──────┐              ┌──────▼──────┐
      │ user-storage│              │ embeddings  │
      │ :50053      │              │ :8888       │
      └─────────────┘              └─────────────┘
```

---

## Prerequisites

### System Requirements

- **OS:** Linux, macOS, or Windows with WSL2
- **Docker:** 24.0+ with Docker Compose V2
- **RAM:** 8GB minimum (16GB recommended)
- **Disk:** 20GB free space
- **CPU:** 4 cores minimum (8 cores recommended)
- **Network:** Internet access for image pulls

### Software Dependencies

```bash
# Check Docker version
docker --version  # Should be 24.0+
docker compose version  # Should be v2.0+

# Check system resources
docker system df
```

---

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/nranjan2code/sutra-memory.git
cd sutra-memory
```

### 2. Configure Environment

```bash
# Create production environment file
cat > .env << 'EOF'
# Edition (simple, community, enterprise)
SUTRA_EDITION=simple

# Version
SUTRA_VERSION=2.0.0

# JWT Secret (CHANGE THIS IN PRODUCTION!)
SUTRA_JWT_SECRET_KEY=$(openssl rand -hex 32)

# Optional: License keys for enterprise edition
# SUTRA_LICENSE_KEY=your_license_key_here
# SUTRA_LICENSE_SECRET=your_license_secret_here
EOF

# Generate secure JWT secret
export SUTRA_JWT_SECRET_KEY=$(openssl rand -hex 32)
echo "SUTRA_JWT_SECRET_KEY=${SUTRA_JWT_SECRET_KEY}" >> .env
```

### 3. Deploy

```bash
# Install and start all services
./sutra-deploy.sh install

# This command will:
# - Build all Docker images
# - Start all services
# - Run health checks
# - Display status
```

### 4. Verify Deployment

```bash
# Check service status
./sutra-deploy.sh status

# View logs
./sutra-deploy.sh logs

# Access UI
open http://localhost:8080
```

---

## Deployment Configuration

### Environment Variables

The system is configured via environment variables in `.env` file:

#### Core Configuration

```bash
# Edition Selection
SUTRA_EDITION=simple|community|enterprise

# Version Control
SUTRA_VERSION=2.0.0

# JWT Authentication (CRITICAL - CHANGE IN PRODUCTION)
SUTRA_JWT_SECRET_KEY=your_secure_random_secret_here
SUTRA_JWT_ALGORITHM=HS256
SUTRA_JWT_EXPIRATION_HOURS=24
SUTRA_JWT_REFRESH_EXPIRATION_DAYS=7
```

#### Service URLs (Internal Docker Network)

These are handled by Docker Compose and don't need to be changed:

```bash
SUTRA_API_URL=http://sutra-api:8000
SUTRA_HYBRID_URL=http://sutra-hybrid:8001
SUTRA_STORAGE_SERVER=storage-server:50051
SUTRA_USER_STORAGE_SERVER=user-storage-server:50051
SUTRA_EMBEDDING_URL=http://embedding-single:8888
```

#### License Keys (Enterprise Only)

```bash
SUTRA_LICENSE_KEY=your_enterprise_license_key
SUTRA_LICENSE_SECRET=your_enterprise_secret
```

### Port Mapping

| Service | Internal Port | External Port | Description |
|---------|--------------|---------------|-------------|
| sutra-client | 8080 | 8080 | Main UI |
| sutra-api | 8000 | 8000 | REST API |
| sutra-hybrid | 8000 | 8001 | Semantic API |
| storage-server | 50051 | 50051 | Domain storage |
| user-storage-server | 50051 | 50053 | User storage |
| embedding-single | 8888 | 8888 | Embeddings |
| sutra-control | 9000 | 9000 | Control Center |

---

## Service Management

### Using sutra-deploy.sh

The unified deployment script provides all necessary commands:

```bash
# Installation and startup
./sutra-deploy.sh install        # Full deployment
./sutra-deploy.sh start          # Start stopped services
./sutra-deploy.sh stop           # Stop all services
./sutra-deploy.sh restart        # Restart all services

# Monitoring
./sutra-deploy.sh status         # Check service health
./sutra-deploy.sh logs           # View all logs
./sutra-deploy.sh logs sutra-api # View specific service

# Updates
./sutra-deploy.sh update         # Update specific service
./sutra-deploy.sh rebuild        # Rebuild all images

# Cleanup
./sutra-deploy.sh clean          # Remove stopped containers
./sutra-deploy.sh purge          # Remove everything (WARNING)

# Version management
./sutra-deploy.sh version        # Show current version
./sutra-deploy.sh release patch  # Release 2.0.0 → 2.0.1
./sutra-deploy.sh deploy v2.0.1  # Deploy specific version
```

### Manual Docker Compose Commands

If needed, you can use Docker Compose directly:

```bash
# Start services with specific edition
SUTRA_EDITION=simple docker compose --profile simple up -d

# View logs
docker compose logs -f sutra-client

# Restart specific service
docker compose restart sutra-api

# Stop everything
docker compose down
```

---

## Health Checks

### Automated Health Checks

All services have built-in health checks:

```bash
# Check all services
docker compose ps

# Expected output:
NAME                STATUS              PORTS
sutra-client        healthy            0.0.0.0:8080->8080/tcp
sutra-api           healthy            0.0.0.0:8000->8000/tcp
sutra-hybrid        healthy            0.0.0.0:8001->8000/tcp
storage-server      healthy            0.0.0.0:50051->50051/tcp
user-storage-server healthy            0.0.0.0:50053->50051/tcp
embedding-single    healthy            0.0.0.0:8888->8888/tcp
```

### Manual Health Verification

```bash
# UI Health
curl http://localhost:8080/health
# Expected: 200 OK, "healthy"

# API Health
curl http://localhost:8000/health
# Expected: {"status":"healthy",...}

# Auth Health
curl http://localhost:8000/auth/health
# Expected: {"status":"healthy","auth_enabled":true}

# Storage Health
nc -zv localhost 50051
# Expected: Connection succeeded

# User Storage Health
nc -zv localhost 50053
# Expected: Connection succeeded
```

### End-to-End Testing

```bash
# 1. Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!","organization":"test-org"}'

# 2. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'
# Save the "access_token" from response

# 3. Create conversation
curl -X POST http://localhost:8000/conversations/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"space_id":"default","domain_storage":"storage-server:50051"}'

# 4. Send message
curl -X POST http://localhost:8000/conversations/CONVERSATION_ID/message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"content":"What is Sutra AI?"}'
```

---

## Data Persistence

### Volume Management

Data is stored in Docker volumes:

```bash
# List volumes
docker volume ls | grep sutra

# Expected volumes:
sutra-models_storage-data
sutra-models_user-storage-data
sutra-models_grid-event-data (enterprise only)

# Backup volumes
docker run --rm -v sutra-models_storage-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/storage-backup.tar.gz /data

docker run --rm -v sutra-models_user-storage-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/user-storage-backup.tar.gz /data

# Restore volumes
docker run --rm -v sutra-models_storage-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/storage-backup.tar.gz -C /
```

### Data Locations

| Volume | Container Path | Purpose |
|--------|---------------|---------|
| storage-data | /data | Domain knowledge graph |
| user-storage-data | /data | Users, sessions, conversations |
| grid-event-data | /data | Grid events (enterprise) |

---

## Monitoring and Logging

### Viewing Logs

```bash
# All services
./sutra-deploy.sh logs

# Specific service
./sutra-deploy.sh logs sutra-client
./sutra-deploy.sh logs sutra-api

# Follow logs in real-time
docker compose logs -f sutra-client

# Last 100 lines
docker compose logs --tail=100 sutra-api
```

### Log Locations

Logs are available via Docker:

```bash
# Container logs
docker logs sutra-client

# nginx access logs (inside container)
docker exec sutra-client cat /var/log/nginx/access.log

# nginx error logs
docker exec sutra-client cat /var/log/nginx/error.log
```

### Performance Monitoring

The UI includes built-in performance monitoring:

- **Core Web Vitals:** CLS, INP, FCP, LCP, TTFB
- **React Query Devtools:** Available in development
- **Browser DevTools:** Network, Performance tabs

---

## Security

### JWT Secret Management

**CRITICAL:** Change the default JWT secret in production:

```bash
# Generate secure secret
openssl rand -hex 32

# Update .env file
SUTRA_JWT_SECRET_KEY=your_newly_generated_secret_here

# Restart services
./sutra-deploy.sh restart
```

### HTTPS Configuration

For production deployments, add HTTPS via reverse proxy:

#### Option 1: Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Option 2: Caddy Reverse Proxy

```caddyfile
your-domain.com {
    reverse_proxy localhost:8080
}
```

### Network Security

```bash
# Restrict external access to internal services
# Only expose sutra-client (8080) externally
# Keep other services on internal Docker network

# Example firewall rules (UFW)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8000/tcp  # Block direct API access
sudo ufw deny 50051/tcp  # Block direct storage access
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
./sutra-deploy.sh logs SERVICE_NAME

# Check dependencies
docker compose ps

# Verify volumes
docker volume ls

# Check disk space
df -h
docker system df
```

### Connection Errors

```bash
# Test internal networking
docker compose exec sutra-client ping sutra-api
docker compose exec sutra-api ping storage-server

# Check health endpoints
curl http://localhost:8080/health
curl http://localhost:8000/health
```

### Authentication Errors

```bash
# Verify JWT secret is set
docker compose exec sutra-api env | grep JWT

# Check user storage
docker compose exec user-storage-server ls -lh /data

# View auth logs
docker compose logs sutra-api | grep auth
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Increase memory limits in docker-compose-grid.yml
deploy:
  resources:
    limits:
      memory: 4G

# Check embedding service
curl http://localhost:8888/health
```

### Database/Storage Issues

```bash
# Check storage files
docker compose exec storage-server ls -lh /data
docker compose exec user-storage-server ls -lh /data

# Verify write permissions
docker compose exec storage-server touch /data/test
docker compose exec user-storage-server touch /data/test

# Check WAL files
docker compose exec storage-server ls -lh /data/*.wal
```

---

## Scaling

### Horizontal Scaling (Enterprise Edition)

For enterprise deployments, scale to multiple instances:

```bash
# Set edition
export SUTRA_EDITION=enterprise

# Deploy with enterprise profile
docker compose --profile enterprise up -d

# This enables:
# - 3x embedding replicas with HAProxy
# - 3x NLG replicas with HAProxy
# - Grid Master for coordination
# - 4+ storage shards
```

### Vertical Scaling

Adjust resource limits in `docker-compose-grid.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 8G
      cpus: '4'
    reservations:
      memory: 4G
      cpus: '2'
```

---

## Backup and Recovery

### Backup Procedure

```bash
# 1. Stop services (optional but recommended)
./sutra-deploy.sh stop

# 2. Backup volumes
mkdir -p backups
docker run --rm -v sutra-models_storage-data:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/storage-$(date +%Y%m%d).tar.gz /data
  
docker run --rm -v sutra-models_user-storage-data:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/user-storage-$(date +%Y%m%d).tar.gz /data

# 3. Backup configuration
cp .env backups/env-$(date +%Y%m%d).backup
cp docker-compose-grid.yml backups/docker-compose-$(date +%Y%m%d).yml.backup

# 4. Restart services
./sutra-deploy.sh start
```

### Recovery Procedure

```bash
# 1. Stop services
./sutra-deploy.sh stop

# 2. Remove old volumes
docker volume rm sutra-models_storage-data
docker volume rm sutra-models_user-storage-data

# 3. Restore volumes
docker volume create sutra-models_storage-data
docker volume create sutra-models_user-storage-data

docker run --rm -v sutra-models_storage-data:/data -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/storage-YYYYMMDD.tar.gz -C /

docker run --rm -v sutra-models_user-storage-data:/data -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/user-storage-YYYYMMDD.tar.gz -C /

# 4. Restart services
./sutra-deploy.sh start
```

---

## Updates and Migrations

### Version Updates

```bash
# Check current version
./sutra-deploy.sh version

# Update to new version
./sutra-deploy.sh deploy v2.1.0

# Or update VERSION file and rebuild
echo "2.1.0" > VERSION
./sutra-deploy.sh rebuild
```

### Rolling Updates

```bash
# Update specific service without downtime
docker compose up -d --no-deps --build sutra-client
```

---

## Production Checklist

Before going to production, verify:

- [ ] JWT secret changed from default
- [ ] HTTPS configured via reverse proxy
- [ ] Firewall rules configured
- [ ] Backup procedure tested
- [ ] Monitoring configured
- [ ] Resource limits appropriate
- [ ] Health checks passing
- [ ] End-to-end tests passing
- [ ] Logs rotating properly
- [ ] Disk space sufficient

---

## Support and Resources

### Documentation

- [Architecture Overview](./CONVERSATION_FIRST_ARCHITECTURE.md)
- [Implementation Roadmap](./IMPLEMENTATION_ROADMAP.md)
- [Session 4.3 Complete](./SESSION_4_3_COMPLETE.md)
- [Main Project README](../../README.md)

### Common Issues

- **"Connection refused"**: Service not started or health check failing
- **"401 Unauthorized"**: JWT token missing or invalid
- **"503 Service Unavailable"**: Backend service not ready
- **Slow performance**: Insufficient resources or embedding service overloaded

### Getting Help

- Check logs: `./sutra-deploy.sh logs`
- Check status: `./sutra-deploy.sh status`
- Check GitHub Issues: https://github.com/nranjan2code/sutra-memory/issues
- Review docs: `docs/` directory

---

**Deployment Guide Complete** ✅

**Next Steps:**
1. Follow Quick Start to deploy
2. Verify all health checks pass
3. Test authentication flow
4. Create first conversation
5. Monitor performance metrics

**Happy Deploying!** 🚀
