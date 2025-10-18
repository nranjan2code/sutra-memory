# Sutra AI Production Deployment Guide

## Overview

This guide covers deploying Sutra AI in production with enterprise-grade durability and high availability (coming soon).

**Current Status:**
- ✅ Zero data loss (WAL integration)
- ✅ Single-node production ready
- 🚧 High availability (in progress - 4 weeks)

---

## Prerequisites

### System Requirements
- **OS:** Linux (Ubuntu 20.04+ / RHEL 8+) or macOS (development)
- **RAM:** 4GB minimum, 16GB recommended
- **CPU:** 2 cores minimum, 8 cores recommended
- **Disk:** 50GB minimum (SSD recommended for storage.dat + WAL)
- **Network:** Low-latency network for replication (when HA is enabled)

### Software Dependencies
```bash
# Rust (for storage server)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustc --version  # Should be 1.70+

# Python (for API/services)
python3 --version  # Should be 3.9+

# Docker (optional, recommended)
docker --version
docker compose --version

# gRPC tools (for testing)
brew install grpcurl  # macOS
apt install grpcurl   # Ubuntu
```

---

## Deployment Options

### Option 1: Docker Compose (Recommended)

**Advantages:**
- All services containerized
- Easy to manage
- Production-ready configuration
- Automatic restarts

**Setup:**
```bash
# 1. Clone repository
git clone https://github.com/your-org/sutra-models.git
cd sutra-models

# 2. Build images
docker compose build

# 3. Start all services
docker compose up -d

# 4. Verify services
docker compose ps
docker compose logs -f storage-server

# 5. Health check
curl http://localhost:9000  # Control center
grpcurl -plaintext localhost:50051 list  # Storage server
```

**Configuration:**
Edit `docker-compose.yml`:
```yaml
services:
  storage-server:
    environment:
      - STORAGE_PATH=/data  # Persistent volume
      - RECONCILE_INTERVAL_MS=10
      - MEMORY_THRESHOLD=50000
      - VECTOR_DIMENSION=768
      - RUST_LOG=info
    volumes:
      - ./data:/data  # WAL and storage.dat persist here
```

---

### Option 2: Systemd Service (Native)

**Advantages:**
- No Docker overhead
- Direct access to hardware
- Easier debugging

**Setup:**

#### 1. Build Storage Server
```bash
cd packages/sutra-storage
cargo build --release --bin storage_server

# Copy binary
sudo cp target/release/storage_server /usr/local/bin/
```

#### 2. Create Service File
`/etc/systemd/system/sutra-storage.service`:
```ini
[Unit]
Description=Sutra Storage Server
After=network.target

[Service]
Type=simple
User=sutra
Group=sutra
WorkingDirectory=/var/lib/sutra
ExecStart=/usr/local/bin/storage_server
Environment="STORAGE_PATH=/var/lib/sutra/knowledge"
Environment="STORAGE_PORT=50051"
Environment="RUST_LOG=info"
Restart=always
RestartSec=10

# Hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/sutra

[Install]
WantedBy=multi-user.target
```

#### 3. Setup User & Directories
```bash
# Create user
sudo useradd -r -s /bin/false sutra

# Create directories
sudo mkdir -p /var/lib/sutra/knowledge
sudo chown -R sutra:sutra /var/lib/sutra

# Create log directory
sudo mkdir -p /var/log/sutra
sudo chown sutra:sutra /var/log/sutra
```

#### 4. Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable sutra-storage
sudo systemctl start sutra-storage
sudo systemctl status sutra-storage

# View logs
sudo journalctl -u sutra-storage -f
```

---

## Data Persistence & Backup

### Storage Layout
```
/var/lib/sutra/knowledge/
├── storage.dat          # Main data file (512MB-10GB)
├── storage.dat.backup   # Automatic backup (created on flush)
└── wal.log             # Write-Ahead Log (<1KB after flush)
```

### Backup Strategy

#### Automated Backups (Recommended)
```bash
#!/bin/bash
# /usr/local/bin/backup-sutra.sh

BACKUP_DIR="/backup/sutra/$(date +%Y%m%d-%H%M%S)"
DATA_DIR="/var/lib/sutra/knowledge"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# 1. Trigger flush (ensures data is on disk)
grpcurl -plaintext localhost:50051 sutra.storage.StorageService/Flush

# 2. Wait for flush to complete
sleep 2

# 3. Copy files
cp "$DATA_DIR/storage.dat" "$BACKUP_DIR/"
cp "$DATA_DIR/wal.log" "$BACKUP_DIR/"

# 4. Compress
tar -czf "$BACKUP_DIR.tar.gz" -C "$BACKUP_DIR" .
rm -rf "$BACKUP_DIR"

