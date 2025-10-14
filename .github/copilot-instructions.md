# Sutra AI System - Copilot Instructions

## Project Overview
This is **Sutra AI** - an explainable graph-based AI system positioning itself as an alternative to traditional LLMs. The system uses associative reasoning, persistent memory graphs, and optional lightweight semantic embeddings (no GPU required).

**Core Philosophy**: Explainability over black-box complexity. Every reasoning step is traceable, memory is persistent, and learning happens in real-time without expensive retraining.

## Architecture Components

### 1. Core Engine (`sutra_ai.py`)
The foundational graph-based reasoning system:
- **Concepts**: Nodes with adaptive strength (1.0-10.0) that grow stronger with repeated access
- **Associations**: Typed edges (semantic, causal, temporal, hierarchical, compositional) with weights and confidence
- **Spreading Activation Search**: BFS-like graph traversal with score propagation for reasoning
- **Multi-Path Plan Aggregation (MPPA)**: Generates diverse reasoning paths and uses consensus voting to prevent single-path derailment

**Key Pattern - Adaptive Focus Learning**:
```python
# Difficult concepts (strength < 4.0) get stronger reinforcement
if existing_concept.strength < 4.0:
    existing_concept.strength *= 1.15  # Strong boost
elif existing_concept.strength > 7.0:
    existing_concept.strength *= 1.01  # Minimal boost
```

**Multi-Path Reasoning**: When `use_multi_path=True`, generates N diverse paths with variation factors, then aggregates using consensus voting (majority threshold). Prevents Chain-of-Thought derailment.

### 2. Hybrid System (`hybrid_llm_replacement.py`)
Combines graph reasoning with lightweight embeddings:
- **LightweightEmbeddings**: Auto-detects `sentence-transformers` (22MB model) or falls back to TF-IDF (no dependencies)
- **SemanticConcept**: Extended concept with `embedding` field and `get_adaptive_temperature()` method
- **Inverse Difficulty Temperature Scaling (IDTS)**: 
  - Strong concepts (≥7.0 strength) → High temp (1.0) for exploration
  - Weak concepts (≤3.0 strength) → Low temp (0.3) for precision
  - Medium concepts → Balanced temp (0.7)
- **HybridAI**: Combines semantic similarity search with graph traversal
- **NaturalLanguageGenerator**: Template-based response generation (no LLM needed)
- **ConversationManager**: Stateful multi-turn conversations with context

**Embedding Compatibility**: System detects dimension mismatches on load and re-encodes concepts automatically when switching between `sentence-transformers` and TF-IDF.

### 3. API Service (`api_service.py`)
FastAPI REST interface with lifecycle management:
- Endpoints: `/api/learn`, `/api/query`, `/api/compose`, `/api/stats`, `/api/benchmark`
- **Lifespan management**: Auto-loads knowledge on startup, saves on shutdown
- Demo setup: `/api/demo/setup` populates with biology knowledge
- Comparison: `/api/comparison/llm` shows advantages over traditional LLMs

## Development Workflows

### Running the System
```bash
# Demo mode with Multi-Path Plan Aggregation
python sutra_ai.py --demo

# Hybrid system (graph + embeddings)
python hybrid_llm_replacement.py

# API server (production)
python api_service.py
# or
uvicorn api_service:app --reload --port 8000

# Docker
docker-compose up           # Production
docker-compose --profile dev up  # Development with hot reload
```

### Adding New Features
1. **New Association Type**: Add to `AssociationType` enum, update extraction patterns in `_extract_associations()`
2. **Custom Reasoning Strategy**: Extend `_spreading_activation_search()` or create new method following the activation pattern
3. **Enhanced Embeddings**: Modify `LightweightEmbeddings._initialize_model()` to add new model options
4. **API Endpoints**: Add to `api_service.py` with proper Pydantic models and error handling

### Testing Patterns
- No formal test framework yet - use demo modes and API endpoints
- Benchmark with `/api/benchmark` endpoint for performance comparisons
- Monitor `stats` dict for system health: `concepts_created`, `associations_formed`, `queries_processed`

## Project-Specific Conventions

### Concept Strength Dynamics
- **Initial**: 1.0 on creation
- **Access boost**: `min(10.0, strength * 1.02)` per access
- **Adaptive boost** (when enabled): 1.15× for weak, 1.01× for strong concepts
- **Max cap**: 10.0 (prevents runaway growth)

### Association Confidence Scores
- **Explicit patterns** (e.g., "X causes Y"): 0.8-0.9 confidence
- **Co-occurrence** (deep extraction): 0.5 confidence
- **Semantic similarity**: Use raw similarity score (0-1)
- **Compositional**: 0.9 confidence (high trust in user-defined compositions)

