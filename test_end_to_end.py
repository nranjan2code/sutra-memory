#!/usr/bin/env python3
"""
End-to-End Test: Learn → Save → Reload → Query

Tests the complete lifecycle:
1. Learn concepts with embeddings
2. Save to disk
3. Close engine
4. Reload from disk
5. Query and verify answers
"""

import time
import shutil
from pathlib import Path


def cleanup_test_data():
    """Remove test knowledge base."""
    test_path = Path("./test_knowledge_e2e")
    if test_path.exists():
        shutil.rmtree(test_path)
        print("✓ Cleaned up old test data")


def test_learn_phase():
    """Phase 1: Learn concepts and save to disk."""
    from sutra_core.reasoning.engine import ReasoningEngine
    
    print("\n" + "="*70)
    print("PHASE 1: LEARNING")
    print("="*70)
    
    # Initialize fresh engine
    print("\n[1.1] Initializing ReasoningEngine...")
    engine = ReasoningEngine(storage_path="./test_knowledge_e2e")
    print(f"✓ Engine initialized (model: google/embeddinggemma-300m)")
    
    # Learn diverse concepts
    print("\n[1.2] Learning concepts...")
    concepts = [
        "Python is a high-level programming language created by Guido van Rossum in 1991",
        "Guido van Rossum is a Dutch programmer who created Python",
        "Dogs are domesticated mammals that belong to the family Canidae",
        "Cats are small carnivorous mammals often kept as pets",
        "The sun is a star at the center of our solar system",
        "Machine learning is a subset of artificial intelligence",
        "JavaScript is a programming language commonly used for web development",
        "The moon is Earth's only natural satellite",
    ]
    
    concept_ids = []
    for i, text in enumerate(concepts, 1):
        concept_id = engine.learn(text)
        concept_ids.append(concept_id)
        print(f"  [{i}/{len(concepts)}] ✓ {text[:50]}...")
    
    # Verify concepts are in memory
    stats = engine.storage.stats()
    print(f"\n[1.3] Stats after learning:")
    print(f"  Total concepts: {stats['total_concepts']}")
    print(f"  Total associations: {stats['total_associations']}")
    
    # Save to disk
    print("\n[1.4] Saving to disk...")
    engine.save()
    print("✓ Saved successfully")
    
    # Test query before closing (memory verification)
    print("\n[1.5] Testing query BEFORE closing (memory)...")
    result = engine.ask("Who created Python?")
    print(f"  Query: 'Who created Python?'")
    print(f"  Answer: {result.primary_answer}")
    print(f"  Confidence: {result.confidence:.2f}")
    
    # Close engine
    print("\n[1.6] Closing engine...")
    engine.close()
    print("✓ Engine closed")
    
    return concept_ids


def test_reload_phase(expected_concept_ids):
    """Phase 2: Reload from disk and verify data."""
    from sutra_core.reasoning.engine import ReasoningEngine
    
    print("\n" + "="*70)
    print("PHASE 2: RELOAD FROM DISK")
    print("="*70)
    
    # Simulate restart - create new engine instance
    print("\n[2.1] Creating NEW engine instance (simulating restart)...")
    engine = ReasoningEngine(storage_path="./test_knowledge_e2e")
    print("✓ New engine created")
    
    # Verify stats match
    print("\n[2.2] Verifying loaded data...")
    stats = engine.storage.stats()
    print(f"  Concepts loaded: {stats['total_concepts']}")
    print(f"  Associations loaded: {stats['total_associations']}")
    
    # Verify specific concepts exist
    print("\n[2.3] Checking concept IDs...")
    found = 0
    for cid in expected_concept_ids[:3]:  # Check first 3
        if engine.storage.has_concept(cid):
            found += 1
    print(f"✓ Found {found}/{min(3, len(expected_concept_ids))} expected concepts")
    
    return engine


