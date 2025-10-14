# sutra-core

Core graph reasoning engine. Production-ready.

## Features

- Concepts (nodes) with adaptive strength (1.0-10.0)
- Associations (edges) with types and confidence
- Spreading activation traversal
- Adaptive learning (strength boost depends on difficulty)
- Text utilities (tokenization, normalization)
- Custom exception hierarchy

## Public APIs

### Core Types

- `sutra_core.Concept`
- `sutra_core.Association`
- `sutra_core.AssociationType`
- `sutra_core.learning.AdaptiveLearner`
- `sutra_core.learning.AssociationExtractor`
- `sutra_core.utils` (extract_words, clean_text, calculate_word_overlap)
- `sutra_core.exceptions` (SutraError and subclasses)

## Usage

### Create and Access Concept

```python
from sutra_core import Concept

c = Concept(id="photosynthesis", content="Photosynthesis converts sunlight")
print(c.strength)   # 1.0
c.access()
print(c.strength)   # 1.02 (access boost)
```

### Learn Knowledge (Adaptive)

```python
from collections import defaultdict
from sutra_core.learning import AdaptiveLearner, AssociationExtractor

concepts = {}
associations = {}
word_to_concepts = defaultdict(set)
concept_neighbors = defaultdict(set)

extractor = AssociationExtractor(
    concepts, word_to_concepts, concept_neighbors, associations
)
learner = AdaptiveLearner(concepts, extractor)

concept_id = learner.learn_adaptive(
    "Enzymes are proteins that speed up reactions",
    source="biology_textbook"
)
print(concept_id)
print(len(associations))
```

### Association Types

```python
from sutra_core import AssociationType

print(list(AssociationType))
# semantic, causal, temporal, hierarchical, compositional
```

## Exceptions

- `SutraError` (base)
- `ConceptError`
- `AssociationError`
- `LearningError`
- `ValidationError`
- `StorageError`
- `ConfigurationError`

## Tests

- Location: `packages/sutra-core/tests/`
- Run:

```bash
PYTHONPATH=packages/sutra-core python -m pytest packages/sutra-core/tests -v
```

Coverage: ~96%

## Notes

- Maintain a `visited` set during traversal to avoid cycles
- Strength max is 10.0 to prevent runaway growth
- Decay factor during propagation: 0.9 per hop
