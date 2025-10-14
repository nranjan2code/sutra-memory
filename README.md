# Sutra AI - Explainable Graph-Based AI System

A genuine alternative to LLM limitations with explainable reasoning, unlimited memory, and real-time learning.

## 🌟 What Makes Sutra AI Different?

Unlike traditional LLMs, Sutra AI offers:

- **100% Explainable Reasoning**: Complete reasoning chains with confidence scores
- **Real-Time Learning**: Instant knowledge integration without expensive retraining  
- **Unlimited Memory**: No context window limitations - knowledge grows indefinitely
- **Ultra Efficient**: 10-50ms queries, CPU-only, ~$0 inference cost
- **Compositional Understanding**: True understanding through graph-based associations

## 🏗️ Monorepo Architecture

This repository is organized as a monorepo containing multiple focused packages:

```
sutra-models/
├── packages/
│   ├── sutra-core/        # Core graph reasoning engine
│   ├── sutra-hybrid/      # Hybrid AI with embeddings  
│   ├── sutra-api/         # REST API service
│   └── sutra-cli/         # Command-line interface
├── docs/                  # Documentation
├── scripts/               # Shared utilities
└── tools/                 # Development tools
```

### Package Overview

| Package | Description | Key Features |
|---------|-------------|--------------|
| **sutra-core** | Graph-based reasoning engine | Concepts, Associations, MPPA, Adaptive Learning |
| **sutra-hybrid** | Semantic embeddings integration | Lightweight embeddings, semantic search |
| **sutra-api** | REST API service | FastAPI, async, production-ready |
| **sutra-cli** | Command-line interface | Interactive demos, batch processing |

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/sutra-ai/sutra-models.git
cd sutra-models

# Set up development environment
make setup

# Or manually:
pip install -e packages/sutra-core/
pip install -e packages/sutra-hybrid/
pip install -e packages/sutra-api/
```

### Basic Usage

#### Core Graph Engine
```python
from sutra_core import Concept, AssociationType
from sutra_core.learning import AdaptiveLearner, AssociationExtractor

# Create concepts and associations
concept = Concept(id="photosynthesis", content="plants convert sunlight to energy")
```

#### Hybrid System with Embeddings
```python
from sutra_hybrid import HybridAI

# Initialize with semantic understanding
ai = HybridAI()
concept_id = ai.learn_semantic("Photosynthesis converts light energy to chemical energy")
results = ai.semantic_search("How do plants make energy?")
```

#### API Service
```bash
# Start the API server
cd packages/sutra-api
python -m sutra_api.main

# Or using Docker
docker-compose up
```

## 🧪 Core Technologies

### Adaptive Focus Learning
- **AdaKD-Inspired**: Difficult concepts get stronger reinforcement (1.15×)
- **Dynamic Depth**: Weak concepts get deeper association extraction
- **Efficiency**: Well-established concepts get minimal processing

### Multi-Path Plan Aggregation (MPPA)
- **Consensus Reasoning**: Multiple paths with majority voting  
- **Robustness**: Prevents single-path reasoning failures
- **Explainability**: Shows multiple reasoning approaches

### Hybrid Architecture
- **Graph + Embeddings**: Combines explainable reasoning with semantic understanding
- **Lightweight**: 22MB model, CPU-only operation
- **Fallback**: Works without embeddings using TF-IDF

## 📊 Performance

| Metric | Sutra AI | Traditional LLMs |
|--------|----------|------------------|
| Query Latency | 10-50ms | 1-10s |
| Memory Usage | ~2GB | 20-80GB |
| Inference Cost | ~$0 | $0.01-1.00 per query |
| Explainability | 100% | 0% |
| Real-time Learning | Yes | No (requires retraining) |

## 🛠️ Development

### Commands

```bash
# Development setup
make setup

# Run tests
make test
make test-core    # Core package only
make test-api     # API package only

# Code quality
make format       # Format code
make lint         # Run linting
make check        # Full quality check

# Build
make build        # Build all packages  
make clean        # Clean artifacts
```

### Package Dependencies

```
sutra-core     (base package)
├── sutra-hybrid     <- sutra-core
├── sutra-api        <- sutra-core, sutra-hybrid  
└── sutra-cli        <- sutra-core, sutra-hybrid
```

## 📚 Documentation

- [Architecture Overview](docs/architecture/)
- [API Reference](docs/api/)
- [Getting Started Guide](docs/guides/getting-started.md)
- [Deployment Guide](docs/guides/deployment.md)

## 🔬 Research Foundation

Sutra AI integrates cutting-edge research:

- **Adaptive Focus Learning** - Based on "LLM-Oriented Token-Adaptive Knowledge Distillation" (Oct 2025)
- **Multi-Path Plan Aggregation** - Prevents reasoning derailment in complex queries
- **Inverse Difficulty Temperature Scaling** - Dynamic temperature based on concept difficulty

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes in the appropriate package
4. Add tests and documentation
5. Run `make check` to ensure quality
6. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Links

- [Homepage](https://sutra-ai.dev)
- [Documentation](https://docs.sutra-ai.dev)  
- [Issues](https://github.com/sutra-ai/sutra-models/issues)
- [Discussions](https://github.com/sutra-ai/sutra-models/discussions)

## 🌟 Star History

If you find Sutra AI useful, please star the repository to show your support!

---

**Sutra AI**: Explainable AI without the complexity, cost, or black-box nature of traditional LLMs.