# Sutra Storage Self-Learning System

**Complete documentation of how sutra-storage learns from data**

---

## Overview

Sutra Storage is a **self-contained learning system** that ingests raw text, automatically extracts knowledge, and builds an explainable concept graph—all without requiring external preprocessing or training. Unlike traditional ML systems that need labeled datasets and model training, Sutra learns in real-time from every piece of data it receives.

### Key Characteristics

- **Zero External Dependencies**: All learning happens inside the storage server
- **Real-Time Learning**: No batch training cycles—concepts are immediately queryable
- **Explainable**: Every learned fact has a traceable audit trail
- **Transactional**: ACID guarantees via Write-Ahead Log (WAL) and 2-Phase Commit (2PC)
- **High Performance**: 57,000 concepts/second write throughput
- **Distributed**: Scales to 10M+ concepts across 16 shards

---

## Documentation Structure

1. **[What Happens By Text Size](./WHAT_HAPPENS_BY_TEXT_SIZE.md)** - 🎯 **START HERE** - Edition-by-edition behavior
2. **[Continuous Learning](./CONTINUOUS_LEARNING.md)** - 🔄 Re-feeding data, updates, duplicates, validation
3. **[Negation Scope Analysis](./NEGATION_SCOPE.md)** - ❌ What negation detection does (and doesn't do)
4. **[Visual Learning Guide](./VISUAL_LEARNING_GUIDE.md)** - 📊 How text gets structured with diagrams
5. **[Learning Architecture](./ARCHITECTURE.md)** - System design and data flow
6. **[Learning Scenarios](./SCENARIOS.md)** - All ways data enters the system
7. **[Natural Language Scenarios](./NATURAL_LANGUAGE_SCENARIOS.md)** - Real-world text processing examples
8. **[Transactional Guarantees](./TRANSACTIONS.md)** - Durability and consistency
9. **[Quick Reference](./QUICK_REFERENCE.md)** - Developer cheat sheet

---

## Quick Start

### Single Concept Learning

```rust
// Storage server learns a concept end-to-end
let pipeline = LearningPipeline::new().await?;
let storage = ConcurrentMemory::new(config);

let concept_id = pipeline.learn_concept(
    &storage,
    "Diabetes requires regular blood glucose monitoring.",
    &LearnOptions::default(),
).await?;

// System automatically:
// 1. Generated 768-dimensional embedding
// 2. Extracted semantic associations
// 3. Classified semantic type (Rule)
// 4. Detected domain (Medical)
// 5. Stored in HNSW index
// 6. Logged to WAL for durability
```

### Batch Learning

```rust
let medical_facts = vec![
    "High cholesterol increases heart disease risk.".to_string(),
    "Regular exercise improves insulin sensitivity.".to_string(),
    "Mediterranean diet reduces inflammation markers.".to_string(),
];

let concept_ids = pipeline.learn_batch(
    &storage,
    &medical_facts,
    &LearnOptions::default(),
).await?;

// Batch processing uses:
// - Single embedding API call (10× faster)
// - Parallel semantic analysis
// - Parallel association extraction
// - Parallel storage operations
```

---

## Learning Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATA INPUT SOURCES                          │
├─────────────────────────────────────────────────────────────────┤
│  • REST API (/learn, /learn/batch)                              │
│  • TCP Protocol (LearnConceptV2, LearnBatch)                    │
│  • Bulk Ingester (CSV, JSON, Parquet)                           │
│  • Python Client (TcpStorageAdapter)                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              UNIFIED LEARNING PIPELINE (Rust)                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. EMBEDDING GENERATION (HA Service)                    │   │
│  │    - nomic-embed-text-v1.5 (768-dim)                    │   │
│  │    - Batch optimization (10× faster)                    │   │
│  │    - L2 normalization                                   │   │
│  │    - Automatic retry with backoff                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 2. SEMANTIC ANALYSIS (Deterministic)                    │   │
│  │    - Type classification (Rule/Event/Entity/etc)        │   │
│  │    - Domain detection (Medical/Legal/Financial)         │   │
│  │    - Temporal extraction (dates, sequences)             │   │
│  │    - Causal relation detection                          │   │
│  │    - Negation scope analysis                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 3. ASSOCIATION EXTRACTION (Embedding-Based)             │   │
│  │    - Sentence segmentation                              │   │
│  │    - Relation type classification                       │   │
│  │    - Entity extraction (capitalization heuristics)      │   │
│  │    - Confidence scoring                                 │   │
│  │    - Types: Semantic, Causal, Temporal, Hierarchical   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 4. CONCEPT ID GENERATION                                │   │
│  │    - Deterministic hash (DefaultHasher)                 │   │
│  │    - Content-based (same text = same ID)                │   │
│  │    - 16-character hex string                            │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER (ACID)                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ A. Write-Ahead Log (WAL)                                │   │
│  │    - Every operation logged before execution            │   │
│  │    - Fsync for durability                               │   │
│  │    - Crash recovery via replay                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ B. Concurrent Memory (Write/Read Planes)                │   │
│  │    - Write Log: lock-free append-only                   │   │
│  │    - Read View: immutable snapshots                     │   │
│  │    - Adaptive Reconciler: background merging            │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ C. HNSW Vector Index (USearch)                          │   │
│  │    - 768-dimensional search                             │   │
│  │    - Persistent mmap (94× faster startup)               │   │
│  │    - <0.01ms query latency                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ D. Graph Storage (Concept Nodes + Associations)         │   │
│  │    - Content + Metadata + Semantic Classification       │   │
│  │    - Typed edges with confidence scores                 │   │
│  │    - BFS/DFS pathfinding with semantic filters          │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              SHARDED DISTRIBUTION (Enterprise)                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Consistent hashing (16 shards)                        │   │
│  │ • Per-shard WAL + HNSW                                  │   │
│  │ • 2-Phase Commit for cross-shard associations           │   │
│  │ • Parallel query execution                              │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Principles

### 1. **Unified Learning Pipeline**

All data ingestion routes through a single Rust-based learning pipeline. There are no alternative paths—whether data comes from REST API, TCP protocol, or bulk ingester, it flows through the same processing stages.

**Location**: `packages/sutra-storage/src/learning_pipeline.rs`

### 2. **Server-Side Processing**

Clients send raw text; the storage server handles:
- Embedding generation (via HA embedding service)
- Semantic analysis (deterministic pattern matching)
- Association extraction (embedding-based NLP)
- Persistence (HNSW + graph + WAL)

Clients don't need ML libraries or preprocessing logic.

### 3. **Transactional Guarantees**

Every learning operation is:
- **Atomic**: All-or-nothing (WAL ensures this)
- **Consistent**: Semantic constraints enforced
- **Isolated**: Transactions don't interfere
- **Durable**: Survives crashes (WAL + fsync)

### 4. **Semantic Understanding**

The system doesn't just store text—it understands:
- **Type**: Is this a rule, event, entity, or definition?
- **Domain**: Medical, legal, financial, technical?
- **Temporality**: When did/will this happen?
- **Causality**: What causes what?
- **Negation**: What is explicitly denied?

This enables domain-specific reasoning impossible with generic vector stores.

### 5. **Explainability First**

Every learned concept has:
- Original content (verbatim)
- Source metadata (where it came from)
- Semantic classification (how it was interpreted)
- Association confidence (why connections were made)
- Timestamp (when it was learned)

No "black box" transformations.

---

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| **Write Throughput** | 57,000 concepts/sec | Single shard, batch mode |
| **Read Latency** | <0.01ms | Zero-copy mmap reads |
| **Embedding Generation** | ~30ms/concept | With HA service (3 replicas) |
| **Batch Embedding** | ~3ms/concept | 10× faster via batching |
| **Association Extraction** | ~20ms/concept | Semantic extractor |
| **HNSW Startup** | 3.5ms | 1M vectors (persistent mmap) |
| **Memory Overhead** | ~0.1KB/concept | Excluding embeddings |
| **Max Scale** | 10M+ concepts | 16 shards |

---

## Next Steps

1. Read **[Learning Architecture](./ARCHITECTURE.md)** for system design
2. Review **[Learning Scenarios](./SCENARIOS.md)** for integration patterns
3. Check **[Performance Analysis](./PERFORMANCE.md)** for optimization tips

---

**Built by the Sutra AI Team**  
*Domain-Specific Explainable AI for Regulated Industries*
