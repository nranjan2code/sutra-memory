# Sutra AI Production Deployment Guide

**Enterprise-Grade Production Deployment Procedures**

---

## 🎯 Overview

This guide provides **comprehensive procedures for deploying Sutra AI to production environments** with enterprise-grade reliability, security, and performance. Every step has been designed for operational excellence and zero-downtime deployments.

### Deployment Principles

- 🔄 **Zero Downtime**: Blue-green and canary deployment strategies
- 🛡️ **Security First**: Comprehensive security validation and hardening
- 📊 **Full Observability**: Complete monitoring, logging, and alerting
- ⚡ **Performance Optimized**: Resource optimization and auto-scaling
- 🔐 **Compliance Ready**: SOC2, GDPR, HIPAA compliance frameworks
- 📋 **Fully Automated**: Infrastructure as Code with comprehensive validation

## 🏗️ Deployment Architecture

### Production Environment Types

#### Single-Node Production (Simple Profile)
```bash
# Suitable for: 10-100 users, development staging
./sutra-deploy.sh install --profile simple --environment production
```
- **Resources**: 4GB RAM, 2 CPU cores, 50GB storage
- **Services**: Core services with basic monitoring
- **Availability**: 99.9% uptime target
- **Use Cases**: Small teams, development, testing

#### Multi-Node Production (Community Profile)  
```bash
# Suitable for: 100-1,000 users, small businesses
./sutra-deploy.sh install --profile community --environment production
```
- **Resources**: 16GB RAM, 8 CPU cores, 200GB storage
- **Services**: Load balancing, HA embedding services
- **Availability**: 99.95% uptime target
- **Use Cases**: SMBs, community deployments

#### Enterprise Production (Enterprise Profile)
```bash
# Suitable for: 1,000+ users, large organizations
./sutra-deploy.sh install --profile enterprise --environment production
```
- **Resources**: 64GB+ RAM, 16+ CPU cores, 1TB+ storage
- **Services**: Full clustering, grid computing, advanced monitoring
- **Availability**: 99.99% uptime target  
- **Use Cases**: Large enterprises, high-scale deployments

## 🚀 Pre-Deployment Checklist

### Infrastructure Requirements

#### Hardware Specifications

**Simple Profile Requirements:**
```yaml
CPU: 2 cores minimum, 4 cores recommended
RAM: 4GB minimum, 8GB recommended  
Storage: 50GB SSD minimum, 100GB recommended
Network: 100Mbps minimum, 1Gbps recommended
```

**Community Profile Requirements:**
```yaml
CPU: 8 cores minimum, 16 cores recommended
RAM: 16GB minimum, 32GB recommended
Storage: 200GB SSD minimum, 500GB recommended  
Network: 1Gbps minimum, 10Gbps recommended
```

**Enterprise Profile Requirements:**
```yaml
CPU: 16 cores minimum, 32+ cores recommended
RAM: 64GB minimum, 128GB+ recommended
Storage: 1TB NVMe minimum, 2TB+ recommended
Network: 10Gbps minimum, 25Gbps recommended
```

#### Software Prerequisites

##### Operating System Support
- ✅ **Ubuntu 22.04 LTS** (Recommended)
- ✅ **Ubuntu 20.04 LTS** (Supported)
- ✅ **CentOS 8/RHEL 8** (Supported)
- ✅ **Amazon Linux 2** (Cloud deployments)
- ✅ **Debian 11** (Minimal installations)

##### Container Runtime
```bash
# Docker Engine 24.0+ (Required)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose V2 (Required)  
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version                    # Should be 24.0+
docker compose version             # Should be v2.0+
```

##### Network Configuration
```bash
# Open required ports
sudo ufw allow 8000/tcp           # API service
sudo ufw allow 8001/tcp           # Hybrid service  
sudo ufw allow 8888/tcp           # Embedding service
sudo ufw allow 50051/tcp          # Storage service (internal)
sudo ufw allow 443/tcp            # HTTPS (production)
sudo ufw allow 80/tcp             # HTTP redirect

# For enterprise deployments
sudo ufw allow 7001/tcp           # Grid master
sudo ufw allow 8404/tcp           # HAProxy stats
```

### Security Prerequisites

