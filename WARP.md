# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# One-command setup (creates venv and installs packages)
make setup

# Manual setup (alternative)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e packages/sutra-core/
pip install -r requirements-dev.txt
```

### Testing & Quality
```bash
# Run core tests (sutra-core - main implementation)
make test-core

# Run all tests (when other packages are implemented)
make test

# Code formatting and linting
make format    # Auto-format with black and isort
make lint      # Lint core package (flake8 + mypy)
make lint-all  # Lint all packages
make check     # Run format + lint + test

# Single test commands (requires venv activation)
PYTHONPATH=packages/sutra-core python -m pytest packages/sutra-core/tests/test_basic.py -v
PYTHONPATH=packages/sutra-core python -m pytest packages/sutra-core/tests/ -k "test_text" -v
```

### Development Demos
```bash
# Run basic core functionality demo
make demo-core

# Run advanced AI reasoning demo (new features)
make demo-ai
```

### Build & Packaging
```bash
make build     # Build all packages
make clean     # Clean build artifacts and caches
```

## Architecture Overview

### Monorepo Structure
This is a Python monorepo with multiple packages in different development stages:

- **`packages/sutra-core/`**: Graph-based reasoning engine (✅ IMPLEMENTED - 60/60 tests passing)
- **`packages/sutra-hybrid/`**: Semantic embeddings integration (🚧 TODO)
- **`packages/sutra-api/`**: REST API service (🚧 TODO)
- **`packages/sutra-cli/`**: Command-line interface (🚧 TODO)
- **`packages/sutra-storage/`**: Rust-based storage backend (🚧 IN PROGRESS)

### Core Package Architecture (`packages/sutra-core/`)
```
sutra_core/
├── graph/           # Core data structures (Concept, Association, ReasoningPath)
├── learning/        # Adaptive learning algorithms and association extraction
├── reasoning/       # Multi-Path Plan Aggregation (MPPA) and reasoning engine
├── utils/           # Text processing (spaCy integration optional)
├── indexing/        # HNSW vector indexing (optional, requires hnswlib)
├── storage/         # Persistence layer
├── api/             # Internal API interfaces
└── services/        # High-level service abstractions
```

### Key Concepts

#### Graph-Based Reasoning System
- **Concepts**: Knowledge units with adaptive strength learning (max 10.0)
- **Associations**: Typed relationships (semantic, causal, temporal, hierarchical, compositional)
- **Reasoning Paths**: Explainable chains of associations between concepts

#### Adaptive Learning Engine
- Research-based adaptive focus learning (AdaKD-inspired)
- Difficult concepts (strength < 4.0): Strong reinforcement (1.15×)
- Easy concepts (strength > 7.0): Minimal reinforcement (1.01×)
- Real-time knowledge updates without retraining

#### Optional Dependencies
- **spaCy** (en_core_web_sm): Enhanced NLP with lemmatization, NER, negation detection
  - Graceful fallback to basic word extraction if unavailable
  - Install with: `pip install -e "packages/sutra-core/[nlp]"`
- **hnswlib**: Vector indexing for O(log N) semantic search
  - Install with: `pip install hnswlib`

## Virtual Environment Management

**IMPORTANT**: Always activate the virtual environment before running tests or development commands:
```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

Most make commands will automatically source the venv, but manual pytest commands require activation.

## Development Workflow

1. **Setup**: Run `make setup` for initial environment
2. **Develop**: Make changes primarily in `packages/sutra-core/`
3. **Test**: Run `make test-core` frequently during development
4. **Format**: Use `make format` before commits
5. **Quality**: Ensure `make check` passes before PR

## Package Dependencies

```
sutra-core     <- (base package - fully functional)
sutra-hybrid   <- sutra-core (planned)
sutra-api      <- sutra-core, sutra-hybrid (planned)
sutra-cli      <- sutra-core, sutra-hybrid (planned)
```

## Testing Strategy

- **Core package**: 60/60 tests passing with ~90%+ coverage
- Tests located in `packages/sutra-core/tests/`
- Run specific test patterns with `-k` flag
- Coverage reports with `--cov-report=html --cov-report=term`

## Code Quality Standards

- **Type coverage**: 95% (mypy strict mode)
- **Line length**: 88 characters (black)
- **Import organization**: isort with black profile
- **Docstrings**: Google style for all public APIs
- **Input validation**: Comprehensive validation with DOS protection

## Performance Characteristics

- **Memory**: ~0.1KB per concept
- **Learning**: ~1000 concepts/second
- **Access**: O(1) concept lookup via word indexing
- **Search**: O(branches^depth) graph traversal, O(log N) with HNSW indexing
- **CPU-only**: No GPU requirements, scales to 100K+ concepts

## Research Foundation

Built on cutting-edge research:
- **Adaptive Focus Learning**: "LLM-Oriented Token-Adaptive Knowledge Distillation" (Oct 2025)
- **Loss-Driven Token Focusing**: More compute for difficult concepts
- **Multi-Path Plan Aggregation (MPPA)**: Consensus-based reasoning with confidence scoring