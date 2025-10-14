# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Architecture Overview

Sutra AI is an explainable graph-based AI system that positions itself as an alternative to traditional LLMs. The system uses associative reasoning, persistent memory graphs, and optional lightweight semantic embeddings (no GPU required).

### Monorepo Structure

This repository is organized as a **monorepo** with modular packages:

```
sutra-models/
├── packages/                    # Core packages
│   ├── sutra-core/             # ✅ Graph reasoning engine (IMPLEMENTED)
│   ├── sutra-hybrid/           # 🚧 Semantic embeddings (TODO)
│   ├── sutra-api/              # 🚧 REST API service (TODO) 
│   └── sutra-cli/              # 🚧 Command-line interface (TODO)
├── scripts/                     # Development utilities
├── .archive/old-structure/      # Legacy code (preserved)
└── venv/                        # Virtual environment
```

**Current Implementation Status**: The **sutra-core** package is fully implemented and tested (**60/60 tests passing, 96% coverage**). The package is production-ready with zero linter errors. Other packages are in progress (sutra-hybrid structure created) or planned.

### Core Components (sutra-core package)

#### 1. Graph Reasoning Engine
- **Concepts** (`sutra_core.Concept`): Nodes with adaptive strength (1.0-10.0) that strengthen with repeated access
- **Associations** (`sutra_core.Association`): Typed edges (semantic, causal, temporal, hierarchical, compositional) with confidence scores
- **Spreading Activation Search**: BFS-like graph traversal with score propagation for explainable reasoning
- **Multi-Path Plan Aggregation (MPPA)**: Generates diverse reasoning paths and uses consensus voting to prevent single-path derailment
- **Adaptive Focus Learning**: Difficult concepts (strength < 4.0) get stronger reinforcement (1.15×), established concepts (> 7.0) get minimal reinforcement (1.01×)

#### 2. Learning System
- **AssociationExtractor** (`sutra_core.learning.AssociationExtractor`): Pattern-based relationship extraction from natural language
- **AdaptiveLearner** (`sutra_core.learning.AdaptiveLearner`): Real-time knowledge integration with adaptive reinforcement

#### 3. Text Processing
- **Word extraction** (`sutra_core.utils.extract_words`): Tokenization and filtering
- **Association patterns** (`sutra_core.utils.get_association_patterns`): Regex patterns for relationship detection
- **Text cleaning** (`sutra_core.utils.clean_text`): Content normalization
- **Word overlap** (`sutra_core.utils.calculate_word_overlap`): Similarity calculation

#### 4. Error Handling
- **Custom exceptions** (`sutra_core.exceptions`): Comprehensive error hierarchy
  - `SutraError` (base), `ConceptError`, `AssociationError`
  - `LearningError`, `ValidationError`, `StorageError`, `ConfigurationError`

### Legacy Architecture (Archived)

The original monolithic implementations are preserved in `.archive/old-structure/`:
- `sutra_ai.py` - Original core engine
- `hybrid_llm_replacement.py` - Original hybrid system with embeddings
- `api_service.py` - Original FastAPI service

These files contain the complete feature set that is being modularized into the new package structure.

## Development Commands

### Environment Setup

```bash
# One-time setup (creates virtual environment and installs packages)
make setup

# Alternative manual setup
python3 -m venv venv
source venv/bin/activate
pip install -e packages/sutra-core/
pip install -r requirements-dev.txt
```

### Running Demos and Tests

```bash
# Run core functionality demo (new modular structure)
make demo-core

# Run tests (requires virtual environment activation)
source venv/bin/activate
make test-core              # Run sutra-core tests (60/60 passing, 96% coverage)
make test                   # Run all package tests

# Manual test running
PYTHONPATH=packages/sutra-core python -m pytest packages/sutra-core/tests/ -v
```

### Legacy System Commands

```bash
# Run original demo (if needed for reference)
python .archive/old-structure/sutra_ai.py --demo

# Run original hybrid system
python .archive/old-structure/hybrid_llm_replacement.py

# Run original API server
python .archive/old-structure/api_service.py
```

