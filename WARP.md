# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Architecture Overview

Sutra AI is an explainable graph-based AI system that positions itself as an alternative to traditional LLMs. The system uses associative reasoning, persistent memory graphs, and optional lightweight semantic embeddings (no GPU required).

### Core Components

#### 1. Core Graph Engine (`sutra_ai.py`)
- **Concepts**: Nodes with adaptive strength (1.0-10.0) that strengthen with repeated access
- **Associations**: Typed edges (semantic, causal, temporal, hierarchical, compositional) with confidence scores
- **Spreading Activation Search**: BFS-like graph traversal with score propagation for explainable reasoning
- **Multi-Path Plan Aggregation (MPPA)**: Generates diverse reasoning paths and uses consensus voting to prevent single-path derailment
- **Adaptive Focus Learning**: Difficult concepts (strength < 4.0) get stronger reinforcement (1.15×), established concepts (> 7.0) get minimal reinforcement (1.01×)

#### 2. Hybrid System (`hybrid_llm_replacement.py`)
- **LightweightEmbeddings**: Auto-detects `sentence-transformers` (22MB model) or falls back to TF-IDF
- **SemanticConcept**: Extended concept with `embedding` field and adaptive temperature scaling
- **Inverse Difficulty Temperature Scaling (IDTS)**: 
  - Strong concepts (≥7.0) → High temp (1.0) for exploration
  - Weak concepts (≤3.0) → Low temp (0.3) for precision
  - Medium concepts → Balanced temp (0.7)
- **NaturalLanguageGenerator**: Template-based response generation (no LLM needed)
- **ConversationManager**: Stateful multi-turn conversations with context

#### 3. API Service (`api_service.py`)
- FastAPI REST interface with lifecycle management
- Endpoints: `/api/learn`, `/api/query`, `/api/compose`, `/api/stats`, `/api/benchmark`
- Auto-loads knowledge on startup, saves on shutdown
- Demo setup: `/api/demo/setup` populates with biology knowledge

## Development Commands

### Running the System

```bash
# Demo mode with Multi-Path Plan Aggregation
python sutra_ai.py --demo

# Hybrid system (graph + embeddings)
python hybrid_llm_replacement.py

# API server (development)
python api_service.py
# or
uvicorn api_service:app --reload --port 8000

# Docker (production)
docker-compose up

# Docker (development with hot reload)
docker-compose --profile dev up
```

### Testing and Validation

```bash
# Run basic tests (note: no formal test framework yet)
python -c "from sutra_ai import SutraAI; ai = SutraAI(); print('✅ Core system working')"

# Test hybrid system
python -c "from hybrid_llm_replacement import HybridAI; ai = HybridAI(); print('✅ Hybrid system working')"

# Benchmark API performance
curl -X POST "http://localhost:8000/api/benchmark" \
  -H "Content-Type: application/json" \
  -d '{"queries": ["What is photosynthesis?"], "iterations": 10}'

# Check system stats
curl http://localhost:8000/api/stats
```

### Package Management

```bash
# Install dependencies
pip install -r requirements.txt

# Optional: Enhanced semantic understanding (22MB model)
pip install sentence-transformers

# Minimal installation (TF-IDF fallback)
pip install fastapi uvicorn pydantic numpy
```

## Key Architectural Patterns

### Concept Strength Dynamics
- **Initial strength**: 1.0 on creation
- **Access boost**: `min(10.0, strength * 1.02)` per access
- **Adaptive boost**: 1.15× for weak concepts, 1.01× for strong concepts
- **Maximum cap**: 10.0 to prevent runaway growth

### Association Confidence Scoring
- **Explicit patterns** (e.g., "X causes Y"): 0.8-0.9 confidence
- **Co-occurrence** (deep extraction): 0.5 confidence
- **Semantic similarity**: Raw similarity score (0-1)
- **Compositional**: 0.9 confidence (high trust in user-defined compositions)

### Multi-Path Reasoning
- **Consensus threshold**: `max(1, num_paths // 2)` - majority voting
- **Consensus boost**: `total_confidence * (1.0 + path_support * 0.2)`
- **Non-consensus penalty**: `best_confidence * 0.8`
- **Default paths**: 3 (configurable via `num_paths` parameter)

### Storage and Persistence
- **JSON persistence**: Concepts and associations stored as structured JSON
- **Embeddings**: Stored as lists with `embedding_version` for dimension tracking
- **Auto-save**: On API shutdown, manual via `/api/save` or `ai.save()`
- **Auto-load**: On startup with dimension compatibility checking
- **Knowledge directories**: `./sutra_knowledge`, `./hybrid_knowledge`, `./api_knowledge`

## Performance Characteristics

- **Query latency**: 10-50ms average (CPU-only)
- **Learning speed**: Instant (no retraining), ~1000 concepts/sec
- **Memory footprint**: ~0.1KB per concept, 2GB total typical
- **Graph traversal**: O(branches^depth) worst case, typically O(5^max_steps)
- **Hardware requirements**: Standard CPU, 2GB RAM, no GPU needed

## Important Implementation Details

### Spreading Activation Score Propagation
```python
propagated_score = current_score * association.confidence * 0.9
```
The 0.9 decay factor prevents infinite loops and ensures convergence.

### Association Extraction Patterns (order matters)
- Causal: `"(.+?) causes (.+)"`
- Hierarchical: `"(.+?) is (?:a|an) (.+)"`
- Compositional: `"(.+?) contains (.+)"`
- Semantic: `"(.+?) similar to (.+)"`
- Temporal: `"(.+?) before (.+)"`

### Embedding Dimension Compatibility
When switching between `sentence-transformers` (384 dims) and TF-IDF (100 dims), the system automatically re-encodes concepts on first load. This has a performance cost but ensures compatibility.

## Common Development Pitfalls

1. **Forgetting to call `concept.access()`**: Concepts don't strengthen automatically
2. **Missing dimension compatibility**: Always check `if embedding is not None`
3. **Infinite loops in reasoning**: Always maintain `visited` set during graph traversal
4. **Temperature range**: Keep temperatures between 0.1-2.0 to avoid numeric instability

## Recent Research Integrations (Oct 2025)

1. **Adaptive Focus (AdaKD)**: Loss-driven token focusing - difficult concepts get more compute time
2. **Multi-Path Plan Aggregation (MPPA)**: Multiple reasoning paths with consensus voting
3. **Inverse Difficulty Temperature Scaling (IDTS)**: Dynamic temperature based on concept difficulty

These optimizations improve reasoning quality without increasing model size or computational requirements.