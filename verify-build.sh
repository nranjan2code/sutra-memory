#!/bin/bash
set -euo pipefail

echo "🔍 Verifying Sutra AI Build System"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅${NC} $1"; }
print_error() { echo -e "${RED}❌${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠️${NC}  $1"; }

REQUIRED_SERVICES=(
    "sutra-storage-server"
    "sutra-api"
    "sutra-hybrid"
    "sutra-client"
    "sutra-control"
    "sutra-grid-master"
    "sutra-grid-agent"
    "sutra-bulk-ingester"
    "sutra-embedding-service"
)

echo "Checking for required Docker images..."
echo ""

MISSING=()
FOUND=()

for service in "${REQUIRED_SERVICES[@]}"; do
    if docker images --format "{{.Repository}}" | grep -q "^${service}$"; then
        SIZE=$(docker images ${service}:latest --format '{{.Size}}')
        print_success "${service} (${SIZE})"
        FOUND+=("${service}")
    else
        print_error "${service} NOT FOUND"
        MISSING+=("${service}")
    fi
done

echo ""
echo "===================================="
echo "Build Verification Summary"
echo "===================================="
echo ""
echo "Found: ${#FOUND[@]}/9 services"
echo "Missing: ${#MISSING[@]}/9 services"
echo ""

if [ ${#MISSING[@]} -eq 0 ]; then
    print_success "ALL 9 SERVICES BUILT SUCCESSFULLY!"
    echo ""
    echo "Total system size:"
    docker images | grep "^sutra" | awk '{sum+=$7} END {print sum " MB"}'
    echo ""
    echo "Next step: ./sutra-deploy.sh up"
    exit 0
else
    print_error "BUILD INCOMPLETE - Missing ${#MISSING[@]} service(s):"
    for service in "${MISSING[@]}"; do
        echo "  - ${service}"
    done
    echo ""
    echo "Run: ./build-all.sh"
    exit 1
fi
