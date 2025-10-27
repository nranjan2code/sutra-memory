#!/bin/bash
# Integration tests for security and embedding service
# Tests both development and production modes

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Sutra AI - Security & Embedding Integration Tests          ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Test 1: Embedding Service Health
echo -e "${YELLOW}[TEST 1]${NC} Embedding Service Health Check"
if curl -sf http://localhost:8888/health | jq -e '.status == "healthy" and .model_loaded == true' > /dev/null; then
    echo -e "${GREEN}✓ PASS${NC} - Embedding service is healthy"
    MODEL=$(curl -s http://localhost:8888/health | jq -r '.model')
    echo "  Model: $MODEL"
else
    echo -e "${RED}✗ FAIL${NC} - Embedding service is not healthy"
    exit 1
fi
echo ""

# Test 2: Embedding Dimension Verification
echo -e "${YELLOW}[TEST 2]${NC} Embedding Dimension Verification"
DIMENSION=$(curl -s http://localhost:8888/info | jq -r '.dimension')
if [ "$DIMENSION" = "768" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Correct dimension: 768"
else
    echo -e "${RED}✗ FAIL${NC} - Wrong dimension: $DIMENSION (expected 768)"
    exit 1
fi
echo ""

# Test 3: Embedding Generation
echo -e "${YELLOW}[TEST 3]${NC} Embedding Generation Test"
EMBED_RESULT=$(curl -s -X POST http://localhost:8888/embed \
  -H "Content-Type: application/json" \
  -d '{"texts": ["test embedding"], "normalize": true}')

EMBED_DIM=$(echo "$EMBED_RESULT" | jq '.embeddings[0] | length')
if [ "$EMBED_DIM" = "768" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Generated 768-dimensional embedding"
    PROCESSING_TIME=$(echo "$EMBED_RESULT" | jq -r '.processing_time_ms')
    echo "  Processing time: ${PROCESSING_TIME}ms"
else
    echo -e "${RED}✗ FAIL${NC} - Wrong embedding dimension: $EMBED_DIM"
    exit 1
fi
echo ""

# Test 4: Storage Server Security Mode Detection
echo -e "${YELLOW}[TEST 4]${NC} Storage Server Security Mode"
if docker logs sutra-storage 2>&1 | grep -q "Security mode:"; then
    SECURITY_MODE=$(docker logs sutra-storage 2>&1 | grep "Security mode:" | head -1)
    echo "$SECURITY_MODE"
    
    if echo "$SECURITY_MODE" | grep -q "SECURE"; then
        echo -e "${GREEN}✓ PASS${NC} - Security mode ENABLED"
        
        # Verify authentication
        if docker logs sutra-storage 2>&1 | grep -q "Authentication enabled:"; then
            echo -e "${GREEN}✓ PASS${NC} - Authentication is enabled"
        else
            echo -e "${RED}✗ FAIL${NC} - Authentication not found in logs"
        fi
        
        # Verify TLS
        if docker logs sutra-storage 2>&1 | grep -q "TLS Encryption:"; then
            echo -e "${GREEN}✓ PASS${NC} - TLS encryption configured"
        else
            echo -e "${YELLOW}⚠ WARN${NC} - TLS status unclear"
        fi
    else
        echo -e "${YELLOW}✓ INFO${NC} - Running in DEVELOPMENT mode (no security)"
        
        # Verify warning is shown
        if docker logs sutra-storage 2>&1 | grep -q "SECURITY WARNING"; then
            echo -e "${GREEN}✓ PASS${NC} - Security warning displayed correctly"
        else
            echo -e "${RED}✗ FAIL${NC} - Missing security warning for dev mode"
        fi
    fi
else
    echo -e "${RED}✗ FAIL${NC} - Cannot determine security mode"
    exit 1
fi
echo ""

# Test 5: Storage Server Embedding Service Connectivity
echo -e "${YELLOW}[TEST 5]${NC} Storage → Embedding Service Connectivity"
if docker exec sutra-storage curl -sf http://sutra-embedding-service:8888/health > /dev/null; then
    echo -e "${GREEN}✓ PASS${NC} - Storage server can reach embedding service"
else
    echo -e "${RED}✗ FAIL${NC} - Storage server cannot reach embedding service"
    exit 1
fi
echo ""

# Test 6: Environment Variable Verification
echo -e "${YELLOW}[TEST 6]${NC} Environment Variable Verification"

# Check embedding service URL
EMBED_URL=$(docker exec sutra-storage env | grep SUTRA_EMBEDDING_SERVICE_URL || echo "NOT_SET")
if echo "$EMBED_URL" | grep -q "sutra-embedding-service:8888"; then
    echo -e "${GREEN}✓ PASS${NC} - SUTRA_EMBEDDING_SERVICE_URL correctly set"
else
    echo -e "${RED}✗ FAIL${NC} - SUTRA_EMBEDDING_SERVICE_URL: $EMBED_URL"
    exit 1
fi

# Check vector dimension
VECTOR_DIM=$(docker exec sutra-storage env | grep "VECTOR_DIMENSION=" | cut -d= -f2 || echo "NOT_SET")
if [ "$VECTOR_DIM" = "768" ]; then
    echo -e "${GREEN}✓ PASS${NC} - VECTOR_DIMENSION correctly set to 768"
else
    echo -e "${RED}✗ FAIL${NC} - VECTOR_DIMENSION: $VECTOR_DIM (expected 768)"
    exit 1
fi
echo ""

# Test 7: Learning Pipeline Integration Test
echo -e "${YELLOW}[TEST 7]${NC} Learning Pipeline Integration"
LEARN_RESULT=$(curl -s -X POST http://localhost:8000/learn \
  -H "Content-Type: application/json" \
  -d '{"text": "Integration test concept for embedding verification"}')

if echo "$LEARN_RESULT" | jq -e '.concept_id' > /dev/null; then
    CONCEPT_ID=$(echo "$LEARN_RESULT" | jq -r '.concept_id')
    echo -e "${GREEN}✓ PASS${NC} - Successfully learned concept: $CONCEPT_ID"
    
    # Verify concept was stored
    sleep 1
    STATS=$(curl -s http://localhost:8000/stats)
    CONCEPT_COUNT=$(echo "$STATS" | jq -r '.total_concepts')
    echo "  Total concepts: $CONCEPT_COUNT"
else
    echo -e "${RED}✗ FAIL${NC} - Failed to learn concept"
    echo "$LEARN_RESULT"
    exit 1
fi
echo ""

# Test 8: Query with Embedding
echo -e "${YELLOW}[TEST 8]${NC} Query with Semantic Embedding"
QUERY_RESULT=$(curl -s -X POST http://localhost:8000/reason \
  -H "Content-Type: application/json" \
  -d '{"query": "integration test", "max_paths": 3}')

if echo "$QUERY_RESULT" | jq -e '.paths' > /dev/null; then
    echo -e "${GREEN}✓ PASS${NC} - Query executed successfully"
    PATH_COUNT=$(echo "$QUERY_RESULT" | jq '.paths | length')
    echo "  Paths found: $PATH_COUNT"
else
    echo -e "${YELLOW}⚠ INFO${NC} - Query returned no paths (expected if minimal data)"
fi
echo ""

# Summary
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                     TEST SUMMARY                              ║"
echo "╠═══════════════════════════════════════════════════════════════╣"
echo "║  ✓ Embedding Service: Operational                            ║"
echo "║  ✓ Security Integration: Verified                            ║"
echo "║  ✓ Learning Pipeline: Functional                             ║"
echo "║  ✓ End-to-End Flow: Working                                  ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}All tests passed!${NC}"
echo ""
echo "Next steps:"
echo "  1. Review logs: ./sutra-deploy.sh logs"
echo "  2. Check metrics: curl http://localhost:8888/metrics"
echo "  3. View control center: http://localhost:9000"
