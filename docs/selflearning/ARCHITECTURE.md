# Learning Architecture

**System design and component interactions for self-learning**

---

## Overview

Sutra Storage's learning architecture is built on three core principles:

1. **Unified Pipeline**: Single code path for all learning operations
2. **Server-Side Intelligence**: Clients send raw text; server does the heavy lifting
3. **Transactional Storage**: ACID guarantees via WAL and 2PC

---

## Architecture Layers

### Layer 1: Data Ingestion (Entry Points)

Multiple interfaces, single pipeline:

```
┌──────────────────────────────────────────────────────────────────┐
│                    DATA INGESTION LAYER                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   REST API      │  │  TCP Protocol   │  │  Bulk Ingester  │ │
│  │  (FastAPI)      │  │   (Binary)      │  │     (Rust)      │ │
│  │                 │  │                 │  │                 │ │
│  │ /learn          │  │ LearnConceptV2  │  │ CSV/JSON        │ │
│  │ /learn/batch    │  │ LearnBatch      │  │ Parquet         │ │
│  │                 │  │                 │  │ Plugins         │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                    │                     │          │
│           └────────────────────┼─────────────────────┘          │
│                                │                                │
└────────────────────────────────┼────────────────────────────────┘
                                 │
                                 ▼
                   ┌──────────────────────────┐
                   │  TcpStorageAdapter       │
                   │  (Python Client)         │
                   │                          │
                   │  learn_concept_v2()      │
                   │  learn_batch_v2()        │
                   └──────────┬───────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │  StorageClient           │
                   │  (TCP Binary Protocol)   │
                   │                          │
                   │  MessagePack serialized  │
                   └──────────┬───────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │  TCP Server              │
                   │  (Rust - Port 50051)     │
                   │                          │
                   │  handle_request()        │
                   └──────────┬───────────────┘
                              │
                              ▼
                     [UNIFIED PIPELINE]
```

**File Locations**:
- REST API: `packages/sutra-api/sutra_api/main.py`
- TCP Protocol: `packages/sutra-storage/src/tcp_server.rs`
- Bulk Ingester: `packages/sutra-bulk-ingester/src/`
- Python Client: `packages/sutra-core/sutra_core/storage/tcp_adapter.py`
- Storage Client: `packages/sutra-storage-client-tcp/sutra_storage_client/`

---

### Layer 2: Learning Pipeline (Core Processing)

**Location**: `packages/sutra-storage/src/learning_pipeline.rs` (256 lines)

```rust
pub struct LearningPipeline {
    embedding_client: EmbeddingClient,        // HA service integration
    semantic_extractor: SemanticExtractor,    // Association extraction
    semantic_analyzer: SemanticAnalyzer,      // Type classification
}

impl LearningPipeline {
    /// Learn a single concept end-to-end
    pub async fn learn_concept<S: LearningStorage>(
        &self,
        storage: &S,
        content: &str,
        options: &LearnOptions,
    ) -> Result<String> {
        // Step 1: Generate embedding (async - HA service call)
        let embedding_opt = if options.generate_embedding {
            self.embedding_client.generate(content, true).await.ok()
        } else { None };

        // Step 2: Generate deterministic concept ID
        let concept_id = self.generate_concept_id(content);
        let id = ConceptId::from_string(&concept_id);

        // Step 3: Analyze semantics (synchronous - pattern matching)
        let semantic = if options.analyze_semantics {
            Some(self.semantic_analyzer.analyze(content))
        } else { None };

        // Step 4: Store concept with semantic metadata
        let sequence = if let Some(semantic_meta) = semantic {
            storage.learn_concept_with_semantic(
                id, content.as_bytes().to_vec(),
                embedding_opt.clone(),
                options.strength, options.confidence,
                semantic_meta,
            )?
        } else {
            storage.learn_concept(
                id, content.as_bytes().to_vec(),
                embedding_opt.clone(),
                options.strength, options.confidence,
            )?
        };

        // Step 5: Extract and store associations (async - embeddings)
        if options.extract_associations {
            let extracted = self.semantic_extractor.extract(content).await?;
            
            for assoc in extracted.into_iter()
                .take(options.max_associations_per_concept) {
                
                if assoc.confidence >= options.min_association_confidence {
                    let target_id_hex = self.generate_concept_id(&assoc.target);
                    let target_id = ConceptId::from_string(&target_id_hex);
                    
                    storage.learn_association(
                        id, target_id, 
                        assoc.assoc_type, assoc.confidence
                    )?;
                }
            }
        }

        Ok(concept_id)
    }

    /// Batch learning with optimizations
    pub async fn learn_batch<S: LearningStorage>(
        &self,
        storage: &S,
        contents: &[String],
        options: &LearnOptions,
    ) -> Result<Vec<String>> {
        // Batch embeddings (single API call - 10× faster)
        let embeddings = if options.generate_embedding {
            self.embedding_client.generate_batch(contents, true).await
        } else {
            vec![None; contents.len()]
        };

        let mut concept_ids = Vec::with_capacity(contents.len());
        
        // Process each concept with pre-computed embedding
        for (content, embedding_opt) in contents.iter().zip(embeddings) {
            // Same logic as learn_concept but with pre-computed embedding
            // ...
        }

        Ok(concept_ids)
    }
}
```

