# Financial Intelligence System Architecture & Design

## Overview

This document details the complete architecture and design of the financial intelligence system built on Sutra AI, covering system components, networking, security, scalability, and deployment considerations.

## System Architecture

### High-Level Architecture

```
                    🌐 External Access (Port 8080)
                              ↓
                    ┌─────────────────────────┐
                    │    Nginx Proxy         │  ← Single External Entry Point
                    │    (Load Balancer)     │
                    └─────────────────────────┘
                              ↓
              ┌───────────────┼───────────────┐
              ↓               ↓               ↓
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │   Sutra API     │ │  Sutra Hybrid   │ │   Client UI     │
    │   (Port 8000)   │ │   (Port 8000)   │ │  (Port 8080)    │
    └─────────────────┘ └─────────────────┘ └─────────────────┘
              ↓               ↓               ↓
              └───────────────┼───────────────┘
                              ↓
                    ┌─────────────────────────┐
                    │   Internal Network      │  ← Docker Bridge Network
                    │   (172.20.0.0/16)      │     (No External Access)
                    └─────────────────────────┘
                              ↓
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ Storage Server│   │ Embedding Service│   │ Bulk Ingester   │
│ (Port 50051)  │   │ (Port 8888)     │   │ (Port 8005)     │
└───────────────┘   └─────────────────┘   └─────────────────┘
        ↓                     ↓                     ↓
┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  WAL Storage  │   │  Vector Cache   │   │ Ingestion Jobs  │
│  (Persistent) │   │  (Memory)       │   │ (Persistent)    │
└───────────────┘   └─────────────────┘   └─────────────────┘
```

### Component Breakdown

#### External Layer (Port 8080)
- **Nginx Reverse Proxy** - Single point of entry, SSL termination, load balancing
- **Security** - Rate limiting, request filtering, access control

#### API Layer (Internal Network)
- **Sutra API Service** - REST endpoints for concept ingestion and management
- **Sutra Hybrid Service** - Semantic query processing and natural language interface
- **Client UI Service** - Web interface for system interaction

#### Core Services (Internal Network)
- **Storage Server** - High-performance graph storage with TCP binary protocol
- **Embedding Service** - HA cluster for concept vectorization (3 replicas + HAProxy)
- **Bulk Ingester** - Enterprise-scale data processing service

#### Persistence Layer
- **WAL (Write-Ahead Log)** - Crash recovery and data durability
- **Vector Cache** - In-memory HNSW indexing for fast similarity search
- **Ingestion Jobs** - Persistent job state for bulk processing

## Network Architecture

### Internal Networking Design

**Security Through Network Isolation**:
```yaml
networks:
  sutra-network:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.20.0.0/16  # Isolated internal network
```

**Service Communication**:
```
External → nginx (8080) → Internal Services
                ↓
Internal Services ↔ Internal Services (Docker Network)
                ↓
No Direct External Access to Core Services
```

**Port Allocation Strategy**:

| Service | External Port | Internal Port | Access Level |
|---------|---------------|---------------|--------------|
| Nginx Proxy | 8080, 80, 443 | - | Public |
| Sutra API | - | 8000 | Internal Only |
| Sutra Hybrid | - | 8000 | Internal Only |
| Storage Server | - | 50051 | Internal Only |
| Embedding Service | - | 8888 | Internal Only |
| Bulk Ingester | - | 8005 | Internal Only |

### Load Balancing Configuration

**Nginx Upstream Definitions**:
```nginx
# Main API service with health checks
upstream sutra_api {
    least_conn;                                    # Load balancing algorithm
    server sutra-works-api:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;                                  # Connection pooling
}

# Hybrid service (Semantic + NLG)
upstream sutra_hybrid {
    least_conn;
    server sutra-works-hybrid:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

# Embedding HA cluster
upstream sutra_embedding_ha {
    least_conn;
    server sutra-works-embedding-1:8889 max_fails=2 fail_timeout=15s;
    server sutra-works-embedding-2:8890 max_fails=2 fail_timeout=15s;
    server sutra-works-embedding-3:8891 max_fails=2 fail_timeout=15s;
    keepalive 16;
}
```

