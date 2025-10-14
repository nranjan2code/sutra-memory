"""
Association extraction and management for the Sutra AI system.

This module handles:
- Pattern-based association extraction from text
- Adaptive depth extraction for difficult concepts
- Co-occurrence based semantic associations
"""

import re
import hashlib
from typing import Dict, Set, Tuple, TYPE_CHECKING
from collections import defaultdict

from ..graph.concepts import Association, AssociationType, Concept
from ..utils.text import get_association_patterns, extract_words

if TYPE_CHECKING:
    from collections import defaultdict


class AssociationExtractor:
    """Extracts and manages associations between concepts."""
    
    def __init__(self, concepts: Dict[str, Concept], 
                 word_to_concepts: defaultdict,
                 concept_neighbors: defaultdict,
                 associations: Dict[Tuple[str, str], Association]):
        """
        Initialize association extractor.
        
        Args:
            concepts: Dictionary of all concepts
            word_to_concepts: Word -> concept ID mapping
            concept_neighbors: Concept -> neighbor IDs mapping  
            associations: All associations in the system
        """
        self.concepts = concepts
        self.word_to_concepts = word_to_concepts
        self.concept_neighbors = concept_neighbors
        self.associations = associations
    
    def extract_associations(self, content: str, concept_id: str) -> int:
        """
        Extract relationships from content using pattern matching.
        
        Args:
            content: Text content to analyze
            concept_id: Central concept ID
            
        Returns:
            Number of associations created
        """
        associations_created = 0
        patterns = get_association_patterns()
        
        for pattern, assoc_type in patterns:
            matches = re.finditer(pattern, content.lower())
            for match in matches:
                source_text = match.group(1).strip()
                target_text = match.group(2).strip()
                
                # Create or find concepts for source and target
                source_id = self._find_or_create_concept(source_text)
                target_id = self._find_or_create_concept(target_text)
                
                # Create association with high confidence for explicit patterns
                if self._create_association(source_id, target_id, assoc_type, 0.8):
                    associations_created += 1
        
        return associations_created
    
    def extract_associations_adaptive(self, content: str, concept_id: str, 
                                    depth: int = 1) -> int:
        """
        Adaptive association extraction based on concept difficulty.
        
        Implements Loss-Driven Adaptive Token Focusing (LATF):
        - Difficult concepts (depth=2): Deeper analysis, co-occurrence extraction
        - Easy concepts (depth=1): Standard pattern extraction only
        
        Args:
            content: Content to extract from
            concept_id: Central concept ID
            depth: Extraction depth (1=normal, 2=deep for difficult concepts)
            
        Returns:
            Total number of associations created
        """
        # Always do standard extraction
        associations_created = self.extract_associations(content, concept_id)
        
        # For difficult concepts, do additional deep extraction
        if depth > 1:
            associations_created += self._extract_cooccurrence_associations(
                content, concept_id
            )
        
        return associations_created
    
    def _extract_cooccurrence_associations(self, content: str, 
                                         concept_id: str) -> int:
        """
        Extract co-occurrence based semantic associations.
        
        Uses sliding window approach: words appearing together are related.
        
        Args:
            content: Text content
            concept_id: Central concept ID
            
        Returns:
            Number of co-occurrence associations created
        """
        associations_created = 0
        words = extract_words(content)
        
        # Sliding window of 3 words to find co-occurrences
        for i, word1 in enumerate(words):
            for word2 in words[i+1:i+4]:  # Window of 3 words
                # Find concepts containing these words
                concepts1 = self.word_to_concepts.get(word1, set())
                concepts2 = self.word_to_concepts.get(word2, set())
                
                # Limit to avoid exponential explosion
                for c1 in list(concepts1)[:3]:
                    for c2 in list(concepts2)[:3]:
                        if c1 != c2:
                            # Weaker confidence for co-occurrence
                            if self._create_association(
                                c1, c2, AssociationType.SEMANTIC, 0.5
                            ):
                                associations_created += 1
        
        return associations_created
    
    def _find_or_create_concept(self, text: str) -> str:
        """
        Find existing concept or create new one.
        
        Args:
            text: Concept text content
            
        Returns:
            Concept ID
        """
        concept_id = hashlib.md5(text.encode()).hexdigest()[:12]
        
        if concept_id not in self.concepts:
            # Create new concept with lower confidence (extracted from associations)
            concept = Concept(id=concept_id, content=text, confidence=0.7)
            self.concepts[concept_id] = concept
            self._index_concept(concept)
        
        return concept_id
    
    def _index_concept(self, concept: Concept) -> None:
        """Index concept for fast retrieval by words."""
        words = extract_words(concept.content)
        for word in words:
            self.word_to_concepts[word.lower()].add(concept.id)
    
    def _create_association(self, source_id: str, target_id: str,
                          assoc_type: AssociationType, confidence: float) -> bool:
        """
        Create or strengthen association between concepts.
        
        Args:
            source_id: Source concept ID
            target_id: Target concept ID
            assoc_type: Type of association
            confidence: Association confidence
            
        Returns:
            True if new association was created, False if existing was strengthened
        """
        key = (source_id, target_id)
        
        if key in self.associations:
            # Strengthen existing association
            self.associations[key].strengthen()
            return False
        else:
            # Create new association
            association = Association(
                source_id=source_id,
                target_id=target_id,
                assoc_type=assoc_type,
                confidence=confidence
            )
            self.associations[key] = association
            
            # Update neighbor indices for fast graph traversal
            self.concept_neighbors[source_id].add(target_id)
            self.concept_neighbors[target_id].add(source_id)
            
            return True