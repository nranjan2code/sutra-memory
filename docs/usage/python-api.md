# Python API Usage

Basic workflow:
- Initialize trainer:
  - t = BiologicalTrainer(base_path="knowledge_store", workspace_id="core")
- Train on a batch:
  - await t.train_from_stream(["Cats chase mice.", "Mice eat cheese."])
- Query:
  - results = t.query_knowledge("cats cheese", max_results=10, hops=2)
- Save/Load:
  - t.save_memory(); t2 = BiologicalTrainer(base_path="knowledge_store", workspace_id="core"); t2.load_memory()

Multi-hop parameters:
- hops: propagation depth
- alpha: per-hop decay
- top_k_neighbors: max neighbors to expand per node

Working memory:
- Recently strengthened concepts receive a small boost in retrieval

Agents:
- Molecular: token-level; Semantic: sentence-level
- Both run concurrently in train_from_stream
