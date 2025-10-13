# Roadmap

Near-term:
- Additional agents (structural, conceptual, relational, specialized temporal, meta)
- Multi-hop controls exposed via CLI flags (--hops, --alpha, --topk)
- Persistence snapshots with lightweight diffs or compaction (still PBSS-based)
- Workspace tools (listing and migration helpers)

Mid-term:
- Additional association types emitted by new agents (causal, analogical, contextual, contradictory)
- Path-aware retrieval scoring
- Optional persistence encryption layer for sensitive deployments

Long-term:
- Distributed persistence (sharded PBSS) with aggregate index
- Rich observability (metrics endpoints) without a classical DB
