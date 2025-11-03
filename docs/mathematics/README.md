# Mathematical Foundations: Sutra Storage Algorithms

This directory contains rigorous mathematical specifications for all core algorithms in the Sutra storage system. Each document provides step-by-step calculations, complexity analysis, and formal proofs.

---

## Document Index

### ✅ Completed

1. **[HNSW Vector Search](01_HNSW_VECTOR_SEARCH.md)** ⭐
   - **Algorithm**: Hierarchical Navigable Small World for k-NN search
   - **Complexity**: $O(d \log N)$ query, $O(N d \log N)$ construction
   - **Key Formulas**:
     - Cosine distance: $\text{dist}(\vec{v}_i, \vec{v}_j) = 1 - (\vec{v}_i \cdot \vec{v}_j)$
     - Layer assignment: $l_i = \lfloor -\ln(\text{uniform}(0,1)) \cdot m_L \rfloor$
   - **Performance**: 94× faster startup with USearch persistence
   - **Implementation**: `packages/sutra-storage/src/hnsw_container.rs`

2. **[Adaptive Reconciliation](02_ADAPTIVE_RECONCILIATION.md)** ⭐
   - **Algorithm**: AI-native self-optimizing write-read plane reconciliation
   - **Key Techniques**: Exponential Moving Average (EMA), linear trend prediction
   - **Key Formulas**:
     - EMA: $Q_t = \alpha \cdot |W(t)| + (1 - \alpha) \cdot Q_{t-1}$
     - Interval optimization: $I^*(t) = f(u(t), I_{\min}, I_{\max})$
     - Health score: $H(t) \in [0, 1]$ piecewise function
   - **Performance**: 80% CPU savings at idle, 10× lower latency during bursts
   - **Implementation**: `packages/sutra-storage/src/adaptive_reconciler.rs`

3. **[Graph Pathfinding](03_GRAPH_PATHFINDING.md)** ⭐
   - **Algorithm**: Multi-strategy graph traversal (BFS, Best-First, Bidirectional)
   - **Complexity**: $O(k \cdot d)$ for k-hop paths
   - **Key Formulas**:
     - Harmonic mean confidence: $C_{\text{harm}} = \frac{n}{\sum_{i=1}^{n} 1/w_i}$
     - Path diversity: Greedy selection with similarity threshold
   - **Performance**: 8× speedup with Rayon parallel pathfinding
   - **Implementation**: `packages/sutra-storage/src/parallel_paths.rs`

4. **[Sharded Storage](04_SHARDED_STORAGE.md)** ⭐
   - **Algorithm**: Hash-based sharding with consistent hashing
   - **Complexity**: $O(d \log(N/S))$ query per shard
   - **Key Formulas**:
     - Shard function: $s(c) = h(\text{id}(c)) \mod S$
     - Expected size: $\mathbb{E}[|C_i|] = N/S$
   - **Performance**: 16 shards → 912K writes/sec (linear scaling)
   - **Implementation**: `packages/sutra-storage/src/sharded_storage.rs`

5. **[Two-Phase Commit (2PC)](05_2PC_TRANSACTIONS.md)** ⭐
   - **Algorithm**: Distributed transaction protocol with coordinator
   - **Complexity**: $O(P)$ for P participants
   - **Key Formulas**:
     - Atomicity guarantee: $\forall p_i, p_j: \text{state}(p_i, T) = \text{state}(p_j, T)$
     - Latency: $L_{\text{2PC}} = 2 \times (L_{\text{network}} + L_{\text{local}})$
   - **Performance**: 22ms typical latency (2 network RTTs)
   - **Implementation**: `packages/sutra-storage/src/transaction.rs`

6. **[Binary Storage Format](06_BINARY_STORAGE_FORMAT.md)** ⭐
   - **Format**: Custom binary with MessagePack WAL
   - **Complexity**: $O(N + M + V)$ read/write
   - **Key Structures**:
     - 64-byte header: magic + version + counts + checksum
     - Concepts: 36-byte header + variable content
     - Vectors: 20 + 4d bytes per vector
   - **Performance**: 478 MB/s read, 190 MB/s write (3.3 GB file)
   - **Implementation**: `packages/sutra-storage/src/mmap_store.rs`

