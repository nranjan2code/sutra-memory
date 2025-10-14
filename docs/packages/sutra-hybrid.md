# sutra-hybrid

Hybrid layer combining graph reasoning with embeddings (semantic or TF-IDF).

## Components

- `HybridAI`: main entry point
- Embedding Providers:
  - `SemanticEmbedding` (sentence-transformers, 384 dims)
  - `TfidfEmbedding` (scikit-learn, default 100 dims)
- Storage/persistence

## Features

- Learn content and generate embeddings
- Semantic similarity search (cosine)
- TF-IDF persistence via pickle (vectorizer state)
- Fallback to TF-IDF if semantic model unavailable

## Usage

### Initialize

```python
from sutra_hybrid import HybridAI

# Semantic embeddings (downloads ~22MB model on first use)
ai = HybridAI(use_semantic=True, storage_path="./hybrid_knowledge")

# TF-IDF only (no downloads)
ai = HybridAI(use_semantic=False, storage_path="./hybrid_knowledge")
```

### Learn and Search

```python
concept_id = ai.learn("Photosynthesis converts sunlight into chemical energy")

results = ai.semantic_search("How do plants make energy?", top_k=5, threshold=0.3)
for cid, sim in results:
    print(cid, sim)
```

### Statistics

```python
stats = ai.get_stats()
print(stats)
```

### Persistence

```python
ai.save()
# After process restart
ai2 = HybridAI(use_semantic=False, storage_path="./hybrid_knowledge")
```

Artifacts written to storage_path:
- `concepts.json`
- `associations.json`
- `embeddings.json`
- `tfidf_vectorizer.pkl` (TF-IDF vectorizer state)

## Performance

- TF-IDF learn ~5ms/entry
- Semantic learn ~50ms/entry
- Search (1000 concepts) ~20ms

## Tests

```bash
PYTHONPATH=packages/sutra-hybrid:packages/sutra-core \
  python -m pytest packages/sutra-hybrid/tests -v
```

Persistence tests verify identical embeddings pre/post save/load.

## Notes

- If loading legacy data without vectorizer state, delete storage and re-learn
- For higher-quality search, enable semantic embeddings (`sentence-transformers`)