# 5. Upload to S3 (optional)
# aws s3 cp "$BACKUP_DIR.tar.gz" s3://your-bucket/sutra-backups/

# 6. Retention (keep last 30 days)
find /backup/sutra -type f -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

#### Schedule with Cron
```bash
# Edit crontab
sudo crontab -e

# Add backup job (runs daily at 2 AM)
0 2 * * * /usr/local/bin/backup-sutra.sh >> /var/log/sutra/backup.log 2>&1
```

---

## Monitoring & Observability

### Health Checks

#### 1. Service Health
```bash
# Check process is running
systemctl status sutra-storage

# Check gRPC endpoint
grpcurl -plaintext localhost:50051 sutra.storage.StorageService/HealthCheck
```

#### 2. Storage Stats
```bash
# Get statistics
grpcurl -plaintext localhost:50051 sutra.storage.StorageService/GetStats

# Example output:
{
  "concepts": "125000",
  "edges": "450000",
  "written": "125000",
  "dropped": "0",
  "pending": "42",
  "reconciliations": "12500",
  "uptime_seconds": "86400"
}
```

#### 3. WAL Health
```bash
# Check WAL file size (should be <1KB after flush)
ls -lh /var/lib/sutra/knowledge/wal.log

# If WAL is growing unbounded → flush not running
# Manually trigger flush:
grpcurl -plaintext localhost:50051 sutra.storage.StorageService/Flush
```

### Prometheus Metrics (Coming Soon)

**Planned Metrics:**
- `sutra_concepts_total` - Total concepts stored
- `sutra_write_latency_ms` - Write latency histogram
- `sutra_wal_size_bytes` - Current WAL size
- `sutra_flush_count` - Number of flushes
- `sutra_replication_lag_ms` - Replica lag (HA only)

---

## Performance Tuning

### Storage Configuration

**For High Write Throughput:**
```bash
# Increase reconciliation interval (less frequent snapshots)
export RECONCILE_INTERVAL_MS=50  # Default: 10ms

# Increase memory threshold (less frequent disk flushes)
export MEMORY_THRESHOLD=100000  # Default: 50000
```

**For Low Latency:**
```bash
# Decrease reconciliation interval (more real-time reads)
export RECONCILE_INTERVAL_MS=5

# Use SSD for storage path
export STORAGE_PATH=/mnt/nvme/sutra
```

**For Large Graphs (>1M concepts):**
```bash
# Increase initial file size
# (Reduces resize operations)
# Note: This requires code change in mmap_store.rs
# Default: 512MB, Recommendation: 2GB for 1M+ concepts
```

### System Tuning

**Linux Kernel Settings:**
```bash
# /etc/sysctl.conf

# Increase file descriptors
fs.file-max = 2097152

# Increase TCP connection limits
net.core.somaxconn = 4096
net.ipv4.tcp_max_syn_backlog = 8192

# Enable TCP fast open
net.ipv4.tcp_fastopen = 3

# Optimize for low latency
net.ipv4.tcp_low_latency = 1

# Apply settings
sudo sysctl -p
```

**Disk I/O Scheduler:**
```bash
# For SSDs, use 'none' or 'deadline'
echo none > /sys/block/nvme0n1/queue/scheduler

# For HDDs, use 'cfq'
echo cfq > /sys/block/sda/queue/scheduler
```

---

## Security

### Network Security

#### 1. Firewall Rules
```bash
# Allow storage server port (internal only)
sudo ufw allow from 10.0.0.0/8 to any port 50051 proto tcp

# Allow control center (public)
sudo ufw allow 9000/tcp

# Deny direct storage access from internet
sudo ufw deny 50051/tcp
```

#### 2. TLS/SSL (Coming in HA Phase)
```bash
# Generate certificates
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout server-key.pem \
  -out server-cert.pem \
  -days 365

# Configure storage server
export SUTRA_TLS_CERT=/path/to/server-cert.pem
export SUTRA_TLS_KEY=/path/to/server-key.pem
```

### Data Security

#### 1. Encryption at Rest
```bash
# Use encrypted file system
sudo cryptsetup luksFormat /dev/nvme0n1p1
sudo cryptsetup open /dev/nvme0n1p1 sutra-encrypted
sudo mkfs.ext4 /dev/mapper/sutra-encrypted
sudo mount /dev/mapper/sutra-encrypted /var/lib/sutra
```

#### 2. Access Control
```bash
# Restrict file permissions
sudo chmod 700 /var/lib/sutra/knowledge
sudo chmod 600 /var/lib/sutra/knowledge/*
```

---

## Troubleshooting

### Issue: Storage Server Won't Start

