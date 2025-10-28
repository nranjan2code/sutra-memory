# Learning System Quick Reference

**Fast lookup guide for developers**

---

## Entry Points

| Method | Throughput | Use Case | Code |
|--------|-----------|----------|------|
| `learn_concept()` | ~33/sec | Interactive | `client.learn_concept(content)` |
| `learn_batch_v2()` | ~330/sec | Bulk | `client.learn_batch_v2(contents)` |
| `learn_association()` | ~100K/sec | Graph | `client.learn_association(src, tgt)` |
| Bulk Ingester | ~10K/sec | Datasets | `POST /ingest {file_path}` |
| REST API | ~33/sec | Web apps | `POST /learn {content}` |

---

## File Locations

### Core Learning
- **Pipeline**: `packages/sutra-storage/src/learning_pipeline.rs`
- **Embedding Client**: `packages/sutra-storage/src/embedding_client.rs`
- **Semantic Analyzer**: `packages/sutra-storage/src/semantic/analyzer.rs`
- **Association Extractor**: `packages/sutra-storage/src/semantic_extractor.rs`

### Storage
- **Concurrent Memory**: `packages/sutra-storage/src/concurrent_memory.rs`
- **Sharded Storage**: `packages/sutra-storage/src/sharded_storage.rs`
- **WAL**: `packages/sutra-storage/src/wal.rs`
- **2PC**: `packages/sutra-storage/src/transaction.rs`

### Clients
- **Python Adapter**: `packages/sutra-core/sutra_core/storage/tcp_adapter.py`
- **TCP Client**: `packages/sutra-storage-client-tcp/sutra_storage_client/`
- **REST API**: `packages/sutra-api/sutra_api/main.py`
- **Bulk Ingester**: `packages/sutra-bulk-ingester/src/`

---

## Common Patterns

### Single Concept
```python
from sutra_core.storage import TcpStorageAdapter

client = TcpStorageAdapter(server_address="localhost:50051")
concept_id = client.learn_concept("Your text here")
```

### Batch Learning
```python
concept_ids = client.learn_batch_v2([
    "Text 1",
    "Text 2",
    "Text 3",
])
```

### With Options
```python
concept_id = client.learn_concept(
    content="Text",
    generate_embedding=True,
    extract_associations=True,
    min_association_confidence=0.6,
    max_associations_per_concept=15,
)
```

### Association Only
```python
client.learn_association(
    source_id="concept_1",
    target_id="concept_2",
    association_type=AssociationType.CAUSAL,
    confidence=0.85
)
```

### Bulk Ingestion
```bash
curl -X POST http://localhost:8005/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "csv",
    "file_path": "/data/medical_facts.csv",
    "batch_size": 100
  }'
```

---

## Configuration

### Environment Variables
```bash
# Embedding Service
SUTRA_EMBEDDING_SERVICE_URL=http://localhost:8888
SUTRA_EMBEDDING_TIMEOUT_SEC=30

# Learning Options
SUTRA_MIN_ASSOCIATION_CONFIDENCE=0.5
SUTRA_MAX_ASSOCIATIONS_PER_CONCEPT=10
SUTRA_SEMANTIC_ANALYSIS=true

# Storage
SUTRA_STORAGE_PATH=./storage
SUTRA_MEMORY_THRESHOLD=50000
SUTRA_VECTOR_DIMENSION=768

# Sharding (Enterprise)
SUTRA_NUM_SHARDS=16

# WAL
SUTRA_WAL_FSYNC=true
SUTRA_WAL_ROTATION_SIZE=1GB

# 2PC
SUTRA_2PC_TIMEOUT_SEC=5

# Reconciler
SUTRA_RECONCILE_MIN_MS=10
SUTRA_RECONCILE_MAX_MS=5000
```

### LearnOptions
```rust
pub struct LearnOptions {
    pub generate_embedding: bool,               // Default: true
    pub embedding_model: Option<String>,        // Default: nomic-embed-text-v1.5
    pub extract_associations: bool,             // Default: true
    pub analyze_semantics: bool,                // Default: true
    pub min_association_confidence: f32,        // Default: 0.5
    pub max_associations_per_concept: usize,    // Default: 10
    pub strength: f32,                          // Default: 1.0
    pub confidence: f32,                        // Default: 1.0
}
```

---

## Performance Metrics

| Operation | Throughput | Latency | Bottleneck |
|-----------|-----------|---------|------------|
| Single learn | 33/sec | 30ms | Embedding |
| Batch (10) | 330/sec | 3ms/concept | Network |
| Batch (100) | 3,300/sec | 0.3ms/concept | Storage |
| Bulk ingester | 10,000/sec | Streaming | Parsing |
| Association | 100,000/sec | 0.1ms | None |
| Cross-shard | 57,000/sec | <0.01ms | 2PC |

### Optimization Tips
1. **Batch when possible** (10× speedup)
2. **Disable embeddings for metadata** (faster)
3. **Tune association limits** (quality vs speed)
4. **Use bulk ingester for large datasets**
5. **Shard by domain** (minimize cross-shard)

---

## Semantic Types

```rust
pub enum SemanticType {
    Rule,          // Policy, requirement, obligation
    Event,         // Action, occurrence, state
    Entity,        // Object, concept, person
    Temporal,      // Time-based relationship
    Causal,        // Cause-effect
    Condition,     // If-then logic
    Negation,      // Exception, prohibition
    Quantitative,  // Number, measurement
    Definitional,  // Explanation, classification
    Unknown,       // Fallback
}
```

