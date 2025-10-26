#!/bin/bash
# Sutra AI - Master Build Script v3.0
# Centralized build orchestration for all services
# Usage: ./build/scripts/build-all.sh [--profile simple|community|enterprise] [--parallel]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BUILD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT_DIR="$(cd "$BUILD_DIR/.." && pwd)"
PROFILE="${SUTRA_EDITION:-simple}"
PARALLEL="${BUILD_PARALLEL:-false}"
VERSION="${SUTRA_VERSION:-latest}"

# Helper functions
log_info() { echo -e "${BLUE}ℹ ${NC}$1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

print_header() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║              Sutra AI - Master Build System v3.0             ║"
    echo "║                    🏗️  BUILD CONSOLIDATION                   ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    log_info "Profile: $PROFILE"
    log_info "Version: $VERSION" 
    log_info "Parallel: $PARALLEL"
    echo ""
}

# Build shared base images first
build_base_images() {
    log_info "Building shared base images..."
    
    # Python base (used by API, Hybrid, etc.)
    log_info "Building sutra-python-base..."
    docker build -f "$BUILD_DIR/docker/base/python-base.dockerfile" \
        -t "sutra-python-base:$VERSION" \
        -t "sutra-python-base:latest" \
        "$ROOT_DIR"
    
    # Rust base (used by Storage services)  
    log_info "Building sutra-rust-base..."
    docker build -f "$BUILD_DIR/docker/base/rust-base.dockerfile" \
        -t "sutra-rust-base:$VERSION" \
        -t "sutra-rust-base:latest" \
        "$ROOT_DIR"
        
    log_success "Base images built successfully"
}

# Build service images
build_service_images() {
    log_info "Building service images for profile: $PROFILE..."
    
    local services=()
    
        # Core services (all profiles)
    local services=(
        "sutra-storage:sutrabuild/docker/services/sutra-storage.dockerfile"
        "sutra-api:sutrabuild/docker/services/sutra-api.dockerfile" 
        "sutra-hybrid:sutrabuild/docker/services/sutra-hybrid.dockerfile"
    )
    
    # Profile-specific services
    case "$PROFILE" in
        simple|community)
            services+=(
                "sutra-embedding-service:sutrabuild/docker/services/sutra-embedding-service.dockerfile"
            )
            ;;
        enterprise)
            services+=(
                "sutra-embedding-service:sutrabuild/docker/services/sutra-embedding-service.dockerfile"
                "sutra-grid-master:packages/sutra-grid-master/Dockerfile"
                "sutra-grid-agent:packages/sutra-grid-agent/Dockerfile"
            )
            ;;
    esac
    
    # Build services
    if [ "$PARALLEL" = "true" ]; then
        build_services_parallel "${services[@]}"
    else
        build_services_sequential "${services[@]}"
    fi
    
    log_success "All service images built for profile: $PROFILE"
}

build_services_sequential() {
    local services=("$@")
    
    for service_def in "${services[@]}"; do
        IFS=':' read -r service_name dockerfile <<< "$service_def"
        
        log_info "Building $service_name..."
        docker build -f "$dockerfile" \
            -t "$service_name:$VERSION" \
            -t "$service_name:latest" \
            "$ROOT_DIR"
            
        log_success "Built $service_name"
    done
}

build_services_parallel() {
    local services=("$@")
    local pids=()
    
    log_info "Building services in parallel..."
    
    for service_def in "${services[@]}"; do
        IFS=':' read -r service_name dockerfile <<< "$service_def"
        
        (
            log_info "Building $service_name..."
            docker build -f "$dockerfile" \
                -t "$service_name:$VERSION" \
                -t "$service_name:latest" \
                "$ROOT_DIR" &> "/tmp/build-$service_name.log"
            log_success "Built $service_name"
        ) &
        
        pids+=($!)
    done
    
    # Wait for all builds to complete
    local failed=0
    for pid in "${pids[@]}"; do
        if ! wait "$pid"; then
            ((failed++))
        fi
    done
    
    if [ "$failed" -gt 0 ]; then
        log_error "$failed service builds failed"
        return 1
    fi
}

# Verify builds
verify_images() {
    log_info "Verifying built images..."
    
    local expected_images=(
        "sutra-python-base:$VERSION"
        "sutra-rust-base:$VERSION" 
        "sutra-storage:$VERSION"
        "sutra-api:$VERSION"
        "sutra-hybrid:$VERSION"
    )
    
    local missing=0
    for image in "${expected_images[@]}"; do
        if docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^$image$"; then
            log_success "$image ✓"
        else
            log_error "Missing: $image"
            ((missing++))
        fi
    done
    
    if [ "$missing" -gt 0 ]; then
        log_error "$missing images missing!"
        return 1
    fi
    
    log_success "All images verified successfully"
}

# Show build summary
show_summary() {
    echo ""
    log_success "═══════════════════════════════════════════════════"
    log_success "  BUILD COMPLETE: Sutra AI $PROFILE Edition"
    log_success "═══════════════════════════════════════════════════"
    echo ""
    log_info "Built images:"
    docker images --filter "reference=sutra-*" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | head -10
    echo ""
    log_info "Next steps:"
    echo "  • Run: docker-compose -f build/compose/docker-compose.yml --profile $PROFILE up"
    echo "  • Or:  ./sutra-deploy.sh up"
    echo ""
}

# Main execution
main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --profile)
                PROFILE="$2"
                shift 2
                ;;
            --parallel)
                PARALLEL="true"
                shift
                ;;
            --version)
                VERSION="$2"
                shift 2
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    print_header
    
    # Execute build pipeline
    build_base_images
    build_service_images
    verify_images
    show_summary
}

# Run main function
main "$@"