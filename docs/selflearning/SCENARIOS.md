# Learning Scenarios

**All documented ways data enters and is learned by sutra-storage**

---

## Overview

This document catalogs **every possible scenario** through which data can be ingested into sutra-storage, based on deep code analysis. Each scenario is traced from entry point to storage layer with exact file locations and code references.

---

## Scenario Categories

1. [Single Concept Learning](#scenario-1-single-concept-learning)
2. [Batch Learning](#scenario-2-batch-learning)
3. [Bulk Data Ingestion](#scenario-3-bulk-data-ingestion)
4. [Direct TCP Client](#scenario-4-direct-tcp-client)
5. [REST API Learning](#scenario-5-rest-api-learning)
6. [Association-Only Learning](#scenario-6-association-only-learning)
7. [Cross-Shard Learning (Enterprise)](#scenario-7-cross-shard-learning-enterprise)
8. [Embedding Failure Scenarios](#scenario-8-embedding-failure-scenarios)
9. [User/Session Learning (API)](#scenario-9-user-session-learning-api)
10. [Space/Permission Learning (API)](#scenario-10-space-permission-learning-api)

---

## Scenario 1: Single Concept Learning

**Most common scenario**: Learn a single piece of text with full pipeline processing.

### Entry Points

#### 1A. Python Client (Recommended)

```python
# File: packages/sutra-core/sutra_core/storage/tcp_adapter.py
from sutra_core.storage import TcpStorageAdapter

client = TcpStorageAdapter(server_address="localhost:50051")

concept_id = client.learn_concept(
    content="Diabetes requires regular blood glucose monitoring.",
    generate_embedding=True,
    extract_associations=True,
    min_association_confidence=0.5,
    max_associations_per_concept=10,
)
# Returns: concept_id (hex string)
```

**Code Path**:
```
TcpStorageAdapter.learn_concept()
  → StorageClient.learn_concept_v2()  [TCP client]
  → TCP Binary Protocol: LearnConceptV2 message
  → tcp_server.rs: handle_request()
  → LearningPipeline.learn_concept()
  → ConcurrentMemory.learn_concept()
  → WAL.append() + WriteLog.append() + HNSW.add_vector()
```

**Files Involved**:
- `packages/sutra-core/sutra_core/storage/tcp_adapter.py` (line 108-156)
- `packages/sutra-storage-client-tcp/sutra_storage_client/__init__.py` (line 98-118)
- `packages/sutra-storage/src/tcp_server.rs` (line 361-373)
- `packages/sutra-storage/src/learning_pipeline.rs` (line 64-124)
- `packages/sutra-storage/src/concurrent_memory.rs` (line 465-509)

#### 1B. Direct TCP Client

```python
# File: packages/sutra-storage-client-tcp/sutra_storage_client/__init__.py
from sutra_storage_client import StorageClient

client = StorageClient(server_address="localhost:50051")

concept_id = client.learn_concept_v2(
    content="Patient must fast for 8 hours before blood test.",
    options={
        "generate_embedding": True,
        "extract_associations": True,
        "min_association_confidence": 0.6,
    }
)
```

**Unique Characteristics**:
- Lower-level API (no retry logic by default)
- Direct MessagePack serialization
- Minimal abstractions

---

## Scenario 2: Batch Learning

**Optimized for bulk operations**: Learn multiple concepts in single API call.

### Entry Points

#### 2A. Python Client Batch

```python
# File: packages/sutra-core/sutra_core/storage/tcp_adapter.py (hypothetical - not yet implemented)
medical_facts = [
    "Diabetes requires regular blood glucose monitoring.",
    "High cholesterol increases heart disease risk.",
    "Regular exercise improves insulin sensitivity.",
]

concept_ids = client.learn_batch_v2(
    contents=medical_facts,
    options={"generate_embedding": True}
)
# Returns: List[concept_id]
```

**Code Path**:
```
TcpStorageAdapter.learn_batch_v2()  [Not yet in adapter]
  → StorageClient.learn_batch_v2()  [TCP client]
  → TCP Binary Protocol: LearnBatch message
  → tcp_server.rs: handle_request()
  → LearningPipeline.learn_batch()
  → Batch embeddings (single API call - 10× faster)
  → Parallel semantic analysis
  → Parallel association extraction
  → ConcurrentMemory.learn_concept() × N
```

**Files Involved**:
- `packages/sutra-storage-client-tcp/sutra_storage_client/__init__.py` (line 118-138)
- `packages/sutra-storage/src/tcp_server.rs` (line 374-395)
- `packages/sutra-storage/src/learning_pipeline.rs` (line 126-206)

**Performance Benefits**:
- Single embedding API call (instead of N calls)
- ~3ms per concept (vs ~30ms single)
- Reduced network overhead
- Parallel processing

---

## Scenario 3: Bulk Data Ingestion

**High-throughput scenario**: Ingest large datasets (CSV, JSON, Parquet) via dedicated service.

### Entry Point

```bash
# Bulk ingester service (Rust - Port 8005)
POST http://localhost:8005/ingest

# Request body
{
  "source_type": "csv",
  "file_path": "/data/medical_protocols.csv",
  "batch_size": 100,
  "learn_options": {
    "generate_embedding": true,
    "extract_associations": true
  }
}
```

**Code Path**:
```
HTTP POST /ingest
  → server.rs: ingest_handler()
  → BulkIngester.process_file()
  → Adapter-specific parsing (CSV/JSON/Parquet)
  → TcpStorageClient.batch_learn_concepts()
  → TCP: LearnBatch message
  → LearningPipeline.learn_batch()
  → ShardedStorage.learn_concept() × N
```

**Files Involved**:
- `packages/sutra-bulk-ingester/src/server.rs` (HTTP server)
- `packages/sutra-bulk-ingester/src/lib.rs` (BulkIngester core)
- `packages/sutra-bulk-ingester/src/storage.rs` (line 137-229)
- `packages/sutra-bulk-ingester/src/adapters.rs` (format parsers)

**Supported Formats**:
- CSV (with header detection)
- JSON (line-delimited or array)
- Parquet (columnar format)
- Plugin system for custom formats

**Performance Characteristics**:
- Streaming (doesn't load entire file into memory)
- Configurable batch size (default: 100)
- Memory limit enforcement (default: 4GB)
- Compression support
- Progress tracking

**Example CSV**:
```csv
content,domain,confidence
"Patient must fast for 8 hours before blood test",medical,0.95
"Aspirin contraindicated in patients with active bleeding",medical,0.98
```

---

## Scenario 4: Direct TCP Client

**Low-level scenario**: Bypass Python wrapper, use raw TCP protocol.

### Entry Point

```python
# Direct MessagePack over TCP
import socket
import msgpack

def learn_concept_raw(content):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 50051))
    
    request = {
        "LearnConceptV2": {
            "content": content,
            "options": {
                "generate_embedding": True,
                "embedding_model": None,
                "extract_associations": True,
                "min_association_confidence": 0.5,
                "max_associations_per_concept": 10,
                "strength": 1.0,
                "confidence": 1.0,
            }
        }
    }
    
    # Length-prefixed MessagePack
    packed = msgpack.packb(request)
    sock.sendall(len(packed).to_bytes(4, 'big'))
    sock.sendall(packed)
    
    # Read response
    length_bytes = sock.recv(4)
    length = int.from_bytes(length_bytes, 'big')
    response_bytes = sock.recv(length)
    response = msgpack.unpackb(response_bytes)
    
    sock.close()
    return response["LearnConceptV2Ok"]["concept_id"]
```

**Use Cases**:
- Custom language bindings (Go, Java, Rust)
- Performance-critical applications
- Integration with non-Python systems

**Protocol Specification**: See `docs/storage/TCP_BINARY_PROTOCOL.md`

---

## Scenario 5: REST API Learning

**Web application scenario**: Learn concepts via HTTP endpoints.

### Entry Points

#### 5A. Single Concept

```bash
POST http://localhost:8000/learn
Content-Type: application/json

{
  "content": "Diabetes requires regular blood glucose monitoring.",
  "source": "medical_protocol_v2.3",
  "category": "patient_care",
  "generate_embedding": true,
  "extract_associations": true
}
```

**Code Path**:
```
FastAPI: /learn endpoint
  → main.py: learn() handler
  → get_storage_client() dependency
  → TcpStorageAdapter.learn_concept()
  → [Same as Scenario 1A]
```

**Files Involved**:
- `packages/sutra-api/sutra_api/main.py` (line 261-304)
- `packages/sutra-api/sutra_api/dependencies.py` (storage client factory)

#### 5B. Batch Learning

```bash
POST http://localhost:8000/learn/batch
Content-Type: application/json

{
  "contents": [
    "Diabetes requires regular blood glucose monitoring.",
    "High cholesterol increases heart disease risk."
  ],
  "source": "medical_protocols",
  "generate_embedding": true
}
```

**Code Path**:
```
FastAPI: /learn/batch endpoint
  → main.py: batch_learn() handler
  → TcpStorageAdapter.learn_batch_v2()  [if implemented]
  → [Same as Scenario 2A]
```

**Files Involved**:
- `packages/sutra-api/sutra_api/main.py` (line 305-337)

**Rate Limiting**:
- `/learn`: 30 requests/min (default)
- `/learn/batch`: 15 requests/min (default)
- Configurable via middleware

---

## Scenario 6: Association-Only Learning

**Explicit relationship scenario**: Add association between existing concepts.

### Entry Point

```python
# Python client
client.learn_association(
    source_id="a3f2c8d1e4b6f9a2",
    target_id="b8e4d9f2a1c7b5e3",
    association_type=AssociationType.CAUSAL,
    confidence=0.85
)
```

**Code Path**:
```
TcpStorageAdapter.learn_association()
  → StorageClient.learn_association()
  → TCP: LearnAssociation message
  → tcp_server.rs: handle_request()
  → ConcurrentMemory.learn_association()
  → WAL.append(WriteAssociation)
  → WriteLog.append_association()
```

**Files Involved**:
- `packages/sutra-core/sutra_core/storage/tcp_adapter.py` (line 161-188)
- `packages/sutra-storage-client-tcp/sutra_storage_client/__init__.py` (line 166-185)
- `packages/sutra-storage/src/tcp_server.rs` (line 428-446)
- `packages/sutra-storage/src/concurrent_memory.rs` (line 510-556)

**Association Types**:
```rust
pub enum AssociationType {
    Semantic = 0,        // Type-of, instance-of
    Causal = 1,          // Causes, leads-to
    Temporal = 2,        // Before, after
    Hierarchical = 3,    // Parent-of, child-of
    Compositional = 4,   // Part-of, contains
}
```

**Important**: Both concepts must exist before creating association.

---

## Scenario 7: Cross-Shard Learning (Enterprise)

**Distributed scenario**: Learn concepts across multiple shards with 2PC.

### Entry Point

```python
# Enterprise edition with 16 shards
config = ShardConfig(num_shards=16)
storage = ShardedStorage(config)

# Concept automatically routed to correct shard
concept_id = storage.learn_concept(
    id=ConceptId::from_string("a3f2..."),
    content=b"Medical content",
    vector=Some(embedding),
    strength=1.0,
    confidence=0.9,
)
```

**Code Path (Same Shard)**:
```
ShardedStorage.learn_concept()
  → get_shard_id() via consistent hashing
  → shards[shard_id].learn_concept()
  → [Same as single-shard scenario]
```

**Code Path (Cross-Shard Association)**:
```
ShardedStorage.create_association()
  → get_shard_id(source) = 3
  → get_shard_id(target) = 7
  → TransactionCoordinator.begin()
  → Phase 1: Prepare both shards
    ├─ shards[3].create_association()
    ├─ txn_coordinator.mark_prepared(txn_id, 3)
    ├─ shards[7].create_association()
    └─ txn_coordinator.mark_prepared(txn_id, 7)
  → Phase 2: Commit or Abort
    ├─ is_ready_to_commit()?
    ├─ commit() if ready
    └─ abort() if timeout/failure
```

**Files Involved**:
- `packages/sutra-storage/src/sharded_storage.rs` (line 132-241)
- `packages/sutra-storage/src/transaction.rs` (2PC implementation)

**2PC Guarantees**:
- **Atomicity**: Both shards commit or both abort
- **Timeout**: 5 seconds (configurable)
- **Durability**: WAL on each shard
- **Isolation**: Transactions serialized

---

## Scenario 8: Embedding Failure Scenarios

**Fault tolerance**: System continues learning even if embedding service fails.

### 8A. Partial Failure (Some Embeddings Fail)

```python
# Batch with mixed success
concept_ids = client.learn_batch_v2([
    "Valid text 1",
    "Valid text 2",
    "🚨 Causes embedding service timeout",
    "Valid text 3",
])
# Result: Concepts learned without embeddings
# - Vector search unavailable for failed concepts
# - Graph traversal still works
# - Semantic metadata still extracted
```

**Code Behavior**:
```rust
// In learning_pipeline.rs
let embedding_opt = if options.generate_embedding {
    match self.embedding_client.generate(content, true).await {
        Ok(vec) => Some(vec),
        Err(e) => { 
            warn!("Embedding failed, continuing without: {}", e); 
            None  // ← Continues without embedding
        }
    }
} else { None };
```

**Consequences**:
- Concept still learned
- No vector available → no semantic search
- Graph traversal still functional
- Associations still extracted
- Semantic type classification still works

### 8B. Complete Failure (Embedding Service Down)

```python
# All embeddings fail but learning continues
concept_ids = client.learn_batch_v2(contents)
# System behavior:
# - All concepts learned without embeddings
# - Semantic analysis still performed
# - Association extraction still attempted
# - Graph structure maintained
# - WAL records complete
```

**Retry Logic**:
```rust
// In embedding_client.rs
for attempt in 0..=self.config.max_retries {
    match self.try_generate_batch(texts, normalize).await {
        Ok(embeddings) => return embeddings,
        Err(e) => {
            if attempt < self.config.max_retries {
                let delay = exponential_backoff(attempt);
                tokio::time::sleep(delay).await;
            }
        }
    }
}
// After 3 retries: return None for all
vec![None; texts.len()]
```

**Configuration**:
- `SUTRA_EMBEDDING_TIMEOUT_SEC=30`
- Max retries: 3
- Backoff: 500ms, 1s, 2s

---

## Scenario 9: User/Session Learning (API)

**Application scenario**: API manages user concepts internally.

### 9A. User Registration

```python
# File: packages/sutra-api/sutra_api/services/user_service.py (line 134)
user_id = self.storage.learn_concept_v2(
    content=f"User: {email}",
    options={
        "generate_embedding": False,  # ← No embedding for metadata
        "extract_associations": False,
    }
)
```

**Metadata Stored**:
```json
{
  "type": "user",
  "email": "user@example.com",
  "role": "admin",
  "organization": "acme_corp",
  "created_at": "2025-01-15T10:30:00Z"
}
```

### 9B. Session Tracking

```python
# File: packages/sutra-api/sutra_api/services/user_service.py (line 238)
session_concept_id = self.storage.learn_concept_v2(
    content=f"Session: {user_id}",
    options={
        "generate_embedding": False,
        "extract_associations": False,
    }
)

# Associate session with user
self.storage.learn_association(
    source_id=session_concept_id,
    target_id=user_id,
    association_type=AssociationType.SEMANTIC,
    confidence=1.0,
)
```

**Use Cases**:
- Authentication tokens
- Session expiry tracking
- User activity logs
- Access control

---

## Scenario 10: Space/Permission Learning (API)

**Multi-tenancy scenario**: Isolated knowledge spaces per organization.

### 10A. Space Creation

```python
# File: packages/sutra-api/sutra_api/services/space_service.py (line 89)
space_concept = self.storage.learn_concept(
    content=f"Space: {name}",
    source="space_management",
    category="system",
    generate_embedding=False,
)
```

**Space Metadata**:
```json
{
  "type": "space",
  "name": "Medical Knowledge Base",
  "description": "Clinical protocols and guidelines",
  "organization": "hospital_system",
  "domain_storage": "medical_kb",
  "created_by": "user_123",
  "visibility": "private"
}
```

### 10B. Permission Grant

```python
# File: packages/sutra-api/sutra_api/services/space_service.py (line 764)
permission_concept = self.storage.learn_concept(
    content=f"Permission: {user_id} → {space_id} ({permission_level})",
    source="permission_management",
    category="system",
    generate_embedding=False,
)

# Link permission to user and space
self.storage.learn_association(permission_id, user_id, ...)
self.storage.learn_association(permission_id, space_id, ...)
```

**Permission Levels**:
- `owner`: Full control
- `editor`: Read + write concepts
- `viewer`: Read-only access
- `none`: No access

---

## Edge Cases and Error Scenarios

### E1. Duplicate Content

```python
# Same content learned twice
id1 = client.learn_concept("Diabetes requires monitoring.")
id2 = client.learn_concept("Diabetes requires monitoring.")

# Result: id1 == id2 (deterministic hash)
# - Second call updates existing concept
# - Associations merged
# - Confidence/strength updated
```

### E2. Malformed Input

```python
# Empty content
client.learn_concept("")  # ← Returns error

# Too large content
client.learn_concept("x" * 11_000_000)  # ← Error: MAX_CONTENT_SIZE exceeded

# Invalid embedding dimension
client.learn_concept(content, embedding=[0.1] * 10000)  # ← Error: MAX_EMBEDDING_DIM
```

**Validation (tcp_server.rs line 402-417)**:
```rust
if content.len() > MAX_CONTENT_SIZE {
    return StorageResponse::Error {
        message: format!("Content too large: {} bytes (max: {})", 
                        content.len(), MAX_CONTENT_SIZE),
    };
}
```

### E3. Network Timeout

```python
# TCP connection lost during learning
try:
    concept_id = client.learn_concept(content)
except ConnectionError:
    # Retry logic in TcpStorageAdapter
    # - 3 automatic retries
    # - Exponential backoff
    # - If all fail: exception raised
```

### E4. WAL Full (Disk Space)

```rust
// In wal.rs
if wal_file_size > MAX_WAL_SIZE {
    log::error!("WAL file too large, rotation required");
    // System behavior:
    // - Writes continue to write log
    // - Reconciler pauses
    // - Manual intervention needed
}
```

---

## Performance Comparison

| Scenario | Throughput | Latency | Use Case |
|----------|-----------|---------|----------|
| **Single Concept** | ~33 concepts/sec | ~30ms | Interactive applications |
| **Batch (10)** | ~330 concepts/sec | ~3ms/concept | Bulk imports |
| **Batch (100)** | ~3,300 concepts/sec | ~0.3ms/concept | Data migrations |
| **Bulk Ingester** | ~10,000 concepts/sec | Streaming | Large datasets |
| **Cross-Shard** | ~57,000 concepts/sec | <0.01ms | Enterprise scale |
| **Association Only** | ~100,000 ops/sec | <0.1ms | Graph construction |

**Bottlenecks**:
- Embedding generation: ~27ms (HA service)
- Semantic extraction: ~20ms (sentence embedding)
- Network round-trip: ~1-3ms (TCP)
- Storage write: <0.1ms (WAL + WriteLog)

---

## Monitoring and Observability

### Learning Metrics

```python
# Get storage statistics
stats = client.stats()

print(f"Total concepts: {stats['concepts']}")
print(f"Total edges: {stats['edges']}")
print(f"Vectors indexed: {stats['vectors']}")
print(f"WAL entries written: {stats['written']}")
print(f"Write log dropped: {stats['dropped']}")
print(f"Reconciliations: {stats['reconciliations']}")
print(f"Uptime: {stats['uptime_seconds']}s")
```

**Files Involved**:
- `packages/sutra-storage/src/tcp_server.rs` (line 546-566)
- `packages/sutra-storage/src/concurrent_memory.rs` (stats methods)

---

## Best Practices

### 1. Batch When Possible

```python
# ❌ Slow (N network calls + N embedding calls)
for content in contents:
    client.learn_concept(content)

# ✅ Fast (1 network call + 1 batch embedding call)
client.learn_batch_v2(contents)
```

### 2. Disable Embeddings for Metadata

```python
# Metadata concepts don't need vector search
user_id = client.learn_concept(
    content=f"User: {email}",
    generate_embedding=False,  # ← Faster
    extract_associations=False,
)
```

### 3. Control Association Extraction

```python
# High-value content: extract many associations
client.learn_concept(
    content=policy_text,
    max_associations_per_concept=20,
    min_association_confidence=0.4,
)

# Simple facts: fewer associations
client.learn_concept(
    content=simple_fact,
    max_associations_per_concept=5,
    min_association_confidence=0.7,
)
```

### 4. Use Bulk Ingester for Large Datasets

```bash
# CSV with 1M rows → Use bulk ingester (not API)
POST http://localhost:8005/ingest
{
  "source_type": "csv",
  "file_path": "/data/large_dataset.csv",
  "batch_size": 1000
}
```

---

## Summary Matrix

| Scenario | Entry Point | Throughput | Embeddings | Associations | Use Case |
|----------|-------------|------------|------------|--------------|----------|
| **1. Single Concept** | Python Client | Low | Yes | Yes | Interactive |
| **2. Batch** | Python Client | Medium | Yes (batched) | Yes | Bulk import |
| **3. Bulk Ingester** | HTTP Service | High | Yes | Yes | Large datasets |
| **4. Direct TCP** | Raw TCP | Low | Yes | Yes | Custom clients |
| **5. REST API** | HTTP | Low | Yes | Yes | Web apps |
| **6. Association Only** | Python Client | Very High | No | N/A | Graph building |
| **7. Cross-Shard** | Rust API | Very High | Yes | Yes | Enterprise scale |
| **8. Embedding Failure** | Any | Varies | Partial/None | Yes | Fault tolerance |
| **9. User/Session** | API Internal | Low | No | No | System metadata |
| **10. Space/Permission** | API Internal | Low | No | No | Multi-tenancy |

---

## Next: [Transactional Guarantees](./TRANSACTIONS.md)