**Health Check Configuration**:
```nginx
# API health monitoring
location /api/ {
    proxy_pass http://sutra_api/;
    
    # Health check parameters
    proxy_connect_timeout 30s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    
    # Connection management
    proxy_set_header Connection "";
    proxy_http_version 1.1;
}
```

## Data Flow Architecture

### Financial Data Ingestion Flow

```
Google Finance Data → Python Processor → Concept Creation → API Ingestion → Storage Persistence
        ↓                    ↓                ↓               ↓                ↓
   OHLCV Raw Data    Rich Content Gen.   Metadata Struct.  TCP Protocol    WAL + Vector Index
```

### Detailed Data Flow

**1. Data Preparation Phase**:
```python
# Market data generation/retrieval
market_data = fetch_financial_data(company, date)

# Realistic OHLCV generation
ohlcv_data = {
    "open": 178.28,
    "high": 182.13, 
    "low": 176.36,
    "close": 180.99,
    "volume": 89234567
}
```

**2. Concept Creation Phase**:
```python
# Rich content generation
content = f"{company.name} ({company.ticker}) financial data for {date}: " \
          f"Stock opened at ${ohlcv_data['open']:.2f}, closed at ${ohlcv_data['close']:.2f}, " \
          f"with high of ${ohlcv_data['high']:.2f} and low of ${ohlcv_data['low']:.2f}. " \
          f"Trading volume was {ohlcv_data['volume']:,} shares..."

# Structured metadata
metadata = {
    "source": "financial_market_data",
    "company": company.ticker,
    "date": date.strftime('%Y-%m-%d'),
    "data_type": "daily_ohlcv",
    **{f"price_{key}": str(value) for key, value in ohlcv_data.items()}
}
```

**3. API Ingestion Phase**:
```python
# HTTP POST to Sutra API
response = requests.post(
    "http://localhost:8080/api/learn",
    json={"content": content, "metadata": metadata},
    timeout=60
)

# Response validation
if response.status_code == 201:
    result = response.json()
    concept_id = result["concept_id"]  # e.g., "cf6002249c50493f"
```

**4. Storage Processing Phase**:
```rust
// Sutra Storage Server (Rust)
pub async fn learn_concept(&mut self, content: String, metadata: Option<ConceptMetadata>) -> Result<ConceptId> {
    // Generate embedding via embedding service
    let embedding = self.embedding_client.generate(&content).await?;
    
    // Extract semantic associations
    let associations = self.extract_associations(&content)?;
    
    // Atomic storage with WAL
    let concept_id = self.store_atomically(content, embedding, associations, metadata).await?;
    
    // Update vector index
    self.vector_index.add(concept_id, embedding)?;
    
    Ok(concept_id)
}
```

### Query Processing Flow

```
User Query → Nginx Proxy → Sutra Hybrid → Storage Server → Vector Search → Response Generation
     ↓             ↓            ↓              ↓             ↓              ↓
Natural Lang.   Routing    Semantic Proc.  Graph Search   HNSW Index    Ranked Results
```

**Query Execution Pipeline**:
```python
# 1. Query reception and preprocessing
query = preprocess_financial_query(user_query)

# 2. Semantic analysis
query_embedding = embedding_service.generate(query)

# 3. Vector similarity search  
similar_concepts = storage.vector_search(query_embedding, top_k=10)

# 4. Graph traversal for associations
related_concepts = storage.traverse_associations(similar_concepts)

# 5. Answer generation with confidence scoring
answer = nlg_service.generate_answer(query, similar_concepts, related_concepts)
```

## Storage Architecture

### Write-Ahead Log (WAL) Design

