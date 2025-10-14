# Architecture Overview

## System Design

Sutra Models is a graph-based AI system that uses associative memory and spreading activation for reasoning. Unlike transformer-based LLMs, it maintains explicit knowledge graphs with typed relationships.

## Core Principles

### 1. Graph-Based Knowledge

Knowledge stored as directed graph:
- **Nodes**: Concepts with content and metadata
- **Edges**: Typed associations with confidence scores
- **Structure**: Explicit, interpretable, modifiable

### 2. Adaptive Strengthening

Concepts strengthen with use:
- Initial strength: 1.0
- Access boost: `strength * 1.02` per access
- Adaptive boost: Higher for weak concepts (1.15×), lower for strong (1.01×)
- Maximum: 10.0

### 3. Multi-Path Reasoning

Avoids single-path errors:
- Explores N paths simultaneously (default: 3)
- Consensus voting across paths
- Confidence boosted when paths agree
- Penalty when paths diverge

### 4. CPU-Only Operation

No GPU required:
- TF-IDF for lightweight embeddings
- Optional sentence-transformers (CPU)
- Graph traversal is memory-bound, not compute-bound
- 10-50ms query latency on standard hardware

## Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  sutra-cli   │  │  sutra-api   │  │ Custom Apps  │ │
│  │  (planned)   │  │   (FastAPI)  │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                    Hybrid Layer                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │            sutra-hybrid (HybridAI)                │  │
│  │  • Semantic search                                │  │
│  │  • Embedding management                           │  │
│  │  • Provider fallback (semantic/TF-IDF)            │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                     Core Layer                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │             sutra-core (Graph Engine)             │  │
│  │  • Concepts & Associations                        │  │
│  │  • Spreading activation                           │  │
│  │  │  • AdaptiveLearner                              │  │
│  │  • AssociationExtractor                           │  │
│  │  • Text utilities                                 │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                    Storage Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   JSON       │  │   Pickle     │  │   Future:    │ │
│  │ (concepts &  │  │ (vectorizer) │  │ PostgreSQL,  │ │
│  │ associations)│  │              │  │   Redis      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Data Flow

### Learning

```
Input Text
    ↓
Extract Words (tokenize, filter stopwords)
    ↓
Create/Retrieve Concepts
    ↓
Pattern Matching (regex-based association patterns)
    ↓
Create Associations (typed edges with confidence)
    ↓
Generate Embeddings (semantic or TF-IDF)
    ↓
Index for Fast Lookup (word→concept, concept→neighbors)
    ↓
Store to Disk (JSON + pickle)
```

### Reasoning

```
Query
    ↓
Extract Query Words
    ↓
Find Starting Concepts (word index lookup)
    ↓
Spreading Activation (BFS-like graph traversal)
    ├─ Path 1: score propagation, confidence decay
    ├─ Path 2: parallel exploration
    └─ Path 3: diverse routes
    ↓
Consensus Voting (agree = boost, disagree = penalty)
    ↓
Rank Results by Confidence
    ↓
Return Top Paths with Explanations
```

### Semantic Search

```
Query
    ↓
Generate Query Embedding
    ↓
Calculate Similarity (cosine) with all concept embeddings
    ↓
Filter by Threshold
    ↓
Sort by Similarity
    ↓
Return Top-K Results
```

## Key Algorithms

### Spreading Activation

Propagates activation scores through graph:

```python
def spread_activation(start_concept, max_steps=3):
    visited = {start_concept.id}
    queue = [(start_concept, 1.0, [])]  # (concept, score, path)
    
    for _ in range(max_steps):
        if not queue:
            break
            
        concept, score, path = queue.pop(0)
        concept.access()  # Strengthen
        
        for neighbor_id in concept_neighbors[concept.id]:
            if neighbor_id not in visited:
                assoc = associations[(concept.id, neighbor_id)]
                new_score = score * assoc.confidence * 0.9  # Decay
                queue.append((concepts[neighbor_id], new_score, path + [neighbor_id]))
                visited.add(neighbor_id)
    
    return queue
```

