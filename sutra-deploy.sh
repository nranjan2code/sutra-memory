#!/bin/bash
# Sutra Grid Deployment Manager v2.0
# Production-grade command center for complete system lifecycle
# 
# Principles:
# - Idempotent operations (safe to run multiple times)
# - Self-healing (auto-fix common issues)
# - Fail-fast validation
# - Clear observability

set -euo pipefail  # Fail on undefined vars and pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose-grid.yml"
PROJECT_NAME="sutra-grid"
BUILD_TIMEOUT=600
STARTUP_TIMEOUT=120
SHUTDOWN_TIMEOUT=30

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_step() {
    echo -e "${CYAN}▶${NC} $1"
}

log_debug() {
    if [ "${DEBUG:-0}" = "1" ]; then
        echo -e "${MAGENTA}[DEBUG]${NC} $1"
    fi
}

print_header() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║       Sutra Grid Command Center v2.0 (Production)            ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
}

# ============================================================================
# PREREQUISITE CHECKS - Fail fast before doing anything
# ============================================================================

check_prerequisites() {
    log_step "Checking prerequisites..."
    local missing=0
    
    # Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not installed"
        ((missing++))
    else
        log_debug "Docker: $(docker --version)"
    fi
    
    # Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose not installed"
        ((missing++))
    else
        log_debug "Docker Compose: $(docker-compose --version)"
    fi
    
    # Docker daemon running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon not running"
        ((missing++))
    fi
    
    # Compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Docker Compose file not found: $COMPOSE_FILE"
        ((missing++))
    fi
    
    # Critical config files
    if [ ! -f "docker/haproxy.cfg" ]; then
        log_error "HAProxy config not found: docker/haproxy.cfg"
        ((missing++))
    fi
    
    if [ $missing -gt 0 ]; then
        log_error "Missing $missing prerequisites. Cannot proceed."
        return 1
    fi
    
    log_success "All prerequisites met"
    return 0
}

# ============================================================================
# STATE DETECTION - Know current system state
# ============================================================================

get_system_state() {
    local running=$(docker ps --filter "name=sutra-" --filter "name=embedding" --format "{{.Names}}" | wc -l | tr -d ' ')
    local stopped=$(docker ps -a --filter "name=sutra-" --filter "name=embedding" --filter "status=exited" --format "{{.Names}}" | wc -l | tr -d ' ')
    local images=$(docker images --filter "reference=sutra-*" --filter "reference=*embedding*" --format "{{.Repository}}" | wc -l | tr -d ' ')
    
    if [ "$running" -gt 0 ]; then
        echo "RUNNING"
    elif [ "$stopped" -gt 0 ]; then
        echo "STOPPED"
    elif [ "$images" -gt 0 ]; then
        echo "BUILT"
    else
        echo "CLEAN"
    fi
}

show_state() {
    local state=$(get_system_state)
    log_info "Current state: $state"
    
    case $state in
        RUNNING)
            log_info "$(docker ps --filter 'name=sutra-' --filter 'name=embedding' --format '{{.Names}}' | wc -l | tr -d ' ') containers running"
            ;;
        STOPPED)
            log_info "Containers exist but stopped"
            ;;
        BUILT)
            log_info "Images exist but no containers"
            ;;
        CLEAN)
            log_info "No existing deployment"
            ;;
    esac
}

# ============================================================================
# BUILD COMMAND - Idempotent, handles HA properly
# ============================================================================

