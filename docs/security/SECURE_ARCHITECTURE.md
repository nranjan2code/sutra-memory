# Secure Architecture Guide
**Version:** 2.0  
**Date:** 2025-10-25  
**Status:** Production-Ready

---

## Overview

This document describes the complete secure architecture for Sutra Models with proper network segre gation, authentication, and encryption.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INTERNET (External Users)                       │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │  Firewall/Loadbal.    │
                    │  (Optional)           │
                    └───────────┬───────────┘
                                │
┌───────────────────────────────┴──────────────────────────────────────────┐
│                       PUBLIC NETWORK (172.21.0.0/24)                     │
│                      🌐 External Access - Auth Required                  │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────────────────┐  │
│  │  sutra-api     │  │  sutra-hybrid  │  │  sutra-control (Admin)   │  │
│  │  Port: 8000    │  │  Port: 8001    │  │  Port: 9000              │  │
│  │  🔒 Auth: User │  │  🔒 Auth: User │  │  🔒 Auth: Admin          │  │
│  └───────┬────────┘  └───────┬────────┘  └──────────┬────────────────┘  │
│          │                   │                      │                    │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  sutra-client (Web UI)                                            │  │
│  │  Port: 8080                                                       │  │
│  │  🔒 Auth: User (pass-through to APIs)                            │  │
│  └───────┬───────────────────────────────────────────────────────────┘  │
│          │                   │                      │                    │
└──────────┼───────────────────┼──────────────────────┼────────────────────┘
           │                   │                      │
           │                   │                      │ Service Tokens
┌──────────┼───────────────────┼──────────────────────┼────────────────────┐
│          ▼                   ▼                      ▼                    │
│                    INTERNAL NETWORK (172.20.0.0/24)                     │
│                   🔒 NO External Access - Isolated                      │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    STORAGE LAYER (INTERNAL ONLY)                │    │
│  │                                                                 │    │
│  │  storage-server (TCP:50051) 🔒 Auth + TLS                      │    │
│  │  ├─ Sharded Storage (4 shards)                                 │    │
│  │  ├─ HNSW Vector Index                                           │    │
│  │  └─ Write-Ahead Log                                             │    │
│  │                                                                 │    │
│  │  grid-event-storage (TCP:50051) 🔒 Auth + TLS                  │    │
│  │  └─ Grid observability storage                                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                  EMBEDDING SERVICE (INTERNAL ONLY)              │    │
│  │                                                                 │    │
│  │  embedding-ha (Load Balancer)                                  │    │
│  │  ├─ embedding-1 (HTTP:8888)                                     │    │
│  │  ├─ embedding-2 (HTTP:8888)                                     │    │
│  │  └─ embedding-3 (HTTP:8888)                                     │    │
│  │     └─ nomic-embed-text-v1.5 (768-d)                           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    GRID INFRASTRUCTURE (INTERNAL ONLY)          │    │
│  │                                                                 │    │
│  │  grid-master (HTTP:7001, TCP:7002) 🔒 Auth                     │    │
│  │  ├─ grid-agent-1 (TCP:8001) 🔒 Auth                            │    │
│  │  └─ grid-agent-2 (TCP:8001) 🔒 Auth                            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                  BULK INGESTION (INTERNAL ONLY)                 │    │
│  │                                                                 │    │
│  │  sutra-bulk-ingester (HTTP:8005) 🔒 Auth                       │    │
│  │  └─ Admin access only via Control Center                        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Network Segregation

### Public Network (172.21.0.0/24)
**Purpose:** External user access with authentication

**Exposed Services:**
- `sutra-api` (Port 8000) - REST API for users
- `sutra-hybrid` (Port 8001) - Semantic API
- `sutra-control` (Port 9000) - Admin dashboard
- `sutra-client` (Port 8080) - User web interface

**Security:**
- ✅ User authentication required (JWT/HMAC)
- ✅ Rate limiting with trusted proxy validation
- ✅ CORS configured
- ✅ TLS encryption (recommended)
- ✅ All requests audited

### Internal Network (172.20.0.0/24)
**Purpose:** Service-to-service communication

**Services:**
- Storage servers
- Embedding services
- Grid infrastructure
- Bulk ingester

**Security:**
- ✅ **NO external access** (`internal: true`)
- ✅ Service authentication with tokens
- ✅ TLS encryption for TCP
- ✅ Only accessible from public network services

---

## Security Layers

### Layer 1: Network Isolation

