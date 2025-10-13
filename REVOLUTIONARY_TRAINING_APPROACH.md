# Biological Training: Technical Design and Current Capabilities

This document explains the system as it exists now—concrete mechanisms, not hype.

## Overview
- Association-first learning: concepts and their relationships form the knowledge substrate.
- No gradient descent; learning happens by creating/reinforcing concepts and associations.
- Biological memory guides strength, consolidation, forgetting, and capacity.
- Multi-agent ingestion (molecular + semantic) runs concurrently; more agents planned.

## Implemented components

### Memory model
- 5 memory tiers: Ephemeral → Short-term → Medium-term → Long-term → Core Knowledge
- Exponential forgetting by time-since-access; very weak non-core concepts are pruned
- Consolidation when strength crosses tier thresholds
- Capacity enforcement per tier (weakest pruned when over capacity)

### Concepts
- One concept per unique content (content index)
- Strength and access_frequency grow via reinforcement on repeated exposure or retrieval
- Emotional weighting supported (used with different agent defaults)

### Associations
- Types currently used: Semantic, Hierarchical (sentence→token), Temporal (across texts)
- Bidirectional edges for easier traversal
- De-duplicated by (source, target, type); repeated co-occurrence reinforces strength with soft cap
- Periodic pruning of weak edges

### Agents (ingestion)
- Molecular agent: token-level features from text with simple normalization and entity heuristic
- Semantic agent: sentence extraction and per-text semantic linking (no cross-history O(n^2))
- Both run concurrently over the same stream

### Retrieval
- Base score: word-overlap content similarity × memory-based boost
- One-hop spreading activation to associated concepts with decay and memory-tier weighting
- Retrieval reinforces seed concepts (use strengthens memory)

### Maintenance
- Ongoing natural forgetting
- Sleep-like consolidation step strengthens frequently accessed concepts and nudges rarely accessed ones down
- Capacity checks run per tier

## Data flow (one batch)
1. Agents ingest text concurrently and create or reinforce sentence and token concepts.
2. Within each text span: sentences inter-link semantically.
3. Sentences connect to their tokens (hierarchical edges).
4. Temporal edges connect sentences across successive texts.
5. Maintenance applies forgetting, pruning, and capacity enforcement.
6. Queries seed content-matched concepts and propagate relevance one hop over associations.

## What this system is not (yet)
- Not a deep learning model; no embeddings or gradient-descent training are used.
- Not multi-hop retrieval beyond one hop (planned).
- Not persistent; all memory is in-process (planned persistence to disk).
- Not using advanced NLP tokenization/segmentation; heuristics are intentionally simple.

## Practical usage
- Minimal runtime dependency (numpy); test suite via pytest.
- Demo: run `demonstrate_biological_training()` or import `BiologicalTrainer` and call `train_from_stream` + `query_knowledge`.

## Roadmap (near-term)
- Add structural, conceptual, relational, specialized temporal, and meta agents
- Multi-hop spreading activation and path-aware scoring
- Persistence layer (JSON/SQLite) and incremental loading
- Additional association types: causal, analogical, contradictory, contextual
- Improved tokenization/NER/POS for molecular agent

## Notes on efficiency
- Learning operations are lightweight: concept/edge upserts and counters.
- Memory/pruning keeps the graph bounded by importance, not just size.
- Retrieval trades off depth (one hop) for speed; multi-hop planned as an optional mode.