### Package Management

```bash
# Install only core dependencies
pip install -e packages/sutra-core/

# Install development dependencies
pip install -r requirements-dev.txt

# Optional: Enhanced semantic understanding (22MB model)
pip install sentence-transformers
```

### Code Quality and Building

```bash
# Format code (black, isort) - Applied to entire codebase
make format

# Run linting (flake8, mypy) - Currently 0 errors
make lint

# Run full quality checks
make check

# Clean build artifacts
make clean

# Build all packages
make build

# Show all available commands
make help
```

### Code Quality Status

**Current Status (as of Oct 2025)**:
- ✅ **0 flake8 errors** (was 136, now fully resolved)
- ✅ **96% test coverage** (was 80%, +16% improvement)
- ✅ **60 tests passing** (was 10, +50 new tests)
- ✅ **All code formatted** with black and isort
- ✅ **Custom exception hierarchy** implemented

## Key Architectural Patterns

### Package Dependency Structure

```
sutra-core     (base package, no dependencies)
├── sutra-hybrid     <- sutra-core
├── sutra-api        <- sutra-core, sutra-hybrid  
└── sutra-cli        <- sutra-core, sutra-hybrid
```

### Development Workflow

1. **Make changes in appropriate package** (currently only `packages/sutra-core/`)
2. **Run tests**: `make test-core` 
3. **Run demos**: `make demo-core`
4. **Code quality**: `make format && make lint`
5. **Build**: `make build` (when ready)

### Concept Strength Dynamics
- **Initial strength**: 1.0 on creation
- **Access boost**: `min(10.0, strength * 1.02)` per access
- **Adaptive boost**: 1.15× for weak concepts, 1.01× for strong concepts
- **Maximum cap**: 10.0 to prevent runaway growth

### Association Confidence Scoring
- **Explicit patterns** (e.g., "X causes Y"): 0.8-0.9 confidence
- **Co-occurrence** (deep extraction): 0.5 confidence
- **Semantic similarity**: Raw similarity score (0-1)
- **Compositional**: 0.9 confidence (high trust in user-defined compositions)

### Multi-Path Reasoning
- **Consensus threshold**: `max(1, num_paths // 2)` - majority voting
- **Consensus boost**: `total_confidence * (1.0 + path_support * 0.2)`
- **Non-consensus penalty**: `best_confidence * 0.8`
- **Default paths**: 3 (configurable via `num_paths` parameter)

### Storage and Persistence
- **JSON persistence**: Concepts and associations stored as structured JSON
- **Embeddings**: Stored as lists with `embedding_version` for dimension tracking
- **Auto-save**: On API shutdown, manual via `/api/save` or `ai.save()`
- **Auto-load**: On startup with dimension compatibility checking
- **Knowledge directories**: `./sutra_knowledge`, `./hybrid_knowledge`, `./api_knowledge`

## Performance Characteristics

- **Query latency**: 10-50ms average (CPU-only)
- **Learning speed**: Instant (no retraining), ~1000 concepts/sec
- **Memory footprint**: ~0.1KB per concept, 2GB total typical
- **Graph traversal**: O(branches^depth) worst case, typically O(5^max_steps)
- **Hardware requirements**: Standard CPU, 2GB RAM, no GPU needed

## Important Implementation Details

### Spreading Activation Score Propagation
```python
propagated_score = current_score * association.confidence * 0.9
```
The 0.9 decay factor prevents infinite loops and ensures convergence.

### Association Extraction Patterns (order matters)
- Causal: `"(.+?) causes (.+)"`
- Hierarchical: `"(.+?) is (?:a|an) (.+)"`
- Compositional: `"(.+?) contains (.+)"`
- Semantic: `"(.+?) similar to (.+)"`
- Temporal: `"(.+?) before (.+)"`

### Embedding Dimension Compatibility
When switching between `sentence-transformers` (384 dims) and TF-IDF (100 dims), the system automatically re-encodes concepts on first load. This has a performance cost but ensures compatibility.

## Important Implementation Details

### Working with the Modular Structure

