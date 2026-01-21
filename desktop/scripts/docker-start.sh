#!/bin/bash
# Sutra Desktop Edition - Quick Start Script
# No Docker expertise required!

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$ROOT_DIR/.sutra/compose/desktop.yml"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Sutra Desktop Edition${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not found!${NC}"
        echo ""
        echo "Please install Docker Desktop:"
        echo "  macOS: https://docs.docker.com/desktop/install/mac-install/"
        echo "  Windows: https://docs.docker.com/desktop/install/windows-install/"
        echo "  Linux: https://docs.docker.com/desktop/install/linux-install/"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker daemon not running!${NC}"
        echo ""
        echo "Please start Docker Desktop and try again."
        exit 1
    fi
}

start_services() {
    print_header
    echo -e "${BLUE}🚀 Starting Sutra Desktop services...${NC}"
    echo ""
    
    check_docker
    
    echo -e "${YELLOW}📦 Building images (first time may take 2-3 minutes)...${NC}"
    docker compose -f "$COMPOSE_FILE" build
    
    echo ""
    echo -e "${YELLOW}🔧 Starting containers...${NC}"
    docker compose -f "$COMPOSE_FILE" up -d
    
    echo ""
    echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
    
    # Wait for storage server
    for i in {1..30}; do
        if docker compose -f "$COMPOSE_FILE" exec -T storage-server timeout 1 bash -c '</dev/tcp/localhost/50051' 2>/dev/null; then
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ Storage server failed to start${NC}"
            echo "Check logs: docker compose -f $COMPOSE_FILE logs storage-server"
            exit 1
        fi
        sleep 1
    done
    
    # Wait for API server
    for i in {1..30}; do
        if curl -sf http://127.0.0.1:8000/health &>/dev/null; then
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ API server failed to start${NC}"
            echo "Check logs: docker compose -f $COMPOSE_FILE logs api"
            exit 1
        fi
        sleep 1
    done
    
    # Wait for web client
    for i in {1..30}; do
        if curl -sf http://127.0.0.1:3000/health &>/dev/null; then
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ Web client failed to start${NC}"
            echo "Check logs: docker compose -f $COMPOSE_FILE logs web-client"
            exit 1
        fi
        sleep 1
    done
    
    echo ""
    echo -e "${GREEN}✅ All services ready!${NC}"
    echo ""
    echo "Services running:"
    echo "  🌐 Web Interface: http://localhost:3000"
    echo "  📡 API Server: http://127.0.0.1:8000"
    echo "  🗄️  Storage Server: localhost:50051"
    echo "  🧠 Embedding Service: (Docker internal)"
    echo ""
    echo -e "${GREEN}🚀 Open http://localhost:3000 in your browser!${NC}"
    echo ""
}

stop_services() {
    print_header
    echo -e "${BLUE}🛑 Stopping Sutra Desktop services...${NC}"
    echo ""
    
    docker compose -f "$COMPOSE_FILE" down
    
    echo ""
    echo -e "${GREEN}✅ Services stopped${NC}"
    echo ""
}

show_status() {
    print_header
    echo -e "${BLUE}📊 Service Status${NC}"
    echo ""
    
    docker compose -f "$COMPOSE_FILE" ps
    
    echo ""
    echo "Logs: docker compose -f $COMPOSE_FILE logs -f"
    echo ""
}

show_logs() {
    docker compose -f "$COMPOSE_FILE" logs -f
}

clean_data() {
    print_header
    echo -e "${YELLOW}⚠️  Warning: This will delete all your knowledge data!${NC}"
    echo ""
    read -p "Are you sure? Type 'yes' to confirm: " confirm
    
    if [ "$confirm" != "yes" ]; then
        echo "Cancelled."
        exit 0
    fi
    
    echo ""
    echo -e "${BLUE}🗑️  Cleaning data...${NC}"
    
    docker compose -f "$COMPOSE_FILE" down -v
    
    echo ""
    echo -e "${GREEN}✅ Data cleaned${NC}"
    echo ""
}

show_help() {
    print_header
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  start   - Start Docker services"
    echo "  stop    - Stop Docker services"
    echo "  status  - Show service status"
    echo "  logs    - Show service logs (follow mode)"
    echo "  clean   - Stop services and delete all data"
    echo "  help    - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start      # Start services"
    echo "  $0 status     # Check if running"
    echo "  $0 logs       # Watch logs"
    echo ""
}

# Main
case "${1:-}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    clean)
        clean_data
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: ${1}${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
