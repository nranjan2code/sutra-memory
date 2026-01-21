#!/bin/bash
# Sutra Desktop Edition - Complete Build & Deploy Script
# This script builds everything from scratch and validates the deployment

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
WEB_CLIENT_DIR="$SCRIPT_DIR/web-client"
COMPOSE_FILE="$ROOT_DIR/.sutra/compose/desktop.yml"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Logging
log_step() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Print header
clear
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                           ║${NC}"
echo -e "${BLUE}║         Sutra Desktop Edition - Build & Deploy           ║${NC}"
echo -e "${BLUE}║              Production Release Pipeline                  ║${NC}"
echo -e "${BLUE}║                                                           ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Pre-flight checks
log_step "Step 1/8: Pre-flight Checks"

# Check Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker not found! Please install Docker Desktop."
    exit 1
fi
log_success "Docker found: $(docker --version)"

if ! docker info &> /dev/null; then
    log_error "Docker daemon not running! Please start Docker Desktop."
    exit 1
fi
log_success "Docker daemon running"

# Check Node.js (for web client)
if ! command -v node &> /dev/null; then
    log_error "Node.js not found! Please install Node.js 18+"
    exit 1
fi
log_success "Node.js found: $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    log_error "npm not found! Please install npm"
    exit 1
fi
log_success "npm found: $(npm --version)"

# Step 2: Clean previous builds
log_step "Step 2/8: Cleaning Previous Builds"

log_info "Stopping existing containers..."
docker compose -f "$COMPOSE_FILE" down 2>/dev/null || true
log_success "Containers stopped"

log_info "Removing old images (if any)..."
docker rmi sutra-desktop-web:latest 2>/dev/null || true
docker rmi sutra-api:latest 2>/dev/null || true
docker rmi sutra-storage:latest 2>/dev/null || true
log_success "Old images removed"

# Step 3: Install web client dependencies
log_step "Step 3/8: Installing Web Client Dependencies"

cd "$WEB_CLIENT_DIR"
log_info "Running npm install..."
npm install --legacy-peer-deps
log_success "Dependencies installed ($(du -sh node_modules | cut -f1))"

# Step 4: Lint and type-check web client
log_step "Step 4/8: Validating Web Client Code"

log_info "Running TypeScript type check..."
npm run type-check
log_success "TypeScript validation passed"

# Step 5: Build web client locally (test)
log_step "Step 5/8: Building Web Client (Test Build)"

log_info "Running production build..."
npm run build
log_success "Web client built successfully ($(du -sh dist | cut -f1))"

# Verify build artifacts
if [ ! -f "dist/index.html" ]; then
    log_error "Build failed: index.html not found"
    exit 1
fi
log_success "Build artifacts verified"

# Step 6: Build Docker images
log_step "Step 6/8: Building Docker Images"

cd "$ROOT_DIR"

log_info "Building storage server image..."
docker build -t sutra-storage:latest -f packages/sutra-storage/Dockerfile .
log_success "Storage server image built"

log_info "Building API server image..."
docker build -t sutra-api:latest -f packages/sutra-api/Dockerfile .
log_success "API server image built"

log_info "Building embedding server image..."
docker build -t sutra-embedding-simple:latest -f desktop/embedding-service/Dockerfile desktop/embedding-service
log_success "Embedding server image built"

log_info "Building web client image..."
docker build -t sutra-desktop-web:latest -f desktop/web-client/Dockerfile desktop/web-client
log_success "Web client image built"

# Show image sizes
log_info "Image sizes:"
docker images | grep -E "sutra-storage|sutra-api|sutra-desktop-web|sutra-embedder" | awk '{print "  " $1 ":" $2 " - " $7 $8}'

# Step 7: Deploy services
log_step "Step 7/8: Deploying Services"

log_info "Starting Docker Compose stack..."
docker compose -f "$COMPOSE_FILE" up -d

log_info "Waiting for services to be healthy..."

# Wait for storage server
log_info "Waiting for storage server..."
for i in {1..60}; do
    if docker compose -f "$COMPOSE_FILE" exec -T storage-server timeout 1 bash -c '</dev/tcp/localhost/50051' 2>/dev/null; then
        log_success "Storage server ready"
        break
    fi
    if [ $i -eq 60 ]; then
        log_error "Storage server failed to start"
        docker compose -f "$COMPOSE_FILE" logs storage-server
        exit 1
    fi
    sleep 1
    echo -n "."
