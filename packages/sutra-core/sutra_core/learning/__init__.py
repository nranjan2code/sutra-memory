"""
Learning components for the Sutra AI system.

This package contains:
- Association extraction and pattern matching  
- Adaptive focus learning algorithms
- Knowledge integration strategies
"""

from .associations import AssociationExtractor
from .adaptive import AdaptiveLearner

__all__ = [
    'AssociationExtractor',
    'AdaptiveLearner'
]