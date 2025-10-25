#!/bin/bash
# ==============================================================================
# Sutra Models - Security Secrets Generation Script
# ==============================================================================
#
# This script generates all required secrets and tokens for secure deployment:
# - Authentication secret
# - Service token
# - Admin token
# - TLS certificates (optional)
#
# ==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
SECRETS_DIR=".secrets"
TLS_DIR="$SECRETS_DIR/tls"
TOKENS_DIR="$SECRETS_DIR/tokens"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Sutra Models - Security Setup${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# ==============================================================================
# Step 1: Create directories
# ==============================================================================

echo -e "${YELLOW}[1/5] Creating secrets directories...${NC}"
mkdir -p "$SECRETS_DIR"
mkdir -p "$TLS_DIR"
mkdir -p "$TOKENS_DIR"

# Secure permissions
chmod 700 "$SECRETS_DIR"
chmod 700 "$TLS_DIR"
chmod 700 "$TOKENS_DIR"

echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# ==============================================================================
# Step 2: Generate authentication secret
# ==============================================================================

echo -e "${YELLOW}[2/5] Generating authentication secret...${NC}"

# Generate strong random secret (32+ characters)
AUTH_SECRET=$(openssl rand -base64 32)
echo "$AUTH_SECRET" > "$SECRETS_DIR/auth_secret.txt"
chmod 600 "$SECRETS_DIR/auth_secret.txt"

echo -e "${GREEN}✓ Authentication secret generated${NC}"
echo -e "   Location: $SECRETS_DIR/auth_secret.txt"
echo ""

# ==============================================================================
# Step 3: Generate service token
# ==============================================================================

echo -e "${YELLOW}[3/5] Generating service token...${NC}"

# Create Python script inline to generate token
cat > /tmp/generate_service_token.py << 'PYTHON_SCRIPT'
import time
import hmac
import hashlib
import json
import base64
import sys

def generate_token(secret, subject, roles, ttl=31536000):  # 1 year TTL
    now = int(time.time())
    payload = {
        "sub": subject,
        "roles": roles,
        "iat": now,
        "exp": now + ttl
    }
    
    payload_json = json.dumps(payload)
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip('=')
    
    signature = hmac.new(
        secret.encode(),
        payload_b64.encode(),
        hashlib.sha256
    ).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
    
    return f"{payload_b64}.{signature_b64}"

if __name__ == "__main__":
    secret = sys.argv[1]
    subject = sys.argv[2]
    roles = sys.argv[3].split(",")
    
    token = generate_token(secret, subject, roles)
    print(token)
PYTHON_SCRIPT

# Generate service token (Service role - long-lived)
SERVICE_TOKEN=$(python3 /tmp/generate_service_token.py "$AUTH_SECRET" "sutra-services" "Service")
echo "$SERVICE_TOKEN" > "$TOKENS_DIR/service_token.txt"
chmod 600 "$TOKENS_DIR/service_token.txt"

echo -e "${GREEN}✓ Service token generated${NC}"
echo -e "   Subject: sutra-services"
echo -e "   Role: Service"
echo -e "   Location: $TOKENS_DIR/service_token.txt"
echo ""

# ==============================================================================
# Step 4: Generate admin token
# ==============================================================================

echo -e "${YELLOW}[4/5] Generating admin token...${NC}"

# Generate admin token (Admin role - long-lived)
ADMIN_TOKEN=$(python3 /tmp/generate_service_token.py "$AUTH_SECRET" "admin" "Admin")
echo "$ADMIN_TOKEN" > "$TOKENS_DIR/admin_token.txt"
chmod 600 "$TOKENS_DIR/admin_token.txt"

echo -e "${GREEN}✓ Admin token generated${NC}"
echo -e "   Subject: admin"
echo -e "   Role: Admin"
echo -e "   Location: $TOKENS_DIR/admin_token.txt"
echo ""

# Cleanup temp script
rm -f /tmp/generate_service_token.py

# ==============================================================================
# Step 5: Generate TLS certificates (optional)
# ==============================================================================

echo -e "${YELLOW}[5/5] TLS Certificates...${NC}"
echo -e "${BLUE}Do you want to generate self-signed TLS certificates for development?${NC}"
echo -e "${RED}(For production, use Let's Encrypt or a commercial CA)${NC}"
read -p "Generate self-signed certs? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Generating self-signed certificates...${NC}"
    
    openssl req -x509 -newkey rsa:4096 \
        -keyout "$TLS_DIR/key.pem" \
        -out "$TLS_DIR/cert.pem" \
        -days 365 -nodes \
        -subj "/CN=localhost" \
        2>/dev/null
    
    chmod 600 "$TLS_DIR/key.pem"
    chmod 644 "$TLS_DIR/cert.pem"
    
    echo -e "${GREEN}✓ Self-signed certificates generated${NC}"
    echo -e "   Cert: $TLS_DIR/cert.pem"
    echo -e "   Key: $TLS_DIR/key.pem"
    echo -e "${RED}   ⚠️  DO NOT use self-signed certificates in production!${NC}"
else
    echo -e "${BLUE}Skipping certificate generation${NC}"
    echo -e "${BLUE}For production, obtain certificates from Let's Encrypt or a CA${NC}"
fi

echo ""

# ==============================================================================
# Step 6: Create .env file
# ==============================================================================

echo -e "${YELLOW}Creating .env file...${NC}"

if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists. Creating .env.new instead${NC}"
    ENV_FILE=".env.new"
else
    ENV_FILE=".env"
fi

cat > "$ENV_FILE" << EOF
# ==============================================================================
# Sutra Models - Secure Deployment Configuration
# ==============================================================================
# Generated on: $(date)
# ==============================================================================

# ==============================================================================
# CRITICAL SECURITY SETTINGS
# ==============================================================================

# Authentication Secret
SUTRA_AUTH_SECRET=$AUTH_SECRET

# Authentication Method
SUTRA_AUTH_METHOD=hmac

# Token TTL
SUTRA_TOKEN_TTL_SECONDS=3600

# Service Token
SUTRA_SERVICE_TOKEN=$SERVICE_TOKEN

# Admin Token
SUTRA_ADMIN_TOKEN=$ADMIN_TOKEN

# ==============================================================================
# TLS CONFIGURATION
# ==============================================================================

# Enable TLS (set to true for production)
SUTRA_TLS_ENABLED=false

# TLS Certificate Paths
# SUTRA_TLS_CERT=$TLS_DIR/cert.pem
# SUTRA_TLS_KEY=$TLS_DIR/key.pem

# ==============================================================================
# RATE LIMITING
# ==============================================================================

SUTRA_BEHIND_PROXY=false
SUTRA_TRUSTED_PROXIES=

# ==============================================================================
# STORAGE & EMBEDDING
# ==============================================================================

SUTRA_STORAGE_MODE=sharded
SUTRA_NUM_SHARDS=4
SUTRA_VECTOR_DIMENSION=768

# ==============================================================================
# LOGGING
# ==============================================================================

RUST_LOG=info
SUTRA_LOG_LEVEL=INFO
EOF

chmod 600 "$ENV_FILE"

echo -e "${GREEN}✓ Configuration file created: $ENV_FILE${NC}"
echo ""

# ==============================================================================
# Summary
# ==============================================================================

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✓ Security setup complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${BLUE}Generated files:${NC}"
echo -e "  • Authentication secret: $SECRETS_DIR/auth_secret.txt"
echo -e "  • Service token: $TOKENS_DIR/service_token.txt"
echo -e "  • Admin token: $TOKENS_DIR/admin_token.txt"
echo -e "  • Environment config: $ENV_FILE"
if [ -f "$TLS_DIR/cert.pem" ]; then
    echo -e "  • TLS certificate: $TLS_DIR/cert.pem"
    echo -e "  • TLS key: $TLS_DIR/key.pem"
fi
echo ""

echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Review the generated $ENV_FILE file"
echo -e "2. Start services with: ${GREEN}docker-compose -f docker-compose-secure.yml up -d${NC}"
echo -e "3. Test authentication: ${GREEN}./scripts/test-security.sh${NC}"
echo ""

echo -e "${RED}⚠️  IMPORTANT SECURITY NOTES:${NC}"
echo -e "  • Keep .secrets/ directory secure (it's in .gitignore)"
echo -e "  • Never commit secrets to version control"
echo -e "  • Rotate secrets regularly (every 90 days recommended)"
echo -e "  • Use proper TLS certificates in production"
echo -e "  • Monitor authentication failures"
echo ""

echo -e "${BLUE}For production deployment, see: PRODUCTION_SECURITY_SETUP.md${NC}"
echo ""
