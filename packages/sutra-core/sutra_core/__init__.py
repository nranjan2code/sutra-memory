"""
Sutra AI Core - Graph-based reasoning system.

This is the core package for the Sutra AI system, providing:
- Concept and Association data structures
- Spreading activation reasoning algorithms
- Multi-Path Plan Aggregation (MPPA) 
- Adaptive focus learning
- Real-time knowledge integration

The system offers a genuine alternative to LLM limitations:
- 100% explainable reasoning paths
- Real-time learning without retraining
- Unlimited persistent memory
- Ultra-efficient CPU-only operation
"""

from .graph import (
    Concept,
    Association,
    AssociationType,
    ReasoningStep, 
    ReasoningPath
)

from .learning import (
    AssociationExtractor,
    AdaptiveLearner
)

from .utils import (
    extract_words,
    get_association_patterns,
    clean_text,
    calculate_word_overlap
)

__version__ = "1.0.0"

__all__ = [
    # Core data structures
    'Concept',
    'Association', 
    'AssociationType',
    'ReasoningStep',
    'ReasoningPath',
    
    # Learning components
    'AssociationExtractor',
    'AdaptiveLearner',
    
    # Utilities
    'extract_words',
    'get_association_patterns',
    'clean_text', 
    'calculate_word_overlap'
]