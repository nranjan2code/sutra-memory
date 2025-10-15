# Phase 6: Direct Rust Integration Plan (Simplified)

**Goal**: Replace Python storage with Rust storage engine directly  
**Timeline**: Days 13-18 (6 days)  
**Approach**: Forward-only, no backward compatibility, no migration

## 🎯 Philosophy

**Clean slate approach**:
- Replace, don't wrap
- Direct integration, no abstraction layers
- Optimize for performance, not compatibility
- Start fresh, no legacy baggage

## 🏗️ Simple Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Application Layer (Python)                       │
│  ReasoningEngine, HybridAI, QueryProcessor              │
└────────────────────┬────────────────────────────────────┘
                     │ Direct calls
                     ↓
┌─────────────────────────────────────────────────────────┐
│         Rust Storage (sutra_storage)                    │
│                                                          │
│  GraphStore (PyO3 bindings)                             │
│  • add_vector(id, vector)                               │
│  • get_vector(id) → vector                              │
│  • add_association(source, target)                      │
│  • get_neighbors(id) → [ids]                           │
│  • search_text(words) → [ids]                          │
│  • stats() → {...}                                      │
└─────────────────────────────────────────────────────────┘
```

## 📊 What We Have

### Rust Storage (Ready to Use)
```python
import sutra_storage

# Create storage
store = sutra_storage.GraphStore("./data", vector_dimension=384)

# Store vectors
store.add_vector(concept_id, embedding)
vector = store.get_vector(concept_id)

# Graph operations
store.add_association(source_id, target_id)
neighbors = store.get_neighbors(concept_id)

# Search
results = store.search_text("photosynthesis energy")
concepts = store.get_concepts_in_range(start_time, end_time)

# Statistics
stats = store.stats()
# {'total_vectors': 100, 'total_concepts': 100, ...}

# Context manager
with store:
    # All operations
    pass  # Auto-saves on exit
```

### What We Need to Add

**1. Concept Metadata Storage**
- Rust stores: vectors (384-dim) + graph structure
- Python needs: content, timestamps, source, confidence, etc.
- **Solution**: Store metadata as JSON sidecar OR extend Rust storage

**2. Type Conversions**
- Python Concept ↔ Rust storage calls
- Python Association ↔ Rust add_association
- Embeddings from NLP processor → Rust vectors

**3. ReasoningEngine Integration**
- Replace `self.concepts` dict with Rust queries
- Replace `self.associations` dict with Rust graph
- Update indexes to query Rust storage

## 📅 Implementation Timeline

### Day 13-14: Rust Storage Adapter

**Objective**: Create clean adapter for Concept/Association ↔ Rust storage

**File**: `packages/sutra-core/sutra_core/storage/rust_adapter.py`

```python
"""
Direct adapter for Rust storage.
No abstractions, just clean type conversions.
"""

import sutra_storage
import numpy as np
from typing import Optional, Dict, List, Tuple
from ..graph.concepts import Concept, Association, AssociationType