### Domain Contexts
```rust
pub enum DomainContext {
    Medical,    // diagnosis, treatment, symptoms
    Legal,      // statute, regulation, compliance
    Financial,  // investment, revenue, portfolio
    Technical,  // system, API, architecture
    Scientific, // hypothesis, research, analysis
    Business,   // strategy, operations, stakeholder
    Unknown,    // Generic
}
```

### Association Types
```rust
pub enum AssociationType {
    Semantic = 0,        // Type-of, instance-of
    Causal = 1,          // Causes, leads-to
    Temporal = 2,        // Before, after
    Hierarchical = 3,    // Parent-of, child-of
    Compositional = 4,   // Part-of, contains
}
```

---

## ACID Guarantees

| Property | Mechanism | File |
|----------|-----------|------|
| **Atomicity** | WAL + 2PC | `wal.rs`, `transaction.rs` |
| **Consistency** | Invariant checks | `concurrent_memory.rs` |
| **Isolation** | Immutable snapshots | `read_view.rs` |
| **Durability** | WAL + fsync | `wal.rs` |

### Recovery
```rust
// Automatic on restart
ConcurrentMemory::new(config)
  → WAL.replay()
  → Reconstruct state
  → Resume operations
```

---

## Error Handling

### Common Errors
```python
# Embedding failure → Continues without embedding
# Warning logged, no exception

# Content too large → Error
# MAX_CONTENT_SIZE = 10MB

# Embedding dimension too large → Error
# MAX_EMBEDDING_DIM = 2048

# Association to non-existent concept → Error

# Disk full → Error (WAL append fails)

# 2PC timeout → Error (transaction aborted)
```

### Retry Logic
```python
# Built into TcpStorageAdapter
# - 3 automatic retries
# - Exponential backoff (500ms, 1s, 2s)
# - Connection pool management
```

---

## Testing

### Unit Tests
```bash
# Rust tests
cd packages/sutra-storage && cargo test

# Python tests
PYTHONPATH=packages/sutra-core python -m pytest tests/
```

### Integration Tests
```bash
# Full pipeline test
pytest tests/test_unified_learning_integration.py

# Embedding service test
./scripts/smoke-test-embeddings.sh

# WAL recovery test
pytest tests/test_wal_recovery.py
```

---

## Monitoring

### Storage Stats
```python
stats = client.stats()

print(f"Concepts: {stats['concepts']}")
print(f"Edges: {stats['edges']}")
print(f"Vectors: {stats['vectors']}")
print(f"WAL written: {stats['written']}")
print(f"WAL dropped: {stats['dropped']}")
print(f"Reconciliations: {stats['reconciliations']}")
print(f"Uptime: {stats['uptime_seconds']}s")
```

### Health Check
```python
# Storage server
response = requests.get("http://localhost:50051/health")

# Embedding service
response = requests.get("http://localhost:8888/health")

# API
response = requests.get("http://localhost:8000/health")
```

---

## Troubleshooting

### Issue: Embeddings failing
**Solution**: Check HA service health
```bash
curl http://localhost:8888/health
docker logs sutra-embedding-service
```

### Issue: Slow learning
**Solution**: Use batch operations
```python
# Instead of
for content in contents:
    client.learn_concept(content)

# Do
client.learn_batch_v2(contents)
```

### Issue: High memory usage
**Solution**: Reduce memory threshold
```bash
SUTRA_MEMORY_THRESHOLD=25000
```

### Issue: WAL growing too large
**Solution**: Configure rotation
```bash
SUTRA_WAL_ROTATION_SIZE=500MB
```

### Issue: Cross-shard timeouts
**Solution**: Increase timeout or shard by domain
```bash
SUTRA_2PC_TIMEOUT_SEC=10
```

---

## Architecture Diagrams

### Learning Pipeline
```
Content → Embedding → Semantic Analysis → Association Extraction → Storage
  ↓         ↓              ↓                      ↓                  ↓
 Text    768-dim        Rule/Event            Entities          WAL + Graph
                       Medical                Causal             + HNSW
```

### Storage Layers
```
Write Log (mutable) → Reconciler → Read View (immutable)
     ↓                                    ↓
   WAL (durability)               HNSW (search)
                                 Graph (traversal)
```

### Sharded Architecture
```
Concept → Hash → Shard ID
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
   Shard 0                 Shard 1
   (WAL + HNSW)           (WAL + HNSW)
        ↓                       ↓
        └───────────┬───────────┘
                    ↓
            2PC Coordinator
```

---

## Best Practices

1. ✅ **Batch operations when possible**
2. ✅ **Disable embeddings for metadata concepts**
3. ✅ **Set appropriate association limits**
4. ✅ **Use bulk ingester for large datasets**
5. ✅ **Monitor WAL dropped count** (should be 0)
6. ✅ **Enable fsync for production** (durability)
7. ✅ **Shard by domain** (minimize cross-shard)
8. ✅ **Test recovery scenarios**

---

## Further Reading

- **[Learning Architecture](./ARCHITECTURE.md)** - System design
- **[Learning Scenarios](./SCENARIOS.md)** - All entry points
- **[Transactional Guarantees](./TRANSACTIONS.md)** - ACID details
- **[TCP Protocol Spec](../storage/TCP_BINARY_PROTOCOL.md)** - Protocol details
- **[Storage Architecture](../architecture/STORAGE_ENGINE.md)** - Storage internals

---

**Last Updated**: 2025-10-28  
**Version**: 2.0.0
