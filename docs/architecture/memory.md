# Memory Model

The memory system uses five tiers with different decay and consolidation thresholds:
- Ephemeral → Short-term → Medium-term → Long-term → Core Knowledge

Key behaviors:
- Exponential forgetting based on time since last access
- Consolidation when strength passes tier threshold
- Capacity enforcement per tier by pruning weakest (low strength, low access, older last_access)
- Emotional weighting influences strengthening

Strengthening:
- strengthen_concept increments access_frequency, updates last_access,
  and increases strength with a logarithmic factor modulated by emotional_weight.

Consolidation audit:
- Transitions are recorded by the audit logger when enabled.

Indexing:
- Content-indexed de-duplication (one concept per unique content)
- Token inverted index for fast candidate selection in retrieval
