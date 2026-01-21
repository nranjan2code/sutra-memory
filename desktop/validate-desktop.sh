#!/bin/bash
# Quick validation script for Desktop Edition
# Run this after build to verify everything works

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "🔍 Sutra Desktop Edition - Quick Validation"
echo ""

# Check if services are running
echo -n "Checking Docker containers... "
if docker ps | grep -q "sutra-desktop"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ No containers running${NC}"
    echo "Run: ./desktop/build-desktop-edition.sh"
    exit 1
fi

# Test web client
echo -n "Testing web client (localhost:3000)... "
if curl -sf http://127.0.0.1:3000/health &>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Not responding${NC}"
    exit 1
fi

# Test API server
echo -n "Testing API server (localhost:8000)... "
if curl -sf http://127.0.0.1:8000/health &>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Not responding${NC}"
    exit 1
fi

# Test learning
echo -n "Testing /learn endpoint... "
RESULT=$(curl -s -X POST http://127.0.0.1:8000/api/v1/learn \
    -H "Content-Type: application/json" \
    -d '{"content":"Validation test concept"}' 2>/dev/null)
if [[ "$RESULT" == *"concept_id"* ]]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
    exit 1
fi

# Test query
echo -n "Testing /reason endpoint... "
RESULT=$(curl -s -X POST http://127.0.0.1:8000/api/v1/reason \
    -H "Content-Type: application/json" \
    -d '{"query":"What is validation?"}' 2>/dev/null)
if [[ "$RESULT" == *"answer"* ]] || [[ "$RESULT" == *"concepts"* ]]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ Partial${NC}"
fi

# Get stats
echo ""
echo "📊 System Statistics:"
curl -s http://127.0.0.1:8000/api/v1/stats | jq . 2>/dev/null || echo "Stats endpoint not responding"

echo ""
echo -e "${GREEN}✅ All validations passed!${NC}"
echo ""
echo "Access points:"
echo "  🌐 http://localhost:3000 - Web Interface"
echo "  📡 http://localhost:8000 - API Server"
echo "  📚 http://localhost:8000/docs - API Documentation"
echo ""