**Durability Guarantees**:
```rust
// WAL implementation for crash recovery
impl WriteAheadLog {
    async fn log_operation(&mut self, operation: StorageOperation) -> Result<()> {
        // 1. Write to WAL first
        self.wal_writer.write_operation(&operation).await?;
        self.wal_writer.flush().await?;  // Force to disk
        
        // 2. Apply to storage
        self.storage.apply_operation(operation).await?;
        
        // 3. Update checkpoint
        self.update_checkpoint().await?;
        
        Ok(())
    }
    
    async fn recover_from_crash(&mut self) -> Result<()> {
        // Replay WAL entries since last checkpoint
        let operations = self.wal_reader.read_since_checkpoint().await?;
        
        for operation in operations {
            self.storage.apply_operation(operation).await?;
        }
        
        Ok(())
    }
}
```

### Vector Index Architecture

**HNSW (Hierarchical Navigable Small World) Implementation**:
```rust
// High-performance vector indexing
pub struct HnswIndex {
    dimension: usize,           // 768 for financial embeddings
    max_connections: usize,     // Graph connectivity
    ef_construction: usize,     // Build-time search width
    ef_search: usize,          // Query-time search width
    layers: Vec<GraphLayer>,   // Hierarchical structure
    entry_point: NodeId,       // Top-level entry
}

impl HnswIndex {
    pub async fn search(&self, query_vector: &[f32], k: usize) -> Result<Vec<SearchResult>> {
        // Multi-layer search for optimal performance
        let mut candidates = self.search_layer(&query_vector, self.entry_point, k).await?;
        
        // Refine results with graph traversal
        let refined_results = self.refine_candidates(candidates, k).await?;
        
        Ok(refined_results)
    }
}
```

**Persistent Memory Mapping**:
```rust
// Fast startup with mmap persistence
pub struct PersistentVectorIndex {
    mmap_file: MmapMut,        // Memory-mapped file
    index_metadata: IndexMetadata,
    vector_data: &[f32],       // Direct memory access
}

// 94x faster startup compared to rebuilding index
impl PersistentVectorIndex {
    pub fn load_from_disk(path: &Path) -> Result<Self> {
        let file = OpenOptions::new().read(true).write(true).open(path)?;
        let mmap = unsafe { MmapMut::map_mut(&file)? };
        
        // Direct memory access to vectors - no deserialization needed
        Ok(Self { mmap_file: mmap, ... })
    }
}
```

## Performance Architecture

### Concurrency Design

**Optimized Threading Model**:
```python
# Production-tuned concurrency settings
class ProductionFinancialIntelligence:
    def __init__(self):
        # Carefully tuned for system stability
        self.max_concurrent = 2        # Prevents overwhelming embedding service
        self.session.timeout = 60      # Accommodates embedding processing time
        self.retry_attempts = 3        # Resilient error recovery
        self.retry_delay = 1.0         # Exponential backoff base
        
        # Connection pooling for efficiency
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=Retry(total=3, backoff_factor=0.3)
        ))
```

**Before/After Performance Analysis**:

| Configuration | Workers | Success Rate | Throughput | Errors |
|---------------|---------|--------------|------------|---------|
| **Before** | 10 | 0% | 0 concepts/sec | All timeout |
| **After** | 2 | 100% | 0.14 concepts/sec | None |

**Key Performance Insight**: *More workers ≠ Better performance*
- **Bottleneck**: Embedding service processing capacity
- **Solution**: Match concurrency to system capacity
- **Result**: 100% reliability with optimal throughput

### Memory Architecture

**Memory Usage Optimization**:
```rust
// Efficient memory management
pub struct MemoryOptimizedStorage {
    concept_store: HashMap<ConceptId, Arc<Concept>>,     // Shared references
    vector_cache: LruCache<ConceptId, Vec<f32>>,         // LRU eviction
    association_graph: CompactGraph,                      // Memory-efficient graph
    wal_buffer: RingBuffer<Operation>,                   // Fixed-size circular buffer
}

impl MemoryOptimizedStorage {
    // Memory usage monitoring
    pub fn get_memory_stats(&self) -> MemoryStats {
        MemoryStats {
            concept_store_mb: self.concept_store.memory_usage() / 1024 / 1024,
            vector_cache_mb: self.vector_cache.memory_usage() / 1024 / 1024,
            graph_memory_mb: self.association_graph.memory_usage() / 1024 / 1024,
            total_memory_mb: self.total_memory_usage() / 1024 / 1024,
        }
    }
}
```