class RustStorageAdapter:
    """Adapter between Python Concepts and Rust storage."""
    
    def __init__(self, storage_path: str, vector_dimension: int = 384):
        self.store = sutra_storage.GraphStore(storage_path, vector_dimension)
        self.vector_dimension = vector_dimension
    
    # Concept operations
    def add_concept(self, concept: Concept, embedding: np.ndarray) -> None:
        """Add concept with its embedding."""
        # Store vector
        self.store.add_vector(concept.id, embedding)
        
        # Store metadata separately (JSON sidecar for now)
        # OR: Extend Rust storage to handle metadata
        # Decision: Start with JSON sidecar, optimize later
    
    def get_concept(self, concept_id: str) -> Optional[Concept]:
        """Retrieve concept by ID."""
        vector = self.store.get_vector(concept_id)
        if vector is None:
            return None
        
        # Load metadata
        # Reconstruct Concept
        return concept
    
    # Association operations
    def add_association(self, assoc: Association) -> None:
        """Add association to graph."""
        self.store.add_association(assoc.source_id, assoc.target_id)
        # Metadata stored separately
    
    def get_neighbors(self, concept_id: str) -> List[str]:
        """Get neighboring concept IDs."""
        return self.store.get_neighbors(concept_id)
    
    # Search operations
    def search_by_text(self, text: str) -> List[str]:
        """Search concepts by text content."""
        words = text.lower().split()
        return self.store.search_text(words)
    
    def search_by_embedding(self, query_vector: np.ndarray, top_k: int = 10) -> List[Tuple[str, float]]:
        """Semantic search using vector similarity."""
        # Use approximate distance for fast search
        results = []
        stats = self.store.stats()
        # Iterate through concepts, compute distances
        # Return top-k
        return results
    
    # Batch operations
    def save(self) -> None:
        """Persist all changes."""
        self.store.save()
    
    def stats(self) -> Dict:
        """Get storage statistics."""
        return self.store.stats()
    
    # Context manager
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.save()
```

**Tasks**:
1. ✅ Create `sutra_core/storage/` directory
2. Create `rust_adapter.py` with full implementation
3. Add metadata storage (JSON sidecar initially)
4. Add comprehensive tests
5. Benchmark adapter overhead

**Metadata Strategy** (Keep it simple):
```python
# Store metadata in: {storage_path}/metadata.json
{
  "concepts": {
    "concept_id": {
      "content": str,
      "created": float,
      "access_count": int,
      "strength": float,
      "last_accessed": float,
      "source": str,
      "category": str,
      "confidence": float
    }
  },
  "associations": {
    "source:target": {
      "assoc_type": str,
      "weight": float,
      "confidence": float,
      "created": float,
      "last_used": float
    }
  }
}
```

### Day 15-16: ReasoningEngine Integration

**Objective**: Replace dict storage with Rust adapter

**Changes to `reasoning/engine.py`**:

```python
class ReasoningEngine:
    def __init__(self, storage_path: str = "./knowledge", ...):
        # OLD:
        # self.concepts: Dict[str, Concept] = {}
        # self.associations: Dict[Tuple[str, str], Association] = {}
        
        # NEW:
        from ..storage.rust_adapter import RustStorageAdapter
        self.storage = RustStorageAdapter(storage_path)
        
        # Keep indexes for fast lookups
        self.concept_neighbors: Dict[str, Set[str]] = defaultdict(set)
        self.word_to_concepts: Dict[str, Set[str]] = defaultdict(set)
        
        # Load existing data if available
        self._load_from_storage()
    
    def learn(self, content: str, source: str = None) -> str:
        """Learn new concept."""
        # Extract concept
        concept = self.adaptive_learner.learn(content, source)
        
        # Get embedding
        embedding = self.nlp_processor.get_embedding(content)
        
        # Store in Rust (vectors + graph)
        self.storage.add_concept(concept, embedding)
        
        # Update local indexes
        words = extract_words(content)
        for word in words:
            self.word_to_concepts[word].add(concept.id)
        
        return concept.id
    
    def get_concept(self, concept_id: str) -> Optional[Concept]:
        """Retrieve concept."""
        return self.storage.get_concept(concept_id)
    
    def add_association(self, source_id: str, target_id: str, 
                       assoc_type: AssociationType, weight: float = 1.0):
        """Add association."""
        assoc = Association(source_id, target_id, assoc_type, weight)
        self.storage.add_association(assoc)
        self.concept_neighbors[source_id].add(target_id)
        self.concept_neighbors[target_id].add(source_id)
    
    def reason(self, query: str, **kwargs) -> ConsensusResult:
        """Reason about query."""
        # Query processing uses storage adapter
        # Path finding queries neighbors via storage
        # MPPA aggregates paths
        result = self.query_processor.process_query(query, **kwargs)
        return result
    
    def save(self) -> None:
        """Save all data."""
        self.storage.save()
    
    # Remove old save_knowledge_base/load_knowledge_base methods
    # Not needed - storage is always up to date
```

**Tasks**:
1. Update `ReasoningEngine.__init__` to use storage adapter
2. Update `learn()` to store in Rust
3. Update `get_concept()` to query Rust
4. Update `add_association()` to use Rust graph
5. Update `reason()` to query Rust storage
6. Remove old save/load methods
7. Update all tests
8. Verify all examples work

### Day 17-18: Performance Testing

**Objective**: Validate performance gains and scale testing

**Test Suite**:

```python
# tests/performance/test_rust_integration.py

