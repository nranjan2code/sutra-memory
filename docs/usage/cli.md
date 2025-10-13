# CLI Usage

Commands:
- Train from text and optionally save:
  - python -m src.cli train "text1" "text2" --base knowledge_store --workspace core --save knowledge_store
- Query:
  - python -m src.cli query cats cheese --base knowledge_store --workspace core --top 10
- Load and print stats:
  - python -m src.cli load knowledge_store --workspace core
- Save snapshot (after load):
  - python -m src.cli save knowledge_store --workspace core

Flags:
- --base: PBSS storage base path (default: knowledge_store)
- --workspace: workspace ID (default: core)
- --top: number of results to display (query)
