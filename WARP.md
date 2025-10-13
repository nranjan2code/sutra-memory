# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Sutra Models implements a revolutionary AI training paradigm based on biological memory principles and swarm intelligence. This is a research project exploring alternatives to traditional gradient descent training that require massive computational resources.

## Key Architecture Components

### Core Training System
The project centers around the **BiologicalTrainer** class (`src/biological_trainer.py`) which implements:
- **7 Memory Types**: Ephemeral → Short-term → Medium-term → Long-term → Core Knowledge with natural forgetting curves
- **Swarm Intelligence**: Multiple specialized learning agents (Molecular and Semantic agents implemented, with 5 more planned)
- **Associative Network Learning**: Knowledge built through relationships rather than parameter updates
- **Continuous Evolution**: Training that never stops, with biological sleep cycles for consolidation

### Memory System Architecture
- **BiologicalMemorySystem**: Manages knowledge concepts with biological memory principles
- **KnowledgeConcept**: Individual knowledge units with strength, access frequency, and emotional weighting
- **Association**: Relationships between concepts with 7 types: Semantic, Temporal, Causal, Analogical, Hierarchical, Contradictory, Contextual

### Swarm Learning Agents
- **MolecularLearningAgent**: Processes word-level patterns, entities, and syntax
- **SemanticLearningAgent**: Learns meaning and conceptual relationships
- Additional agents planned: Structural, Conceptual, Relational, Temporal, Meta

## Common Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the System
```bash
# Run the biological training demonstration
python3 -c "from src.biological_trainer import demonstrate_biological_training; import asyncio; asyncio.run(demonstrate_biological_training())"

# Import and use the trainer in Python
python3 -c "from src.biological_trainer import BiologicalTrainer; trainer = BiologicalTrainer(); print('Trainer initialized')"
```

### Testing
```bash
# Run tests (when tests are written)
pytest tests/

# Run tests with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_biological_trainer.py
```

### Code Quality
```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/
```

## Development Approach

### Biological Training Principles
This project implements training based on biological intelligence rather than traditional computational approaches:
- **Natural Forgetting**: Weak memories fade automatically, important ones strengthen
- **Spaced Repetition**: Repeated access builds stronger neural pathways  
- **Emotional Weighting**: Important concepts receive enhanced retention
- **Parallel Multi-Scale Processing**: Multiple agents process simultaneously at different granularities

### Key Innovation Areas
1. **Energy Efficiency**: Orders of magnitude less computational requirements than gradient descent
2. **Continuous Learning**: Models that never stop learning and adapting
3. **Associative Understanding**: True comprehension through relationship networks
4. **Emergent Intelligence**: Complex behaviors emerging from simple agent interactions

### Current Implementation Status
- ✅ **Phase 1**: Biological memory system with 7 memory types
- ✅ **Phase 1**: Multi-agent swarm architecture (2/7 agents implemented)
- ✅ **Phase 1**: Associative network infrastructure  
- ✅ **Phase 1**: Continuous learning pipeline
- 🔄 **Phase 2**: Complete 7-agent swarm implementation
- 🔄 **Phase 2**: Advanced association types and traversal

## File Structure Notes

- `src/biological_trainer.py`: Core implementation of the biological training system
- `REVOLUTIONARY_TRAINING_APPROACH.md`: Comprehensive overview of the paradigm shift from traditional training
- `docs/infinite-knowledge-training-paradigm.md`: Technical details on implementation approach
- `data/`: Datasets organized into raw/, processed/, external/ subdirectories
- `models/`: Trained model artifacts (large files ignored by git)

## Development Context

This project is part of a larger research initiative exploring infinite knowledge methodologies. It builds upon concepts from the sutra-swarm project to create AI models that learn like biological systems rather than through computational brute force.

The system demonstrates learning **44 knowledge concepts in 0.000 seconds** with **20 associative connections** formed automatically through parallel molecular + semantic agent processing.