def test_load_10k_concepts():
    """Load 10k concepts and measure performance."""
    engine = ReasoningEngine(storage_path="./perf_test")
    
    start = time.time()
    for i in range(10000):
        content = f"Test concept {i} with unique content about topic {i % 100}"
        concept_id = engine.learn(content)
    elapsed = time.time() - start
    
    print(f"Loaded 10k concepts in {elapsed:.2f}s")
    print(f"Throughput: {10000/elapsed:.0f} concepts/sec")
    
    # Target: >1000 concepts/sec
    assert elapsed < 10.0

def test_query_performance():
    """Measure query performance on large graph."""
    # Load 10k concepts
    engine = load_large_graph(10000)
    
    # Query 100 times
    queries = generate_test_queries(100)
    
    start = time.time()
    for query in queries:
        result = engine.reason(query)
    elapsed = time.time() - start
    
    print(f"100 queries in {elapsed:.2f}s")
    print(f"Average: {elapsed*1000/100:.2f}ms per query")
    
    # Target: <50ms per query
    assert elapsed / 100 < 0.05

def test_1m_concepts():
    """Stress test with 1M concepts."""
    engine = ReasoningEngine(storage_path="./stress_test")
    
    print("Loading 1M concepts...")
    start = time.time()
    
    for i in range(1_000_000):
        if i % 10000 == 0:
            print(f"  {i:,} concepts loaded...")
        content = f"Concept {i}"
        engine.learn(content)
    
    elapsed = time.time() - start
    print(f"Loaded 1M concepts in {elapsed:.2f}s")
    print(f"Throughput: {1_000_000/elapsed:.0f} concepts/sec")
    
    # Query performance on large graph
    stats = engine.storage.stats()
    print(f"Storage stats: {stats}")
    
    # Random queries
    print("Testing query performance...")
    query_times = []
    for _ in range(100):
        query = f"Concept {random.randint(0, 999999)}"
        start = time.time()
        result = engine.reason(query)
        query_times.append(time.time() - start)
    
    avg_query_time = np.mean(query_times)
    p95_query_time = np.percentile(query_times, 95)
    
    print(f"Average query: {avg_query_time*1000:.2f}ms")
    print(f"P95 query: {p95_query_time*1000:.2f}ms")
    
    # Targets
    assert avg_query_time < 0.1  # <100ms average
    assert p95_query_time < 0.5  # <500ms p95
```

**Benchmarks to Run**:
1. **Throughput**: Concepts/sec learning rate
2. **Latency**: Query response time (p50, p95, p99)
3. **Memory**: RAM usage vs concept count
4. **Storage**: Disk usage with compression
5. **Scalability**: Performance at 10k, 100k, 1M concepts

**Expected Results**:
- **Learning**: >1000 concepts/sec
- **Query latency**: <50ms average, <200ms p95
- **Memory**: ~50MB per 10k concepts (with compression)
- **Storage**: ~20MB per 10k concepts on disk
- **Scale**: Linear performance up to 1M concepts

## 🎯 Success Criteria

### Functional
- ✅ All existing tests pass
- ✅ All examples work with Rust storage
- ✅ Reasoning results are correct
- ✅ No data loss on restart

### Performance
- ✅ >1000 concepts/sec learning rate
- ✅ <50ms average query latency
- ✅ 1M concepts load successfully
- ✅ Memory usage reasonable (<1GB for 100k concepts)

### Quality
- ✅ 100% test coverage on new code
- ✅ Type hints everywhere
- ✅ Documentation complete
- ✅ Examples updated

## 📦 Deliverables

### Code
- [x] `sutra_core/storage/rust_adapter.py` (clean adapter)
- [ ] Updated `ReasoningEngine` (direct Rust integration)
- [ ] Updated `HybridAI` (embeddings in Rust)
- [ ] Metadata storage (JSON sidecar)

### Tests
- [ ] Adapter unit tests (20+ tests)
- [ ] Integration tests (30+ tests)
- [ ] Performance tests (10 benchmarks)
- [ ] Stress test (1M concepts)

### Documentation
- [ ] Integration guide
- [ ] API changes documentation
- [ ] Performance benchmarks report
- [ ] Examples updated

## 🚀 Phase 6 Completion

When we're done:
- **Zero Python dict storage** - all in Rust
- **Sub-millisecond queries** - memory-mapped reads
- **Scales to millions** - proven with load tests
- **Production ready** - crash recovery, ACID guarantees

---

**Status**: Planning complete, ready to implement! 🎯

**Next**: Create `rust_adapter.py` with full implementation.
