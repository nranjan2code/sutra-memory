#!/usr/bin/env python3
"""
Sutra Core - Basic Demo

This demonstrates the core graph-based reasoning capabilities
using the new modular structure.
"""

import time
from collections import defaultdict

from sutra_core import Association, AssociationType, Concept, ReasoningStep
from sutra_core.learning import AdaptiveLearner, AssociationExtractor
from sutra_core.utils import extract_words


def demo_basic_functionality():
    """Demo basic concept and association functionality."""
    print("🧪 BASIC CONCEPT & ASSOCIATION DEMO")
    print("=" * 50)

    # Create concepts
    photosynthesis = Concept(
        id="photosynthesis",
        content="process by which plants convert light energy to chemical energy",
        category="biology",
    )

    mitochondria = Concept(
        id="mitochondria",
        content="cellular organelles that produce ATP energy",
        category="biology",
    )

    # Test concept access (strengthening)
    print(f"📊 Initial strength: {photosynthesis.strength}")
    photosynthesis.access()
    photosynthesis.access()
    print(f"📊 After 2 accesses: {photosynthesis.strength:.3f}")

    # Create association
    energy_assoc = Association(
        source_id="photosynthesis",
        target_id="mitochondria",
        assoc_type=AssociationType.SEMANTIC,
        confidence=0.8,
    )

    print(
        f"🔗 Created association: {energy_assoc.assoc_type.value} (confidence: {energy_assoc.confidence})"
    )

    # Test serialization
    concept_data = photosynthesis.to_dict()
    restored_concept = Concept.from_dict(concept_data)
    print(f"💾 Serialization works: {restored_concept.content[:30]}...")


def demo_adaptive_learning():
    """Demo the adaptive learning system."""
    print("\n🧠 ADAPTIVE LEARNING DEMO")
    print("=" * 50)

    # Set up the learning system
    concepts = {}
    associations = {}
    word_to_concepts = defaultdict(set)
    concept_neighbors = defaultdict(set)

    # Create extractor and learner
    extractor = AssociationExtractor(
        concepts, word_to_concepts, concept_neighbors, associations
    )
    learner = AdaptiveLearner(concepts, extractor)

    # Learn biology knowledge
    knowledge_items = [
        "Photosynthesis converts sunlight into chemical energy in plants",
        "Mitochondria are the powerhouses of cells that produce ATP",
        "DNA stores genetic information in double helix structure",
        "Chloroplasts contain chlorophyll that captures light energy",
        "ATP provides energy for cellular processes in living organisms",
    ]

    print(f"📚 Learning {len(knowledge_items)} concepts...")
    start_time = time.time()

    for item in knowledge_items:
        concept_id = learner.learn_adaptive(item, source="biology_demo")
        print(f"   ✅ Learned: {item[:45]}... (ID: {concept_id[:8]})")

    learning_time = time.time() - start_time
    print(f"\n⚡ Learning completed in {learning_time:.3f} seconds")
    print(f"📊 Created {len(concepts)} concepts")
    print(f"🔗 Formed {len(associations)} associations")

    # Show learning statistics
    stats = learner.get_learning_stats()
    print(f"\n📈 Learning Statistics:")
    print(f"   • Total concepts: {stats['total_concepts']}")
    print(f"   • Difficult concepts: {stats['difficult_concepts']} (strength < 4.0)")
    print(f"   • Easy concepts: {stats['easy_concepts']} (strength > 7.0)")
    print(f"   • Average strength: {stats['average_strength']:.2f}")


def demo_text_processing():
    """Demo text processing utilities."""
    print("\n📝 TEXT PROCESSING DEMO")
    print("=" * 50)

    test_texts = [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning algorithms process large datasets",
        "Photosynthesis is a crucial biological process",
    ]

    for text in test_texts:
        words = extract_words(text)
        print(f"Text: {text}")
        print(f"   → Words: {words}")

    # Demo association patterns
    from sutra_core.utils import get_association_patterns

    patterns = get_association_patterns()

    print(f"\n🔍 Available Association Patterns:")
    for pattern, assoc_type in patterns:
        print(f"   • {assoc_type.value}: {pattern}")


def demo_association_extraction():
    """Demo association extraction from text."""
    print("\n🔍 ASSOCIATION EXTRACTION DEMO")
    print("=" * 50)

    # Set up system
    concepts = {}
    associations = {}
    word_to_concepts = defaultdict(set)
    concept_neighbors = defaultdict(set)

    extractor = AssociationExtractor(
        concepts, word_to_concepts, concept_neighbors, associations
    )

    # Test texts with different relationship types
    test_texts = [
        "Sunlight causes photosynthesis in plant leaves",
        "A mitochondrion is a cellular organelle",
        "Cells contain various organelles and structures",
        "DNA is similar to RNA in molecular structure",
        "Photosynthesis occurs before cellular respiration",
    ]

    print("🔍 Extracting associations from text...")
    for text in test_texts:
        print(f"\nText: {text}")
        associations_created = extractor.extract_associations(text, "test_concept")
        print(f"   → Created {associations_created} associations")

        # Show the associations
        for key, assoc in list(associations.items())[-associations_created:]:
            source_concept = concepts.get(assoc.source_id, {"content": assoc.source_id})
            target_concept = concepts.get(assoc.target_id, {"content": assoc.target_id})
            print(
                f"   • {source_concept['content'] if isinstance(source_concept, dict) else source_concept.content}"
            )
            print(f"     --[{assoc.assoc_type.value}]--> ")
            print(
                f"     {target_concept['content'] if isinstance(target_concept, dict) else target_concept.content}"
            )


def main():
    """Run the comprehensive demo."""
    print("🚀 SUTRA CORE - COMPREHENSIVE DEMO")
    print("=" * 60)
    print("Demonstrating graph-based reasoning with explainable AI")
    print("=" * 60)

    # Run all demos
    demo_basic_functionality()
    demo_adaptive_learning()
    demo_text_processing()
    demo_association_extraction()

    print("\n" + "=" * 60)
    print("🎉 SUTRA CORE DEMO COMPLETE!")
    print("✅ Modular graph-based reasoning system")
    print("✅ Adaptive focus learning")
    print("✅ Real-time knowledge integration")
    print("✅ 100% explainable associations")
    print("=" * 60)


if __name__ == "__main__":
    main()