**Key Design Decisions**:

1. **Async Boundaries**: Only embedding generation is async; semantic analysis and storage are sync
2. **Batch Optimization**: Single embedding API call for entire batch (10× speedup)
3. **Trait-Based Storage**: Works with both `ConcurrentMemory` and `ShardedStorage`
4. **Configurable Options**: Enable/disable embedding, associations, semantic analysis

---

### Layer 3: Embedding Generation (HA Service)

**Location**: `packages/sutra-storage/src/embedding_client.rs` (298 lines)

```rust
pub struct EmbeddingClient {
    config: EmbeddingConfig,  // Service URL, timeout, retries
    client: reqwest::Client,  // HTTP client
}

impl EmbeddingClient {
    /// Generate single embedding
    pub async fn generate(&self, text: &str, normalize: bool) -> Result<Vec<f32>> {
        let embeddings = self.generate_batch(&[text.to_string()], normalize).await;
        embeddings.into_iter().next().flatten()
            .ok_or_else(|| anyhow!("No embedding returned"))
    }

    /// Batch embedding generation (production-grade)
    pub async fn generate_batch(
        &self,
        texts: &[String],
        normalize: bool,
    ) -> Vec<Option<Vec<f32>>> {
        let mut last_error = None;
        
        // Retry loop with exponential backoff
        for attempt in 0..=self.config.max_retries {
            match self.try_generate_batch(texts, normalize).await {
                Ok(embeddings) => return embeddings.into_iter().map(Some).collect(),
                Err(e) => {
                    last_error = Some(e);
                    if attempt < self.config.max_retries {
                        let delay = Duration::from_millis(
                            self.config.retry_delay_ms * (2_u64.pow(attempt as u32))
                        );
                        tokio::time::sleep(delay).await;
                    }
                }
            }
        }
        
        // Return None for all texts on complete failure
        vec![None; texts.len()]
    }
}
```

**HA Embedding Service Architecture**:

```
┌────────────────────────────────────────────────────────────────┐
│                    HA EMBEDDING SERVICE                         │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                   HAProxy (:8888)                        │ │
│  │                 Load Balancer                            │ │
│  │                                                          │ │
│  │  • Round-robin distribution                             │ │
│  │  • Health checks every 30s                              │ │
│  │  • Automatic failover                                   │ │
│  └──────────────────┬──────────────────┬──────────────────┬─┘ │
│                     │                  │                  │   │
│                     ▼                  ▼                  ▼   │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────┐ │
│  │  Embedding Replica 1 │  │  Embedding Replica 2 │  │  ... │ │
│  │     (:8889)          │  │     (:8890)          │  │      │ │
│  │                      │  │                      │  │      │ │
│  │ nomic-embed-text-v1.5│  │ nomic-embed-text-v1.5│  │      │ │
│  │  (768 dimensions)    │  │  (768 dimensions)    │  │      │ │
│  │  LRU cache (1000)    │  │  LRU cache (1000)    │  │      │ │
│  └──────────────────────┘  └──────────────────────┘  └──────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Performance**:
- Single embedding: ~30ms
- Batch (10 texts): ~3ms per text (10× speedup)
- Cache hit: <1ms
- Model: nomic-embed-text-v1.5 (768-dim)

---

### Layer 4: Semantic Analysis (Deterministic)

**Location**: `packages/sutra-storage/src/semantic/analyzer.rs` (459 lines)

```rust
pub struct SemanticAnalyzer {
    custom_patterns: HashMap<DomainContext, Vec<Regex>>,
}

