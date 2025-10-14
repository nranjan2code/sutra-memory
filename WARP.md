# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

The Revolutionary AI System is a lightweight alternative to Large Language Models (LLMs) that addresses fundamental LLM limitations through algorithmic approaches rather than scaling parametric models. It features real-time learning, explainable reasoning, persistent memory, and 1000x cost efficiency compared to LLMs.

## Common Development Commands

### Core System Operations
```bash
# Run the core system demonstration
python revolutionary_ai.py --demo

# Run comprehensive tests
python test_revolutionary.py

# Start API server (development)
python api_service.py
# or with uvicorn
uvicorn api_service:app --reload --port 8000

# Interactive API documentation
curl http://localhost:8000/docs
```

### Docker Operations
```bash
# Build and run with Docker Compose
docker-compose up --build

# Development mode with hot reload
docker-compose --profile dev up

# Build Docker image
docker build -t revolutionary-ai .

# Run specific commands
docker run revolutionary-ai python3 revolutionary_ai.py --demo
docker run revolutionary-ai python3 test_revolutionary.py
```

### Testing and Validation
```bash
# Run all tests and benchmarks
python test_revolutionary.py

# Test API endpoints (requires server running)
curl -X POST http://localhost:8000/api/learn \
  -H "Content-Type: application/json" \
  -d '{"content": "Test knowledge", "source": "test"}'

curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "max_steps": 5}'

curl http://localhost:8000/api/stats
```

### Knowledge Base Management
```bash
# Knowledge is automatically saved/loaded from ./revolutionary_knowledge/ or ./api_knowledge/
# Manual operations within Python:
# ai.save("backup_knowledge.json")  # Export knowledge
# ai.load("backup_knowledge.json")  # Import knowledge
```

## Architecture Overview

### Core Components

1. **Concept Graph (`revolutionary_ai.py`)**: The heart of the system
   - **Concept class**: Living knowledge entities with vitality, strength, and access tracking
   - **Association class**: Weighted relationships between concepts (semantic, causal, temporal, hierarchical, compositional)
   - **Dynamic strengthening**: Concepts and associations strengthen with use, decay without reinforcement

2. **Spreading Activation Reasoning Engine**: 
   - Multi-hop reasoning through concept associations using priority queue search
   - Complete reasoning chain tracking for 100% explainability
   - No black-box operations - every step is traceable

3. **Real-Time Learning Engine**:
   - Instant knowledge integration without retraining (vs. LLM's expensive retraining)
   - Pattern-based relationship extraction from natural language
   - Automatic concept indexing and association creation

4. **API Service (`api_service.py`)**:
   - FastAPI-based REST endpoints for all system operations
   - Real-time learning endpoints (`/api/learn`, `/api/learn/batch`)
   - Explainable reasoning API (`/api/query`)
   - Compositional understanding (`/api/compose`)
   - System statistics and performance metrics (`/api/stats`, `/api/benchmark`)

### System Data Flow
```
Input Text → Learn() → Concept Creation → Association Extraction → Index Updates
Query → Find Relevant Concepts → Spreading Activation Search → Reasoning Path → Explainable Answer
```

### Key Algorithms

#### Spreading Activation Search
- Priority queue traversal through concept associations
- Score propagation: `propagated_score = current_score * association.confidence * 0.9`
- Builds complete reasoning chains with confidence scores

#### Real-Time Learning
- Creates concepts instantly without training phases
- Extracts relationships using regex patterns for causal, hierarchical, compositional, semantic, and temporal associations
- Updates retrieval indices for O(1) concept lookup

#### Compositional Understanding
- Combines existing concepts to create new understanding
- Creates explicit compositional associations between composed concept and its components

## Development Guidelines

### Code Architecture Patterns
- **Modular design**: Core AI logic (`revolutionary_ai.py`) separate from API layer (`api_service.py`)
- **Dataclass-based models**: Use `@dataclass` for clean data structures (Concept, Association, ReasoningStep, etc.)
- **Explainability first**: Every operation must be traceable and explainable
- **Performance metrics**: Track all operations for benchmarking against LLMs

### Key Classes and Their Roles
- `RevolutionaryAI`: Main system class with learning, reasoning, and composition methods
- `Concept`: Individual knowledge units with dynamic strengthening
- `Association`: Relationships between concepts with confidence scores
- `ReasoningPath`: Complete reasoning chains from query to answer
- `AssociationType`: Enum for relationship types (semantic, causal, temporal, hierarchical, compositional)

### Testing Approach
The system includes comprehensive testing that demonstrates:
- Real-time learning performance (concepts/second)
- Explainable reasoning with complete chains
- Compositional understanding capabilities  
- Performance benchmarks vs LLMs (speed, cost, explainability)
- API endpoint functionality

### Performance Characteristics
- **Learning**: ~400+ concepts/second without retraining
- **Querying**: ~30-50ms average response time (vs 2000ms for GPT-4)
- **Memory**: Unlimited persistent knowledge base growth
- **Cost**: ~$0.0001 per query (vs $0.03 for LLMs)
- **Explainability**: 100% reasoning chain visibility

### Knowledge Storage
- JSON-based persistent storage for concepts and associations
- Automatic saving on API server shutdown
- Directory structure: `./revolutionary_knowledge/` for core system, `./api_knowledge/` for API server
- Knowledge bases can be backed up, restored, and merged

### Extension Points
- **Association Types**: Add new relationship types by extending `AssociationType` enum
- **Reasoning Algorithms**: Override reasoning methods for custom search strategies
- **NLP Integration**: Enhance word extraction with libraries like spaCy or NLTK
- **Custom Learning Patterns**: Add new regex patterns for relationship extraction

## API Integration

### Core Endpoints Structure
- **Learning**: POST `/api/learn` (single), POST `/api/learn/batch` (multiple)
- **Reasoning**: POST `/api/query` with explainable reasoning chains
- **Composition**: POST `/api/compose` for concept combination
- **System**: GET `/api/stats`, POST `/api/benchmark`, GET `/api/health`
- **Demo**: GET `/api/demo/setup`, GET `/api/comparison/llm`

### Request/Response Models
All API models use Pydantic for validation and documentation. Key models:
- `LearnRequest`/`LearnResponse` for knowledge ingestion
- `QueryRequest`/`QueryResponse` for reasoning with explainability
- `ComposeRequest`/`ComposeResponse` for compositional understanding
- `BenchmarkRequest`/`BenchmarkResponse` for performance comparison

## Dependencies and Environment

### Minimal Dependencies
The system intentionally uses minimal dependencies (no heavy ML libraries):
- `fastapi` + `uvicorn`: API framework
- `pydantic`: Data validation
- `pytest` + `httpx` + `requests`: Testing
- No PyTorch, TensorFlow, transformers, or other bloated ML libraries

### Python Version
- Python 3.11+ recommended
- Uses modern Python features like dataclasses, type hints, and asyncio

This architecture demonstrates that revolutionary AI capabilities can be achieved through principled algorithmic approaches rather than scaling parametric models, resulting in a system that's faster, cheaper, more explainable, and more capable of real-time learning than current LLMs.