cmd_build() {
    log_step "BUILD: Building all Docker images"
    
    # Check prerequisites first
    check_prerequisites || return 1
    
    local state=$(get_system_state)
    log_info "Current state: $state"
    
    # Clean up any partial builds
    log_step "Cleaning up stale build artifacts..."
    docker builder prune -f > /dev/null 2>&1 || true
    
    # CRITICAL: Build embedding service ONCE for HA replicas
    # This prevents the 3-way race condition
    log_step "Building embedding service (shared by 3 HA replicas)..."
    if [ -f "packages/sutra-embedding-service/Dockerfile" ]; then
        if docker build -t sutra-embedding-service:latest packages/sutra-embedding-service; then
            log_success "Embedding service image ready"
        else
            log_error "Failed to build embedding service"
            return 1
        fi
    else
        log_error "Embedding service Dockerfile not found"
        return 1
    fi
    
    # Build all other services in parallel using docker-compose
    log_step "Building remaining services..."
    if docker-compose -f "$COMPOSE_FILE" build --parallel; then
        log_success "All services built"
    else
        log_warning "Some builds may have failed (check logs)"
    fi
    
    # Verify critical images exist
    log_step "Verifying critical images..."
    local critical_images=(
        "sutra-storage-server:latest"
        "sutra-embedding-service:latest"
        "sutra-hybrid:latest"
        "sutra-api:latest"
        "sutra-grid-master:latest"
    )
    
    local missing=0
    for image in "${critical_images[@]}"; do
        if docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^$image$"; then
            log_debug "✓ $image"
        else
            log_error "Missing: $image"
            ((missing++))
        fi
    done
    
    if [ $missing -gt 0 ]; then
        log_error "$missing critical images missing"
        return 1
    fi
    
    echo ""
    log_success "BUILD COMPLETE: All images ready"
    log_info "Built images:"
    docker images --filter "reference=sutra-*" --filter "reference=*embedding*" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | head -15
    
    return 0
}

# ============================================================================
# UP COMMAND - Idempotent start with validation
# ============================================================================

cmd_up() {
    log_step "UP: Starting Sutra Grid system"
    
    # Check prerequisites
    check_prerequisites || return 1
    
    local state=$(get_system_state)
    log_info "Current state: $state"
    
    # Auto-build if no images exist
    if [ "$state" = "CLEAN" ]; then
        log_warning "No images found. Building first..."
        cmd_build || return 1
    fi
    
    # Fix HAProxy config if it has known issues
    log_step "Validating HAProxy configuration..."
    if grep -q "option httpchk GET /health" docker/haproxy.cfg 2>/dev/null; then
        log_warning "Found deprecated HAProxy syntax - auto-fixing..."
        sed -i.bak 's/option httpchk GET \/health HTTP\/1\.1.*/http-check send meth GET uri \/health ver HTTP\/1.1 hdr Host embedding/' docker/haproxy.cfg
        log_success "HAProxy config fixed"
    fi
    
    # Start services
    log_step "Starting all services..."
    if docker-compose -f "$COMPOSE_FILE" up -d 2>&1 | tee /tmp/sutra-up.log | grep -E "(Started|Creating|recreated)" > /dev/null; then
        log_success "Services started"
    else
        log_error "Failed to start services"
        log_info "Check /tmp/sutra-up.log for details"
        return 1
    fi
    
    # Wait for critical services
    log_step "Waiting for services to initialize..."
    sleep 5
    
    # Show status
    echo ""
    cmd_status
    
    # Validate critical services
    echo ""
    log_step "Validating critical services..."
    if validate_embedding_service_quick && validate_storage_quick; then
        log_success "Critical services operational"
    else
        log_warning "Some services still starting. Run './sutra-deploy.sh validate' for full health check"
    fi
    
    echo ""
    log_success "UP COMPLETE: System running"
    return 0
}

cmd_validate() {
    log_info "Running comprehensive service validation..."
    echo ""
    
    local failures=0
    
    # Check if all containers are running
    log_info "Checking container status..."
    local containers=("sutra-storage" "sutra-embedding-service" "sutra-hybrid" "sutra-api" "sutra-control" "sutra-client" "sutra-grid-master" "sutra-grid-events" "sutra-grid-agent-1" "sutra-grid-agent-2")
    
    for container in "${containers[@]}"; do
        if docker ps | grep -q "$container"; then
            log_success "$container: Running"
        else
            log_error "$container: Not running"
            ((failures++))
        fi
    done
    
    echo ""
    
    # Validate embedding service
    if ! validate_embedding_service; then
        ((failures++))
    fi
    echo ""
    
    # Validate hybrid service
    if ! validate_hybrid_service; then
        ((failures++))
    fi
    echo ""
    
    # Test key endpoints
    log_info "Testing service endpoints..."
    local endpoints=(
        "http://localhost:8000/health:API"
        "http://localhost:8001/ping:Hybrid"
        "http://localhost:8888/health:Embedding"
        "http://localhost:9000/health:Control"
        "http://localhost:7001/health:Grid Master"
    )
    
    for endpoint in "${endpoints[@]}"; do
        local url="${endpoint%:*}"
        local name="${endpoint#*:}"
        if curl -f -s "$url" > /dev/null 2>&1; then
            log_success "$name endpoint: Responding"
        else
            log_error "$name endpoint: Not responding"
            ((failures++))
        fi
    done
    
    echo ""
    
    # Final summary
    if [ $failures -eq 0 ]; then
        log_success "All validation checks passed! System is production-ready."
        return 0
    else
        log_error "$failures validation checks failed. System is NOT production-ready."
        log_info "Check service logs and fix issues before deployment."
        return 1
    fi
}