---

## Mathematical Notation Guide

### Common Symbols

| Symbol | Meaning | Example |
|--------|---------|---------|
| $N$ | Number of concepts/vectors | $N = 1,000,000$ |
| $d$ | Vector dimension | $d = 768$ |
| $k$ | Number of nearest neighbors | $k = 10$ |
| $M$ | Maximum connections per layer | $M = 16$ |
| $\alpha$ | EMA smoothing factor | $\alpha = 0.3$ |
| $u(t)$ | Queue utilization | $u \in [0, 1]$ |
| $O(\cdot)$ | Big-O complexity | $O(d \log N)$ |

### Set Theory

- $\mathcal{V} \subset \mathbb{R}^d$: Vector space
- $\vec{v}_i \in \mathbb{R}^d$: Vector in d-dimensional space
- $W = \{w_1, \ldots, w_n\}$: Write operation set
- $\mathcal{N}_l(v)$: Neighbor set at layer $l$

### Probability & Statistics

- $\mathbb{E}[X]$: Expected value
- $\text{Var}(X)$: Variance
- $P(\cdot)$: Probability
- $\text{uniform}(a,b)$: Uniform distribution

---

## Algorithm Taxonomy

### By Purpose

**Search & Retrieval**:
- HNSW Vector Search (approximate k-NN)
- Parallel Pathfinding (graph traversal)

**Data Management**:
- Adaptive Reconciliation (write-read consistency)
- Sharding (horizontal scaling)
- 2PC (distributed transactions)

**Storage**:
- Binary Format (serialization)
- WAL (durability)
- Memory-mapped files (zero-copy)

### By Complexity Class

**Logarithmic** $O(\log N)$:
- HNSW search (per query)
- Binary search (WAL replay)

**Log-linear** $O(N \log N)$:
- HNSW construction
- Sorting operations

**Linear** $O(N)$:
- Sequential scans
- Full graph traversal

**Constant** $O(1)$:
- Hash lookups
- EMA updates
- Atomic operations

---

## Performance Characteristics

### Measured Benchmarks (10M Concepts)

| Operation | Latency | Throughput | Complexity |
|-----------|---------|------------|------------|
| Write (buffered) | Low latency | Optimized | $O(1)$ |
| Read (mmap) | <0.01ms | 100K reads/sec | $O(1)$ |
| Vector search | <50ms (P50) | 20 queries/sec | $O(d \log N)$ |
| Pathfinding | ~1ms (3-hop) | 1K paths/sec | $O(k \cdot d)$ |
| Flush to disk | ~500ms | 2 flushes/sec | $O(N)$ |

### Scaling Properties

**Horizontal (Sharding)**:
- $N$ concepts → $S$ shards
- Per-shard size: $N/S$
- Query latency: $O(d \log(N/S))$ per shard
- Parallel search: $O(d \log(N/S))$ total

**Vertical (Single Node)**:
- Memory: ~2 KB per concept (excluding vectors)
- Storage: ~3 KB per vector (768-d)
- Max scale: 10M+ concepts per shard

---

## Theoretical Foundations

### Graph Theory
- **Small World Networks**: Average path length $L = O(\log N)$
- **Navigability**: Greedy routing finds near-optimal paths
- **Connectivity**: Probabilistic guarantees with $M$ connections

### Information Theory
- **Entropy**: Optimal encoding for graph structure
- **Compression**: MessagePack ~4.4× smaller than JSON
- **Lossy compression**: Vector quantization (PQ/SQ)

### Queueing Theory
- **M/M/1 Queue**: Arrival rate $\lambda$, service rate $\mu$
- **Utilization**: $\rho = \lambda / \mu < 1$ for stability
- **Adaptive control**: Dynamic $\mu$ via interval adjustment