impl SemanticAnalyzer {
    pub fn analyze(&self, text: &str) -> SemanticMetadata {
        SemanticMetadata {
            semantic_type: self.classify_type(text),        // Rule/Event/Entity/etc
            temporal_bounds: self.extract_temporal(text),   // Dates, sequences
            causal_relations: self.extract_causal(text),    // Cause-effect
            domain_context: self.detect_domain(text),       // Medical/Legal/etc
            negation_scope: self.extract_negation(text),    // Exceptions
            classification_confidence: self.calculate_confidence(text),
        }
    }

    fn classify_type(&self, text: &str) -> SemanticType {
        let mut scores: HashMap<SemanticType, f32> = HashMap::new();
        
        // Rule patterns (highest priority)
        if PATTERNS.rule_modal.is_match(text) {
            *scores.entry(SemanticType::Rule).or_insert(0.0) += 3.0;
        }
        
        // Temporal patterns
        if PATTERNS.temporal_after.is_match(text) {
            *scores.entry(SemanticType::Temporal).or_insert(0.0) += 2.0;
        }
        
        // Causal patterns
        if PATTERNS.causal_direct.is_match(text) {
            *scores.entry(SemanticType::Causal).or_insert(0.0) += 2.5;
        }
        
        // Return type with highest score
        scores.into_iter()
            .max_by(|a, b| a.1.partial_cmp(&b.1).unwrap())
            .map(|(t, _)| t)
            .unwrap_or(SemanticType::Unknown)
    }
}
```

**Semantic Types**:
- `Rule`: Policy statements, requirements, obligations
- `Event`: Actions, occurrences, states
- `Entity`: Objects, concepts, people
- `Temporal`: Time-based relationships
- `Causal`: Cause-effect relationships
- `Condition`: If-then logic
- `Negation`: Exceptions, prohibitions
- `Quantitative`: Numbers, measurements
- `Definitional`: Explanations, classifications

**Domain Contexts**:
- Medical (diagnosis, treatment, symptoms)
- Legal (statute, regulation, compliance)
- Financial (investment, revenue, portfolio)
- Technical (system, API, architecture)
- Scientific (hypothesis, research, analysis)
- Business (strategy, operations, stakeholder)

---

### Layer 5: Association Extraction (Embedding-Based)

**Location**: `packages/sutra-storage/src/semantic_extractor.rs` (380 lines)

```rust
pub struct SemanticExtractor {
    embedding_client: EmbeddingClient,
    relation_embeddings: HashMap<AssociationType, Vec<f32>>,
    similarity_threshold: f32,
    min_entity_length: usize,
}

impl SemanticExtractor {
    /// Extract associations from text
    pub async fn extract(&self, text: &str) -> Result<Vec<SemanticAssociation>> {
        // Step 1: Split into sentences
        let sentences = self.split_sentences(text);
        
        // Step 2: Batch embed all sentences
        let sentence_embeddings = self.embedding_client
            .generate_batch(&sentences, true).await;
        
        // Step 3: Process each sentence
        let mut associations = Vec::new();
        
        for (sentence, emb_opt) in sentences.iter().zip(sentence_embeddings) {
            if let Some(emb) = emb_opt {
                // Classify relation type by cosine similarity
                let (assoc_type, confidence) = self.classify_relation(&emb);
                
                if confidence >= self.similarity_threshold {
                    // Extract entities from sentence
                    let entities = self.extract_entities(sentence);
                    
                    // Create associations (first entity is subject)
                    for target in &entities[1..] {
                        associations.push(SemanticAssociation {
                            target: target.clone(),
                            assoc_type,
                            confidence,
                        });
                    }
                }
            }
        }
        
        Ok(associations)
    }