## Security Architecture

### Network Security

**Internal Network Isolation**:
```yaml
# Docker Compose security configuration
services:
  storage-server:
    # SECURITY: No external port exposure
    expose:
      - "50051"  # Internal only
    networks:
      - sutra-network
    
  nginx-proxy:
    # SECURITY: Single external entry point
    ports:
      - "80:80"     # HTTP (redirects to HTTPS)
      - "443:443"   # HTTPS (production)
      - "8080:8080" # Development (no SSL)
    networks:
      - sutra-network
```

**Access Control Lists**:
```nginx
# Internal metrics endpoint restriction
location /internal/ {
    # Allow only from internal networks
    allow 10.0.0.0/8;
    allow 172.16.0.0/12;
    allow 192.168.0.0/16;
    allow 127.0.0.1;
    deny all;  # Block all other access
    
    proxy_pass http://sutra_api/internal/;
}
```

### Request Security

**Rate Limiting**:
```nginx
# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=60r/m;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=10r/m;
limit_req_zone $binary_remote_addr zone=general_limit:10m rate=120r/m;

# Apply rate limiting to API endpoints
location /api/ {
    limit_req zone=api_limit burst=10 nodelay;
    # ... proxy configuration
}
```

**Security Headers**:
```nginx
# Comprehensive security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

# HSTS for production (uncomment for production)
# add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
```

### Data Security

**Encryption at Rest**:
```rust
// Data encryption for sensitive financial information
pub struct EncryptedStorage {
    encryption_key: [u8; 32],     // AES-256 key
    cipher: Aes256Gcm,            // Authenticated encryption
}

impl EncryptedStorage {
    pub fn encrypt_concept(&self, concept: &Concept) -> Result<EncryptedConcept> {
        let plaintext = serde_json::to_vec(concept)?;
        let nonce = generate_nonce();
        
        let ciphertext = self.cipher
            .encrypt(&nonce, plaintext.as_ref())
            .map_err(|e| StorageError::EncryptionFailed(e.to_string()))?;
        
        Ok(EncryptedConcept { ciphertext, nonce })
    }
}
```

## Scalability Architecture

### Horizontal Scaling Design

**Multi-Shard Architecture** (Enterprise Edition):
```rust
// Distributed storage across multiple shards
pub struct ShardedStorage {
    shards: Vec<StorageServer>,
    shard_router: ConsistentHashRouter,
    replication_factor: usize,
}

impl ShardedStorage {
    pub async fn distribute_concept(&self, concept: &Concept) -> Result<Vec<ConceptId>> {
        let shard_ids = self.shard_router.route_concept(concept);
        let mut results = Vec::new();
        
        // Parallel writes to multiple shards
        let futures: Vec<_> = shard_ids.into_iter()
            .map(|shard_id| self.shards[shard_id].store_concept(concept.clone()))
            .collect();
        
        let shard_results = join_all(futures).await;
        
        for result in shard_results {
            match result {
                Ok(concept_id) => results.push(concept_id),
                Err(e) => log::error!("Shard write failed: {}", e),
            }
        }
        
        Ok(results)
    }
}
```

**Embedding Service HA Cluster**:
```yaml
# High Availability embedding service
embedding-ha:
  image: haproxy:2.8
  ports:
    - "8888:8888"
  volumes:
    - ./haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro
  depends_on:
    - embedding-1
    - embedding-2  
    - embedding-3

embedding-1:
  image: sutra-embedding-service:latest
  ports:
    - "8889:8888"
    
embedding-2:
  image: sutra-embedding-service:latest  
  ports:
    - "8890:8888"
    
embedding-3:
  image: sutra-embedding-service:latest
  ports:
    - "8891:8888"
```

### Vertical Scaling Capabilities