```yaml
networks:
  sutra-internal:
    driver: bridge
    internal: true  # 🔒 NO external routing
    
  sutra-public:
    driver: bridge
    internal: false  # ✅ External access
```

**Effect:**
- Storage server CANNOT be accessed from internet
- Grid infrastructure CANNOT be accessed from internet
- Embedding services CANNOT be accessed from internet
- Only API gateway services are exposed

### Layer 2: Authentication

**User Authentication** (Public APIs):
```
User → API → Validate JWT/HMAC → Authorize → Process
```

**Service Authentication** (Internal):
```
API → Storage → Validate Service Token → Process
```

**Tokens:**
- User tokens: Short-lived (1 hour)
- Service tokens: Long-lived (1 year)
- Admin tokens: Long-lived with elevated privileges

### Layer 3: Authorization (RBAC)

| Role | Can Access | Cannot Access |
|------|-----------|---------------|
| **Admin** | Everything | - |
| **Writer** | Read, Write APIs | Admin endpoints, Flush |
| **Reader** | Read APIs | Write APIs, Admin |
| **Service** | Internal APIs | Admin endpoints |

### Layer 4: Rate Limiting

**IP-based with Proxy Validation:**
- Direct connection: Uses `request.client.host`
- Behind proxy: Validates `X-Forwarded-For` against trusted IPs
- **Cannot be spoofed** when properly configured

### Layer 5: TLS Encryption

**Enabled for:**
- Storage TCP connections (port 50051)
- API HTTPS (recommended with reverse proxy)

**Certificates:**
- Development: Self-signed
- Production: Let's Encrypt or commercial CA

---

## Port Exposure Summary

### Externally Accessible (require authentication)

| Port | Service | Purpose | Auth Required |
|------|---------|---------|---------------|
| 8000 | sutra-api | REST API | ✅ User |
| 8001 | sutra-hybrid | Semantic API | ✅ User |
| 8080 | sutra-client | Web UI | ✅ User |
| 9000 | sutra-control | Admin Dashboard | ✅ Admin |

### Internal Only (NOT accessible from internet)

| Port | Service | Network | Auth |
|------|---------|---------|------|
| 50051 | storage-server | Internal | ✅ Service |
| 50051 | grid-event-storage | Internal | ✅ Service |
| 7001 | grid-master (HTTP) | Internal | ✅ Service |
| 7002 | grid-master (TCP) | Internal | ✅ Service |
| 8001 | grid-agent-1 | Internal | ✅ Service |
| 8001 | grid-agent-2 | Internal | ✅ Service |
| 8888 | embedding-ha | Internal | ❌ None |
| 8005 | bulk-ingester | Internal | ✅ Service |

---

## Authentication Flow

### 1. User Login Flow

```
┌──────┐                  ┌─────────┐                ┌──────────┐
│ User │                  │   API   │                │  Storage │
└──┬───┘                  └────┬────┘                └────┬─────┘
   │                           │                          │
   │ POST /auth/login          │                          │
   │ (username, password)      │                          │
   ├──────────────────────────>│                          │
   │                           │                          │
   │                           │ Validate credentials     │
   │                           │ Generate JWT/HMAC        │
   │                           │                          │
   │ <200 OK>                  │                          │
   │ {token: "abc.xyz"}        │                          │
   │<──────────────────────────┤                          │
   │                           │                          │
   │ GET /learn                │                          │
   │ Authorization: Bearer abc │                          │
   ├──────────────────────────>│                          │
   │                           │                          │
   │                           │ Validate token           │
   │                           │ Check permissions        │
   │                           │                          │
   │                           │ Forward with service token│
   │                           ├─────────────────────────>│
   │                           │                          │
   │                           │ Validate service token   │
   │                           │ Process request          │
   │                           │                          │
   │                           │<─────────────────────────┤
   │ <200 OK>                  │                          │
   │ {result}                  │                          │
   │<──────────────────────────┤                          │
```

### 2. Service-to-Service Flow

```
┌─────────┐                ┌──────────┐
│   API   │                │  Storage │
└────┬────┘                └────┬─────┘
     │                          │
     │ LearnConcept Request     │
     │ + Service Token          │
     ├─────────────────────────>│
     │                          │
     │                          │ Validate service token
     │                          │ Check Service role
     │                          │ Process request
     │                          │
     │ <Response>               │
     │<─────────────────────────┤
```

---

## Deployment Steps

### 1. Generate Secrets

