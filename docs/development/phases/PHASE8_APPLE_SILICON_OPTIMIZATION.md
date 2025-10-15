# 🚀 Phase 8: Apple Silicon Optimization Plan

**Target Platform**: Apple M-series Silicon (Metal Performance Shaders)  
**Start Date**: October 15, 2025  
**Current Performance**: 64 concepts/sec (synthetic), 30 concepts/sec (real Ollama data)  
**Target Performance**: 300-640 concepts/sec  

---

## 📋 Overview

Phase 8 optimizes Sutra's learning pipeline for Apple Silicon using:
1. **Batch Processing** - Process concepts in parallel batches
2. **MPS Acceleration** - GPU acceleration via Metal Performance Shaders
3. **Approximate Nearest Neighbors** - Fast similarity search with HNSW/FAISS

Unlike CUDA (NVIDIA), we'll use:
- **PyTorch MPS backend** for GPU acceleration
- **FAISS with CPU optimizations** (FAISS MPS support is experimental)
- **Native ARM64 optimizations** built into modern Python packages

---

## 🎯 Phase 8A: Batch Processing (1-2 days)

### Goal
Process multiple concepts simultaneously instead of one-at-a-time.

### Current Bottleneck
```python
# Current: Sequential processing
for concept_text in batch:
    concept = engine.learn(concept_text)  # One at a time
```

### Target Architecture
```python
# Target: Batch processing
concepts = engine.learn_batch(concept_texts)  # All at once
```

### Implementation Tasks

#### Task 8A.1: Batch Embedding Generation ✅ (0.5 days)
- [ ] Create `EmbeddingBatchProcessor` class
- [ ] Load sentence-transformer model with MPS support
- [ ] Implement `encode_batch()` for parallel embedding generation
- [ ] Add embedding caching to avoid recomputation
- [ ] Benchmark: Aim for 5-10x speedup

#### Task 8A.2: Parallel Association Extraction (0.5 days)
- [ ] Refactor `AssociationExtractor` for batch mode
- [ ] Use multiprocessing for CPU-bound pattern matching
- [ ] Pool shared resources (nlp_processor, regex patterns)
- [ ] Optimize co-occurrence computation for batches

#### Task 8A.3: Batch Learning API (0.5 days)
- [ ] Add `ReasoningEngine.learn_batch()` method
- [ ] Implement transaction-like semantics (all or nothing)
- [ ] Update HNSW index with batch insertions
- [ ] Add comprehensive error handling

#### Task 8A.4: Update Benchmarks (0.5 days)
- [ ] Modify `continuous_learning_benchmark.py` for batch mode
- [ ] Add batch size tuning experiments
- [ ] Measure memory usage vs batch size
- [ ] Document optimal batch sizes for M1/M2/M3

**Expected Gain**: 5-10x speedup → **150-320 concepts/sec**

---

## 🎯 Phase 8B: MPS GPU Acceleration (2-3 days)

### Goal
Leverage Apple Silicon GPU for embedding generation.

### Current Setup
```python
# CPU-only sentence-transformers
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(texts)  # CPU bound
```

### Target Setup
```python
# MPS-accelerated with PyTorch
model = SentenceTransformer('all-MiniLM-L6-v2')
model.to('mps')  # Move to Metal GPU
embeddings = model.encode(texts, device='mps')  # GPU accelerated
```

### Implementation Tasks

#### Task 8B.1: MPS Environment Setup (0.5 days)
- [ ] Verify PyTorch 2.0+ with MPS support installed
- [ ] Test MPS availability: `torch.backends.mps.is_available()`
- [ ] Benchmark MPS vs CPU for different batch sizes
- [ ] Document hardware requirements (M1/M2/M3 differences)

#### Task 8B.2: MPS-Optimized Embeddings (1 day)
- [ ] Create `MPSEmbeddingGenerator` class
- [ ] Implement automatic fallback to CPU if MPS unavailable
- [ ] Add batch size auto-tuning for memory limits
- [ ] Optimize data transfer between CPU and GPU
- [ ] Add mixed-precision support (FP16) for memory efficiency

#### Task 8B.3: Integration & Testing (0.5 days)
- [ ] Integrate MPS embeddings into `AdaptiveLearner`
- [ ] Add configuration flags for MPS enable/disable
- [ ] Test on various batch sizes (1, 10, 50, 100, 500)
- [ ] Verify embedding quality unchanged

#### Task 8B.4: Performance Tuning (1 day)
- [ ] Profile memory usage on M1/M2/M3
- [ ] Find optimal batch size per chip (M1: ~32, M2: ~64, M3: ~128)
- [ ] Implement dynamic batch sizing based on available GPU memory
- [ ] Benchmark against CPU baseline

**Expected Gain**: 3-10x speedup on batches → **320-640 concepts/sec** (combined with 8A)

---

## 🎯 Phase 8C: Approximate Nearest Neighbors (2-3 days)

### Goal
Scale similarity search to 100K+ concepts with sub-millisecond queries.

### Current Architecture
```python
# HNSW index (already implemented!)
self.vector_index = VectorIndex(dimension=384)
```

### Optimization Opportunities

#### Task 8C.1: HNSW Tuning (0.5 days)
- [ ] Experiment with `ef_construction` values (100-400)
- [ ] Tune `M` parameter (8-32) for memory vs speed
- [ ] Optimize `ef_search` dynamically based on query
- [ ] Benchmark recall@10 vs speed tradeoff

#### Task 8C.2: Product Quantization (Optional, 1 day)
- [ ] Integrate FAISS for advanced PQ compression
- [ ] Implement PQ + HNSW hybrid index
- [ ] Compare memory footprint: raw vs PQ
- [ ] Target: 4-8x memory reduction for 100K+ concepts

