#!/bin/bash
set -euo pipefail

echo "🚀 Building Complete Sutra AI System"
echo "====================================="
echo "Using official Docker Hub images:"
echo "  • python:3.11-slim"
echo "  • rust:1.82-slim"  
echo "  • node:18-slim"
echo "  • nginx:alpine"
echo "  • debian:bookworm-slim"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_size() { echo -e "${BLUE}[SIZE]${NC} $1"; }

# Track success
BUILT_SERVICES=()
FAILED_SERVICES=()

# All services are required - ZERO failures accepted
print_status "Building required services..."

print_status "1/9 Building Storage Server (Rust)..."
if docker build -f packages/sutra-storage/Dockerfile -t sutra-storage-server:latest . >/dev/null 2>&1; then
    SIZE=$(docker images sutra-storage-server:latest --format '{{.Size}}')
    print_size "Storage Server: $SIZE"
    BUILT_SERVICES+=("sutra-storage-server")
else
    echo "❌ Storage Server failed"
    FAILED_SERVICES+=("sutra-storage-server")
fi

print_status "2/9 Building API (Python)..."
if docker build -f packages/sutra-api/Dockerfile -t sutra-api:latest . >/dev/null 2>&1; then
    SIZE=$(docker images sutra-api:latest --format '{{.Size}}')
    print_size "API: $SIZE"
    BUILT_SERVICES+=("sutra-api")
else
    echo "❌ API failed"
    FAILED_SERVICES+=("sutra-api")
fi

print_status "3/9 Building Hybrid (Python)..."
if docker build -f packages/sutra-hybrid/Dockerfile -t sutra-hybrid:latest . >/dev/null 2>&1; then
    SIZE=$(docker images sutra-hybrid:latest --format '{{.Size}}')
    print_size "Hybrid: $SIZE"
    BUILT_SERVICES+=("sutra-hybrid")
else
    echo "❌ Hybrid failed"
    FAILED_SERVICES+=("sutra-hybrid")
fi

print_status "4/9 Building Client (Node + Nginx)..."
if docker build -t sutra-client:latest packages/sutra-client >/dev/null 2>&1; then
    SIZE=$(docker images sutra-client:latest --format '{{.Size}}')
    print_size "Client: $SIZE"
    BUILT_SERVICES+=("sutra-client")
else
    echo "❌ Client failed"
    FAILED_SERVICES+=("sutra-client")
fi

print_status "5/9 Building Control Center (React + Python)..."
if docker build -f packages/sutra-control/Dockerfile -t sutra-control:latest . >/dev/null 2>&1; then
    SIZE=$(docker images sutra-control:latest --format '{{.Size}}')
    print_size "Control: $SIZE"
    BUILT_SERVICES+=("sutra-control")
else
    echo "❌ Control failed"
    FAILED_SERVICES+=("sutra-control")
fi

# Grid services (required for distributed operations)
print_status "6/9 Building Grid Master (Rust)..."
if docker build -f packages/sutra-grid-master/Dockerfile -t sutra-grid-master:latest . >/dev/null 2>&1; then
    SIZE=$(docker images sutra-grid-master:latest --format '{{.Size}}')
    print_size "Grid Master: $SIZE"
    BUILT_SERVICES+=("sutra-grid-master")
else
    echo "❌ Grid Master failed (REQUIRED)"
    FAILED_SERVICES+=("sutra-grid-master")
fi

print_status "7/9 Building Grid Agent (Rust)..."
if docker build -f packages/sutra-grid-agent/Dockerfile -t sutra-grid-agent:latest . >/dev/null 2>&1; then
    SIZE=$(docker images sutra-grid-agent:latest --format '{{.Size}}')
    print_size "Grid Agent: $SIZE"
    BUILT_SERVICES+=("sutra-grid-agent")
else
    echo "❌ Grid Agent failed (REQUIRED)"
    FAILED_SERVICES+=("sutra-grid-agent")
fi

print_status "8/9 Building Bulk Ingester (Rust + Python)..."
if docker build -f packages/sutra-bulk-ingester/Dockerfile -t sutra-bulk-ingester:latest . >/dev/null 2>&1; then
    SIZE=$(docker images sutra-bulk-ingester:latest --format '{{.Size}}')
    print_size "Bulk Ingester: $SIZE"
    BUILT_SERVICES+=("sutra-bulk-ingester")
else
    echo "❌ Bulk Ingester failed (REQUIRED)"
    FAILED_SERVICES+=("sutra-bulk-ingester")
fi

# Embedding service (CRITICAL for semantic search)
print_status "9/9 Building Embedding Service (Python)..."
if [ -f packages/sutra-embedding-service/Dockerfile ]; then
    if docker build -t sutra-embedding-service:latest packages/sutra-embedding-service >/dev/null 2>&1; then
        SIZE=$(docker images sutra-embedding-service:latest --format '{{.Size}}')
        print_size "Embedding Service: $SIZE"
        BUILT_SERVICES+=("sutra-embedding-service")
    else
        echo "❌ Embedding Service failed (REQUIRED)"
        FAILED_SERVICES+=("sutra-embedding-service")
    fi
else
    echo "❌ Embedding Service Dockerfile not found (REQUIRED)"
    FAILED_SERVICES+=("sutra-embedding-service")
fi

echo ""
echo "======================================"
echo "✅ Build Summary"
echo "======================================"
echo ""
echo "Successfully built (${#BUILT_SERVICES[@]} services):"
for service in "${BUILT_SERVICES[@]}"; do
    echo "  ✅ $service"
done

if [ ${#FAILED_SERVICES[@]} -gt 0 ]; then
    echo ""
    echo "Failed/Skipped (${#FAILED_SERVICES[@]} services):"
    for service in "${FAILED_SERVICES[@]}"; do
        echo "  ⚠️  $service"
    done
fi

echo ""
echo "Built Images:"
docker images | grep "sutra" | head -20

echo ""
echo "======================================"

if [ ${#FAILED_SERVICES[@]} -eq 0 ]; then
    echo "✅ BUILD SUCCESS - All 9 services ready"
else
    echo "❌ BUILD FAILED - ${#FAILED_SERVICES[@]} service(s) failed"
    echo ""
    echo "CRITICAL: All 9 services are REQUIRED."
    echo "See BUILD_AND_DEPLOY.md for troubleshooting."
    exit 1
fi

echo "======================================"
echo "Next Steps:"
echo "======================================"
echo "  1. Verify build:   ./verify-build.sh"
echo "  2. Deploy system:  ./sutra-deploy.sh up"
echo "  3. Check status:   ./sutra-deploy.sh status"
echo ""
