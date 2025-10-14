#!/usr/bin/env python3
"""
Validation script for monorepo reorganization.

This script tests that all modules can be imported correctly
and basic functionality works after the reorganization.
"""

import sys
import os

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages', 'sutra-core'))

def test_imports():
    """Test that all main modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from sutra_core import (
            Concept, 
            Association, 
            AssociationType,
            ReasoningStep,
            ReasoningPath,
            extract_words,
            get_association_patterns
        )
        print("✅ Core imports successful")
    except Exception as e:
        print(f"❌ Core import failed: {e}")
        return False
    
    try:
        from sutra_core.learning import AdaptiveLearner, AssociationExtractor
        print("✅ Learning module imports successful")
    except Exception as e:
        print(f"❌ Learning import failed: {e}")
        return False
    
    try:
        from sutra_core.utils import extract_words, calculate_word_overlap
        print("✅ Utils module imports successful")
    except Exception as e:
        print(f"❌ Utils import failed: {e}")
        return False
    
    return True


def test_basic_functionality():
    """Test basic functionality of core components."""
    print("\n🧪 Testing basic functionality...")
    
    from sutra_core import Concept, Association, AssociationType
    from collections import defaultdict
    
    # Test concept creation and access
    concept = Concept(id="test", content="test concept", source="validation")
    initial_strength = concept.strength
    concept.access()
    
    if concept.strength > initial_strength:
        print("✅ Concept access strengthening works")
    else:
        print("❌ Concept access strengthening failed")
        return False
    
    # Test association creation
    assoc = Association(
        source_id="a",
        target_id="b", 
        assoc_type=AssociationType.SEMANTIC,
        confidence=0.8
    )
    
    if assoc.source_id == "a" and assoc.assoc_type == AssociationType.SEMANTIC:
        print("✅ Association creation works")
    else:
        print("❌ Association creation failed")
        return False
    
    # Test text processing
    from sutra_core.utils import extract_words
    words = extract_words("The quick brown fox jumps")
    
    if "quick" in words and "the" not in words:
        print("✅ Text processing works")
    else:
        print("❌ Text processing failed")
        return False
    
    return True


def test_adaptive_learning():
    """Test adaptive learning components."""
    print("\n🧪 Testing adaptive learning...")
    
    from sutra_core.learning import AdaptiveLearner, AssociationExtractor
    from collections import defaultdict
    
    # Set up learning system
    concepts = {}
    associations = {}
    word_to_concepts = defaultdict(set)
    concept_neighbors = defaultdict(set)
    
    try:
        extractor = AssociationExtractor(
            concepts, word_to_concepts, concept_neighbors, associations
        )
        learner = AdaptiveLearner(concepts, extractor)
        
        # Test basic learning
        concept_id = learner.learn_adaptive(
            "Test knowledge for validation",
            source="validation_test"
        )
        
        if concept_id in concepts:
            print("✅ Adaptive learning works")
            return True
        else:
            print("❌ Adaptive learning failed - concept not created")
            return False
            
    except Exception as e:
        print(f"❌ Adaptive learning failed: {e}")
        return False


def test_serialization():
    """Test serialization functionality."""
    print("\n🧪 Testing serialization...")
    
    from sutra_core import Concept, Association, AssociationType
    
    # Test concept serialization
    original_concept = Concept(
        id="test_serialize",
        content="test content",
        source="test_source",
        strength=5.0
    )
    
    concept_data = original_concept.to_dict()
    restored_concept = Concept.from_dict(concept_data)
    
    if (restored_concept.id == original_concept.id and 
        restored_concept.content == original_concept.content and
        restored_concept.strength == original_concept.strength):
        print("✅ Concept serialization works")
    else:
        print("❌ Concept serialization failed")
        return False
    
    # Test association serialization
    original_assoc = Association(
        source_id="src",
        target_id="tgt",
        assoc_type=AssociationType.CAUSAL,
        confidence=0.9
    )
    
    assoc_data = original_assoc.to_dict()
    restored_assoc = Association.from_dict(assoc_data)
    
    if (restored_assoc.source_id == original_assoc.source_id and
        restored_assoc.assoc_type == original_assoc.assoc_type and
        restored_assoc.confidence == original_assoc.confidence):
        print("✅ Association serialization works")
        return True
    else:
        print("❌ Association serialization failed")
        return False


def main():
    """Run all validation tests."""
    print("🚀 Sutra AI Monorepo Reorganization Validation")
    print("=" * 50)
    
    all_passed = True
    
    # Run all tests
    tests = [
        test_imports,
        test_basic_functionality, 
        test_adaptive_learning,
        test_serialization
    ]
    
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Monorepo reorganization successful!")
        print("\n✨ Next steps:")
        print("  1. Install development dependencies: pip install -r requirements-dev.txt")
        print("  2. Run full test suite: make test")
        print("  3. Continue with hybrid and API package implementation")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())