# ============================================================================
# DOWN COMMAND - Graceful shutdown
# ============================================================================

cmd_down() {
    log_step "DOWN: Stopping Sutra Grid system"
    
    local state=$(get_system_state)
    log_info "Current state: $state"
    
    if [ "$state" = "CLEAN" ]; then
        log_info "System already stopped"
        return 0
    fi
    
    # Graceful shutdown with timeout
    log_step "Stopping services gracefully..."
    if docker-compose -f "$COMPOSE_FILE" down --timeout "$SHUTDOWN_TIMEOUT" 2>&1 | grep -E "(Stopping|Stopped|Removing)" > /dev/null; then
        log_success "All services stopped"
    else
        log_warning "Some services may still be running"
    fi
    
    log_success "DOWN COMPLETE: System stopped"
    return 0
}

# ============================================================================
# RESTART COMMAND - Safe restart with validation
# ============================================================================

cmd_restart() {
    log_step "RESTART: Restarting Sutra Grid system"
    
    # Stop first
    cmd_down || log_warning "Shutdown had issues, continuing anyway"
    
    # Wait for ports to be released
    log_step "Waiting for ports to be released..."
    sleep 3
    
    # Start again
    cmd_up
    
    return $?
}

cmd_status() {
    log_info "System Status:"
    echo ""
    docker-compose -f $COMPOSE_FILE ps
    echo ""
    
    log_info "Service URLs:"
    echo "  • Sutra Control Center: http://localhost:9000"
    echo "  • Sutra Client (UI):    http://localhost:8080"
    echo "  • Sutra API:            http://localhost:8000"
    echo "  • Sutra Hybrid API:     http://localhost:8001"
    echo "  • Sutra Embedding Service: http://localhost:8888"
    echo "  • Grid Master (HTTP):   http://localhost:7001"
    echo "  • Grid Master (gRPC):   localhost:7002"
    echo "  • Storage Server:       localhost:50051"
}

# ============================================================================
# VALIDATION FUNCTIONS - Quick and comprehensive checks
# ============================================================================

validate_embedding_service_quick() {
    # Quick check - just verify HAProxy is responding
    if curl -f -s http://localhost:8888/health > /dev/null 2>&1; then
        return 0
    fi
    return 1
}

validate_storage_quick() {
    # Quick check - verify storage server is listening
    if nc -z localhost 50051 2>/dev/null; then
        return 0
    fi
    return 1
}

validate_embedding_service() {
    log_step "Validating embedding service (HA)..."
    
    # Check if HAProxy is running
    if ! docker ps | grep -q "embedding-ha"; then
        log_error "HAProxy load balancer not running!"
        return 1
    fi
    
    # Wait for service to be ready (up to 90 seconds)
    log_info "Waiting for embedding service to load model..."
    for i in {1..18}; do
        if curl -f -s http://localhost:8888/health > /dev/null 2>&1; then
            break
        fi
        echo -n "."
        sleep 5
    done
    echo ""
    
    # Test health endpoint
    if ! curl -f -s http://localhost:8888/health > /dev/null 2>&1; then
        log_error "Embedding service health check failed!"
        log_info "Checking logs:"
        docker logs sutra-embedding-service --tail 10
        return 1
    fi
    
    # Validate model and dimension
    local health_response
    health_response=$(curl -s http://localhost:8888/health 2>/dev/null || echo "{}")
    
    local model_loaded
    local dimension
    model_loaded=$(echo "$health_response" | jq -r '.model_loaded // false' 2>/dev/null || echo "false")
    dimension=$(echo "$health_response" | jq -r '.dimension // 0' 2>/dev/null || echo "0")
    
    if [ "$model_loaded" != "true" ]; then
        log_error "Embedding model not loaded!"
        return 1
    fi
    
    if [ "$dimension" != "768" ]; then
        log_error "Wrong embedding dimension: $dimension (expected 768)"
        return 1
    fi
    
    # Test embedding generation
    local embed_response
    embed_response=$(curl -s -X POST http://localhost:8888/embed \
        -H "Content-Type: application/json" \
        -d '{"texts": ["test"], "normalize": true}' 2>/dev/null || echo "{}")
    
    local embed_length
    embed_length=$(echo "$embed_response" | jq -r '.embeddings[0] | length' 2>/dev/null || echo "0")
    
    if [ "$embed_length" != "768" ]; then
        log_error "Embedding generation failed (got $embed_length dimensions)"
        return 1
    fi
    
    log_success "Embedding service fully operational (nomic-embed-text-v1.5, 768-d)"
    return 0
}

validate_hybrid_service() {
    log_info "Validating hybrid service connection to embedding service..."
    
    # Check if hybrid is healthy (not restarting)
    local hybrid_status
    hybrid_status=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep sutra-hybrid | awk '{print $2}' || echo "Down")
    
    if echo "$hybrid_status" | grep -q "Restarting"; then
        log_error "Hybrid service is restarting! Check embedding service connection."
        log_info "Recent hybrid logs:"
        docker logs sutra-hybrid --tail 5 2>&1 | grep -E "(embedding|PRODUCTION)"
        return 1
    fi
    
    # Test hybrid ping endpoint
    if ! curl -f -s http://localhost:8001/ping > /dev/null 2>&1; then
        log_warning "Hybrid service ping endpoint not responding"
        return 1
    fi
    
    log_success "Hybrid service operational and connected to embedding service"
    return 0
}