    /// Classify relation type by similarity to pre-computed embeddings
    fn classify_relation(&self, sentence_embedding: &[f32]) -> (AssociationType, f32) {
        let mut best_match = (AssociationType::Semantic, 0.0);
        
        for (rel_type, rel_embedding) in &self.relation_embeddings {
            let similarity = cosine_similarity(sentence_embedding, rel_embedding);
            if similarity > best_match.1 {
                best_match = (*rel_type, similarity);
            }
        }
        
        best_match
    }

    /// Extract entities using capitalization heuristics
    fn extract_entities(&self, sentence: &str) -> Vec<String> {
        // Capitalized words = entities
        // Multi-word phrases preserved
        // Punctuation cleaned
        // Minimum length enforced
    }
}
```

**Association Types**:
- `Semantic`: Type-of, instance-of, category relationships
- `Causal`: Causes, leads-to, results-in
- `Temporal`: Before, after, during, while
- `Hierarchical`: Parent-of, child-of, subclass
- `Compositional`: Part-of, contains, consists-of

**Relation Type Embeddings** (pre-computed):
```rust
let relation_descriptions = vec![
    (AssociationType::Semantic,
     "is a type of, is an example of, belongs to category"),
    (AssociationType::Causal,
     "causes, leads to, results in, triggers, produces"),
    (AssociationType::Temporal,
     "happens before, occurs after, during, while, when"),
    // ... etc
];
```

---

### Layer 6: Storage Layer (ACID Transactions)

**Location**: `packages/sutra-storage/src/concurrent_memory.rs` (1142 lines)

```rust
pub struct ConcurrentMemory {
    write_log: Arc<WriteLog>,              // Lock-free append-only
    read_view: Arc<ReadView>,              // Immutable snapshots
    reconciler: AdaptiveReconciler,        // Background merging
    hnsw_container: Arc<HnswContainer>,    // Persistent HNSW
    wal: Arc<Mutex<WriteAheadLog>>,        // Durability
    config: ConcurrentConfig,
}

impl ConcurrentMemory {
    pub fn learn_concept(
        &self,
        id: ConceptId,
        content: Vec<u8>,
        vector: Option<Vec<f32>>,
        strength: f32,
        confidence: f32,
    ) -> Result<u64> {
        // 1. Write-Ahead Log (durability)
        let wal_op = Operation::WriteConcept {
            concept_id: id,
            content_len: content.len() as u32,
            vector_len: vector.as_ref().map(|v| v.len() as u32).unwrap_or(0),
            created: now_micros(),
            modified: now_micros(),
        };
        let sequence = self.wal.lock().append(wal_op)?;

        // 2. Append to write log (never blocks)
        self.write_log.append_concept(id, content.clone(), strength, confidence)?;

        // 3. Store vector in HNSW (if provided)
        if let Some(vec) = vector {
            self.vectors.write().insert(id, vec.clone());
            self.hnsw_container.add_vector(id, &vec)?;
        }

        // 4. Background reconciler will merge to read view
        Ok(sequence)
    }
}
```

**Storage Architecture**:

```
┌──────────────────────────────────────────────────────────────────┐
│                     CONCURRENT MEMORY                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Write-Ahead Log (WAL)                                     │ │
│  │  • Every operation logged before execution                 │ │
│  │  • Fsync for durability                                    │ │
│  │  • Replay on crash recovery                                │ │
│  │  File: storage_path/wal.log                                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Write Log (Append-Only)                                   │ │
│  │  • Lock-free circular buffer                               │ │
│  │  • Never blocks writes                                     │ │
│  │  • Bursts handled gracefully                               │ │
│  │  • Dropped on overflow (stats tracked)                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Adaptive Reconciler (Background Thread)                   │ │
│  │  • Merges write log → read view                            │ │
│  │  • Dynamic interval (10ms to 5s)                           │ │
│  │  • Load-aware throttling                                   │ │
│  │  • Metrics: reconciliations, latency, throughput           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Read View (Immutable Snapshot)                            │ │
│  │  • HashMap<ConceptId, ConceptNode>                         │ │
│  │  • Adjacency lists for graph traversal                     │ │
│  │  • Zero-copy reads (no locks)                              │ │
│  │  • Replaced atomically by reconciler                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  HNSW Container (USearch)                                  │ │
│  │  • 768-dimensional vector index                            │ │
│  │  • Persistent mmap (94× faster startup)                    │ │
│  │  • <0.01ms query latency                                   │ │
│  │  • Automatic index building                                │ │
│  │  File: storage_path/hnsw.usearch                           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

