# Installation

## Prerequisites

- Python 3.8 or higher
- pip package manager
- 2GB RAM minimum
- 500MB disk space

## Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

## Package Installation

### Core Package Only

```bash
pip install -e packages/sutra-core/
```

Provides:
- Graph reasoning engine
- Adaptive learning
- Association extraction
- Text utilities

### Hybrid Package (with Embeddings)

```bash
# Without semantic embeddings (TF-IDF only)
pip install -e packages/sutra-hybrid/

# With semantic embeddings (recommended)
pip install -e "packages/sutra-hybrid/[embeddings]"
```

Adds:
- Semantic similarity search
- TF-IDF or transformer embeddings
- Hybrid reasoning strategies

### API Package

```bash
pip install -e packages/sutra-api/
```

Provides:
- REST API server (FastAPI)
- HTTP endpoints for all operations
- OpenAPI documentation

### CLI Package (Planned)

```bash
pip install -e packages/sutra-cli/
```

Provides:
- Command-line interface
- Interactive mode
- Batch operations

## Development Installation

```bash
# Install all packages with dev dependencies
pip install -r requirements-dev.txt

# Install all packages in editable mode
make setup
```

Development tools:
- pytest (testing)
- black (code formatting)
- isort (import sorting)
- flake8 (linting)
- mypy (type checking)

## Verify Installation

### Test Core Package

```bash
python -c "from sutra_core import Concept, AdaptiveLearner; print('Core OK')"
```

### Test Hybrid Package

```bash
python -c "from sutra_hybrid import HybridAI; print('Hybrid OK')"
```

### Test API Package

```bash
python -c "from sutra_api import settings; print('API OK')"
```

### Run Test Suite

```bash
# Test core package
PYTHONPATH=packages/sutra-core pytest packages/sutra-core/tests/ -v

# Test hybrid package
PYTHONPATH=packages/sutra-hybrid:packages/sutra-core pytest packages/sutra-hybrid/tests/ -v

# Or use Makefile
make test-core
make test
```

## Optional Dependencies

### Semantic Embeddings

For high-quality semantic understanding:

```bash
pip install sentence-transformers
```

- Model: all-MiniLM-L6-v2 (22MB)
- Dimension: 384
- Download: Automatic on first use

Without this, system falls back to TF-IDF (scikit-learn).

### API Server

Already included with sutra-api:

```bash
pip install fastapi uvicorn[standard]
```

## Troubleshooting

### Import Errors

```bash
# Ensure PYTHONPATH includes package directories
export PYTHONPATH="packages/sutra-core:packages/sutra-hybrid"
```

### Virtual Environment Issues

```bash
# Recreate environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

### Test Failures

```bash
# Clean pytest cache
rm -rf .pytest_cache
rm -rf packages/*/.pytest_cache

# Re-run with verbose output
pytest packages/sutra-core/tests/ -vv
```

### Memory Issues

If you encounter memory issues:

1. Use TF-IDF instead of semantic embeddings
2. Limit max_concepts in configuration
3. Increase system swap space

## Uninstallation

```bash
pip uninstall sutra-core sutra-hybrid sutra-api sutra-cli -y
```

## Next Steps

- [Quick Start Guide](quickstart.md)
- [Configuration Options](configuration.md)
- [Basic Tutorial](tutorials/learning.md)
