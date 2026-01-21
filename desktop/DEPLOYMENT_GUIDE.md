# Desktop Edition - Development & Deployment Guide

Complete guide for developers building and deploying the Desktop Edition.

## Project Structure

```
desktop/
├── web-client/               # React web application
│   ├── src/
│   │   ├── api/             # API client
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── store/           # State management
│   │   └── ...
│   ├── Dockerfile           # Production build
│   ├── nginx.conf           # Nginx config
│   └── package.json         # Dependencies
├── scripts/
│   └── docker-start.sh      # Service management
├── build-desktop-edition.sh # Complete build script
├── validate-desktop.sh      # Validation script
├── DESKTOP_EDITION.md       # User documentation
├── QUICKSTART.md            # Quick start guide
└── RELEASE_CHECKLIST.md     # Release process

.sutra/compose/
└── desktop.yml              # Docker Compose config
```

## Development Workflow

### 1. Local Development (Web Client)

```bash
cd desktop/web-client

# Install dependencies
npm install --legacy-peer-deps

# Start dev server with hot reload
npm run dev

# Open browser
open http://localhost:3000
```

**Backend services must be running separately:**
```bash
./desktop/scripts/docker-start.sh start
```

### 2. Build for Production

```bash
cd desktop/web-client

# TypeScript check
npm run type-check

# Production build
npm run build

# Output: dist/ directory
```

### 3. Docker Build

```bash
# Build web client image
docker build -t sutra-desktop-web:latest \
  -f desktop/web-client/Dockerfile \
  desktop/web-client

# Or use the complete build script
./desktop/build-desktop-edition.sh
```

## Complete Build Process

The `build-desktop-edition.sh` script does everything:

### Phase 1: Pre-flight Checks
- Verify Docker is installed and running
- Check Node.js and npm are available
- Validate environment

### Phase 2: Clean Previous Builds
- Stop running containers
- Remove old images
- Clean npm cache if needed

### Phase 3: Web Client Dependencies
- Run `npm install` with proper flags
- Verify node_modules installed

### Phase 4: Code Validation
- TypeScript type checking
- Linting (if configured)

### Phase 5: Web Client Build
- Production build with Vite
- Verify dist/ artifacts
- Check bundle sizes

### Phase 6: Docker Images
- Build storage server image
- Build API server image
- Build web client image with nginx
- Pull embedding service image

### Phase 7: Deploy Services
- Start Docker Compose stack
- Wait for health checks
- Verify all containers running

### Phase 8: End-to-End Validation
- Test API health endpoint
- Test learning endpoint
- Test query endpoint
- Test web client serves correctly
- Fetch and display statistics

## Docker Compose Configuration

### Services

**storage-server**
- Image: `sutra-storage:latest`
- Port: 127.0.0.1:50051
- Purpose: Graph storage engine
- Health check: TCP connection to port 50051

**embedding**
- Image: `ghcr.io/nranjan2code/sutra-embedder:v1.0.1`
- Port: 8888 (internal only)
- Purpose: Semantic embeddings
- Health check: HTTP /health endpoint

**api**
- Image: `sutra-api:latest`
- Port: 127.0.0.1:8000
- Purpose: REST API backend
- Depends on: storage-server
- Health check: HTTP /health endpoint

**web-client**
- Image: `sutra-desktop-web:latest`
- Port: 127.0.0.1:3000
- Purpose: React web interface
- Depends on: api
- Health check: HTTP / endpoint

### Volumes

```yaml
volumes:
  storage-data:      # Persistent storage data
    driver: local
```

### Networks

```yaml
networks:
  desktop-network:   # Internal communication
    driver: bridge
```

## Environment Variables

### Storage Server
- `RUST_LOG`: Log level (info, debug)
- `STORAGE_PATH`: Data directory path
- `VECTOR_DIMENSION`: Embedding dimensions (768)
- `SUTRA_EDITION`: Edition type (simple)

### API Server
- `PYTHONUNBUFFERED`: Enable unbuffered output
- `SUTRA_STORAGE_SERVER`: Storage server address
- `SUTRA_JWT_SECRET_KEY`: JWT secret (local use)

### Web Client
- `VITE_API_URL`: API server URL (build time)

## Testing

### Automated Testing

```bash
# Full build + test
./desktop/build-desktop-edition.sh

# Quick validation only
./desktop/validate-desktop.sh
```

### Manual Testing

1. **Web Interface**
   ```bash
   open http://localhost:3000
   ```
   - Navigate all pages
   - Test chat functionality
   - Test knowledge browser
   - Check analytics

2. **API Endpoints**
   ```bash
   # Health check
   curl http://localhost:8000/health
   
   # Learn endpoint
   curl -X POST http://localhost:8000/api/v1/learn \
     -H "Content-Type: application/json" \
     -d '{"content":"Test concept"}'
   
   # Query endpoint
   curl -X POST http://localhost:8000/api/v1/reason \
     -H "Content-Type: application/json" \
     -d '{"query":"What is a test?"}'
   
   # Stats endpoint
   curl http://localhost:8000/api/v1/stats
   ```

