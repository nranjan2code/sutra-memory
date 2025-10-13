# Architecture Overview

This document summarizes the core components and their responsibilities.

Components:
- BiologicalMemorySystem
  - Owns concepts, associations, memory tiers, token index, and audit integration
  - Enforces forgetting, consolidation, and capacity per tier
  - Provides association de-duplication and reinforcement
- Swarm agents
  - Molecular: token-level extraction (lightweight heuristic)
  - Semantic: sentence extraction and per-text semantic associations
- BiologicalTrainer
  - Orchestrates concurrent agent learning
  - Builds hierarchical and temporal associations
  - Runs maintenance and provides query interface
- Persistence (PBSS)
  - Pure binary nodes for concepts, associations, and audit entries
  - Workspace-aware tagging and filtering on load

Data flow (per batch):
1) Agents process the text stream and create/reinforce concepts
2) Semantic links within each text; hierarchical links sentence→tokens; temporal links across texts
3) Maintenance applies forgetting, pruning, and capacity checks
4) Retrieval uses token index for candidates, seeds on content overlap + memory boost, then multi-hop propagation over association graph

Non-goals:
- No gradient descent/embeddings; the model is association-first
- No traditional database; state is persisted as binary nodes
