#!/bin/bash
set -euo pipefail

echo "🧹 Complete Cleanup and Fresh Production Build"
echo "=============================================="
echo "This will:"
echo "  1. Stop all running containers"
echo "  2. Remove ALL Sutra images (base + services)"
echo "  3. Remove volumes and build cache"
echo "  4. Rebuild everything with production optimization"
echo "  5. Deploy fresh system"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Confirmation prompt
read -p "⚠️  This will DELETE all Sutra images and data. Continue? (yes/no): " confirm
if [[ "$confirm" != "yes" ]]; then
    print_error "Aborted by user"
    exit 1
fi

echo ""
print_status "Step 1: Stopping all containers..."
docker-compose -f docker-compose-grid.yml down || true

print_status "Step 2: Removing Sutra containers..."
docker ps -a | grep sutra | awk '{print $1}' | xargs -r docker rm -f || true

print_status "Step 3: Removing Sutra images..."
docker images | grep -E "(sutra-|sutra-base)" | awk '{print $1":"$2}' | xargs -r docker rmi -f || true

print_status "Step 4: Removing volumes..."
docker volume ls | grep sutra | awk '{print $2}' | xargs -r docker volume rm || true

print_status "Step 5: Pruning build cache..."
docker builder prune -f

print_status "Step 6: Showing cleaned state..."
echo ""
echo "Remaining Sutra artifacts (should be empty):"
docker images | grep -E "(sutra-|REPOSITORY)" || echo "  ✅ No Sutra images found"
docker ps -a | grep sutra || echo "  ✅ No Sutra containers found"
docker volume ls | grep sutra || echo "  ✅ No Sutra volumes found"

echo ""
print_status "Step 7: Building production-optimized images..."
./build.sh

echo ""
print_status "Step 8: Deploying fresh system..."
./sutra-deploy.sh up

echo ""
print_status "✅ Complete! Fresh production system deployed."
print_status "Run './sutra-deploy.sh status' to verify."