### Adaptive Learning

Adjusts boost based on concept strength:

```python
def adaptive_boost(concept):
    if concept.strength < 4.0:  # Weak concept
        return 1.15  # Strong boost
    elif concept.strength > 7.0:  # Strong concept
        return 1.01  # Minimal boost
    else:  # Medium concept
        return 1.05  # Moderate boost
```

### Association Extraction

Pattern-based relationship detection:

```python
patterns = {
    "causal": r"(.+?) causes (.+)",
    "hierarchical": r"(.+?) is (?:a|an) (.+)",
    "compositional": r"(.+?) contains (.+)",
    "semantic": r"(.+?) similar to (.+)",
    "temporal": r"(.+?) before (.+)",
}

for pattern_type, regex in patterns.items():
    matches = re.findall(regex, text, re.IGNORECASE)
    for source, target in matches:
        create_association(source, target, pattern_type, confidence=0.8)
```

## Memory Management

### Concept Storage

Each concept:
```python
{
    "id": str (UUID),
    "content": str (original text),
    "strength": float (1.0-10.0),
    "access_count": int,
    "created_at": datetime,
    "source": str (optional),
}
```

Size: ~0.1KB per concept (without embedding)

### Association Storage

Each association:
```python
{
    "source_id": str,
    "target_id": str,
    "type": AssociationType,
    "confidence": float (0.0-1.0),
}
```

Size: ~0.05KB per association

### Embedding Storage

- **TF-IDF**: 100 dimensions × 4 bytes = 400 bytes
- **Semantic**: 384 dimensions × 4 bytes = 1.5KB

## Scalability

### Current Limits

- **Tested**: 10,000 concepts
- **Expected**: 100,000 concepts without issues
- **Memory**: ~100MB for 10K concepts (with embeddings)
- **Query time**: O(branches^depth), typically O(5^3) = 125 operations

### Optimization Strategies

1. **Index pruning**: Remove weak concepts (strength < threshold)
2. **Batch processing**: Learn multiple concepts before re-indexing
3. **Lazy loading**: Load subgraphs on demand
4. **Caching**: Cache frequent query results
5. **Quantization**: Reduce embedding precision (float32 → int8)

## Extensibility Points

### Custom Association Types

```python
class CustomAssociationType(str, Enum):
    REQUIRES = "requires"
    IMPLEMENTS = "implements"
    DEPENDS_ON = "depends_on"
```

### Custom Confidence Scoring

```python
def custom_confidence(source, target, pattern_type):
    # Domain-specific logic
    if pattern_type == "requires":
        return 0.95  # High confidence
    return 0.5
```

### Custom Embedding Providers

```python
class CustomEmbedding(EmbeddingProvider):
    def encode(self, texts):
        # Your embedding logic
        return embeddings
```

## Comparison with Other Approaches

| Feature | Sutra Models | Transformers | Knowledge Graphs |
|---------|-------------|-------------|-----------------|
| Interpretability | High | Low | High |
| Memory | Explicit | Implicit | Explicit |
| Training | None | Extensive | Manual |
| Hardware | CPU | GPU | CPU/GPU |
| Latency | 10-50ms | 100-1000ms | 10-100ms |
| Scalability | O(N) | O(N²) | O(N log N) |
| Explainability | Full paths | Attention | Queries |

## Performance Characteristics

### Time Complexity

- **Learning**: O(M × K) where M = words, K = pattern matches
- **Search (semantic)**: O(N) where N = total concepts
- **Reasoning (spreading)**: O(B^D) where B = branches, D = depth
- **Storage**: O(C + A) where C = concepts, A = associations

### Space Complexity

- **Concepts**: O(N)
- **Associations**: O(N²) worst case, O(N log N) typical
- **Embeddings**: O(N × D) where D = embedding dimension
- **Indices**: O(W × C) where W = vocabulary size

## Next Steps

- [Graph Structure](graph.md) - Detailed graph mechanics
- [Learning System](learning.md) - Knowledge extraction details
- [Storage Format](storage.md) - Persistence specification
