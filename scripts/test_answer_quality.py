#!/usr/bin/env python3
"""
Test answer quality with Phase 8A+ parallel associations.

Verifies that the parallel extraction maintains answer quality
by testing with a diverse set of questions and knowledge.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "sutra-core"))

from sutra_core.reasoning.engine import ReasoningEngine


def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def test_basic_facts():
    """Test basic factual knowledge."""
    print_section("TEST 1: Basic Factual Knowledge")
    
    engine = ReasoningEngine(
        storage_path="./test_quality_basic",
        enable_batch_embeddings=True,
        enable_parallel_associations=True,
        association_workers=4,
        use_rust_storage=False,
    )
    
    # Teach basic facts
    knowledge = [
        ("Python is a high-level programming language created by Guido van Rossum", None, "Programming"),
        ("Machine learning is a subset of artificial intelligence", None, "AI"),
        ("Deep learning uses neural networks with multiple layers", None, "AI"),
        ("TensorFlow is a machine learning framework developed by Google", None, "Tools"),
        ("PyTorch is a machine learning library developed by Facebook", None, "Tools"),
        ("JavaScript is a programming language used for web development", None, "Programming"),
        ("React is a JavaScript library for building user interfaces", None, "Tools"),
        ("SQL is used for managing relational databases", None, "Databases"),
        ("MongoDB is a NoSQL document database", None, "Databases"),
        ("Docker is a containerization platform", None, "DevOps"),
    ]
    
    print(f"Teaching {len(knowledge)} concepts...")
    start = time.time()
    concept_ids = engine.learn_batch(knowledge)
    elapsed = time.time() - start
    print(f"✅ Learned in {elapsed:.3f}s ({len(concept_ids)/elapsed:.1f} concepts/sec)\n")
    
    # Test questions
    test_cases = [
        {
            "question": "What is Python?",
            "expected_keywords": ["programming", "language", "high-level"],
            "min_confidence": 0.5,
        },
        {
            "question": "What is machine learning?",
            "expected_keywords": ["artificial intelligence", "subset", "ai"],
            "min_confidence": 0.5,
        },
        {
            "question": "Tell me about TensorFlow",
            "expected_keywords": ["machine learning", "framework", "google"],
            "min_confidence": 0.5,
        },
        {
            "question": "What is React used for?",
            "expected_keywords": ["javascript", "user interface", "library"],
            "min_confidence": 0.5,
        },
    ]
    
    passed = 0
    for i, test in enumerate(test_cases, 1):
        print(f"\nQuestion {i}: {test['question']}")
        print("-" * 70)
        
        result = engine.ask(test['question'], num_reasoning_paths=5)
        
        print(f"Answer: {result.primary_answer or 'No answer found'}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Reasoning paths: {len(result.supporting_paths)}")
        print(f"Consensus strength: {result.consensus_strength:.2f}")
        
        # Check quality
        answer_lower = (result.primary_answer or "").lower()
        keywords_found = [kw for kw in test['expected_keywords'] 
                         if kw.lower() in answer_lower]
        
        has_answer = result.primary_answer is not None and len(result.primary_answer) > 0
        has_confidence = result.confidence >= test['min_confidence']
        has_keywords = len(keywords_found) > 0
        
        print(f"\nQuality Check:")
        print(f"  ✓ Has answer: {has_answer}")
        print(f"  ✓ Confidence ≥ {test['min_confidence']}: {has_confidence} ({result.confidence:.2f})")
        print(f"  ✓ Contains keywords: {has_keywords} ({keywords_found})")
        
        if has_answer and (has_confidence or has_keywords):
            print("  ✅ PASS")
            passed += 1
        else:
            print("  ❌ FAIL")
    
    print(f"\n{'=' * 70}")
    print(f"Basic Facts: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def test_relational_reasoning():
    """Test reasoning across relationships."""
    print_section("TEST 2: Relational Reasoning")
    
    engine = ReasoningEngine(
        storage_path="./test_quality_relations",
        enable_batch_embeddings=True,
        enable_parallel_associations=True,
        association_workers=4,
        use_rust_storage=False,
    )
    
    # Teach related concepts
    knowledge = [
        ("Dogs are domesticated mammals that are often kept as pets", None, "Animals"),
        ("Cats are small carnivorous mammals that are popular pets", None, "Animals"),
        ("Pets provide companionship and emotional support to humans", None, "Animals"),
        ("Veterinarians are doctors who treat animals", None, "Professions"),
        ("Pet food is specially formulated nutrition for domesticated animals", None, "Products"),
        ("Exercise is important for maintaining pet health", None, "Health"),
        ("Training helps dogs learn commands and good behavior", None, "Training"),
        ("Cats are independent animals that groom themselves", None, "Animals"),
    ]
    
    print(f"Teaching {len(knowledge)} concepts...")
    start = time.time()
    concept_ids = engine.learn_batch(knowledge)
    elapsed = time.time() - start
    print(f"✅ Learned in {elapsed:.3f}s\n")
    
    # Test relational questions
    test_cases = [
        {
            "question": "What are pets?",
            "check_content": ["dog", "cat", "animal", "companion", "mammal"],
        },
        {
            "question": "Who takes care of animals?",
            "check_content": ["veterinarian", "doctor", "treat"],
        },
        {
            "question": "What do pets need?",
            "check_content": ["food", "exercise", "health", "training"],
        },
    ]
    
    passed = 0
    for i, test in enumerate(test_cases, 1):
        print(f"\nQuestion {i}: {test['question']}")
        print("-" * 70)
        
        result = engine.ask(test['question'], num_reasoning_paths=5)
        
        print(f"Answer: {result.primary_answer or 'No answer found'}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Paths found: {len(result.supporting_paths)}")
        
        if result.supporting_paths:
            print(f"\nReasoning paths:")
            for j, path in enumerate(result.supporting_paths[:3], 1):
                print(f"  Path {j}: Confidence: {path.confidence:.2f}, Steps: {len(path.steps)}")
        
        # Check if answer contains relevant content
        answer_lower = (result.primary_answer or "").lower()
        relevant_found = [word for word in test['check_content'] 
                         if word.lower() in answer_lower]
        
        has_answer = result.primary_answer is not None and len(result.primary_answer) > 0
        has_paths = len(result.supporting_paths) > 0
        has_relevant = len(relevant_found) > 0
        
        print(f"\nQuality Check:")
        print(f"  ✓ Has answer: {has_answer}")
        print(f"  ✓ Has reasoning paths: {has_paths}")
        print(f"  ✓ Relevant content: {has_relevant} ({relevant_found})")
        
        if has_answer and has_paths:
            print("  ✅ PASS")
            passed += 1
        else:
            print("  ❌ FAIL")
    
    print(f"\n{'=' * 70}")
    print(f"Relational Reasoning: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def test_complex_knowledge():
    """Test with more complex, interconnected knowledge."""
    print_section("TEST 3: Complex Knowledge Graph")
    
    engine = ReasoningEngine(
        storage_path="./test_quality_complex",
        enable_batch_embeddings=True,
        enable_parallel_associations=True,
        association_workers=4,
        use_rust_storage=False,
    )
    
    # Teach complex interconnected knowledge
    knowledge = [
        ("Climate change is caused by greenhouse gas emissions", None, "Environment"),
        ("Greenhouse gases trap heat in the atmosphere", None, "Science"),
        ("Carbon dioxide is a major greenhouse gas", None, "Science"),
        ("Fossil fuels release carbon dioxide when burned", None, "Energy"),
        ("Coal, oil, and natural gas are fossil fuels", None, "Energy"),
        ("Renewable energy produces minimal greenhouse gas emissions", None, "Energy"),
        ("Solar panels convert sunlight into electricity", None, "Technology"),
        ("Wind turbines generate electricity from wind", None, "Technology"),
        ("Electric vehicles reduce fossil fuel consumption", None, "Transportation"),
        ("Forests absorb carbon dioxide from the atmosphere", None, "Environment"),
        ("Deforestation increases atmospheric carbon dioxide levels", None, "Environment"),
        ("Ocean acidification is caused by absorbed carbon dioxide", None, "Environment"),
    ]
    
    print(f"Teaching {len(knowledge)} concepts...")
    start = time.time()
    concept_ids = engine.learn_batch(knowledge)
    elapsed = time.time() - start
    print(f"✅ Learned in {elapsed:.3f}s\n")
    
    # Test complex questions requiring multi-hop reasoning
    test_cases = [
        {
            "question": "What causes climate change?",
            "must_have": ["greenhouse gas", "emission", "carbon dioxide"],
        },
        {
            "question": "How can we reduce carbon emissions?",
            "should_have": ["renewable", "solar", "wind", "electric", "forest"],
        },
        {
            "question": "What are fossil fuels?",
            "must_have": ["coal", "oil", "gas", "natural gas"],
        },
    ]
    
    passed = 0
    for i, test in enumerate(test_cases, 1):
        print(f"\nQuestion {i}: {test['question']}")
        print("-" * 70)
        
        result = engine.ask(test['question'], num_reasoning_paths=7)
        
        print(f"Answer: {result.primary_answer or 'No answer found'}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Paths: {len(result.supporting_paths)}")
        print(f"Consensus: {result.consensus_strength:.2f}")
        
        if result.supporting_paths:
            print(f"\nTop reasoning paths:")
            for j, path in enumerate(result.supporting_paths[:2], 1):
                print(f"  {j}. Confidence: {path.confidence:.2f}, Steps: {len(path.steps)}")
        
        # Check answer quality
        answer_lower = (result.primary_answer or "").lower()
        
        must_have_found = []
        should_have_found = []
        
        if "must_have" in test:
            must_have_found = [term for term in test['must_have'] 
                              if term.lower() in answer_lower]
        
        if "should_have" in test:
            should_have_found = [term for term in test['should_have'] 
                                if term.lower() in answer_lower]
        
        has_answer = result.primary_answer is not None and len(result.primary_answer) > 0
        has_must_have = len(must_have_found) > 0 if "must_have" in test else True
        has_should_have = len(should_have_found) > 0 if "should_have" in test else True
        
        print(f"\nQuality Check:")
        print(f"  ✓ Has answer: {has_answer}")
        if "must_have" in test:
            print(f"  ✓ Must-have terms: {has_must_have} ({must_have_found})")
        if "should_have" in test:
            print(f"  ✓ Should-have terms: {has_should_have} ({should_have_found})")
        
        if has_answer and has_must_have:
            print("  ✅ PASS")
            passed += 1
        else:
            print("  ❌ FAIL")
    
    print(f"\n{'=' * 70}")
    print(f"Complex Knowledge: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def main():
    """Run all quality tests."""
    print("=" * 70)
    print("ANSWER QUALITY TEST SUITE - Phase 8A+")
    print("=" * 70)
    print("\nTesting answer quality with parallel association extraction...")
    
    results = {
        "Basic Facts": test_basic_facts(),
        "Relational Reasoning": test_relational_reasoning(),
        "Complex Knowledge": test_complex_knowledge(),
    }
    
    # Final summary
    print_section("FINAL RESULTS")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:25} {status}")
    
    print(f"\n{'=' * 70}")
    print(f"Overall: {total_passed}/{total_tests} test suites passed")
    
    if total_passed == total_tests:
        print("\n🎉 SUCCESS! All answer quality tests passed!")
        print("Parallel association extraction maintains high quality.")
    else:
        print(f"\n⚠️  {total_tests - total_passed} test suite(s) failed.")
        print("Quality may need improvement.")
    
    return total_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