cmd_logs() {
    local service=$1
    
    if [ -z "$service" ]; then
        log_info "Showing logs for all services (Ctrl+C to exit)..."
        docker-compose -f $COMPOSE_FILE logs -f
    else
        log_info "Showing logs for $service (Ctrl+C to exit)..."
        docker-compose -f $COMPOSE_FILE logs -f $service
    fi
}

# ============================================================================
# CLEAN COMMAND - Complete system cleanup
# ============================================================================

cmd_clean() {
    log_step "CLEAN: Removing all containers, volumes, and images"
    
    local state=$(get_system_state)
    log_info "Current state: $state"
    
    if [ "$state" = "CLEAN" ]; then
        log_info "System already clean"
        return 0
    fi
    
    log_warning "This will remove:"
    echo "  • All Sutra containers"
    echo "  • All data volumes (PERMANENT DATA LOSS)"
    echo "  • All Docker images"
    echo ""
    read -p "Continue? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log_info "Clean cancelled"
        return 0
    fi
    
    # Stop and remove everything
    log_step "Stopping and removing containers..."
    docker-compose -f "$COMPOSE_FILE" down -v --timeout "$SHUTDOWN_TIMEOUT" 2>&1 | grep -E "(Stopping|Removing)" || true
    
    # Remove any orphaned containers
    log_step "Cleaning up orphaned containers..."
    docker ps -a --filter "name=sutra-" --filter "name=embedding" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null || true
    
    # Remove images
    log_step "Removing Docker images..."
    docker images --filter "reference=sutra-*" --filter "reference=*embedding*" --format "{{.ID}}" | xargs -r docker rmi -f 2>/dev/null || true
    
    # Clean build cache
    log_step "Cleaning build cache..."
    docker builder prune -f > /dev/null 2>&1 || true
    
    # Verify clean state
    local new_state=$(get_system_state)
    if [ "$new_state" = "CLEAN" ]; then
        log_success "CLEAN COMPLETE: System reset to clean state"
    else
        log_warning "Some artifacts may remain. Check with 'docker ps -a' and 'docker images'"
    fi
    
    return 0
}

# ============================================================================
# INSTALL COMMAND - Complete first-time setup
# ============================================================================