**Symptoms:**
```
Error: Failed to open WAL file
```

**Solution:**
```bash
# Check permissions
ls -la /var/lib/sutra/knowledge/

# Fix ownership
sudo chown -R sutra:sutra /var/lib/sutra

# Check disk space
df -h /var/lib/sutra
```

---

### Issue: WAL File Growing Unbounded

**Symptoms:**
```bash
ls -lh /var/lib/sutra/knowledge/wal.log
# Output: 500M+ (should be <1KB)
```

**Solution:**
```bash
# Manually trigger flush
grpcurl -plaintext localhost:50051 sutra.storage.StorageService/Flush

# Check if auto-flush is working
# Should flush every 50K concepts by default
```

---

### Issue: High Memory Usage

**Symptoms:**
```
RSS: 8GB+
```

**Solution:**
```bash
# 1. Reduce memory threshold
export MEMORY_THRESHOLD=25000

# 2. Increase flush frequency
# (Flushes to disk more often, frees memory)

# 3. Check for memory leaks
# View metrics:
grpcurl -plaintext localhost:50051 sutra.storage.StorageService/GetStats
```

---

### Issue: Slow Writes

**Symptoms:**
```
Write latency: >5ms
```

**Diagnostics:**
```bash
# 1. Check if WAL fsync is blocking
# Disable fsync for testing (NOT RECOMMENDED IN PRODUCTION):
# Code change needed in wal.rs: fsync=false

# 2. Check disk I/O
iostat -x 1 10

# 3. Check for backpressure
grpcurl -plaintext localhost:50051 sutra.storage.StorageService/GetStats
# Look at "dropped" counter (should be 0)
```

**Solution:**
- Use SSD instead of HDD
- Reduce fsync frequency (trade durability for speed)
- Increase `RECONCILE_INTERVAL_MS`

---

## High Availability (Coming Soon)

**Status:** In development (4-week timeline)

### Planned Architecture
```
┌──────────┐       ┌──────────┐       ┌──────────┐
│  Primary │──WAL──│ Replica1 │       │ Replica2 │
│  (Write) │ Stream│  (Read)  │       │  (Read)  │
└──────────┘       └──────────┘       └──────────┘
```

### Setup Preview (Available in 4 weeks)
```bash
# Leader configuration
export SUTRA_NODE_ROLE=leader
export SUTRA_REPLICAS=replica1:50052,replica2:50053

# Replica configuration
export SUTRA_NODE_ROLE=replica
export SUTRA_LEADER=leader:50051
```

**Metrics:**
- RPO: ~10ms (async) or 0ms (sync option)
- RTO: <5 seconds (automatic failover)

**See:** `docs/HA_REPLICATION_DESIGN.md` for details

---

## Production Checklist

### Pre-Deployment
- [ ] Storage directory created with correct permissions
- [ ] Systemd service file configured
- [ ] Backup script setup and tested
- [ ] Monitoring configured
- [ ] Firewall rules applied
- [ ] Disk space allocated (10GB+ recommended)

### Post-Deployment
- [ ] Service is running (`systemctl status sutra-storage`)
- [ ] Health check passes (`grpcurl ... HealthCheck`)
- [ ] Data persists after restart
- [ ] Backups are running successfully
- [ ] Logs are being collected
- [ ] WAL file size is normal (<1KB after flush)

### Weekly Maintenance
- [ ] Check disk usage (`df -h /var/lib/sutra`)
- [ ] Review logs for errors (`journalctl -u sutra-storage`)
- [ ] Verify backups (`ls /backup/sutra/`)
- [ ] Test restore procedure

---

## Support & Resources

- **Documentation:** See WARP.md and docs/ directory
- **GitHub Issues:** https://github.com/your-org/sutra-models/issues
- **Changelog:** See CHANGELOG.md
- **HA Design:** See docs/HA_REPLICATION_DESIGN.md
- **Phase 1 Plan:** See docs/HA_PHASE1_PLAN.md

---

## Appendix

### Quick Reference Commands

```bash
# Start service
sudo systemctl start sutra-storage

# Stop service
sudo systemctl stop sutra-storage

# Restart service
sudo systemctl restart sutra-storage

# View logs
sudo journalctl -u sutra-storage -f

# Trigger flush
grpcurl -plaintext localhost:50051 sutra.storage.StorageService/Flush

# Get statistics
grpcurl -plaintext localhost:50051 sutra.storage.StorageService/GetStats

# Health check
grpcurl -plaintext localhost:50051 sutra.storage.StorageService/HealthCheck

# Backup now
sudo /usr/local/bin/backup-sutra.sh

# List backups
ls -lh /backup/sutra/
```
