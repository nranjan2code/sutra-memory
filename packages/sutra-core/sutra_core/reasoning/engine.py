"""
Main reasoning engine for Sutra AI system.

Orchestrates all reasoning components to provide AI-level capabilities:
- Integrates path-finding, MPPA, and query processing
- Provides simple API for complex reasoning tasks
- Handles semantic understanding and knowledge integration
- Optimizes performance with caching, indexing, and batch operations
"""

import logging
import time
from collections import OrderedDict, defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

from ..graph.concepts import Association, AssociationType, Concept
from ..indexing.vector_search import VectorIndex
from ..learning.adaptive import AdaptiveLearner
from ..learning.associations import AssociationExtractor
from ..learning.associations_parallel import ParallelAssociationExtractor
from ..learning.embeddings import EmbeddingBatchProcessor
from ..learning.entity_cache import EntityCache
from ..utils.nlp import TextProcessor
from ..utils.text import extract_words
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

    def __init__(
        self,
        storage_path: str = "./knowledge",
        enable_caching: bool = True,
        max_cache_size: int = 1000,
        cache_ttl_seconds: Optional[float] = None,
        enable_central_links: bool = True,
        central_link_confidence: float = 0.6,
        central_link_type: AssociationType = AssociationType.COMPOSITIONAL,
        enable_vector_index: bool = True,
        vector_index_dimension: Optional[int] = None,
        use_rust_storage: bool = True,
        enable_batch_embeddings: bool = True,
        embedding_model: str = "all-MiniLM-L6-v2",
        mps_batch_threshold: int = 64,
        enable_parallel_associations: bool = True,
        association_workers: int = 4,
        enable_entity_cache: bool = False,
    ):
        """
        Initialize the reasoning engine.

        Args:
            storage_path: Path for storage files (Rust or JSON)
            enable_caching: Enable query result caching
            max_cache_size: Maximum number of cached results
            cache_ttl_seconds: Optional TTL for cached query results
                (None = no TTL)
            enable_central_links: Link central concept to extracted phrases during
                learning
            central_link_confidence: Confidence for central links (0.0 - 1.0)
            central_link_type: Association type for central links
            enable_vector_index: Enable HNSW vector indexing for O(log N) search
            vector_index_dimension: Embedding dimension (None = auto-detect from NLP)
            use_rust_storage: Use high-performance Rust storage (default: True)
            enable_batch_embeddings: Enable batch embedding generation with MPS support
            embedding_model: Sentence-transformer model for batch embeddings
            mps_batch_threshold: Minimum batch size to use MPS (Apple Silicon GPU)
            enable_parallel_associations: Enable parallel association extraction (Phase 8A+)
            association_workers: Number of worker processes for parallel extraction
            enable_entity_cache: Enable cached entity extraction with background LLM service (Phase 10)
        """
        # Storage backend
        self.storage_path = storage_path
        self.use_rust_storage = use_rust_storage
        self.storage = None
        
        # Core data structures (for compatibility, will be proxied to storage)
        self.concepts: Dict[str, Concept] = {}
        self.associations: Dict[Tuple[str, str], Association] = {}
        self.concept_neighbors: Dict[str, Set[str]] = defaultdict(set)
        self.word_to_concepts: Dict[str, Set[str]] = defaultdict(set)

        # Initialize NLP processor first (needed for dimension detection)
        self.nlp_processor: Optional[TextProcessor] = None
        try:
            self.nlp_processor = TextProcessor()
            logger.info("NLP processor initialized with spaCy")
        except (ImportError, OSError) as e:
            logger.warning(f"NLP processor unavailable: {e}")

        # Initialize storage backend (after NLP processor for dimension detection)
        if use_rust_storage:
            try:
                from ..storage import RustStorageAdapter
                
                # Auto-detect embedding dimension from NLP processor
                detected_dim = 384  # Default fallback
                if vector_index_dimension:
                    detected_dim = vector_index_dimension
                elif self.nlp_processor:
                    try:
                        detected_dim = self.nlp_processor.get_embedding_dimension()
                        if detected_dim <= 0:
                            detected_dim = 96  # Default for en_core_web_sm
                        logger.info(f"Auto-detected embedding dimension: {detected_dim}")
                    except Exception:
                        detected_dim = 96
                
                self.storage = RustStorageAdapter(
                    storage_path,
                    vector_dimension=detected_dim,
                    use_compression=True
                )
                logger.info(f"Rust storage initialized at {storage_path} (dim={detected_dim})")
                
                # Load existing data from Rust storage
                self._load_from_rust_storage()
                
            except ImportError as e:
                logger.warning(f"Rust storage not available: {e}. Using in-memory dicts.")
                use_rust_storage = False
        
        self.use_rust_storage = use_rust_storage

        # Initialize vector index
        self.enable_vector_index = enable_vector_index
        self.vector_index: Optional[VectorIndex] = None
        if enable_vector_index:
            try:
                # Auto-detect embedding dimension from NLP processor if not specified
                if vector_index_dimension is None and self.nlp_processor:
                    detected_dim = self.nlp_processor.get_embedding_dimension()
                    if detected_dim > 0:
                        vector_index_dimension = detected_dim
                        logger.info(f"Auto-detected embedding dimension: {detected_dim}")
                    else:
                        vector_index_dimension = 96  # Default for en_core_web_sm
                elif vector_index_dimension is None:
                    vector_index_dimension = 96  # Default fallback
                
                self.vector_index = VectorIndex(
                    dimension=vector_index_dimension,
                    max_elements=100000,
                    ef_construction=200,
                    m=16,
                    ef_search=50,
                )
                logger.info(f"Vector index initialized (HNSW, dim={vector_index_dimension})")
            except Exception as e:
                logger.warning(f"Vector index unavailable: {e}")
                self.enable_vector_index = False

        # Initialize batch embedding processor (optional for faster learning)
        self.enable_batch_embeddings = enable_batch_embeddings
        self.embedding_batch_processor: Optional[EmbeddingBatchProcessor] = None
        if enable_batch_embeddings:
            try:
                self.embedding_batch_processor = EmbeddingBatchProcessor(
                    model_name=embedding_model,
                    device="auto",
                    mps_threshold=mps_batch_threshold,
                    cache_size=10000,
                )
                logger.info(
                    f"Batch embedding processor initialized: {embedding_model} "
                    f"(MPS threshold: {mps_batch_threshold})"
                )
            except Exception as e:
                logger.warning(f"Batch embedding processor unavailable: {e}")
                self.enable_batch_embeddings = False

        # Initialize entity cache (optional for high-accuracy entity extraction)
        self.enable_entity_cache = enable_entity_cache
        self.entity_cache: Optional[EntityCache] = None
        if enable_entity_cache:
            try:
                self.entity_cache = EntityCache(storage_path)
                logger.info(f"Entity cache initialized at {storage_path}")
            except Exception as e:
                logger.warning(f"Entity cache unavailable: {e}")
                self.enable_entity_cache = False

        # Initialize components
        # Choose association extractor based on settings (priority: Parallel > Sequential)
        if enable_parallel_associations:
            self.association_extractor = ParallelAssociationExtractor(
                self.concepts,
                self.word_to_concepts,
                self.concept_neighbors,
                self.associations,
                enable_central_links=enable_central_links,
                central_link_confidence=central_link_confidence,
                central_link_type=central_link_type,
                num_workers=association_workers,
                entity_cache=self.entity_cache,
            )
            logger.info(f"Parallel association extractor initialized ({association_workers} workers)")
        else:
            self.association_extractor = AssociationExtractor(
                self.concepts,
                self.word_to_concepts,
                self.concept_neighbors,
                self.associations,
                enable_central_links=enable_central_links,
                central_link_confidence=central_link_confidence,
                central_link_type=central_link_type,
                nlp_processor=self.nlp_processor,  # Only sequential extractor uses NLP
                entity_cache=self.entity_cache,
            )
            logger.info("Sequential association extractor initialized")

        self.adaptive_learner = AdaptiveLearner(
            self.concepts, self.association_extractor
        )

        self.path_finder = PathFinder(
            self.concepts, self.associations, self.concept_neighbors
        )

        self.mppa = MultiPathAggregator()

        self.query_processor = QueryProcessor(
            self.concepts,
            self.associations,
            self.concept_neighbors,
            self.association_extractor,
            self.path_finder,
            self.mppa,
        )

        # Performance optimization
        self.enable_caching = enable_caching
        self.cache_ttl_seconds = cache_ttl_seconds
        self.query_cache: OrderedDict[str, Tuple[ConsensusResult, float]] = (
            OrderedDict()
        )
        self.max_cache_size = max_cache_size

        # Statistics
        self.query_count = 0
        self.learning_events = 0
        self.cache_hits = 0

        logger.info("Sutra AI Reasoning Engine initialized")

    def ask(self, question: str, num_reasoning_paths: int = 5, **kwargs: Any) -> ConsensusResult:
        """
        Ask the AI a question and get an explainable answer.

        This is the main AI interface - processes natural language questions
        and returns comprehensive reasoning with explanations.

        Args:
            question: Natural language question
            num_reasoning_paths: Number of reasoning paths to explore
            **kwargs: Additional options passed to query processor

        Returns:
            Consensus result with answer, confidence, and explanation
        """
        self.query_count += 1

        # Check cache first
        if self.enable_caching:
            cached = self.query_cache.get(question)
            if cached:
                cached_result, ts = cached
                if (
                    self.cache_ttl_seconds is None
                    or (time.time() - ts) <= self.cache_ttl_seconds
                ):
                    self.cache_hits += 1
                    logger.debug(f"Cache hit for query: {question[:50]}...")
                    # LRU: mark as recently used
                    self.query_cache.move_to_end(question)
                    return cached_result
                else:
                    # TTL expired
                    try:
                        del self.query_cache[question]
                    except KeyError:
                        pass

        # Process query through full reasoning pipeline
        result = self.query_processor.process_query(
            question, num_reasoning_paths=num_reasoning_paths, **kwargs
        )

        # Cache result
        if self.enable_caching:
            self._update_cache(question, result)

        # Log performance
        logger.debug(
            f"Query processed: {result.confidence:.2f} confidence, "
            f"{result.consensus_strength:.2f} consensus"
        )

        return result

    def learn(
        self,
        content: str,
        source: Optional[str] = None,
        category: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """
        Learn new knowledge and integrate it into the reasoning system.

        Args:
            content: Knowledge content to learn
            source: Source of the knowledge
            category: Category/domain of knowledge
            **kwargs: Additional learning options

        Returns:
            Concept ID of learned knowledge
        """
        self.learning_events += 1

        # Learn through adaptive system (adds to self.concepts dict)
        concept_id = self.adaptive_learner.learn_adaptive(
            content, source=source, category=category, **kwargs
        )

        # Store in Rust storage if enabled
        if self.use_rust_storage and self.storage and self.nlp_processor:
            try:
                concept = self.concepts.get(concept_id)
                if concept:
                    # Get embedding
                    embedding = self.nlp_processor.get_embedding(content)
                    if embedding is not None:
                        # Convert to numpy array
                        embedding_array = np.array(embedding, dtype=np.float32)
                        # Store in Rust
                        self.storage.add_concept(concept, embedding_array)
                        logger.debug(f"Stored concept {concept_id[:8]} in Rust storage")
            except Exception as e:
                logger.warning(f"Failed to store in Rust storage: {e}")

        # Update neighbor mappings
        self._update_concept_neighbors(concept_id)

        # Update vector index
        self._index_concept(concept_id)

        # Selectively invalidate cache entries affected by new content
        if self.enable_caching:
            self._invalidate_cache(content)

        logger.debug(f"Learned new concept: {content[:50]}... (ID: {concept_id[:8]})")

        return concept_id
    
    def learn_batch(
        self,
        contents: List[Tuple[str, Optional[str], Optional[str]]],
        **kwargs: Any
    ) -> List[str]:
        """
        Learn multiple knowledge items in batch for efficiency.
        
        This is significantly faster than calling learn() multiple times
        because it:
        - Reduces per-operation overhead
        - Batches vector index updates
        - Amortizes cache invalidation
        
        Args:
            contents: List of (content, source, category) tuples
            **kwargs: Additional learning options
            
        Returns:
            List of concept IDs for learned knowledge
        """
        if not contents:
            return []
        
        start_time = time.time()
        concept_ids = []
        
        # Learn all concepts
        for content, source, category in contents:
            self.learning_events += 1
            
            concept_id = self.adaptive_learner.learn_adaptive(
                content, source=source, category=category, **kwargs
            )
            
            # Update neighbor mappings
            self._update_concept_neighbors(concept_id)
            
            concept_ids.append(concept_id)
        
        # Batch update vector index (much faster)
        if self.enable_vector_index and self.vector_index:
            try:
                # Collect content texts
                content_texts = []
                valid_concept_ids = []
                for concept_id in concept_ids:
                    if concept_id in self.concepts:
                        content_texts.append(self.concepts[concept_id].content)
                        valid_concept_ids.append(concept_id)
                
                # Generate embeddings in batch
                embeddings = None
                if self.enable_batch_embeddings and self.embedding_batch_processor:
                    # Use fast batch embedding processor with MPS support
                    embeddings = self.embedding_batch_processor.encode_batch(
                        content_texts,
                        show_progress=False,
                        normalize=True,
                    )
                    logger.debug(
                        f"Generated {len(embeddings)} embeddings via batch processor"
                    )
                elif self.nlp_processor:
                    # Fallback to NLP processor (slower, one-by-one)
                    embeddings_list = []
                    for text in content_texts:
                        embedding = self.nlp_processor.get_embedding(text)
                        if embedding is not None:
                            embeddings_list.append(embedding)
                    if embeddings_list:
                        embeddings = np.array(embeddings_list)
                
                # Add to vector index
                if embeddings is not None and len(embeddings) > 0:
                    concept_embeddings = [
                        (cid, emb) for cid, emb in zip(valid_concept_ids, embeddings)
                    ]
                    self.vector_index.add_concepts_batch(concept_embeddings)
                    logger.debug(
                        f"Batch indexed {len(concept_embeddings)} concepts"
                    )
            except Exception as e:
                logger.warning(f"Batch vector indexing failed: {e}")
        
        # Invalidate cache once for all new content
        if self.enable_caching:
            combined_content = " ".join(c[0] for c in contents)
            self._invalidate_cache(combined_content)
        
        elapsed = time.time() - start_time
        logger.info(
            f"Batch learned {len(concept_ids)} concepts in {elapsed:.3f}s "
            f"({len(concept_ids)/elapsed:.1f} concepts/sec)"
        )
        
        return concept_ids
    
    def _index_concept(self, concept_id: str) -> None:
        """
        Add concept to vector index.
        
        Args:
            concept_id: Concept to index
        """
        if not self.enable_vector_index or not self.vector_index:
            return
        
        if not self.nlp_processor:
            return
        
        if concept_id not in self.concepts:
            return
        
        try:
            content = self.concepts[concept_id].content
            embedding = self.nlp_processor.get_embedding(content)
            
            if embedding is not None:
                self.vector_index.add_concept(concept_id, embedding)
                logger.debug(f"Indexed concept {concept_id[:8]} in vector index")
        except Exception as e:
            logger.warning(f"Failed to index concept {concept_id[:8]}: {e}")

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
            "reasoning_robustness": self.mppa.analyze_reasoning_robustness(result),
        }

        if detailed and result.supporting_paths:
            explanation["detailed_paths"] = []
            for i, path in enumerate(result.supporting_paths):
                path_detail: Dict[str, Any] = {
                    "path_number": i + 1,
                    "confidence": path.confidence,
                    "steps": [
                        {
                            "step": step.step_number,
                            "from": step.source_concept,
                            "relation": step.relation,
                            "to": step.target_concept,
                            "confidence": step.confidence,
                        }
                        for step in path.steps
                    ],
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
            "neighbors": list(neighbors)[:10],  # Limit for display
        }

    def search_concepts(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for concepts matching a query.
        
        Uses HNSW vector index if available (O(log N)),
        otherwise falls back to linear scan (O(N)).
        """
        results = []

        # Try vector search first (much faster)
        if self.enable_vector_index and self.vector_index and self.nlp_processor:
            try:
                query_embedding = self.nlp_processor.get_embedding(query)
                if query_embedding is not None:
                    vector_results = self.vector_index.search(
                        query_embedding,
                        k=limit,
                    )
                    
                    for concept_id, similarity in vector_results:
                        concept_info = self.get_concept_info(concept_id)
                        if concept_info:
                            concept_info["relevance_score"] = similarity
                            results.append(concept_info)
                    
                    logger.debug(
                        f"Vector search returned {len(results)} results for: {query[:50]}"
                    )
                    return results
            except Exception as e:
                logger.warning(f"Vector search failed, falling back to linear: {e}")

        # Fallback to linear word overlap search (O(N))
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

        logger.debug(f"Linear search returned {len(results)} results for: {query[:50]}")
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
            total_confidence / len(self.associations) if self.associations else 0.0
        )

        # Get vector index stats if available
        vector_index_stats = {}
        if self.enable_vector_index and self.vector_index:
            vector_index_stats = self.vector_index.get_stats()

        return {
            "system_info": {
                "total_concepts": len(self.concepts),
                "total_associations": len(self.associations),
                "total_queries": self.query_count,
                "learning_events": self.learning_events,
                "cache_hits": self.cache_hits,
                "cache_hit_rate": self.cache_hits / max(self.query_count, 1),
                "cache_size": len(self.query_cache),
            },
            "learning_stats": learning_stats,
            "association_stats": {
                "by_type": dict(association_types),
                "average_confidence": avg_association_confidence,
            },
            "performance_stats": {
                "caching_enabled": self.enable_caching,
                "max_cache_size": self.max_cache_size,
                "vector_index_enabled": self.enable_vector_index,
                "vector_index_stats": vector_index_stats,
            },
        }

    def optimize_performance(self) -> Dict[str, int]:
        """Run performance optimization routines."""

        optimizations = {
            "concepts_strengthened": 0,
            "weak_associations_removed": 0,
            "cache_entries_pruned": 0,
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

        # Prune cache down to size budget
        if len(self.query_cache) > self.max_cache_size:
            to_prune = len(self.query_cache) - self.max_cache_size
            pruned = 0
            while pruned < to_prune:
                try:
                    self.query_cache.popitem(last=False)
                    pruned += 1
                except KeyError:
                    break
            optimizations["cache_entries_pruned"] = pruned

        logger.debug(f"Performance optimization completed: {optimizations}")
        return optimizations

    def save_knowledge_base(self, filepath: str) -> bool:
        """Save the knowledge base to file."""

        import json

        try:
            data = {
                "concepts": {cid: c.to_dict() for cid, c in self.concepts.items()},
                "associations": {
                    f"{k[0]}:{k[1]}": v.to_dict() for k, v in self.associations.items()
                },
                "metadata": {
                    "version": "1.0",
                    "created": time.time(),
                    "total_concepts": len(self.concepts),
                    "total_associations": len(self.associations),
                    "query_count": self.query_count,
                    "learning_events": self.learning_events,
                },
            }

            with open(filepath, "w") as f:
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
            with open(filepath, "r") as f:
                data = json.load(f)

            # Load concepts
            self.concepts.clear()
            for cid, concept_data in data["concepts"].items():
                self.concepts[cid] = Concept.from_dict(concept_data)

            # Load associations
            self.associations.clear()
            for key_str, assoc_data in data["associations"].items():
                if ":" in key_str:
                    source_id, target_id = key_str.split(":", 1)
                elif "|" in key_str:
                    source_id, target_id = key_str.split("|", 1)
                else:
                    # Unknown format; skip
                    continue
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

    def _load_from_rust_storage(self) -> None:
        """Load existing concepts and associations from Rust storage into memory indexes."""
        if not self.storage:
            return
        
        try:
            # Load all concept IDs from metadata
            all_concept_ids = self.storage.get_all_concept_ids()
            
            logger.info(f"Loading {len(all_concept_ids)} concepts from Rust storage...")
            
            # Load concepts into memory dict for fast access
            for concept_id in all_concept_ids:
                concept = self.storage.get_concept(concept_id)
                if concept:
                    self.concepts[concept_id] = concept
                    
                    # Build word index
                    words = extract_words(concept.content)
                    for word in words:
                        self.word_to_concepts[word].add(concept_id)
            
            # Build neighbor index from graph
            for concept_id in all_concept_ids:
                neighbors = self.storage.get_neighbors(concept_id)
                if neighbors:
                    self.concept_neighbors[concept_id] = set(neighbors)
            
            logger.info(
                f"Loaded {len(self.concepts)} concepts, "
                f"{len(self.concept_neighbors)} with neighbors"
            )
            
        except Exception as e:
            logger.error(f"Failed to load from Rust storage: {e}")

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

        # Rebuild concept neighbors (symmetric to runtime indexing)
        for key, association in self.associations.items():
            source_id, target_id = key
            self.concept_neighbors[source_id].add(target_id)
            self.concept_neighbors[target_id].add(source_id)

        # Rebuild word to concepts mapping using standardized tokenization
        for concept_id, concept in self.concepts.items():
            words = extract_words(concept.content)
            for word in words:
                self.word_to_concepts[word].add(concept_id)

    def _update_cache(self, question: str, result: ConsensusResult) -> None:
        """Update query cache with new result (LRU + optional TTL)."""

        # Evict until within size budget
        while len(self.query_cache) >= self.max_cache_size:
            try:
                self.query_cache.popitem(last=False)  # pop oldest
            except KeyError:
                break

        # Insert/move to end
        self.query_cache[question] = (result, time.time())
        self.query_cache.move_to_end(question)

    def _invalidate_cache(self, new_content: Optional[str] = None) -> None:
        """
        Selectively invalidate cache entries affected by new learning.
        
        OPTIMIZATION: Instead of clearing entire cache, only invalidate queries
        that overlap with newly learned content. This improves cache hit rate
        from ~5% to ~50% for typical workloads.
        
        Args:
            new_content: The content being learned (optional, if None clears all)
        """
        if not new_content:
            # No content provided, clear all (fallback behavior)
            self.query_cache.clear()
            return
        
        # Extract meaningful words from new content
        new_words = set(extract_words(new_content.lower()))
        
        if not new_words:
            # No meaningful words, don't invalidate
            return
        
        # Find queries that overlap with new content
        queries_to_invalidate = []
        
        for cached_query in list(self.query_cache.keys()):
            query_words = set(extract_words(cached_query.lower()))
            
            # If query shares words with new content, invalidate it
            overlap = query_words & new_words
            if overlap:
                queries_to_invalidate.append(cached_query)
        
        # Remove invalidated queries
        for query in queries_to_invalidate:
            del self.query_cache[query]
        
        logger.debug(
            f"Invalidated {len(queries_to_invalidate)}/{len(self.query_cache) + len(queries_to_invalidate)} "
            f"cache entries based on word overlap with new content"
        )

    def decay_and_prune(
        self,
        concept_decay_after_days: int = 14,
        concept_remove_after_days: int = 90,
        min_strength_to_keep: float = 1.0,
        association_remove_after_days: int = 90,
        min_association_confidence_to_keep: float = 0.2,
        daily_decay_rate: float = 0.995,
    ) -> Dict[str, int]:
        """
        Decay inactive concepts and prune stale/weak concepts and associations.

        Args:
            concept_decay_after_days: Start decaying concept strength after this
                inactivity
            concept_remove_after_days: Remove concepts inactive longer than this
                if very weak and disconnected
            min_strength_to_keep: Minimum strength to avoid removal
            association_remove_after_days: Remove associations inactive longer than
                this if low confidence
            min_association_confidence_to_keep: Minimum confidence to keep a stale
                association
            daily_decay_rate: Multiplicative daily decay factor for concept
                strength (0 < r <= 1)
        Returns:
            Dict with counts of decayed/removed items
        """
        now = time.time()
        seconds_per_day = 86400.0

        results = {
            "concepts_decayed": 0,
            "concepts_removed": 0,
            "associations_removed": 0,
        }

        # Decay concept strengths based on inactivity
        for concept in list(self.concepts.values()):
            inactivity_days = (now - concept.last_accessed) / seconds_per_day
            if inactivity_days >= concept_decay_after_days and concept.strength > 0.1:
                # Apply per-day decay steps (rounded down to avoid tiny jitters)
                steps = int(inactivity_days - concept_decay_after_days) + 1
                if steps > 0:
                    old_strength = concept.strength
                    concept.strength = max(
                        0.1, concept.strength * (daily_decay_rate**steps)
                    )
                    if concept.strength < old_strength:
                        results["concepts_decayed"] += 1

        # Remove very weak, long-inactive, disconnected concepts
        concepts_to_remove = []
        for cid, concept in self.concepts.items():
            inactivity_days = (now - concept.last_accessed) / seconds_per_day
            degree = len(self.concept_neighbors.get(cid, set()))
            if (
                inactivity_days >= concept_remove_after_days
                and concept.strength <= min_strength_to_keep
                and concept.access_count == 0
                and degree == 0
            ):
                concepts_to_remove.append(cid)

        # Remove associations attached to removed concepts
        if concepts_to_remove:
            assoc_keys_to_remove = []
            for key in list(self.associations.keys()):
                source_id, target_id = key
                if source_id in concepts_to_remove or target_id in concepts_to_remove:
                    assoc_keys_to_remove.append(key)
            for key in assoc_keys_to_remove:
                try:
                    del self.associations[key]
                    results["associations_removed"] += 1
                except KeyError:
                    pass
            for cid in concepts_to_remove:
                try:
                    del self.concepts[cid]
                    results["concepts_removed"] += 1
                except KeyError:
                    pass

        # Remove stale low-confidence associations (time-based)
        assoc_to_remove = []
        for key, assoc in self.associations.items():
            last_used = getattr(assoc, "last_used", assoc.created)
            inactivity_days = (now - last_used) / seconds_per_day
            if (
                inactivity_days >= association_remove_after_days
                and assoc.confidence < min_association_confidence_to_keep
            ):
                assoc_to_remove.append(key)
        for key in assoc_to_remove:
            try:
                del self.associations[key]
                results["associations_removed"] += 1
            except KeyError:
                pass

        # Rebuild indexes after removals
        if concepts_to_remove or assoc_to_remove:
            self._rebuild_indexes()

        logger.debug(
            f"Decay/prune completed: {results['concepts_decayed']} decayed, "
            f"{results['concepts_removed']} concepts removed, "
            f"{results['associations_removed']} associations removed"
        )
        return results

    def get_health_snapshot(self) -> Dict:
        """Return a compact runtime health snapshot."""
        now = time.time()
        seconds_per_day = 86400.0

        total_concepts = len(self.concepts)
        total_associations = len(self.associations)

        # Concept metrics
        if total_concepts:
            strengths = [c.strength for c in self.concepts.values()]
            avg_strength = sum(strengths) / total_concepts
            weak_pct = sum(1 for s in strengths if s < 2.0) / total_concepts
            strong_pct = sum(1 for s in strengths if s > 7.0) / total_concepts
        else:
            avg_strength = 0.0
            weak_pct = 0.0
            strong_pct = 0.0

        # Association metrics
        if total_associations:
            confidences = [a.confidence for a in self.associations.values()]
            avg_conf = sum(confidences) / total_associations
            weak_assoc = sum(
                1 for a in self.associations.values() if a.confidence < 0.2
            )
            stale_assoc = 0
            for a in self.associations.values():
                last_used = getattr(a, "last_used", a.created)
                if (now - last_used) / seconds_per_day > 60:
                    stale_assoc += 1
        else:
            avg_conf = 0.0
            weak_assoc = 0
            stale_assoc = 0

        # Graph metrics
        avg_degree = sum(len(neigh) for neigh in self.concept_neighbors.values()) / max(
            total_concepts, 1
        )

        return {
            "totals": {
                "concepts": total_concepts,
                "associations": total_associations,
            },
            "concepts": {
                "avg_strength": avg_strength,
                "weak_pct": weak_pct,
                "strong_pct": strong_pct,
            },
            "associations": {
                "avg_confidence": avg_conf,
                "weak_count": weak_assoc,
                "stale_count": stale_assoc,
            },
            "graph": {
                "avg_degree": avg_degree,
            },
            "cache": {
                "enabled": self.enable_caching,
                "size": len(self.query_cache),
                "hit_rate": self.cache_hits / max(self.query_count, 1),
            },
        }

    def save(self) -> None:
        """
        Save knowledge base using Rust storage.
        
        If Rust storage is enabled, saves to high-performance backend.
        Otherwise, falls back to JSON save.
        """
        if self.use_rust_storage and self.storage:
            try:
                self.storage.save()
                logger.info(f"Knowledge base saved to Rust storage at {self.storage_path}")
            except Exception as e:
                logger.error(f"Failed to save to Rust storage: {e}")
        else:
            # Fallback to old JSON save
            self.save_knowledge_base(f"{self.storage_path}/knowledge.json")