### Layer 7: Sharded Distribution (Enterprise)

**Location**: `packages/sutra-storage/src/sharded_storage.rs` (416 lines)

```rust
pub struct ShardedStorage {
    config: ShardConfig,
    shards: Vec<Arc<ConcurrentMemory>>,      // 16 shards default
    shard_map: Arc<RwLock<ShardMap>>,
    txn_coordinator: Arc<TransactionCoordinator>,  // 2PC
}

impl ShardedStorage {
    /// Get shard ID via consistent hashing
    fn get_shard_id(&self, concept_id: ConceptId) -> u32 {
        let mut hasher = DefaultHasher::new();
        concept_id.0.hash(&mut hasher);
        let hash = hasher.finish();
        (hash % self.config.num_shards as u64) as u32
    }

    /// Learn concept (routed to correct shard)
    pub fn learn_concept(
        &self,
        id: ConceptId,
        content: Vec<u8>,
        vector: Option<Vec<f32>>,
        strength: f32,
        confidence: f32,
    ) -> Result<u64> {
        let shard = self.get_shard(id);
        shard.learn_concept(id, content, vector, strength, confidence)
    }

    /// Create association with 2PC for cross-shard atomicity
    pub fn create_association(
        &self,
        source: ConceptId,
        target: ConceptId,
        assoc_type: AssociationType,
        strength: f32,
    ) -> Result<u64> {
        let source_shard_id = self.get_shard_id(source);
        let target_shard_id = self.get_shard_id(target);
        
        // Fast path: Same shard (no 2PC needed)
        if source_shard_id == target_shard_id {
            let shard = &self.shards[source_shard_id as usize];
            return shard.create_association(source, target, assoc_type, strength);
        }
        
        // Cross-shard: Use 2-Phase Commit
        let txn_id = self.txn_coordinator.begin(TxnOperation::CreateAssociation {
            source, target, source_shard: source_shard_id,
            target_shard: target_shard_id, assoc_type, strength,
        });
        
        // Phase 1: Prepare both shards
        let source_shard = &self.shards[source_shard_id as usize];
        let target_shard = &self.shards[target_shard_id as usize];
        
        source_shard.create_association(source, target, assoc_type, strength)?;
        self.txn_coordinator.mark_prepared(txn_id, source_shard_id)?;
        
        target_shard.create_association(target, source, assoc_type, strength)?;
        self.txn_coordinator.mark_prepared(txn_id, target_shard_id)?;
        
        // Phase 2: Commit if all prepared
        if self.txn_coordinator.is_ready_to_commit(txn_id)? {
            self.txn_coordinator.commit(txn_id)?;
            self.txn_coordinator.complete(txn_id);
            Ok(sequence)
        } else {
            self.txn_coordinator.abort(txn_id)?;
            Err(anyhow!("2PC transaction aborted"))
        }
    }
}
```

**Sharding Architecture**:

```
┌──────────────────────────────────────────────────────────────────┐
│                   SHARDED STORAGE (16 Shards)                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐    │
│  │  Shard 0  │  │  Shard 1  │  │  Shard 2  │  │    ...    │    │
│  │           │  │           │  │           │  │           │    │
│  │  Own WAL  │  │  Own WAL  │  │  Own WAL  │  │  Own WAL  │    │
│  │  Own HNSW │  │  Own HNSW │  │  Own HNSW │  │  Own HNSW │    │
│  │  Own Graph│  │  Own Graph│  │  Own Graph│  │  Own Graph│    │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘    │
│        │              │              │              │            │
│        └──────────────┴──────────────┴──────────────┘            │
│                             │                                     │
│                             ▼                                     │
│          ┌─────────────────────────────────────┐                 │
│          │   2PC Transaction Coordinator       │                 │
│          │   • Cross-shard atomicity           │                 │
│          │   • 5-second timeout                │                 │
│          │   • Prepare → Commit/Abort          │                 │
│          └─────────────────────────────────────┘                 │
│                                                                   │
│  Consistent Hashing:                                              │
│  • Hash(concept_id) % 16 = shard_id                              │
│  • Even distribution                                              │
│  • Parallel query execution                                       │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Example

### Single Concept Learning

```
User: "Diabetes requires regular blood glucose monitoring."