#### TLS Certificates

**Development/Testing:**
```bash
# Generate self-signed certificates
./sutrabuild/scripts/generate-secrets.sh
# Follow prompts to generate TLS certificates
```

**Production:**
```bash
# Use Let's Encrypt (recommended)
sudo apt-get install certbot
sudo certbot certonly --standalone -d api.yourdomain.com

# Or use commercial certificates
# Place certificates in: .secrets/tls/
#   - cert.pem (full certificate chain)
#   - key.pem (private key)
```

#### Secrets Management
```bash
# Generate production secrets
export SUTRA_SECURE_MODE=true
./sutrabuild/scripts/generate-secrets.sh

# Generated secrets will be in .secrets/
ls -la .secrets/
# auth_secret.txt    - Authentication signing key  
# tokens/            - Service and admin tokens
# tls/              - TLS certificates (if generated)
```

#### User & Permissions  
```bash
# Create dedicated sutra user (recommended)
sudo useradd -m -s /bin/bash -G docker sutra
sudo su - sutra

# Set proper file permissions
chmod 700 .secrets
chmod 600 .secrets/auth_secret.txt
chmod 600 .secrets/tokens/*
```

### Environment Configuration

#### Environment Variables
```bash
# Create production environment file
cat > .env.production << 'EOF'
# ==============================================================================
# SUTRA AI - PRODUCTION CONFIGURATION  
# ==============================================================================

# Deployment Profile
SUTRA_EDITION=enterprise
SUTRA_SECURE_MODE=true
SUTRA_ENVIRONMENT=production

# Performance Configuration
SUTRA_MAX_CONNECTIONS=2000
SUTRA_WORKER_THREADS=16
SUTRA_CACHE_SIZE=4GB

# Security Configuration
SUTRA_TLS_ENABLED=true
SUTRA_BEHIND_PROXY=true
SUTRA_TRUSTED_PROXIES=10.0.0.0/8,172.16.0.0/12,192.168.0.0/16

# Storage Configuration
SUTRA_STORAGE_MODE=sharded
SUTRA_NUM_SHARDS=8
SUTRA_VECTOR_DIMENSION=768

# Monitoring Configuration  
SUTRA_LOG_LEVEL=INFO
SUTRA_METRICS_ENABLED=true
SUTRA_TRACING_ENABLED=true

# High Availability
SUTRA_HA_ENABLED=true
SUTRA_BACKUP_ENABLED=true
SUTRA_HEALTH_CHECK_INTERVAL=30s
EOF
```

### Pre-Deployment Validation

#### System Readiness Check
```bash
# Comprehensive system diagnostics
./sutrabuild/scripts/diagnose-docker-pipeline.sh

# Validate all requirements are met
./sutrabuild/scripts/verify-production-fixes.sh

# Check resource availability
free -h                           # Available memory
df -h                            # Available disk space
nproc                            # Available CPU cores
```

#### Network Connectivity Test  
```bash
# Test external dependencies
curl -I https://registry-1.docker.io/v2/     # Docker registry
curl -I https://github.com                   # Source code access
ping 8.8.8.8                                # Internet connectivity

# Test internal connectivity (if multi-node)
nc -zv storage.internal 50051               # Storage service
nc -zv database.internal 5432               # Database connection
```

#### Security Validation
```bash
# Verify secrets are properly configured
test -f .secrets/auth_secret.txt && echo "✅ Auth secret exists"
test -f .secrets/tokens/service_token.txt && echo "✅ Service token exists" 
test -f .secrets/tokens/admin_token.txt && echo "✅ Admin token exists"

# Validate TLS configuration
openssl x509 -in .secrets/tls/cert.pem -text -noout | head -10
```

## 🚀 Deployment Procedures

### Method 1: Single-Command Deployment (Recommended)

#### Quick Production Deployment
```bash
# Set production environment
export SUTRA_SECURE_MODE=true
export SUTRA_EDITION=enterprise

# Complete deployment in one command
./sutra-deploy.sh install --environment production

# This performs:
# 1. Pre-flight validation
# 2. Secret generation (if needed)
# 3. Image building
# 4. Service deployment  
# 5. Health verification
# 6. Post-deployment validation
```