```python
# Import from the new modular packages
from sutra_core import (
    Concept,
    Association,
    AssociationType,
    SutraError,  # Custom exceptions available
    ConceptError,
    LearningError,
)
from sutra_core.learning import AdaptiveLearner, AssociationExtractor
from sutra_core.utils import extract_words, clean_text, calculate_word_overlap

# Create concepts with proper access patterns
concept = Concept(id="example", content="example content")
concept.access()  # Strengthens the concept

# Error handling with custom exceptions
try:
    learner.learn_adaptive(content)
except LearningError as e:
    # Handle learning-specific errors
    print(f"Learning failed: {e}")
```

### Single Test Running

```bash
# Run a specific test file
source venv/bin/activate
PYTHONPATH=packages/sutra-core python -m pytest packages/sutra-core/tests/test_basic.py::test_concept_creation -v

# Run tests with coverage
PYTHONPATH=packages/sutra-core python -m pytest packages/sutra-core/tests/ -v --cov=sutra_core --cov-report=html
```

### Package Development

```bash
# Install package in development mode
pip install -e packages/sutra-core/

# After making changes, verify they work
make demo-core
make test-core

# IMPORTANT: Always run formatters before committing
black packages/sutra-core/
isort packages/sutra-core/
flake8 packages/sutra-core/sutra_core/
```

### Test Organization

The test suite is organized by functionality:

- `test_basic.py` - Core concept and association tests (10 tests)
- `test_text_utils.py` - Text processing utilities (27 tests)
- `test_associations.py` - Association extraction (23 tests)

**Total: 60 tests, 96% coverage**

## Common Development Pitfalls

1. **Forgetting to activate virtual environment**: Always run `source venv/bin/activate` before testing
2. **Forgetting to call `concept.access()`**: Concepts don't strengthen automatically - must call during traversal
3. **Missing PYTHONPATH**: When running tests manually, set `PYTHONPATH=packages/sutra-core`
4. **Package import confusion**: Use the new imports (`sutra_core.*`) not the old monolithic ones
5. **Infinite loops in reasoning**: Always maintain `visited` set during graph traversal
6. **Working with archived code**: Legacy implementations are in `.archive/old-structure/` for reference only
7. **Code style violations**: Always run `make format` before committing - we maintain 0 linter errors
8. **Skipping tests**: Always run tests after changes - we maintain 96% coverage

## Recent Research Integrations (Oct 2025)

1. **Adaptive Focus (AdaKD)**: Loss-driven token focusing - difficult concepts get more compute time
2. **Multi-Path Plan Aggregation (MPPA)**: Multiple reasoning paths with consensus voting
3. **Inverse Difficulty Temperature Scaling (IDTS)**: Dynamic temperature based on concept difficulty

These optimizations improve reasoning quality without increasing model size or computational requirements.

## Recent Improvements (Oct 2025)

### Code Quality Overhaul
1. **Fixed 136 style violations** → Now 0 errors
2. **Improved test coverage** from 80% to 96%
3. **Added 50 new tests** across 2 new test files
4. **Implemented custom exception hierarchy**
5. **Applied black and isort** formatting throughout

### Enhanced Testing
- `test_text_utils.py`: Comprehensive text processing tests
- `test_associations.py`: Deep association extraction testing
- Edge case coverage for all utility functions
- Boundary condition testing for learning algorithms

### Package Structure Progress
- ✅ **sutra-core**: Production-ready (96% coverage, 60 tests)
- 🚧 **sutra-hybrid**: Structure created, implementation in progress
- ⏳ **sutra-api**: Planned (FastAPI REST service)
- ⏳ **sutra-cli**: Planned (Click-based CLI)

### Development Best Practices
The codebase now follows enterprise-grade standards:
- **Zero linter errors** (flake8, black, isort)
- **High test coverage** (96% overall)
- **Custom exceptions** for better error handling
- **Comprehensive docstrings** on all public APIs
- **Type hints** throughout the codebase

For detailed progress tracking, see `IMPROVEMENTS_COMPLETED.md`.
