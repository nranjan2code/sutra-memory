# Configuration

All global defaults live in src/config.py via a Settings dataclass. You can tune retrieval and memory behavior here.

Key fields:
- BASE_PATH: default PBSS storage base path
- WORKSPACE_ID: default workspace for tagging and filtering nodes
- AUDIT_ENABLED: enable PBSS audit logging
- RETRIEVAL_HOPS: default propagation depth for query_knowledge
- RETRIEVAL_ALPHA: per-hop decay for propagation
- RETRIEVAL_TOPK_NEIGHBORS: limit of neighbors per node
- WORKING_MEMORY_SIZE: size of recent concept deque
- WORKING_MEMORY_BOOST: minor boost applied to recently accessed concepts
- MEMORY_TYPE_WEIGHTS: per-tier weighting applied in retrieval
- ASSOCIATION_TYPE_WEIGHTS: per-association-type propagation weights

Override strategy:
- Edit src/config.py and restart the process (values are read on module load)
- Or pass base_path/workspace_id/audit_enabled to BiologicalTrainer