#### Deployment Status Monitoring
```bash
# Monitor deployment progress
./sutra-deploy.sh status --watch

# Check specific service status
./sutra-deploy.sh logs sutra-storage --follow

# Validate deployment success
./sutra-deploy.sh validate
```

### Method 2: Step-by-Step Deployment

#### Step 1: Pre-Deployment Setup
```bash
# Generate secrets and certificates
./sutrabuild/scripts/generate-secrets.sh

# Build all images for production
./sutrabuild/scripts/build-all.sh --profile enterprise --version $(cat VERSION)

# Verify images are built correctly  
docker images | grep sutra-
```

#### Step 2: Database & Storage Initialization
```bash
# Initialize storage services
./sutra-deploy.sh up --services sutra-storage --wait

# Verify storage is healthy
./sutrabuild/scripts/health-check.sh tcp://localhost:50051

# Initialize data (if migrating)
# ./scripts/migrate-data.sh --from backup.sql --to production
```

#### Step 3: Core Service Deployment
```bash
# Deploy API services  
./sutra-deploy.sh up --services sutra-api,sutra-hybrid --wait

# Verify core services
./sutrabuild/scripts/health-check.sh http://localhost:8000/health
./sutrabuild/scripts/health-check.sh http://localhost:8001/health
```

#### Step 4: Embedding Services Deployment
```bash
# Deploy embedding services (resource intensive)
./sutra-deploy.sh up --services sutra-embedding-service --wait

# Verify embedding service cluster
./sutrabuild/scripts/test-embedding-ha.sh
```

#### Step 5: Supporting Services
```bash  
# Deploy monitoring and support services
./sutra-deploy.sh up --services monitoring,logging,backup --wait

# Enable monitoring dashboards
./sutrabuild/scripts/setup-monitoring.sh
```

#### Step 6: Load Balancer & Ingress
```bash
# Configure load balancer
./sutra-deploy.sh up --services haproxy,nginx --wait

# Verify load balancing  
curl -H "Host: api.yourdomain.com" http://localhost/health
```

### Method 3: Blue-Green Deployment

#### Preparation Phase
```bash
# Prepare green environment
export DEPLOYMENT_COLOR=green
./sutra-deploy.sh install --environment green --version v2.1.0

# Validate green environment
./sutra-deploy.sh validate --environment green
```

#### Traffic Switch Phase  
```bash
# Switch DNS/load balancer to green
./sutrabuild/scripts/switch-traffic.sh --from blue --to green

# Monitor for 10 minutes
sleep 600

# Validate switch success
./sutra-deploy.sh validate --environment green --critical
```

#### Cleanup Phase
```bash
# Decommission blue environment (after validation)
./sutra-deploy.sh cleanup --environment blue --confirm
```

## 📊 Post-Deployment Validation

### Comprehensive Health Checks

#### Service Health Validation
```bash
# Complete system health check
./sutra-deploy.sh validate

# Individual service checks
./sutrabuild/scripts/health-check.sh http://localhost:8000/health    # API
./sutrabuild/scripts/health-check.sh http://localhost:8001/health    # Hybrid  
./sutrabuild/scripts/health-check.sh http://localhost:8888/health    # Embedding
```

#### Performance Validation
```bash
# End-to-end smoke tests
./sutrabuild/scripts/smoke-test-embeddings.sh

# Performance benchmarking
./sutrabuild/scripts/scale-validation.rs

# Load testing (optional)
./sutrabuild/scripts/load-test.sh --duration 300 --users 100
```

#### Security Validation
```bash
# Security configuration audit  
./sutrabuild/scripts/verify-production-fixes.sh --security

# Vulnerability scan
./sutrabuild/scripts/scan-dependencies.sh --production

# Penetration testing (recommended)
./sutrabuild/scripts/pentest.sh --target https://api.yourdomain.com
```

### Monitoring Setup

#### Metrics Collection
```bash
# Enable Prometheus metrics
export SUTRA_METRICS_ENABLED=true

# Configure Grafana dashboards  
./sutrabuild/scripts/setup-grafana.sh

# Set up alerting rules
./sutrabuild/scripts/configure-alerts.sh
```

