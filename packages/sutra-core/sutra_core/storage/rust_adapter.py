"""
Direct adapter for Rust storage engine.

Provides clean integration between Python Concept/Association objects
and the Rust sutra_storage module. No abstraction layers, just efficient
type conversions and direct calls.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

try:
    import sutra_storage
    RUST_STORAGE_AVAILABLE = True
except ImportError:
    RUST_STORAGE_AVAILABLE = False
    sutra_storage = None

from ..graph.concepts import Association, AssociationType, Concept

logger = logging.getLogger(__name__)


class RustStorageAdapter:
    """
    Direct adapter for Rust storage.
    
    Handles:
    - Vector storage (Rust: high performance)
    - Graph structure (Rust: fast indexes)
    - Metadata storage (JSON sidecar: flexibility)
    
    Usage:
        adapter = RustStorageAdapter("./knowledge")
        adapter.add_concept(concept, embedding)
        neighbors = adapter.get_neighbors(concept_id)
        adapter.save()
    """

    def __init__(
        self,
        storage_path: str,
        vector_dimension: int = 384,
        use_compression: bool = True,
    ):
        """
        Initialize Rust storage adapter.

        Args:
            storage_path: Directory for storage files
            vector_dimension: Embedding dimension (default 384 for sentence-transformers)
            use_compression: Enable Product Quantization (32x compression)
        
        Raises:
            ImportError: If sutra_storage module not available
            RuntimeError: If storage initialization fails
        """
        if not RUST_STORAGE_AVAILABLE:
            raise ImportError(
                "sutra_storage module not available. "
                "Build with: cd packages/sutra-storage && maturin develop"
            )

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.vector_dimension = vector_dimension
        self.use_compression = use_compression

        # Initialize Rust storage
        try:
            self.store = sutra_storage.GraphStore(
                str(self.storage_path),
                vector_dimension=vector_dimension,
                use_compression=use_compression,
            )
            logger.info(
                f"Rust storage initialized at {storage_path} "
                f"(dim={vector_dimension}, compression={use_compression})"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Rust storage: {e}")

        # Metadata files
        self.metadata_file = self.storage_path / "metadata.json"
        
        # In-memory metadata cache
        self.concept_metadata: Dict[str, dict] = {}
        self.association_metadata: Dict[str, dict] = {}
        
        # Load existing metadata
        self._load_metadata()

    # ===== Concept Operations =====

    def add_concept(self, concept: Concept, embedding: np.ndarray) -> None:
        """
        Add concept with its embedding.

        Args:
            concept: Concept object with all attributes
            embedding: Vector embedding (numpy array)
        
        Raises:
            ValueError: If embedding dimension doesn't match
        """
        if len(embedding) != self.vector_dimension:
            raise ValueError(
                f"Embedding dimension {len(embedding)} doesn't match "
                f"expected {self.vector_dimension}"
            )

        # Store vector in Rust (high performance)
        self.store.add_vector(concept.id, embedding.astype(np.float32))

        # Store metadata in JSON (flexibility)
        self.concept_metadata[concept.id] = {
            "content": concept.content,
            "created": concept.created,
            "access_count": concept.access_count,
            "strength": concept.strength,
            "last_accessed": concept.last_accessed,
            "source": concept.source,
            "category": concept.category,
            "confidence": concept.confidence,
        }

        logger.debug(f"Added concept {concept.id[:8]}...")

    def get_concept(self, concept_id: str) -> Optional[Concept]:
        """
        Retrieve concept by ID.

        Args:
            concept_id: Unique concept identifier
        
        Returns:
            Concept object or None if not found
        """
        # Check if metadata exists
        metadata = self.concept_metadata.get(concept_id)
        if metadata is None:
            return None

        # Vector exists check (optional - metadata is source of truth)
        vector = self.store.get_vector(concept_id)
        if vector is None:
            logger.warning(f"Concept {concept_id[:8]}... has metadata but no vector")

        # Reconstruct Concept
        concept = Concept(
            id=concept_id,
            content=metadata["content"],
            created=metadata["created"],
            access_count=metadata["access_count"],
            strength=metadata["strength"],
            last_accessed=metadata["last_accessed"],
            source=metadata.get("source"),
            category=metadata.get("category"),
            confidence=metadata.get("confidence", 1.0),
        )

        return concept

    def get_all_concept_ids(self) -> List[str]:
        """Get all concept IDs in storage."""
        return list(self.concept_metadata.keys())

    def delete_concept(self, concept_id: str) -> None:
        """Delete concept and its vector."""
        self.store.remove_vector(concept_id)
        if concept_id in self.concept_metadata:
            del self.concept_metadata[concept_id]

    # ===== Association Operations =====

    def add_association(self, association: Association) -> None:
        """
        Add association to graph.

        Args:
            association: Association object
        """
        # Add to Rust graph (fast neighbor queries)
        self.store.add_association(association.source_id, association.target_id)

        # Store metadata
        key = f"{association.source_id}:{association.target_id}"
        self.association_metadata[key] = {
            "assoc_type": association.assoc_type.value,
            "weight": association.weight,
            "confidence": association.confidence,
            "created": association.created,
            "last_used": association.last_used,
        }

        logger.debug(
            f"Added association {association.source_id[:8]}... → "
            f"{association.target_id[:8]}..."
        )

    def get_association(
        self, source_id: str, target_id: str
    ) -> Optional[Association]:
        """Get association between two concepts."""
        key = f"{source_id}:{target_id}"
        metadata = self.association_metadata.get(key)
        
        if metadata is None:
            return None

        return Association(
            source_id=source_id,
            target_id=target_id,
            assoc_type=AssociationType(metadata["assoc_type"]),
            weight=metadata["weight"],
            confidence=metadata["confidence"],
            created=metadata["created"],
            last_used=metadata["last_used"],
        )

    def get_neighbors(self, concept_id: str) -> List[str]:
        """
        Get neighboring concept IDs.

        Args:
            concept_id: Concept to get neighbors for
        
        Returns:
            List of neighbor concept IDs
        """
        return self.store.get_neighbors(concept_id)

    # ===== Vector Operations =====

    def get_vector(self, concept_id: str) -> Optional[np.ndarray]:
        """Get vector embedding for concept."""
        return self.store.get_vector(concept_id)

    def distance(self, id1: str, id2: str) -> Optional[float]:
        """
        Compute distance between two concept vectors.

        Args:
            id1: First concept ID
            id2: Second concept ID
        
        Returns:
            Cosine distance or None if vectors not found
        """
        return self.store.distance(id1, id2)

    def approximate_distance(self, id1: str, id2: str) -> Optional[float]:
        """
        Fast approximate distance using quantization.

        Args:
            id1: First concept ID
            id2: Second concept ID
        
        Returns:
            Approximate distance or None
        """
        return self.store.approximate_distance(id1, id2)

    # ===== Search Operations =====

    def search_by_text(self, text: str) -> List[str]:
        """
        Search concepts by text content (inverted index).

        Args:
            text: Query text
        
        Returns:
            List of matching concept IDs
        """
        if not text:
            return []
        
        # search_text expects a single string, not a list
        return self.store.search_text(text.lower())

    def search_by_time_range(
        self, start_time: float, end_time: float
    ) -> List[str]:
        """
        Search concepts created in time range.

        Args:
            start_time: Start timestamp
            end_time: End timestamp
        
        Returns:
            List of concept IDs in range
        """
        return self.store.get_concepts_in_range(start_time, end_time)

    def semantic_search(
        self, query_vector: np.ndarray, top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Semantic search using vector similarity.

        Args:
            query_vector: Query embedding
            top_k: Number of results to return
        
        Returns:
            List of (concept_id, distance) tuples, sorted by distance
        """
        results = []
        
        # Iterate through all concepts
        for concept_id in self.concept_metadata.keys():
            distance = self.store.distance(concept_id, query_vector)
            if distance is not None:
                results.append((concept_id, distance))
        
        # Sort by distance and return top-k
        results.sort(key=lambda x: x[1])
        return results[:top_k]

    # ===== Batch Operations =====

    def train_quantizer(self, num_training_vectors: int = 1000) -> None:
        """
        Train Product Quantization for compression.

        Args:
            num_training_vectors: Number of vectors to use for training
        """
        if not self.use_compression:
            logger.warning("Compression disabled, skipping quantizer training")
            return

        all_ids = self.get_all_concept_ids()
        
        if len(all_ids) < num_training_vectors:
            logger.warning(
                f"Only {len(all_ids)} concepts available, "
                f"need {num_training_vectors} for training"
            )
            num_training_vectors = len(all_ids)

        # Sample random vectors for training
        import random
        training_ids = random.sample(all_ids, num_training_vectors)
        training_vectors = []
        
        for concept_id in training_ids:
            vector = self.store.get_vector(concept_id)
            if vector is not None:
                training_vectors.append(vector)

        if not training_vectors:
            logger.error("No vectors available for training")
            return

        # Convert to numpy array
        training_array = np.array(training_vectors, dtype=np.float32)
        
        # Train quantizer
        self.store.train_quantizer(training_array)
        logger.info(f"Quantizer trained with {len(training_vectors)} vectors")

    # ===== Persistence =====

    def save(self) -> None:
        """Persist all changes to disk."""
        # Save Rust storage (vectors + graph)
        self.store.save()
        
        # Save metadata (JSON)
        self._save_metadata()
        
        logger.info("Storage saved successfully")

    def _load_metadata(self) -> None:
        """Load metadata from JSON file."""
        if not self.metadata_file.exists():
            logger.info("No existing metadata file")
            return

        try:
            with open(self.metadata_file, "r") as f:
                data = json.load(f)
            
            self.concept_metadata = data.get("concepts", {})
            self.association_metadata = data.get("associations", {})
            
            logger.info(
                f"Loaded metadata: {len(self.concept_metadata)} concepts, "
                f"{len(self.association_metadata)} associations"
            )
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")

    def _save_metadata(self) -> None:
        """Save metadata to JSON file."""
        try:
            data = {
                "concepts": self.concept_metadata,
                "associations": self.association_metadata,
            }
            
            with open(self.metadata_file, "w") as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Metadata saved to {self.metadata_file}")
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")

    # ===== Statistics =====

    def stats(self) -> Dict:
        """
        Get storage statistics.

        Returns:
            Dictionary with storage stats
        """
        rust_stats = self.store.stats()
        
        return {
            # Rust storage stats
            "total_vectors": rust_stats.get("total_vectors", 0),
            "compressed_vectors": rust_stats.get("compressed_vectors", 0),
            "compression_ratio": rust_stats.get("compression_ratio", 1.0),
            "dimension": rust_stats.get("dimension", self.vector_dimension),
            
            # Graph stats
            "total_concepts": rust_stats.get("total_concepts", 0),
            "total_edges": rust_stats.get("total_edges", 0),
            "total_words": rust_stats.get("total_words", 0),
            
            # Metadata stats
            "metadata_concepts": len(self.concept_metadata),
            "metadata_associations": len(self.association_metadata),
            
            # Storage config
            "vector_dimension": self.vector_dimension,
            "compression_enabled": self.use_compression,
            "storage_path": str(self.storage_path),
        }

    # ===== Context Manager =====

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, *args):
        """Exit context manager - auto-save."""
        self.save()

    def __repr__(self) -> str:
        """String representation."""
        stats = self.stats()
        return (
            f"RustStorageAdapter("
            f"path='{self.storage_path}', "
            f"concepts={stats['total_concepts']}, "
            f"vectors={stats['total_vectors']}, "
            f"compression={stats['compression_ratio']:.1f}x)"
        )
