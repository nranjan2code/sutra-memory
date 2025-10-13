# Association Types and Policies

Association types (bidirectional, reinforced, pruned when weak):
- Semantic: sentence co-occurrence within a text
- Hierarchical: sentence → token edges created per text
- Temporal: across successive texts and across batches
- Causal/Analogical/Contextual/Contradictory: weights defined for retrieval, may be produced by future agents

De-duplication and reinforcement:
- Associations are keyed by (source, target, type) and stored once
- Repeated creation increments reinforcement_count and increases strength nonlinearly (soft cap)

Propagation weights (used in retrieval):
- semantic: 1.0; hierarchical: 0.9; temporal: 0.7; causal: 1.1; analogical: 0.9; contextual: 0.8; contradictory: 0.2
