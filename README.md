# Sutra Models

Biological Training System prototype focused on associative learning, biological memory, and swarm-style multi-agent processing. No gradient-descent training; knowledge is represented as concepts and reinforced associations that evolve continuously.

Status: Prototype POC with production-grade associative engine.

## What’s implemented

- Biological memory system
  - 5 memory types: Ephemeral, Short-term, Medium-term, Long-term, Core Knowledge
  - Exponential forgetting with pruning of very weak, non-core concepts
  - Consolidation: concepts move up tiers when strengthened
  - Capacity enforcement per tier (prunes weakest when above capacity)
- Concepts and deduplication
  - One concept per unique content (content index)
  - Reinforcement on repeated exposure (strength and access frequency grow)
- Associations (bidirectional, reinforced)
  - Types used today: Semantic, Hierarchical (sentence→token), Temporal (across successive texts)
  - De-duplicated edge set with reinforcement and soft-capped strength
  - Weak association pruning
- Swarm learning (2 agents for now)
  - Molecular agent: token-level patterns (lightweight tokenization, entity heuristic)
  - Semantic agent: sentence-level concepts with per-text semantic linking (no cross-history O(n^2))
- Graph-aware retrieval
  - Base content match + memory-based boost
  - One-hop spreading activation across associations with memory-type weighting
  - Retrieval reinforces accessed seeds (use strengthens memory)
- Async training and maintenance
  - Parallel agent learning
  - Sleep-like consolidation step
  - Continuous training API
- Tests and minimal dependencies
  - pytest tests for dedup/strengthening, temporal links, retrieval via associations, and association de-duplication
  - Minimal runtime dependency: numpy only (plus dev tools)

## Project structure

```
sutra-models/
├── src/                  # Core implementation
├── tests/                # Pytest suite
├── models/               # Artifacts (if any)
├── data/                 # Datasets (if any)
├── docs/                 # Documentation
├── requirements.txt      # Python dependencies (minimal)
└── README.md             # This file
```

## Installation

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Quickstart

Run the demonstration:

```bash
python3 -c "from src.biological_trainer import demonstrate_biological_training; import asyncio; asyncio.run(demonstrate_biological_training())"
```

Use the trainer programmatically:

```python
from src.biological_trainer import BiologicalTrainer
import asyncio

async def main():
    trainer = BiologicalTrainer()
    await trainer.train_from_stream([
        "Cats chase mice.",
        "Mice eat cheese.",
    ])
    results = trainer.query_knowledge("cats cheese", max_results=5)
    for r in results:
        print(r["content"], r["relevance"])  # spreading activation should surface linked content

asyncio.run(main())
```

## Documentation

- docs/README.md — documentation index
- docs/architecture/overview.md — high-level architecture
- docs/architecture/memory.md — memory model and consolidation
- docs/architecture/associations.md — association types and policies
- docs/architecture/retrieval.md — retrieval algorithm and multi-hop propagation
- docs/architecture/persistence.md — PBSS persistence, workspaces, and audit
- docs/usage/quickstart.md — install and quickstart
- docs/usage/cli.md — CLI usage
- docs/usage/python-api.md — Python API usage
- docs/configuration.md — global settings in src/config.py
- docs/testing.md — tests and how to run them
- docs/roadmap.md — planned work

## Development

- Run tests:
  ```bash
  pytest -q
  ```
- Format and lint:
  ```bash
  black src/ tests/
  isort src/ tests/
  flake8 src/ tests/
  ```

## Limitations (current)
- Only 2 agents implemented (molecular, semantic); other agents are planned.
- Retrieval uses one-hop spreading activation (multi-hop is an obvious extension).
- Persistence is in-memory only (no on-disk graph yet).
- Tokenization and sentence splitting are intentionally simple.

## Roadmap
- Additional agents: structural, conceptual, relational, temporal (specialized), meta
- Multi-hop spreading activation and path-aware retrieval
- Persistence (JSON/SQLite) and incremental loading
- Richer association policies (causal, analogical, contradictory, contextual)
- Better tokenization/segmentation and basic NER/POS for molecular agent

## License
TBD

## Changelog
- 2025-10: Production-grade associative engine: concept/association dedup + reinforcement, per-text links, hierarchical + temporal edges, capacity + forgetting, graph-aware retrieval, tests, and minimal dependencies.