### Multi-Path Reasoning Thresholds
- **Consensus threshold**: `max(1, num_paths // 2)` - majority voting
- **Consensus boost**: `total_confidence * (1.0 + path_support * 0.2)`
- **Non-consensus penalty**: `best_confidence * 0.8`
- Default paths: 3 (configurable via `num_paths` parameter)

### Temperature Scaling (IDTS)
```python
# Concept.get_adaptive_temperature() returns:
strength >= 7.0 → 1.0   # Exploration
strength <= 3.0 → 0.3   # Precision  
else           → 0.7   # Balanced
```
Apply with `_apply_temperature()` using exponential scaling with normalization.

### Storage Format
- **JSON persistence**: `{concepts: {id: {content, strength, ...}}, associations: {...}}`
- **Embeddings**: Stored as lists with `embedding_version` field for dimension tracking
- **Auto-save**: On API shutdown, manual via `/api/save` or `ai.save()`
- **Auto-load**: On startup with dimension compatibility checking

## Critical Implementation Details

### Spreading Activation Score Propagation
```python
propagated_score = current_score * association.confidence * 0.9
```
The 0.9 decay factor prevents infinite loops and ensures convergence.

### Variation Factor for Path Diversity
```python
variation_factor = 1.0 - (path_idx * 0.15)  # 1.0, 0.85, 0.7...
```
Each path gets progressively smaller decay to explore different graph regions.

### Concept Indexing
- **Word extraction**: Regex `\b\w+\b`, filter short words (<3 chars) and stop words
- **Index structure**: `word_to_concepts: Dict[str, Set[str]]` for O(1) word lookups
- **Neighbor cache**: `concept_neighbors: Dict[str, Set[str]]` for fast graph traversal

### Association Extraction Patterns
Regex patterns in `_extract_associations()`:
- Causal: `"(.+?) causes (.+)"`
- Hierarchical: `"(.+?) is (?:a|an) (.+)"`
- Compositional: `"(.+?) contains (.+)"`
- Semantic: `"(.+?) similar to (.+)"`
- Temporal: `"(.+?) before (.+)"`

Pattern order matters - more specific patterns should come first.

## Common Pitfalls

1. **Forgetting to call `concept.access()`**: Concepts don't strengthen automatically - must call during traversal
2. **Missing dimension compatibility**: When switching embedding models, old embeddings become invalid. The system handles this with re-encoding, but be aware of the performance cost on first load.
3. **Infinite loops in reasoning**: Always check `visited` set before exploring neighbors
4. **Embedding None checks**: Not all concepts have embeddings (especially after dimension mismatches). Always check `if embedding is not None`.
5. **Temperature range**: Keep temperatures between 0.1-2.0. Extreme values cause numeric instability in `_apply_temperature()`.

## Performance Characteristics

- **Query latency**: 10-50ms average (CPU-only)
- **Learning**: Instant (no retraining), ~1000 concepts/sec
- **Memory**: ~0.1KB per concept, 2GB total footprint typical
- **Graph traversal**: O(branches^depth) worst case, typically O(5^max_steps)
- **Semantic search**: O(n) where n = total concepts with embeddings

## External Dependencies

**Required**:
- `fastapi`, `uvicorn` - API server
- `pydantic` - Data validation
- `numpy` - Vector operations

**Optional but recommended**:
- `sentence-transformers` - Semantic embeddings (22MB model, CPU-friendly)
- Falls back to TF-IDF if unavailable

**Not used**: No PyTorch, TensorFlow, or heavy ML frameworks. No GPU required.

## Integration Points

- **API server**: Port 8000 (default), CORS-enabled for web frontends
- **Knowledge storage**: JSON files in configurable directory (`./sutra_knowledge`, `./hybrid_knowledge`, `./api_knowledge`)
- **Docker volumes**: Mount `/app/knowledge` for persistent storage across container restarts
- **Health check**: `GET /api/health` for container orchestration

## Key Files to Reference

- **Graph algorithms**: `sutra_ai.py` lines 350-550 (`_spreading_activation_search`, `_multi_path_reasoning`)
- **Embedding logic**: `hybrid_llm_replacement.py` lines 30-130 (`LightweightEmbeddings`)
- **Temperature scaling**: `hybrid_llm_replacement.py` lines 145-175 (`get_adaptive_temperature`, `_apply_temperature`)
- **API lifecycle**: `api_service.py` lines 85-105 (`lifespan` context manager)
- **Association extraction**: `sutra_ai.py` lines 235-270 (`_extract_associations`)

## Recent Research Integrations (Oct 2025)

1. **Adaptive Focus (AdaKD)**: Loss-driven token focusing - difficult concepts get more compute time
2. **Multi-Path Plan Aggregation (MPPA)**: Multiple reasoning paths with consensus voting to prevent derailment
3. **Inverse Difficulty Temperature Scaling (IDTS)**: Low temp for hard concepts (precision), high temp for easy concepts (exploration)

These are research-inspired optimizations that improve reasoning quality without increasing model size.