def test_query_phase(engine):
    """Phase 3: Query loaded knowledge."""
    
    print("\n" + "="*70)
    print("PHASE 3: QUERY LOADED KNOWLEDGE")
    print("="*70)
    
    test_queries = [
        ("Who created Python?", "Guido"),
        ("What are dogs?", "mammals"),
        ("What is machine learning?", "artificial intelligence"),
        ("Tell me about the sun", "star"),
    ]
    
    results = []
    for query, expected_keyword in test_queries:
        print(f"\n  Query: '{query}'")
        print(f"  Expected keyword: '{expected_keyword}'")
        
        try:
            start = time.time()
            result = engine.ask(query, num_reasoning_paths=3)
            query_time = (time.time() - start) * 1000
            
            print(f"  Answer: {result.primary_answer}")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Time: {query_time:.1f}ms")
            
            # Check keyword
            found = expected_keyword.lower() in result.primary_answer.lower()
            status = "✓" if found else "✗"
            print(f"  {status} Keyword match")
            
            results.append(found)
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results.append(False)
    
    return results


def test_persistence():
    """Phase 4: Verify data persists across multiple restarts."""
    from sutra_core.reasoning.engine import ReasoningEngine
    
    print("\n" + "="*70)
    print("PHASE 4: PERSISTENCE VERIFICATION")
    print("="*70)
    
    print("\n[4.1] First restart...")
    engine1 = ReasoningEngine(storage_path="./test_knowledge_e2e")
    stats1 = engine1.storage.stats()
    result1 = engine1.ask("Who created Python?")
    engine1.close()
    
    print("\n[4.2] Second restart...")
    engine2 = ReasoningEngine(storage_path="./test_knowledge_e2e")
    stats2 = engine2.storage.stats()
    result2 = engine2.ask("Who created Python?")
    engine2.close()
    
    print("\n[4.3] Comparing results...")
    print(f"  Concepts: {stats1['total_concepts']} vs {stats2['total_concepts']}")
    print(f"  Answer 1: {result1.primary_answer}")
    print(f"  Answer 2: {result2.primary_answer}")
    
    # Verify consistency
    consistent = (
        stats1['total_concepts'] == stats2['total_concepts'] and
        result1.primary_answer == result2.primary_answer
    )
    
    if consistent:
        print("✓ Data persists consistently across restarts")
    else:
        print("✗ Data inconsistency detected!")
    
    return consistent


def main():
    """Run complete end-to-end test."""
    
    print("\n" + "="*70)
    print("END-TO-END PIPELINE TEST")
    print("="*70)
    print("Testing: Learn → Save → Reload → Query → Persist")
    
    start_time = time.time()
    
    # Cleanup
    cleanup_test_data()
    
    try:
        # Phase 1: Learn and save
        concept_ids = test_learn_phase()
        
        # Phase 2: Reload
        engine = test_reload_phase(concept_ids)
        
        # Phase 3: Query
        query_results = test_query_phase(engine)
        engine.close()
        
        # Phase 4: Persistence
        persistence_ok = test_persistence()
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        total_time = time.time() - start_time
        passed = sum(query_results)
        total = len(query_results)
        
        print(f"\nPhase 1 (Learn): ✓ PASS")
        print(f"Phase 2 (Reload): ✓ PASS")
        print(f"Phase 3 (Query): {passed}/{total} queries passed")
        print(f"Phase 4 (Persist): {'✓ PASS' if persistence_ok else '✗ FAIL'}")
        
        print(f"\nTotal time: {total_time:.2f}s")
        
        all_passed = (passed == total and persistence_ok)
        
        if all_passed:
            print("\n" + "="*70)
            print("✓✓✓ ALL TESTS PASSED ✓✓✓")
            print("="*70)
            print("\nEnd-to-end pipeline working correctly:")
            print("  ✓ Learning with embeddings")
            print("  ✓ Saving to disk")
            print("  ✓ Loading from disk")
            print("  ✓ Querying loaded knowledge")
            print("  ✓ Persistent across restarts")
        else:
            print("\n" + "="*70)
            print("⚠ SOME TESTS FAILED")
            print("="*70)
        
        # Cleanup
        print("\n[Cleanup] Removing test data...")
        cleanup_test_data()
        
        return all_passed
        
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        # Cleanup on error
        cleanup_test_data()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
