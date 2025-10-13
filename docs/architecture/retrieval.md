# Retrieval Algorithm

Seed selection:
- Token index provides candidate concept IDs for query tokens; falls back to full scan if needed
- Each candidate gets a base score: content-overlap × (strength × log(1 + access_frequency))

Multi-hop propagation:
- Parameters: hops (depth), alpha (per-hop decay), top_k_neighbors (limit per node)
- For each hop, propagate score to strongest neighbors weighted by:
  - association strength
  - association type weight
  - neighbor memory-type weight
  - optional working-memory boost if neighbor was recently accessed

Working memory:
- Small deque of recently strengthened concept IDs
- Provides a minor boost to reflect recency

Ranking:
- Combine base scores with propagated scores and return top results
