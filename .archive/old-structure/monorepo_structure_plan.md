# Sutra AI Monorepo Structure Plan

## Current Structure Issues
- All Python files in root directory
- No proper package structure
- Mixed concerns (core, hybrid, API) in same level
- No separation for future projects
- Documentation scattered

## Proposed Monorepo Structure

```
sutra-models/                          # Root monorepo
├── README.md                          # Main monorepo README
├── CHANGELOG.md                       # Monorepo changelog
├── .gitignore                         # Global gitignore
├── pyproject.toml                     # Workspace configuration
├── requirements-dev.txt               # Development dependencies
├── Makefile                           # Common commands
│
├── packages/                          # All packages/projects
│   ├── sutra-core/                    # Core graph AI engine
│   │   ├── README.md
│   │   ├── pyproject.toml
│   │   ├── requirements.txt
│   │   ├── sutra_core/
│   │   │   ├── __init__.py
│   │   │   ├── graph/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── concepts.py        # Concept & Association classes
│   │   │   │   ├── reasoning.py       # Spreading activation, MPPA
│   │   │   │   └── storage.py         # Persistence layer
│   │   │   ├── learning/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── adaptive.py        # Adaptive focus learning
│   │   │   │   └── associations.py    # Association extraction
│   │   │   └── utils/
│   │   │       ├── __init__.py
│   │   │       └── text.py            # Text processing utilities
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── test_concepts.py
│   │   │   ├── test_reasoning.py
│   │   │   └── test_learning.py
│   │   └── examples/
│   │       └── basic_demo.py
│   │
│   ├── sutra-hybrid/                  # Hybrid AI with embeddings
│   │   ├── README.md
│   │   ├── pyproject.toml
│   │   ├── requirements.txt
│   │   ├── sutra_hybrid/
│   │   │   ├── __init__.py
│   │   │   ├── embeddings/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── lightweight.py     # LightweightEmbeddings
│   │   │   │   └── semantic.py        # Semantic concept extensions
│   │   │   ├── search/
│   │   │   │   ├── __init__.py
│   │   │   │   └── semantic.py        # Semantic search
│   │   │   └── generation/
│   │   │       ├── __init__.py
│   │   │       └── templates.py       # Response generation
│   │   ├── tests/
│   │   └── examples/
│   │
│   ├── sutra-api/                     # REST API service
│   │   ├── README.md
│   │   ├── pyproject.toml
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   ├── sutra_api/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                # FastAPI app
│   │   │   ├── routers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── learning.py        # Learning endpoints
│   │   │   │   ├── reasoning.py       # Query endpoints
│   │   │   │   └── admin.py           # Admin endpoints
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── requests.py        # Pydantic request models
│   │   │   │   └── responses.py       # Pydantic response models
│   │   │   └── services/
│   │   │       ├── __init__.py
│   │   │       └── ai_service.py      # AI instance management
│   │   ├── tests/
│   │   └── examples/
│   │       └── client_example.py
│   │
│   └── sutra-cli/                     # Command-line interface (future)
│       ├── README.md
│       ├── pyproject.toml
│       ├── requirements.txt
│       └── sutra_cli/
│           ├── __init__.py
│           └── main.py
│
├── docs/                              # Documentation
│   ├── README.md
│   ├── architecture/
│   │   ├── core-concepts.md
│   │   ├── reasoning-algorithms.md
│   │   └── hybrid-approach.md
│   ├── api/
│   │   └── openapi-spec.yml
│   ├── guides/
│   │   ├── getting-started.md
│   │   ├── deployment.md
│   │   └── best-practices.md
│   └── research/
│       ├── swot-analysis.md
│       └── benchmarks.md
│
├── scripts/                           # Shared scripts
│   ├── setup-dev.sh                   # Development environment setup
│   ├── run-tests.sh                   # Run all tests
│   ├── build-all.sh                   # Build all packages
│   └── deploy.sh                      # Deployment script
│
├── tools/                             # Development tools
│   ├── linting/
│   │   ├── .pylintrc
│   │   └── .flake8
│   └── ci/
│       └── github-actions/
│
└── .github/                           # GitHub configuration
    ├── workflows/
    │   ├── test.yml                   # CI/CD pipeline
    │   ├── build.yml
    │   └── release.yml
    └── ISSUE_TEMPLATE/
```

## Migration Benefits

1. **Separation of Concerns**: Each package has clear responsibility
2. **Independent Development**: Packages can be developed/released independently  
3. **Proper Dependencies**: Clear dependency management between packages
4. **Scalability**: Easy to add new projects (sutra-ui, sutra-benchmarks, etc.)
5. **Testing**: Isolated test suites for each component
6. **Documentation**: Organized docs structure
7. **CI/CD**: Package-specific build and deployment pipelines

## Package Dependencies

```
sutra-core (base package)
├── No internal dependencies
├── External: numpy, json, hashlib

sutra-hybrid 
├── Depends on: sutra-core
├── External: sentence-transformers (optional), numpy

sutra-api
├── Depends on: sutra-core, sutra-hybrid
├── External: fastapi, uvicorn, pydantic

sutra-cli
├── Depends on: sutra-core, sutra-hybrid
├── External: click, rich
```

## Implementation Steps

1. Create new directory structure
2. Split current files into logical modules
3. Create proper `__init__.py` files with exports
4. Update import statements
5. Create package configuration files
6. Update documentation
7. Test all functionality
8. Update CI/CD pipelines