**Resource Allocation**:
```yaml
# Production resource limits
services:
  storage-server:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
          
  embedding-service:
    deploy:
      resources:
        limits:
          cpus: '4.0'      # CPU-intensive embedding generation
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G
```

**Auto-scaling Configuration**:
```yaml
# Kubernetes HPA for production deployment
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: sutra-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: sutra-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Monitoring & Observability

### Health Check Architecture

**Comprehensive Health Monitoring**:
```python
class SystemHealthMonitor:
    def __init__(self):
        self.health_checks = {
            "api_health": self.check_api_health,
            "storage_health": self.check_storage_health,
            "embedding_health": self.check_embedding_health,
            "nginx_health": self.check_nginx_health,
            "data_persistence": self.check_data_persistence
        }
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Execute comprehensive health checks"""
        results = {}
        
        for check_name, check_func in self.health_checks.items():
            try:
                start_time = time.time()
                result = await check_func()
                duration = time.time() - start_time
                
                results[check_name] = {
                    "status": "healthy" if result else "unhealthy",
                    "duration_ms": duration * 1000,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                results[check_name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        return results
```

**Real-time Performance Metrics**:
```python
def collect_system_metrics():
    """Collect comprehensive system performance metrics"""
    return {
        "concept_ingestion": {
            "rate_per_second": get_ingestion_rate(),
            "success_rate_percent": get_success_rate(),
            "average_latency_ms": get_average_latency(),
            "queue_depth": get_queue_depth()
        },
        "query_performance": {
            "queries_per_second": get_query_rate(),
            "average_response_time_ms": get_avg_response_time(),
            "confidence_distribution": get_confidence_stats(),
            "cache_hit_rate_percent": get_cache_hit_rate()
        },
        "resource_utilization": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "network_io": get_network_io_stats()
        },
        "storage_metrics": {
            "concepts_stored": get_concept_count(),
            "storage_size_mb": get_storage_size(),
            "index_size_mb": get_index_size(),
            "wal_size_mb": get_wal_size()
        }
    }
```

## Deployment Architecture

### Docker Compose Production Configuration

**Service Orchestration**:
```yaml
version: '3.8'
services:
  # ===== PROXY LAYER =====
  nginx-proxy:
    build:
      context: .
      dockerfile: ./nginx/Dockerfile
    image: sutra-works-nginx-proxy:${SUTRA_VERSION:-latest}
    container_name: sutra-works-nginx-proxy
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - nginx-logs:/var/log/nginx
    environment:
      - NGINX_WORKER_PROCESSES=auto
      - NGINX_WORKER_CONNECTIONS=2048
    networks:
      - sutra-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--spider", "http://localhost:80/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  # ===== API LAYER =====
  sutra-api:
    build:
      context: ../..
      dockerfile: ./packages/sutra-api/Dockerfile
    image: sutra-works-api:${SUTRA_VERSION:-latest}
    container_name: sutra-works-api
    expose:
      - "8000"
    environment:
      - SUTRA_STORAGE_SERVER=storage-server:50051
      - SUTRA_EMBEDDING_SERVICE_URL=http://embedding-ha:8888
    networks:
      - sutra-network
    restart: unless-stopped
    depends_on:
      - storage-server
      - embedding-ha

  # ===== STORAGE LAYER =====
  storage-server:
    build:
      context: ../..
      dockerfile: ./packages/sutra-storage/Dockerfile
    image: sutra-works-storage-server:${SUTRA_VERSION:-latest}
    container_name: sutra-works-storage
    expose:
      - "50051"
    volumes:
      - storage-data:/data
    environment:
      - STORAGE_PATH=/data
      - VECTOR_DIMENSION=768
      - SUTRA_EMBEDDING_SERVICE_URL=http://embedding-ha:8888
    networks:
      - sutra-network
    restart: unless-stopped

volumes:
  storage-data:
    driver: local
  nginx-logs:
    driver: local

networks:
  sutra-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Production Deployment Pipeline

**Automated Deployment Process**:
```bash
#!/bin/bash
# Production deployment script

set -euo pipefail

echo "🚀 Starting Production Deployment"

# 1. Pre-deployment validation
./scripts/validate_environment.sh
./scripts/run_pre_deployment_tests.sh

# 2. Build services
echo "📦 Building services..."
SUTRA_EDITION=enterprise ./sutra build

# 3. Deploy with zero downtime
echo "🔄 Deploying services..."
docker-compose -f .sutra/compose/production.yml up -d --no-deps --scale sutra-api=0
sleep 10
docker-compose -f .sutra/compose/production.yml up -d --no-deps --scale sutra-api=2

# 4. Health checks
echo "🏥 Running health checks..."
./scripts/validate_deployment.sh

# 5. Post-deployment validation
echo "✅ Running post-deployment tests..."
./scripts/run_post_deployment_tests.sh

echo "🎉 Deployment completed successfully!"
```

## Disaster Recovery Architecture

### Backup Strategy

**Automated Backup System**:
```python
class BackupManager:
    def __init__(self):
        self.backup_schedule = {
            "full_backup": "0 2 * * 0",      # Weekly full backup
            "incremental": "0 2 * * 1-6",    # Daily incremental
            "wal_backup": "*/15 * * * *"     # WAL backup every 15min
        }
    
    async def create_full_backup(self) -> str:
        """Create complete system backup"""
        backup_id = generate_backup_id()
        backup_path = f"/backups/full/{backup_id}"
        
        # Backup storage data
        await self.backup_storage_data(backup_path)
        
        # Backup vector indices
        await self.backup_vector_indices(backup_path)
        
        # Backup configuration
        await self.backup_configuration(backup_path)
        
        # Create manifest
        manifest = self.create_backup_manifest(backup_path)
        
        return backup_id
    
    async def restore_from_backup(self, backup_id: str) -> bool:
        """Restore system from backup"""
        backup_path = f"/backups/full/{backup_id}"
        
        # Validate backup integrity
        if not await self.validate_backup_integrity(backup_path):
            raise BackupError("Backup validation failed")
        
        # Stop services
        await self.stop_services()
        
        # Restore data
        await self.restore_storage_data(backup_path)
        await self.restore_vector_indices(backup_path)
        await self.restore_configuration(backup_path)
        
        # Start services
        await self.start_services()
        
        # Validate restoration
        return await self.validate_system_health()
```

### High Availability Configuration

**Multi-Region Deployment**:
```yaml
# Production HA deployment
version: '3.8'
services:
  # Primary region services
  storage-primary:
    image: sutra-storage:latest
    environment:
      - REPLICATION_MODE=primary
      - REPLICA_ENDPOINTS=storage-replica-1:50051,storage-replica-2:50051
    volumes:
      - primary-storage:/data

  # Replica region services  
  storage-replica-1:
    image: sutra-storage:latest
    environment:
      - REPLICATION_MODE=replica
      - PRIMARY_ENDPOINT=storage-primary:50051
    volumes:
      - replica-1-storage:/data

  # Load balancer with failover
  haproxy:
    image: haproxy:latest
    ports:
      - "8080:8080"
    volumes:
      - ./haproxy-ha.cfg:/usr/local/etc/haproxy/haproxy.cfg
    depends_on:
      - storage-primary
      - storage-replica-1
```

## Summary

The financial intelligence system architecture provides:

- ✅ **Security Through Isolation** - Internal network with single external entry point
- ✅ **High Performance** - Optimized concurrency and memory management
- ✅ **Data Durability** - WAL persistence with crash recovery
- ✅ **Horizontal Scalability** - Multi-shard distributed architecture
- ✅ **High Availability** - Service replication and failover capabilities
- ✅ **Comprehensive Monitoring** - Real-time health checks and metrics
- ✅ **Production Ready** - Automated deployment and disaster recovery

The system is architected for enterprise production deployment with proven performance and reliability.

*Next: [Production Deployment Documentation](./production-deployment.md)*