done
echo ""

# Wait for API server
log_info "Waiting for API server..."
for i in {1..60}; do
    if curl -sf http://127.0.0.1:8000/health &>/dev/null; then
        log_success "API server ready"
        break
    fi
    if [ $i -eq 60 ]; then
        log_error "API server failed to start"
        docker compose -f "$COMPOSE_FILE" logs api
        exit 1
    fi
    sleep 1
    echo -n "."
done
echo ""

# Wait for web client
log_info "Waiting for web client..."
for i in {1..60}; do
    if curl -sf http://127.0.0.1:3000/health &>/dev/null; then
        log_success "Web client ready"
        break
    fi
    if [ $i -eq 60 ]; then
        log_error "Web client failed to start"
        docker compose -f "$COMPOSE_FILE" logs web-client
        exit 1
    fi
    sleep 1
    echo -n "."
done
echo ""

# Step 8: End-to-end validation
log_step "Step 8/8: End-to-End Validation"

# Test API health
log_info "Testing API health..."
API_HEALTH=$(curl -s http://127.0.0.1:8000/health)
if [[ "$API_HEALTH" == *"healthy"* ]] || [[ "$API_HEALTH" == *"ok"* ]]; then
    log_success "API health check passed"
else
    log_error "API health check failed: $API_HEALTH"
    exit 1
fi

# Test learning endpoint
log_info "Testing learning endpoint..."
LEARN_RESULT=$(curl -s -X POST http://127.0.0.1:8000/api/v1/learn \
    -H "Content-Type: application/json" \
    -d '{"content":"Test concept for build validation"}')
if [[ "$LEARN_RESULT" == *"concept_id"* ]]; then
    log_success "Learning endpoint works"
else
    log_error "Learning endpoint failed: $LEARN_RESULT"
    exit 1
fi

# Test query endpoint
log_info "Testing query endpoint..."
QUERY_RESULT=$(curl -s -X POST http://127.0.0.1:8000/api/v1/reason \
    -H "Content-Type: application/json" \
    -d '{"query":"What is a test?"}')
if [[ "$QUERY_RESULT" == *"answer"* ]] || [[ "$QUERY_RESULT" == *"concepts"* ]]; then
    log_success "Query endpoint works"
else
    log_error "Query endpoint failed: $QUERY_RESULT"
fi

# Test web client
log_info "Testing web client..."
WEB_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000/)
if [ "$WEB_RESPONSE" = "200" ]; then
    log_success "Web client serves content (HTTP $WEB_RESPONSE)"
else
    log_error "Web client failed (HTTP $WEB_RESPONSE)"
    exit 1
fi

# Get statistics
log_info "Fetching system statistics..."
STATS=$(curl -s http://127.0.0.1:8000/api/v1/stats)
echo "$STATS" | jq . 2>/dev/null || echo "$STATS"

# Final summary
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                           ║${NC}"
echo -e "${GREEN}║            ✅ BUILD & DEPLOY SUCCESSFUL! ✅                ║${NC}"
echo -e "${GREEN}║                                                           ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}🌐 Access your Sutra Desktop Edition:${NC}"
echo ""
echo -e "   ${GREEN}➜${NC} Web Interface:  ${YELLOW}http://localhost:3000${NC}"
echo -e "   ${GREEN}➜${NC} API Server:     ${YELLOW}http://localhost:8000${NC}"
echo -e "   ${GREEN}➜${NC} API Docs:       ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
echo -e "${BLUE}📊 Services Status:${NC}"
docker compose -f "$COMPOSE_FILE" ps
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo -e "   • User Guide:     ${YELLOW}desktop/DESKTOP_EDITION.md${NC}"
echo -e "   • Web Client:     ${YELLOW}desktop/web-client/README.md${NC}"
echo -e "   • Architecture:   ${YELLOW}DESKTOP_EDITION_IMPLEMENTATION.md${NC}"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo -e "   • View logs:      ${YELLOW}./desktop/scripts/docker-start.sh logs${NC}"
echo -e "   • Check status:   ${YELLOW}./desktop/scripts/docker-start.sh status${NC}"
echo -e "   • Stop services:  ${YELLOW}./desktop/scripts/docker-start.sh stop${NC}"
echo ""
echo -e "${GREEN}Ready for testing! Open http://localhost:3000 in your browser.${NC}"
echo ""