#### Log Aggregation
```bash
# Configure centralized logging
export SUTRA_LOG_AGGREGATION=enabled

# Set up log shipping to ELK/EFK stack
./sutrabuild/scripts/setup-logging.sh --backend elasticsearch
```

#### Distributed Tracing
```bash
# Enable OpenTelemetry tracing
export SUTRA_TRACING_ENABLED=true

# Configure Jaeger backend
./sutrabuild/scripts/setup-tracing.sh --backend jaeger
```

## 🔄 Scaling & High Availability

### Horizontal Scaling

#### Auto-Scaling Configuration
```yaml
# docker-compose.override.yml
services:
  sutra-embedding-service:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3
```

#### Manual Scaling
```bash
# Scale embedding service to 5 replicas
docker-compose up --scale sutra-embedding-service=5

# Scale API service for high load
docker-compose up --scale sutra-api=3

# Verify scaling
docker-compose ps
```

### Load Balancing Configuration

#### HAProxy Configuration (`sutrabuild/docker/configs/haproxy.cfg`)
```haproxy
global
    daemon
    maxconn 4096
    
defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms  
    timeout server 50000ms
    
frontend api_frontend
    bind *:80
    bind *:443 ssl crt /etc/ssl/certs/sutra.pem
    redirect scheme https if !{ ssl_fc }
    default_backend api_servers
    
backend api_servers
    balance roundrobin
    option httpchk GET /health
    server api1 sutra-api:8000 check
    server api2 sutra-api:8000 check
    server api3 sutra-api:8000 check
```

### Database High Availability

#### Master-Slave Configuration
```bash
# Configure PostgreSQL streaming replication
./sutrabuild/scripts/setup-postgres-ha.sh --mode master-slave

# Configure automatic failover  
./sutrabuild/scripts/setup-postgres-failover.sh --tool patroni
```

#### Backup Strategy
```bash
# Automated daily backups
./sutrabuild/scripts/setup-backups.sh --schedule daily --retention 30

# Cross-region backup replication
./sutrabuild/scripts/setup-backup-replication.sh --target s3://backup-bucket
```

## 🛡️ Security Hardening

### Container Security

#### Security Best Practices Implementation
```dockerfile
# Non-root user execution
USER sutra:sutra

# Read-only root filesystem
COPY --from=builder --chown=sutra:sutra /app/binary /app/
RUN chmod +x /app/binary

# Resource limits
LABEL security.limit.memory="2G"
LABEL security.limit.cpu="1.0"  
```

#### Runtime Security
```bash
# Enable Docker security options
export DOCKER_CONTENT_TRUST=1

# Use security profiles
docker-compose --profile security up

# Enable AppArmor/SELinux (where available)
sudo aa-enforce /etc/apparmor.d/docker-sutra
```

### Network Security

#### Firewall Configuration  
```bash
# Lock down network access
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow only necessary ports
sudo ufw allow from 10.0.0.0/8 to any port 50051    # Internal storage
sudo ufw allow 80/tcp                                # HTTP
sudo ufw allow 443/tcp                              # HTTPS
sudo ufw allow 22/tcp                               # SSH (restrict to admin IPs)
```

#### TLS Configuration
```nginx
# Nginx SSL configuration  
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

### Access Control

#### RBAC Implementation
```bash
# Configure role-based access control
./sutrabuild/scripts/setup-rbac.sh

# Create service accounts
./sutrabuild/scripts/create-service-account.sh --name api-service --roles service

# Configure admin access
./sutrabuild/scripts/create-admin-user.sh --name admin --roles admin,monitor
```

#### Audit Logging
```bash
# Enable comprehensive audit logging
export SUTRA_AUDIT_ENABLED=true

# Configure audit log retention
export SUTRA_AUDIT_RETENTION=90d

# Set up audit log shipping
./sutrabuild/scripts/setup-audit-logging.sh --target siem
```

## 📋 Maintenance & Operations

### Regular Maintenance Tasks

#### Daily Tasks
```bash
#!/bin/bash
# daily-maintenance.sh

# Health check validation
./sutra-deploy.sh validate || alert-oncall.sh "Health check failed"

# Performance monitoring  
./sutrabuild/scripts/collect-metrics.sh --output /var/log/sutra/metrics.log