1. REST API receives POST /learn
   ↓
2. TcpStorageAdapter.learn_concept()
   ↓
3. TCP Binary Protocol: LearnConceptV2 message
   ↓
4. tcp_server.rs handles request
   ↓
5. LearningPipeline.learn_concept()
   ├─ EmbeddingClient.generate() → [768-dim vector]
   ├─ SemanticAnalyzer.analyze()
   │  ├─ Type: Rule (modal "requires")
   │  ├─ Domain: Medical ("Diabetes", "glucose")
   │  └─ Confidence: 0.92
   ├─ SemanticExtractor.extract()
   │  ├─ Sentence: "Diabetes requires ... monitoring"
   │  ├─ Entities: ["Diabetes", "blood glucose monitoring"]
   │  ├─ Relation: Semantic (type-of)
   │  └─ Confidence: 0.78
   └─ generate_concept_id() → "a3f2c8d1e4b6f9a2"
   ↓
6. ConcurrentMemory.learn_concept()
   ├─ WAL.append(WriteConcept) → seq#1234
   ├─ WriteLog.append_concept() → buffered
   ├─ HNSW.add_vector() → indexed
   └─ return sequence: 1234
   ↓
7. SemanticExtractor associations:
   ├─ learn_association(a3f2c8d1, target_id, Semantic, 0.78)
   └─ WAL.append(WriteAssociation) → seq#1235
   ↓
8. TCP response: LearnConceptV2Ok { concept_id: "a3f2c8d1e4b6f9a2" }
   ↓
9. REST API returns: { "concept_id": "a3f2c8d1...", "associations": 1 }

Background:
- AdaptiveReconciler merges WriteLog → ReadView (every 10ms)
- HNSW builds graph connections
- WAL syncs to disk (fsync)
```

---

## Key Invariants

1. **All learning flows through LearningPipeline**: No backdoors or alternative paths
2. **WAL before execution**: Every operation logged before applied
3. **Deterministic IDs**: Same content always generates same concept ID
4. **Immutable reads**: Read view never modified (replaced atomically)
5. **Bounded retries**: Embedding failures don't block indefinitely
6. **Semantic metadata always computed**: Even if embeddings fail

---

## Component Dependencies

```
LearningPipeline
├─ EmbeddingClient (HA Service)
│  └─ reqwest::Client
├─ SemanticExtractor
│  └─ EmbeddingClient (relation embeddings)
├─ SemanticAnalyzer
│  └─ regex::Regex (compiled patterns)
└─ LearningStorage trait
   ├─ ConcurrentMemory
   │  ├─ WriteLog
   │  ├─ ReadView
   │  ├─ AdaptiveReconciler
   │  ├─ HnswContainer (USearch)
   │  └─ WriteAheadLog
   └─ ShardedStorage
      ├─ Vec<ConcurrentMemory>
      └─ TransactionCoordinator (2PC)
```

---

## Configuration

### Learning Options

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

### Environment Variables

```bash
# Embedding service
SUTRA_EMBEDDING_SERVICE_URL=http://localhost:8888
SUTRA_EMBEDDING_TIMEOUT_SEC=30

# Association extraction
SUTRA_MIN_ASSOCIATION_CONFIDENCE=0.5
SUTRA_MAX_ASSOCIATIONS_PER_CONCEPT=10

# Semantic analysis
SUTRA_SEMANTIC_ANALYSIS=true

# Storage
SUTRA_STORAGE_PATH=./storage
SUTRA_MEMORY_THRESHOLD=50000
SUTRA_VECTOR_DIMENSION=768

# Sharding
SUTRA_NUM_SHARDS=16
```

---

## Next: [Learning Pipeline Details](./PIPELINE.md)
