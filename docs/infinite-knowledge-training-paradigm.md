# Infinite Knowledge Training Paradigm (Implementation Overview)

This document describes how the current implementation realizes an association-first, biologically inspired training paradigm, and what remains to be built.

## Goals
- Replace heavy parameter optimization with lightweight, continuous association-building.
- Use biological memory to prioritize, consolidate, and forget.
- Enable multi-agent, multi-scale ingestion that evolves knowledge structures over time.

## Current implementation

### Memory
- 5 tiers with decay and consolidation thresholds
- Exponential forgetting by time-since-access; pruning of very weak, non-core concepts
- Capacity enforcement prunes weakest within a tier

### Concepts
- Content-indexed de-duplication: one concept per unique content
- Reinforcement on re-exposure (strength and access_frequency)
- Emotional weighting available to bias reinforcement

### Associations
- Semantic: per-text sentence co-occurrence
- Hierarchical: sentence → token edges within each text
- Temporal: links across successive texts and batches
- Bidirectional, de-duplicated, reinforced edges with soft-capped strength

### Agents
- Molecular: lightweight token extraction and simple entity heuristic
- Semantic: sentence segmentation and per-text semantic linking
- Agents run concurrently on the same stream

### Retrieval
- Seed: content overlap × memory boost
- One-hop spreading activation over associations with decay (alpha) and memory-tier weights
- Reinforces accessed seed concepts (use strengthens memory)

### Maintenance
- Natural forgetting, weak-edge pruning, capacity checks
- Sleep-like consolidation step to strengthen frequently accessed items

## Usage
- Install dependencies: `numpy` at runtime; `pytest/black/flake8/isort` for development.
- Run the demo or import and drive the trainer with your own text stream.

## Planned extensions
- Additional association types: causal, analogical, contradictory, contextual
- Additional agents: structural, conceptual, relational, temporal (specialized), meta
- Multi-hop spreading activation with path-aware scoring and controls
- Persistence (JSON/SQLite), incremental save/load, snapshotting
- Better tokenization/segmentation, light NER/POS for molecular agent

## Design notes
- Efficiency comes from de-duplication, reinforcement, and bounded memory via pruning.
- Graph grows where usage reinforces value; weak, unused edges and concepts fade away.
- Retrieval leverages structure without expensive model inference.

## Limitations
- In-memory only; restart loses state.
- One-hop spreading activation; deeper traversal is planned.
- Heuristic NLP; no embeddings are used at this stage.

This is an evolving implementation; contributions should preserve the core principles: biological memory, association-first learning, and concurrent multi-agent ingestion.