cmd_install() {
    log_step "INSTALL: Complete first-time installation"
    
    # Check prerequisites
    check_prerequisites || return 1
    
    local state=$(get_system_state)
    if [ "$state" != "CLEAN" ]; then
        log_warning "System not in clean state: $state"
        log_info "Run './sutra-deploy.sh clean' first for fresh install"
        read -p "Continue anyway? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            return 0
        fi
    fi
    
    # Build images
    log_step "Step 1/2: Building images..."
    if ! cmd_build; then
        log_error "Build failed"
        return 1
    fi
    
    echo ""
    
    # Start services
    log_step "Step 2/2: Starting services..."
    if ! cmd_up; then
        log_error "Startup failed"
        return 1
    fi
    
    echo ""
    log_success "═══════════════════════════════════════════════════"
    log_success "  INSTALL COMPLETE: Sutra Grid System Ready"
    log_success "═══════════════════════════════════════════════════"
    echo ""
    log_info "Access Points:"
    echo "  • Control Center:  http://localhost:9000"
    echo "  • Client UI:       http://localhost:8080"
    echo "  • API:             http://localhost:8000"
    echo "  • Hybrid API:      http://localhost:8001"
    echo ""
    log_info "Next Steps:"
    echo "  • Run './sutra-deploy.sh validate' for full health check"
    echo "  • Run './sutra-deploy.sh status' to see service status"
    echo ""
    
    return 0
}

cmd_maintenance() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                    Maintenance Menu                           ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "  1) View system status"
    echo "  2) Check service health"
    echo "  3) Restart unhealthy services"
    echo "  4) View logs"
    echo "  5) Clean up unused resources"
    echo "  6) Backup data volumes"
    echo "  7) Exit"
    echo ""
    read -p "Select option: " option
    
    case $option in
        1)
            cmd_status
            ;;
        2)
            log_info "Checking service health..."
            docker-compose -f $COMPOSE_FILE ps --format json | jq -r '.[] | "\(.Service): \(.Health)"'
            ;;
        3)
            log_info "Restarting unhealthy services..."
            unhealthy=$(docker-compose -f $COMPOSE_FILE ps --format json | jq -r '.[] | select(.Health == "unhealthy") | .Service')
            if [ -z "$unhealthy" ]; then
                log_success "All services are healthy!"
            else
                for service in $unhealthy; do
                    log_warning "Restarting $service..."
                    docker-compose -f $COMPOSE_FILE restart $service
                done
                log_success "Services restarted!"
            fi
            ;;
        4)
            read -p "Enter service name (or press Enter for all): " service
            cmd_logs $service
            ;;
        5)
            log_info "Cleaning up unused Docker resources..."
            docker system prune -f
            log_success "Cleanup complete!"
            ;;
        6)
            log_info "Backing up data volumes..."
            timestamp=$(date +%Y%m%d_%H%M%S)
            mkdir -p backups
            docker run --rm -v sutra-models_storage-data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/storage-data-$timestamp.tar.gz -C /data .
            docker run --rm -v sutra-models_grid-event-data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/grid-event-data-$timestamp.tar.gz -C /data .
            log_success "Backups saved to: backups/"
            ;;
        7)
            exit 0
            ;;
        *)
            log_error "Invalid option"
            ;;
    esac
}

cmd_help() {
    echo "Usage: ./sutra-deploy.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install      - First-time installation (build + start)"
    echo "  build        - Build all Docker images"
    echo "  up           - Start all services"
    echo "  down         - Stop all services"
    echo "  restart      - Restart all services"
    echo "  status       - Show service status and URLs"
    echo "  validate     - Run comprehensive health checks (including embedding service)"
    echo "  logs [svc]   - Show logs (optionally for specific service)"
    echo "  clean        - Remove all containers, volumes, and images"
    echo "  maintenance  - Interactive maintenance menu"
    echo "  help         - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./sutra-deploy.sh install         # First-time setup"
    echo "  ./sutra-deploy.sh up              # Start services"
    echo "  ./sutra-deploy.sh validate        # Check system health"
    echo "  ./sutra-deploy.sh logs sutra-api  # View API logs"
    echo "  ./sutra-deploy.sh maintenance     # Maintenance menu"
    echo ""
}

# Main script
print_header

# Check if compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    log_error "Docker Compose file not found: $COMPOSE_FILE"
    exit 1
fi

# Parse command
COMMAND=${1:-help}

case $COMMAND in
    install)
        cmd_install
        ;;
    build)
        cmd_build
        ;;
    up|start)
        cmd_up
        ;;
    down|stop)
        cmd_down
        ;;
    restart)
        cmd_restart
        ;;
    status)
        cmd_status
        ;;
    validate)
        cmd_validate
        ;;
    logs)
        cmd_logs $2
        ;;
    clean)
        cmd_clean
        ;;
    maintenance|maint)
        cmd_maintenance
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        log_error "Unknown command: $COMMAND"
        echo ""
        cmd_help
        exit 1
        ;;
esac

echo ""