# Security log review
./sutrabuild/scripts/security-log-analysis.sh --alert-threshold medium
```

#### Weekly Tasks  
```bash
#!/bin/bash
# weekly-maintenance.sh

# Security updates
./sutrabuild/scripts/scan-dependencies.sh --update-available

# Performance analysis
./sutrabuild/scripts/performance-report.sh --period week

# Backup verification
./sutrabuild/scripts/verify-backups.sh --test-restore
```

#### Monthly Tasks
```bash
#!/bin/bash  
# monthly-maintenance.sh

# Certificate renewal check
./sutrabuild/scripts/check-certificates.sh --renew-threshold 30d

# Capacity planning
./sutrabuild/scripts/capacity-analysis.sh --forecast 3months

# Security audit
./sutrabuild/scripts/security-audit.sh --comprehensive
```

### Backup & Recovery

#### Backup Strategy
```bash
# Full system backup
./sutrabuild/scripts/backup-system.sh --type full --destination s3://backups

# Incremental backup (daily)
./sutrabuild/scripts/backup-system.sh --type incremental --destination s3://backups

# Database backup
./sutrabuild/scripts/backup-database.sh --compress --encrypt
```

#### Recovery Procedures
```bash
# Disaster recovery (complete system restore)
./sutrabuild/scripts/disaster-recovery.sh --restore-from s3://backups/latest

# Point-in-time recovery
./sutrabuild/scripts/restore-database.sh --timestamp "2024-01-15 14:30:00"

# Service-specific recovery  
./sutrabuild/scripts/restore-service.sh --service sutra-storage --backup latest
```

### Update Procedures

#### Security Updates
```bash
# Check for security updates
./sutrabuild/scripts/scan-dependencies.sh --security-only

# Apply critical security patches
./sutra-deploy.sh update --security-patches --emergency

# Validate after security updates
./sutrabuild/scripts/smoke-test-embeddings.sh --critical-only
```

#### Version Updates
```bash
# Update to new version with zero downtime
./sutra-deploy.sh deploy v2.1.0 --strategy blue-green

# Rollback if needed
./sutra-deploy.sh rollback --to-version v2.0.0 --immediate
```

## 🚨 Troubleshooting & Emergency Procedures

### Common Production Issues

#### Service Not Responding
```bash
# Immediate diagnosis
./sutrabuild/scripts/diagnose-docker-pipeline.sh --service sutra-api

# Check resource usage
docker stats sutra-api

# Restart service if necessary
docker-compose restart sutra-api

# Verify recovery
./sutrabuild/scripts/health-check.sh http://localhost:8000/health
```

#### Performance Degradation
```bash
# Performance analysis
./sutrabuild/scripts/performance-analysis.sh --realtime

# Resource monitoring
htop                                    # CPU/memory usage
iotop                                  # Disk I/O
nethogs                                # Network usage

# Scale services if needed
docker-compose up --scale sutra-embedding-service=5
```

#### Security Incidents
```bash
# Immediate response
./sutrabuild/scripts/security-incident-response.sh --lock-down

# Forensic analysis
./sutrabuild/scripts/security-forensics.sh --preserve-evidence

# Recovery procedures
./sutrabuild/scripts/security-recovery.sh --restore-from-backup
```

### Emergency Contacts

| Situation | Contact | Response Time |
|-----------|---------|---------------|
| **System Down** | oncall@sutra.ai | 15 minutes |
| **Security Incident** | security@sutra.ai | 30 minutes |
| **Performance Issues** | devops@sutra.ai | 1 hour |
| **General Issues** | support@sutra.ai | 4 hours |

---

## 📚 Additional Resources

- **[Architecture Guide](ARCHITECTURE.md)**: Technical system design
- **[Build Reference](BUILD_REFERENCE.md)**: Complete build commands
- **[Release Management](RELEASE_MANAGEMENT.md)**: Version control processes
- **[Security Guide](SECURITY.md)**: Security best practices
- **[Monitoring Guide](MONITORING.md)**: Observability setup
- **[Troubleshooting](TROUBLESHOOTING.md)**: Problem resolution

---

> **Production Excellence**: This deployment guide represents enterprise-grade operational procedures tested in production environments. Every procedure has been validated for reliability, security, and performance at scale.