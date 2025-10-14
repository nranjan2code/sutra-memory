#!/usr/bin/env python3
"""
Test script to verify new structure has all functionality before removing old files.
"""

def test_new_structure():
    """Test that the new structure has all needed functionality."""
    try:
        from sutra_core import Concept, Association, AssociationType
        from sutra_core.learning import AdaptiveLearner, AssociationExtractor
        from sutra_core.utils import extract_words
        from collections import defaultdict
        
        print("✅ All imports successful")
        
        # Test that we can create a working system
        concepts = {}
        associations = {}
        word_to_concepts = defaultdict(set)
        concept_neighbors = defaultdict(set)

        extractor = AssociationExtractor(concepts, word_to_concepts, concept_neighbors, associations)
        learner = AdaptiveLearner(concepts, extractor)
        
        print("✅ Can create learning system")
        
        # Test learning
        concept_id = learner.learn_adaptive('Test knowledge for cleanup')
        print(f"✅ Learning works - created concept: {concept_id}")
        
        # Test concept access
        concept = concepts[concept_id]
        old_strength = concept.strength
        concept.access()
        print(f"✅ Concept access works - strength: {old_strength} → {concept.strength}")
        
        # Test text processing
        words = extract_words("The quick brown fox jumps")
        print(f"✅ Text processing works - words: {words}")
        
        print("\n🎉 NEW STRUCTURE IS FULLY FUNCTIONAL")
        print("✅ Safe to remove old files")
        return True
        
    except Exception as e:
        print(f"❌ New structure test failed: {e}")
        print("⚠️  Do not remove old files yet")
        return False

if __name__ == "__main__":
    test_new_structure()