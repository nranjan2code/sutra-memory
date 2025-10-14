"""
Main reasoning engine for Sutra AI system.

Orchestrates all reasoning components to provide AI-level capabilities:
- Integrates path-finding, MPPA, and query processing
- Provides simple API for complex reasoning tasks
- Handles semantic understanding and knowledge integration
- Optimizes performance with caching and indexing
"""

import logging
import time
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

from ..graph.concepts import Association, Concept
from ..learning.adaptive import AdaptiveLearner
from ..learning.associations import AssociationExtractor
from .mppa import ConsensusResult, MultiPathAggregator
from .paths import PathFinder
from .query import QueryProcessor

logger = logging.getLogger(__name__)


class ReasoningEngine:
    """
    Main AI reasoning engine that coordinates all components.
    
    This is the primary interface for AI-level reasoning capabilities:
    - Natural language query processing
    - Multi-path reasoning with consensus
    - Real-time learning and knowledge integration
    - Explainable AI with confidence scoring
    """
    
    def __init__(self, enable_caching: bool = True, max_cache_size: int = 1000):
        """
        Initialize the reasoning engine.
        
        Args:
            enable_caching: Enable query result caching
            max_cache_size: Maximum number of cached results
        """
        # Core data structures
        self.concepts: Dict[str, Concept] = {}
        self.associations: Dict[Tuple[str, str], Association] = {}
        self.concept_neighbors: Dict[str, Set[str]] = defaultdict(set)
        self.word_to_concepts: Dict[str, Set[str]] = defaultdict(set)
        
        # Initialize components
        self.association_extractor = AssociationExtractor(
            self.concepts, 
            self.word_to_concepts,
            self.concept_neighbors,
            self.associations
        )
        
        self.adaptive_learner = AdaptiveLearner(
            self.concepts,
            self.association_extractor
        )
        
        self.path_finder = PathFinder(
            self.concepts,
            self.associations, 
            self.concept_neighbors
        )
        
        self.mppa = MultiPathAggregator()
        
        self.query_processor = QueryProcessor(
            self.concepts,
            self.associations,
            self.concept_neighbors,
            self.association_extractor,
            self.path_finder,
            self.mppa
        )
        
        # Performance optimization
        self.enable_caching = enable_caching
        self.query_cache: Dict[str, ConsensusResult] = {}
        self.max_cache_size = max_cache_size
        
        # Statistics
        self.query_count = 0
        self.learning_events = 0
        self.cache_hits = 0
        
        logger.info("Sutra AI Reasoning Engine initialized")
    
    def ask(self, question: str, **kwargs) -> ConsensusResult:
        """
        Ask the AI a question and get an explainable answer.
        
        This is the main AI interface - processes natural language questions
        and returns comprehensive reasoning with explanations.
        
        Args:
            question: Natural language question
            **kwargs: Additional options (num_paths, etc.)
            
        Returns:
            Consensus result with answer, confidence, and explanation
        """
        self.query_count += 1
        
        # Check cache first
        if self.enable_caching and question in self.query_cache:
            self.cache_hits += 1
            logger.debug(f"Cache hit for query: {question[:50]}...")
            return self.query_cache[question]
        
        # Process query through full reasoning pipeline
        result = self.query_processor.process_query(question, **kwargs)
        
        # Cache result
        if self.enable_caching:
            self._update_cache(question, result)
        
        # Log performance
        logger.info(
            f"Query processed: {result.confidence:.2f} confidence, "
            f"{result.consensus_strength:.2f} consensus"
        )
        
        return result
    
    def learn(self, content: str, source: Optional[str] = None, **kwargs) -> str:
        """
        Learn new knowledge and integrate it into the reasoning system.
        
        Args:
            content: Knowledge content to learn
            source: Source of the knowledge
            **kwargs: Additional learning options
            
        Returns:
            Concept ID of learned knowledge
        """
        self.learning_events += 1
        
        # Learn through adaptive system
        concept_id = self.adaptive_learner.learn_adaptive(
            content, source=source, **kwargs
        )
        
        # Update neighbor mappings
        self._update_concept_neighbors(concept_id)
        
        # Clear relevant cache entries
        if self.enable_caching:
            self._invalidate_cache()
        
        logger.debug(f"Learned new concept: {content[:50]}... (ID: {concept_id[:8]})")
        
        return concept_id
    
    def explain_reasoning(self, question: str, detailed: bool = False) -> Dict:
        """
        Get detailed explanation of how the AI reasoned about a question.
        
        Args:
            question: Question to explain reasoning for
            detailed: Include detailed path information
            
        Returns:
            Dictionary with reasoning explanation details
        """
        result = self.ask(question)
        
        explanation = {
            "question": question,
            "answer": result.primary_answer,
            "confidence": result.confidence,
            "consensus_strength": result.consensus_strength,
            "reasoning_explanation": result.reasoning_explanation,
            "alternative_answers": result.alternative_answers,
            "reasoning_robustness": self.mppa.analyze_reasoning_robustness(result)
        }
        
        if detailed and result.supporting_paths:
            explanation["detailed_paths"] = []
            for i, path in enumerate(result.supporting_paths):
                path_detail = {
                    "path_number": i + 1,
                    "confidence": path.confidence,
                    "steps": [
                        {
                            "step": step.step_number,
                            "from": step.source_concept,
                            "relation": step.relation,
                            "to": step.target_concept,
                            "confidence": step.confidence
                        }
                        for step in path.steps
                    ]
                }
                explanation["detailed_paths"].append(path_detail)
        
        return explanation
    
    def get_concept_info(self, concept_id: str) -> Optional[Dict]:
        """Get information about a specific concept."""
        
        if concept_id not in self.concepts:
            return None
            
        concept = self.concepts[concept_id]
        neighbors = self.concept_neighbors.get(concept_id, set())
        
        return {
            "id": concept.id,
            "content": concept.content,
            "strength": concept.strength,
            "confidence": concept.confidence,
            "access_count": concept.access_count,
            "created": concept.created,
            "last_accessed": concept.last_accessed,
            "source": concept.source,
            "category": concept.category,
            "neighbor_count": len(neighbors),
            "neighbors": list(neighbors)[:10]  # Limit for display
        }
    
    def search_concepts(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for concepts matching a query."""
        
        results = []
        query_words = set(query.lower().split())
        
        # Score concepts by relevance
        concept_scores = []
        for concept_id, concept in self.concepts.items():
            content_words = set(concept.content.lower().split())
            overlap = len(query_words & content_words)
            
            if overlap > 0:
                score = overlap / max(len(query_words), 1) * concept.strength
                concept_scores.append((concept_id, score))
        
        # Sort and return top matches
        concept_scores.sort(key=lambda x: x[1], reverse=True)
        
        for concept_id, score in concept_scores[:limit]:
            concept_info = self.get_concept_info(concept_id)
            if concept_info:
                concept_info["relevance_score"] = score
                results.append(concept_info)
        
        return results
    
    def get_system_stats(self) -> Dict:
        """Get comprehensive system statistics."""
        
        learning_stats = self.adaptive_learner.get_learning_stats()
        
        # Calculate association statistics
        association_types = defaultdict(int)
        total_confidence = 0.0
        
        for association in self.associations.values():
            association_types[association.assoc_type.value] += 1
            total_confidence += association.confidence
        
        avg_association_confidence = (
            total_confidence / len(self.associations) 
            if self.associations else 0.0
        )
        
        return {
            "system_info": {
                "total_concepts": len(self.concepts),
                "total_associations": len(self.associations),
                "total_queries": self.query_count,
                "learning_events": self.learning_events,
                "cache_hits": self.cache_hits,
                "cache_hit_rate": self.cache_hits / max(self.query_count, 1),
                "cache_size": len(self.query_cache)
            },
            "learning_stats": learning_stats,
            "association_stats": {
                "by_type": dict(association_types),
                "average_confidence": avg_association_confidence
            },
            "performance_stats": {
                "caching_enabled": self.enable_caching,
                "max_cache_size": self.max_cache_size
            }
        }
    
    def optimize_performance(self) -> Dict[str, int]:
        """Run performance optimization routines."""
        
        optimizations = {
            "concepts_strengthened": 0,
            "weak_associations_removed": 0,
            "cache_entries_pruned": 0
        }
        
        # Strengthen frequently accessed concepts
        for concept in self.concepts.values():
            if concept.access_count > 10:
                old_strength = concept.strength
                concept.strength = min(10.0, concept.strength * 1.05)
                if concept.strength > old_strength:
                    optimizations["concepts_strengthened"] += 1
        
        # Remove very weak associations to reduce noise
        weak_associations = []
        for key, association in self.associations.items():
            if association.confidence < 0.1:
                weak_associations.append(key)
        
        for key in weak_associations:
            del self.associations[key]
            optimizations["weak_associations_removed"] += 1
        
        # Prune old cache entries if cache is full
        if len(self.query_cache) > self.max_cache_size:
            # Simple strategy: remove random half
            cache_items = list(self.query_cache.items())
            self.query_cache = dict(cache_items[::2])
            optimizations["cache_entries_pruned"] = len(cache_items) // 2
        
        logger.info(f"Performance optimization completed: {optimizations}")
        return optimizations
    
    def save_knowledge_base(self, filepath: str) -> bool:
        """Save the knowledge base to file."""
        
        import json
        
        try:
            data = {
                "concepts": {cid: c.to_dict() for cid, c in self.concepts.items()},
                "associations": {
                    f"{k[0]}|{k[1]}": v.to_dict() 
                    for k, v in self.associations.items()
                },
                "metadata": {
                    "version": "1.0",
                    "created": time.time(),
                    "total_concepts": len(self.concepts),
                    "total_associations": len(self.associations),
                    "query_count": self.query_count,
                    "learning_events": self.learning_events
                }
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Knowledge base saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save knowledge base: {e}")
            return False
    
    def load_knowledge_base(self, filepath: str) -> bool:
        """Load knowledge base from file."""
        
        import json
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Load concepts
            self.concepts.clear()
            for cid, concept_data in data["concepts"].items():
                self.concepts[cid] = Concept.from_dict(concept_data)
            
            # Load associations
            self.associations.clear()
            for key_str, assoc_data in data["associations"].items():
                source_id, target_id = key_str.split("|", 1)
                key = (source_id, target_id)
                self.associations[key] = Association.from_dict(assoc_data)
            
            # Rebuild indexes
            self._rebuild_indexes()
            
            # Update statistics
            metadata = data.get("metadata", {})
            self.query_count = metadata.get("query_count", 0)
            self.learning_events = metadata.get("learning_events", 0)
            
            logger.info(
                f"Knowledge base loaded: {len(self.concepts)} concepts, "
                f"{len(self.associations)} associations"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to load knowledge base: {e}")
            return False
    
    def _update_concept_neighbors(self, concept_id: str) -> None:
        """Update neighbor mappings for a concept."""
        
        for key, association in self.associations.items():
            source_id, target_id = key
            
            if source_id == concept_id:
                self.concept_neighbors[concept_id].add(target_id)
            elif target_id == concept_id:
                self.concept_neighbors[source_id].add(concept_id)
    
    def _rebuild_indexes(self) -> None:
        """Rebuild all performance indexes."""
        
        # Clear existing indexes
        self.concept_neighbors.clear()
        self.word_to_concepts.clear()
        
        # Rebuild concept neighbors
        for key, association in self.associations.items():
            source_id, target_id = key
            self.concept_neighbors[source_id].add(target_id)
        
        # Rebuild word to concepts mapping
        for concept_id, concept in self.concepts.items():
            words = concept.content.lower().split()
            for word in words:
                word = word.strip('.,!?;:"()[]{}')
                if len(word) > 2:  # Skip very short words
                    self.word_to_concepts[word].add(concept_id)
    
    def _update_cache(self, question: str, result: ConsensusResult) -> None:
        """Update query cache with new result."""
        
        # Simple cache management
        if len(self.query_cache) >= self.max_cache_size:
            # Remove oldest entry (FIFO)
            oldest_key = next(iter(self.query_cache))
            del self.query_cache[oldest_key]
        
        self.query_cache[question] = result
    
    def _invalidate_cache(self) -> None:
        """Invalidate cache entries that might be affected by new learning."""
        
        # Simple strategy: clear all cache when new knowledge is learned
        # More sophisticated strategies could selectively invalidate
        self.query_cache.clear()