```bash
# Run the security setup script
chmod +x scripts/generate-secrets.sh
./scripts/generate-secrets.sh

# This generates:
# - Authentication secret
# - Service token
# - Admin token
# - TLS certificates (optional)
# - .env file
```

### 2. Review Configuration

```bash
# Review generated .env file
cat .env

# Verify secrets are generated
ls -la .secrets/
```

### 3. Deploy Securely

```bash
# Start with secure configuration
docker-compose -f docker-compose-secure.yml up -d

# Check service status
docker-compose -f docker-compose-secure.yml ps

# Verify authentication is enabled
docker logs sutra-storage | grep "Authentication"
# Should see: ✅ Authentication: ENABLED
```

### 4. Test Security

```bash
# Test without authentication (should fail)
curl http://localhost:8000/learn

# Test with authentication (should succeed)
TOKEN=$(cat .secrets/tokens/service_token.txt)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/health
```

---

## Security Checklist

### Pre-Deployment

- [ ] Strong authentication secret generated (32+ characters)
- [ ] Service and admin tokens generated
- [ ] TLS certificates obtained (Let's Encrypt or CA)
- [ ] Network segregation configured (internal/public)
- [ ] Firewall rules configured
- [ ] Secrets stored securely (not in git)
- [ ] .env file permissions set to 600

### Post-Deployment

- [ ] Verify no internal services exposed externally
- [ ] Test authentication on all public endpoints
- [ ] Verify rate limiting works
- [ ] Test RBAC (different roles)
- [ ] Monitor authentication failures
- [ ] Set up log aggregation
- [ ] Configure alerts for security events

### Ongoing

- [ ] Rotate secrets every 90 days
- [ ] Review access logs weekly
- [ ] Update TLS certificates before expiration
- [ ] Monitor for security vulnerabilities
- [ ] Test backup/restore procedures
- [ ] Audit user permissions quarterly

---

## Troubleshooting

### Service Cannot Connect to Storage

**Symptom:** API returns "Connection refused" errors

**Check:**
```bash
# Verify networks
docker network inspect sutra-models_sutra-internal

# Check service is on correct network
docker inspect sutra-api | grep -A 10 Networks

# Test internal connectivity
docker exec sutra-api ping storage-server
```

**Fix:** Ensure service is on `sutra-internal` network

### Authentication Failures

**Symptom:** "401 Unauthorized" errors

**Check:**
```bash
# Verify secret matches
docker exec sutra-api env | grep SUTRA_AUTH_SECRET
docker exec sutra-storage env | grep SUTRA_AUTH_SECRET

# Test token generation
./scripts/generate-token.py
```

**Fix:** Ensure all services use same `SUTRA_AUTH_SECRET`

### Port Already in Use

**Symptom:** "Address already in use" error

**Check:**
```bash
# Find what's using the port
lsof -i :8000

# Or using netstat
netstat -tulpn | grep 8000
```

**Fix:** Stop conflicting service or change port mapping

---

## Production Recommendations

### Network

1. **Use Docker Swarm or Kubernetes** for production orchestration
2. **Deploy behind reverse proxy** (Nginx, Traefik) with TLS termination
3. **Use cloud network ACLs** (AWS Security Groups, GCP Firewall Rules)
4. **Implement DDoS protection** (Cloudflare, AWS Shield)

### Authentication

1. **Rotate secrets every 90 days**
2. **Use short-lived user tokens** (15 minutes - 1 hour)
3. **Implement token refresh** mechanism
4. **Enable MFA** for admin access
5. **Integrate with SSO** (OAuth2, SAML)

### Monitoring

1. **Track authentication failures** (potential attacks)
2. **Monitor rate limit hits** (DoS attempts)
3. **Alert on authorization denials** (privilege escalation)
4. **Log all admin actions** (audit trail)
5. **Set up SIEM integration** (Splunk, ELK)

### Compliance

- **GDPR:** Encryption at rest and in transit
- **HIPAA:** Audit trails, access controls
- **SOC 2:** Security monitoring, incident response
- **PCI DSS:** Network segmentation, encryption

---

## Migration from Insecure Setup

See: `PRODUCTION_SECURITY_SETUP.md` section "Migration from Insecure Setup"

---

## Support

- **Security Issues:** Open a confidential issue
- **Documentation:** See `docs/SECURITY.md`
- **Architecture Questions:** See `WARP.md`

**Last Updated:** 2025-10-25