### Control Theory
- **PID-like behavior**: EMA provides proportional response
- **Stability**: Bounded oscillations via $\alpha$ tuning
- **Steady-state error**: Converges to true mean

---

## Implementation Principles

### 1. Zero-Copy Architecture
- Memory-mapped files (mmap)
- Immutable snapshots (arc-swap)
- Structural sharing (persistent data structures)

**Mathematical benefit**: Reduces clone complexity from $O(N)$ to $O(\log N)$

### 2. Lock-Free Concurrency
- Write log: Append-only (crossbeam channel)
- Read view: Immutable (Arc)
- Atomic operations: Compare-and-swap

**Mathematical benefit**: No blocking, $O(1)$ write latency

### 3. Approximation Algorithms
- HNSW: Approximate k-NN (>95% recall)
- EMA: Approximate mean (exponential decay)

**Mathematical benefit**: Trade exactness for speed

### 4. Adaptive Systems
- Dynamic interval adjustment (reconciler)
- Capacity reservation (HNSW)

**Mathematical benefit**: Self-optimization based on workload

---

## How to Read These Documents

### For Researchers
- Focus on **Section 1** (problem definition) and **Theoretical Guarantees**
- See **References** for academic papers
- Complexity analysis provides worst-case bounds

### For Engineers
- Start with **Algorithm** pseudocode sections
- Check **Implementation Details** for code patterns
- **Example Calculations** show real-world scenarios

### For Performance Tuning
- Review **Performance Analysis** sections
- Check **Parameter Tuning Guides**
- Measure against **Benchmark Results**

---

## Verification

All algorithms are:
1. **Tested**: 107 passing tests in storage suite
2. **Benchmarked**: Scale validation up to 10M concepts
3. **Production-proven**: Running in deployed systems
4. **Formally specified**: Step-by-step calculations included

---

## Contributing

When adding new algorithms, please include:

1. **Problem Definition**
   - Input/output specification
   - Constraints and assumptions

2. **Mathematical Formulation**
   - Core equations
   - Step-by-step derivation
   - Worked examples

3. **Complexity Analysis**
   - Time complexity (worst, average, best case)
   - Space complexity
   - Proof sketches

4. **Implementation**
   - Pseudocode
   - Actual code references
   - Test coverage

5. **Performance**
   - Benchmark results
   - Scaling behavior
   - Tuning guidelines

---

## Quick Reference

### Most Important Formulas

**HNSW Query**:
$$T_{\text{query}} = O(d \cdot \log N)$$

**Adaptive Interval**:
$$I^*(t) = \begin{cases}
I_{\max} & u(t) < 0.20 \\
I_{\text{base}} & 0.20 \leq u(t) \leq 0.70 \\
I_{\min} + (1-p) \cdot (I_{\text{base}} - I_{\min}) & u(t) > 0.70
\end{cases}$$

where $p = \frac{u(t) - 0.70}{0.30}$

**Path Confidence**:
$$C_{\text{path}} = \prod_{i=1}^{n-1} 0.85 = 0.85^{n-1}$$

**Hash-Based Sharding**:
$$\text{shard\_id}(\text{concept\_id}) = \text{hash}(\text{concept\_id}) \mod N_{\text{shards}}$$

---

## Related Documentation

- **Architecture**: `docs/sutra-storage/ARCHITECTURE.md`
- **API Reference**: `docs/sutra-storage/API.md`
- **Performance**: `docs/storage/PRODUCTION_GRADE_COMPLETE.md`
- **Deployment**: `WARP.md` (project root)

---

## Status

- ✅ **HNSW Vector Search**: Complete (557 lines)
- ✅ **Adaptive Reconciliation**: Complete (720 lines)
- ✅ **Graph Pathfinding**: Complete (771 lines)
- ✅ **Sharded Storage**: Complete (733 lines)
- ✅ **Two-Phase Commit**: Complete (824 lines)
- ✅ **Binary Storage Format**: Complete (1024 lines)

**Total**: 4,629 lines of rigorous mathematical specifications 🎉

**Last Updated**: 2025-10-24  
**Maintainer**: Sutra Models Team
