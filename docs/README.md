# Sutra Models Documentation

Technical documentation for the Sutra Models graph-based AI system.

## Contents

### Getting Started
- [Installation](installation.md) - Setup and dependencies
- [Quick Start](quickstart.md) - Basic usage examples
- [Configuration](configuration.md) - Environment and settings

### Architecture
- [System Overview](architecture/overview.md) - Core concepts and design
- [Graph Structure](architecture/graph.md) - Concepts and associations
- [Learning System](architecture/learning.md) - Knowledge extraction
- [Storage Format](architecture/storage.md) - Persistence mechanisms

### Packages
- [sutra-core](packages/sutra-core.md) - Graph reasoning engine
- [sutra-hybrid](packages/sutra-hybrid.md) - Semantic embeddings
- [sutra-api](packages/sutra-api.md) - REST API service
- [sutra-cli](packages/sutra-cli.md) - Command-line interface

### API Reference
- [REST Endpoints](api/endpoints.md) - HTTP API documentation
- [Request/Response Models](api/models.md) - Data schemas
- [Error Handling](api/errors.md) - Error codes and responses

### Development
- [Setup Guide](development/setup.md) - Development environment
- [Testing](development/testing.md) - Running tests
- [Contributing](development/contributing.md) - Code standards
- [Troubleshooting](development/troubleshooting.md) - Common issues

### Tutorials
- [Basic Learning](tutorials/learning.md) - Teaching the system
- [Reasoning Queries](tutorials/reasoning.md) - Asking questions
- [Semantic Search](tutorials/search.md) - Finding similar concepts
- [API Integration](tutorials/api-usage.md) - Using the REST API

## Project Status

**Current Version**: 1.0.0

| Package | Status | Test Coverage | Tests Passing |
|---------|--------|---------------|---------------|
| sutra-core | Production | 96% | 60/60 |
| sutra-hybrid | Beta | 86% | 9/9 |
| sutra-api | Beta | - | - |
| sutra-cli | Planned | - | - |

## Requirements

- Python 3.8+
- 2GB RAM minimum
- CPU-only (no GPU required)
- Optional: sentence-transformers for semantic embeddings

## Key Features

1. **Graph-based reasoning** - Associative memory with spreading activation
2. **Adaptive learning** - Concepts strengthen with repeated access
3. **Multiple reasoning paths** - Consensus voting prevents errors
4. **TF-IDF fallback** - Works without external models
5. **Persistent storage** - JSON + pickle serialization
6. **REST API** - FastAPI with OpenAPI documentation

## Performance Characteristics

- Query latency: 10-50ms (CPU-only)
- Learning: ~1000 concepts/second
- Memory: ~0.1KB per concept
- Graph traversal: O(branches^depth)

## License

MIT License - See LICENSE file for details.
