#!/bin/bash

# Sutra Grid Docker Deployment Script
# Builds and deploys the complete Sutra AI system with Grid integration

set -e  # Exit on error

echo "🚀 Sutra Grid Docker Deployment"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose-grid.yml"
BUILD_PARALLEL=4

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create necessary directories
setup_directories() {
    log_info "Setting up volume directories..."
    
    mkdir -p docker-volumes/{storage-data,grid-events,agent1-data,agent2-data}
    
    # Set appropriate permissions
    chmod 755 docker-volumes/*
    
    log_success "Volume directories created"
}

# Clean up old containers and images
cleanup() {
    log_info "Cleaning up old containers and images..."
    
    # Stop and remove containers
    docker-compose -f $COMPOSE_FILE down --remove-orphans 2>/dev/null || true
    
    # Remove old images (optional - uncomment if you want to force rebuild)
    # docker rmi $(docker images | grep -E "(sutra-|grid-)" | awk '{print $3}') 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# Build all images
build_images() {
    log_info "Building Docker images..."
    log_warn "This may take several minutes on first run..."
    
    # Build all services in parallel
    docker-compose -f $COMPOSE_FILE build --parallel
    
    log_success "All images built successfully"
}

# Deploy the stack
deploy_stack() {
    log_info "Deploying Sutra Grid stack..."
    
    # Start services with dependency order
    docker-compose -f $COMPOSE_FILE up -d
    
    log_success "Stack deployed successfully"
}

# Wait for services to be healthy
wait_for_health() {
    log_info "Waiting for services to become healthy..."
    
    local max_wait=300  # 5 minutes
    local wait_time=0
    local check_interval=10
    
    while [ $wait_time -lt $max_wait ]; do
        local unhealthy_services=$(docker-compose -f $COMPOSE_FILE ps --services --filter "health=unhealthy" | wc -l)
        local starting_services=$(docker-compose -f $COMPOSE_FILE ps --services --filter "health=starting" | wc -l)
        
        if [ "$unhealthy_services" -eq 0 ] && [ "$starting_services" -eq 0 ]; then
            log_success "All services are healthy!"
            return 0
        fi
        
        echo -n "."
        sleep $check_interval
        wait_time=$((wait_time + check_interval))
    done
    
    log_warn "Some services may still be starting up. Check status with: docker-compose -f $COMPOSE_FILE ps"
}

# Show service status
show_status() {
    log_info "Service Status:"
    echo
    docker-compose -f $COMPOSE_FILE ps
    echo
    
    log_info "Service URLs:"
    echo "• Sutra Control Center (Grid Management): http://localhost:9000"
    echo "• Sutra Control Center Grid UI:           http://localhost:9000/grid"
    echo "• Sutra Client (Interactive AI):          http://localhost:8080"
    echo "• Sutra API:                             http://localhost:8000"
    echo "• Sutra Hybrid API:                      http://localhost:8001"
    echo "• Grid Master gRPC:                      localhost:7000"
    echo "• Storage Server gRPC:                   localhost:50051"
    echo "• Grid Events Storage gRPC:              localhost:50052"
    echo
}

# Show logs for debugging
show_logs() {
    log_info "Recent logs from all services:"
    echo
    docker-compose -f $COMPOSE_FILE logs --tail=20
}

# Test Grid functionality
test_grid() {
    log_info "Testing Grid functionality..."
    
    # Wait a bit for services to fully start
    sleep 10
    
    # Test Control Center health
    if curl -sf http://localhost:9000/health > /dev/null; then
        log_success "✅ Control Center is healthy"
    else
        log_error "❌ Control Center is not responding"
        return 1
    fi
    
    # Test Grid API endpoints
    if curl -sf http://localhost:9000/api/grid/status > /dev/null; then
        log_success "✅ Grid API is responding"
    else
        log_warn "⚠️ Grid API may still be starting up"
    fi
    
    # Test if Grid agents are registered
    local agents=$(curl -s http://localhost:9000/api/grid/agents 2>/dev/null | grep -o '"agent_id"' | wc -l || echo 0)
    if [ "$agents" -gt 0 ]; then
        log_success "✅ Grid agents are registered ($agents found)"
    else
        log_warn "⚠️ No Grid agents registered yet (may still be connecting)"
    fi
    
    log_info "Grid functionality test completed"
}

# Main deployment flow
main() {
    echo
    log_info "Starting Sutra Grid deployment..."
    echo
    
    # Parse command line arguments
    case "${1:-deploy}" in
        "cleanup")
            cleanup
            ;;
        "build")
            check_prerequisites
            setup_directories
            build_images
            ;;
        "deploy")
            check_prerequisites
            setup_directories
            cleanup
            build_images
            deploy_stack
            wait_for_health
            show_status
            test_grid
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "test")
            test_grid
            ;;
        "stop")
            log_info "Stopping all services..."
            docker-compose -f $COMPOSE_FILE down
            log_success "All services stopped"
            ;;
        "restart")
            log_info "Restarting services..."
            docker-compose -f $COMPOSE_FILE restart
            wait_for_health
            show_status
            ;;
        *)
            echo "Usage: $0 [deploy|build|cleanup|status|logs|test|stop|restart]"
            echo
            echo "Commands:"
            echo "  deploy   - Full deployment (default)"
            echo "  build    - Build images only"
            echo "  cleanup  - Clean up old containers/images"
            echo "  status   - Show service status and URLs"
            echo "  logs     - Show recent logs"
            echo "  test     - Test Grid functionality"
            echo "  stop     - Stop all services"
            echo "  restart  - Restart all services"
            exit 1
            ;;
    esac
    
    echo
    log_success "🎉 Sutra Grid deployment completed!"
    echo
    if [ "${1:-deploy}" = "deploy" ]; then
        log_info "Access the Grid Management UI at: http://localhost:9000/grid"
        log_info "Monitor with: ./deploy-docker-grid.sh status"
        log_info "View logs with: ./deploy-docker-grid.sh logs"
    fi
}

# Run main function with all arguments
main "$@"