#### Task 8C.3: Multi-Index Strategy (1 day)
- [ ] Create domain-specific sub-indices
- [ ] Implement routing logic based on query context
- [ ] Add cache for frequent queries
- [ ] Lazy-load indices for memory efficiency

#### Task 8C.4: Benchmark at Scale (0.5 days)
- [ ] Test with 10K, 50K, 100K, 500K concepts
- [ ] Measure query latency percentiles (p50, p95, p99)
- [ ] Profile memory usage vs index size
- [ ] Document scaling characteristics

**Expected Gain**: 10-100x for large-scale retrieval (100K+ concepts)

---

## 📊 Combined Performance Targets

| Metric | Current | After 8A | After 8A+8B | After 8A+8B+8C |
|--------|---------|----------|-------------|----------------|
| **Learning** | 30-64/sec | 150-320/sec | 320-640/sec | 320-640/sec |
| **Query** | 1.3M ops/sec | 1.3M ops/sec | 1.3M ops/sec | 10-100M ops/sec |
| **Scalability** | 10K concepts | 50K concepts | 100K concepts | 1M+ concepts |
| **Memory** | ~100MB/10K | ~200MB/10K | ~250MB/10K | ~50MB/10K (PQ) |

---

## 🛠️ Implementation Timeline

### Week 1 (Days 1-2): Phase 8A - Batch Processing
- Day 1: Batch embeddings + parallel associations
- Day 2: Batch API + benchmarks

**Checkpoint**: 150-320 concepts/sec learning

### Week 2 (Days 3-5): Phase 8B - MPS Acceleration
- Day 3: MPS setup + testing
- Day 4: MPS embedding integration
- Day 5: Performance tuning + documentation

**Checkpoint**: 320-640 concepts/sec learning

### Week 2-3 (Days 6-8): Phase 8C - ANN Optimization
- Day 6: HNSW tuning + multi-index
- Day 7: Optional PQ compression
- Day 8: Scale benchmarks + documentation

**Checkpoint**: 10-100x faster queries at scale

---

## 🔧 Technical Stack

### Core Dependencies
```python
# Already installed
sentence-transformers>=2.2.2
hnswlib>=0.7.0
numpy>=1.24.0

# New for Phase 8
torch>=2.0.0  # MPS support
faiss-cpu>=1.7.4  # Optional for PQ
```

### Apple Silicon Specifics
- **PyTorch MPS**: Native Metal Performance Shaders backend
- **ARM64 optimizations**: Most packages now ARM-native
- **Memory**: Unified memory architecture (shared CPU/GPU)
- **Chips**: 
  - M1: 8-16GB RAM, 7-8 GPU cores
  - M2: 8-24GB RAM, 8-10 GPU cores
  - M3: 8-24GB RAM, 10-16 GPU cores

---

## 🧪 Testing Strategy

### Performance Benchmarks
1. **Micro-benchmarks**: Individual component speedup
2. **Integration tests**: End-to-end learning pipeline
3. **Scale tests**: 10K → 100K → 1M concepts
4. **Memory profiling**: Peak usage and leaks

### Validation
1. **Embedding quality**: Cosine similarity unchanged
2. **Association accuracy**: Pattern extraction correctness
3. **Query recall**: HNSW recall@10 ≥ 0.95
4. **Reasoning quality**: Path quality preserved

### Compatibility
1. **Fallback to CPU**: If MPS unavailable
2. **Cross-platform**: Still works on Linux/Windows
3. **Backward compatible**: Existing code unchanged

---

## 📈 Success Metrics

### Phase 8A Success
- ✅ Batch API implemented
- ✅ 5-10x speedup measured
- ✅ Memory usage acceptable (<2GB for 50K concepts)
- ✅ No accuracy degradation

### Phase 8B Success
- ✅ MPS acceleration working
- ✅ 3-10x additional speedup on batches
- ✅ Auto-fallback to CPU functional
- ✅ Stable across M1/M2/M3 chips

### Phase 8C Success
- ✅ Sub-millisecond queries at 100K scale
- ✅ Recall@10 ≥ 0.95
- ✅ 4-8x memory reduction (if PQ used)
- ✅ Scales to 1M+ concepts

---

## 🎓 Key Learnings & Considerations

### Apple Silicon Advantages
- ✅ Unified memory (no CPU↔GPU transfer overhead)
- ✅ Energy efficient (great for laptops)
- ✅ Native ARM64 performance
- ✅ Metal shaders highly optimized

### Apple Silicon Limitations
- ⚠️ MPS less mature than CUDA
- ⚠️ Some ML libraries lack MPS support
- ⚠️ Smaller GPU memory (vs dedicated GPUs)
- ⚠️ Limited profiling tools vs NVIDIA

### Optimization Tips
1. **Batch size tuning is critical** - M1/M2/M3 differ
2. **Profile memory carefully** - Unified memory shared
3. **Use FP16 where possible** - Double throughput
4. **Benchmark CPU vs MPS** - Sometimes CPU faster for small batches
5. **Consider asymmetric processing** - GPU for embeddings, CPU for NLP

---

## 📚 Next Steps

1. **Review this plan** - Confirm priorities and timeline
2. **Setup environment** - Verify PyTorch MPS installed
3. **Start Phase 8A** - Implement batch processing
4. **Measure baseline** - Benchmark current performance
5. **Iterate rapidly** - Profile → Optimize → Test

Let's start with **Phase 8A (Batch Processing)** - it provides the foundation for MPS acceleration and gives immediate 5-10x gains!

Ready to begin? 🚀