3. **Container Health**
   ```bash
   docker ps | grep sutra-desktop
   docker compose -f .sutra/compose/desktop.yml ps
   ```

## Deployment

### Local Deployment

```bash
./desktop/build-desktop-edition.sh
```

### Production Deployment

1. **Build images**
   ```bash
   ./desktop/build-desktop-edition.sh
   ```

2. **Tag with version**
   ```bash
   VERSION=1.0.0
   docker tag sutra-desktop-web:latest sutra-desktop-web:$VERSION
   docker tag sutra-api:latest sutra-api:$VERSION
   docker tag sutra-storage:latest sutra-storage:$VERSION
   ```

3. **Push to registry** (optional)
   ```bash
   docker push sutra-desktop-web:$VERSION
   docker push sutra-api:$VERSION
   docker push sutra-storage:$VERSION
   ```

4. **Deploy**
   ```bash
   export SUTRA_VERSION=$VERSION
   docker compose -f .sutra/compose/desktop.yml up -d
   ```

## Troubleshooting

### Build Failures

**npm install fails**
```bash
cd desktop/web-client
rm -rf node_modules package-lock.json
npm cache clean --force
npm install --legacy-peer-deps
```

**TypeScript errors**
```bash
cd desktop/web-client
npm run type-check
# Fix reported errors
```

**Docker build fails**
```bash
# Clear Docker cache
docker builder prune -a

# Rebuild
docker build --no-cache -t sutra-desktop-web:latest \
  -f desktop/web-client/Dockerfile desktop/web-client
```

### Runtime Issues

**Container won't start**
```bash
# Check logs
docker compose -f .sutra/compose/desktop.yml logs <service-name>

# Restart specific service
docker restart sutra-desktop-<service>
```

**API errors**
```bash
# Check API logs
docker logs sutra-desktop-api

# Check storage logs
docker logs sutra-desktop-storage

# Check connectivity
docker exec sutra-desktop-api curl http://storage-server:50051
```

**Web client blank page**
```bash
# Check nginx logs
docker logs sutra-desktop-web

# Check if dist/ was built
docker exec sutra-desktop-web ls -la /usr/share/nginx/html

# Rebuild web client
cd desktop/web-client
npm run build
docker build -t sutra-desktop-web:latest .
```

## Performance Optimization

### Web Client
- Use `npm run build` for production (minified)
- Enable gzip in nginx (already configured)
- Use CDN for static assets (if needed)
- Implement code splitting (already done via Vite)

### Docker
- Use multi-stage builds (already implemented)
- Optimize layer caching
- Use .dockerignore files
- Allocate sufficient memory to Docker

### API
- Use connection pooling
- Enable caching headers
- Optimize query complexity

## Security Best Practices

### Development
- Keep dependencies updated
- Run `npm audit` regularly
- Use environment variables for secrets
- Never commit sensitive data

### Production
- Use HTTPS (not applicable for localhost)
- Implement rate limiting
- Add authentication (for public access)
- Regular security updates

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Desktop Edition

on:
  push:
    branches: [ main ]
    paths:
      - 'desktop/**'
      - '.sutra/compose/desktop.yml'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Build Desktop Edition
        run: ./desktop/build-desktop-edition.sh
      
      - name: Run Validation
        run: ./desktop/validate-desktop.sh
```

## Monitoring

### Logs
```bash
# All services
./desktop/scripts/docker-start.sh logs

# Specific service
docker logs -f sutra-desktop-web
docker logs -f sutra-desktop-api
docker logs -f sutra-desktop-storage
```

### Metrics
```bash
# Container stats
docker stats sutra-desktop-web sutra-desktop-api sutra-desktop-storage

# System statistics
curl http://localhost:8000/api/v1/stats | jq .
```

## Backup & Restore

### Backup
```bash
# Backup storage data
docker run --rm -v sutra-desktop-storage-data:/data \
  -v $(pwd):/backup alpine \
  tar czf /backup/sutra-backup-$(date +%Y%m%d).tar.gz -C /data .
```

### Restore
```bash
# Restore from backup
docker run --rm -v sutra-desktop-storage-data:/data \
  -v $(pwd):/backup alpine \
  tar xzf /backup/sutra-backup-20260121.tar.gz -C /data
```

## Release Process

See `desktop/RELEASE_CHECKLIST.md` for the complete release process.

Quick steps:
1. Update version numbers
2. Run full build and tests
3. Tag git commit
4. Create release archive
5. Update documentation
6. Announce release

## Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: `docs/` directory
- **API Docs**: http://localhost:8000/docs (when running)
