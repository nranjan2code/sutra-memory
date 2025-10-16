#!/usr/bin/env python3
"""
Comprehensive test with 50 diverse concepts to validate:
- Embedding quality at scale
- Vector search accuracy
- Query performance
- Save/reload consistency
"""

import time
from pathlib import Path
from sutra_core.config import production_config
from sutra_core.reasoning import ReasoningEngine

# 50 diverse concepts across multiple domains
CONCEPTS = [
    # Programming (10)
    "Python is a high-level programming language created by Guido van Rossum in 1991",
    "JavaScript is a scripting language commonly used for web development",
    "Java is an object-oriented programming language developed by Sun Microsystems",
    "C++ is a powerful systems programming language created by Bjarne Stroustrup",
    "Rust is a memory-safe systems programming language",
    "TypeScript is a typed superset of JavaScript developed by Microsoft",
    "Go is a statically typed compiled language created at Google",
    "Swift is Apple's programming language for iOS and macOS development",
    "Kotlin is a modern programming language that runs on the JVM",
    "Ruby is a dynamic object-oriented programming language created by Yukihiro Matsumoto",
    
    # Science (10)
    "DNA is the molecule that carries genetic instructions in living organisms",
    "Photosynthesis is the process plants use to convert sunlight into energy",
    "The speed of light in vacuum is approximately 299,792 kilometers per second",
    "Water molecules consist of two hydrogen atoms and one oxygen atom",
    "Gravity is the force that attracts objects toward each other",
    "The Earth orbits the Sun once every 365.25 days",
    "Atoms are the basic units of matter composed of protons, neutrons, and electrons",
    "Evolution is the process of change in species over generations through natural selection",
    "Black holes are regions of spacetime with extremely strong gravitational effects",
    "Quantum mechanics describes the behavior of matter at atomic and subatomic scales",
    
    # History (10)
    "World War II ended in 1945 with the surrender of Germany and Japan",
    "The Renaissance was a cultural movement in Europe from the 14th to 17th century",
    "The Roman Empire was one of the largest empires in ancient history",
    "The Industrial Revolution began in Britain in the late 18th century",
    "The Great Wall of China was built over centuries to protect against invasions",
    "Alexander the Great created one of the largest empires in ancient history",
    "The French Revolution began in 1789 and transformed French society",
    "The American Civil War was fought from 1861 to 1865",
    "The Apollo 11 mission landed humans on the Moon in 1969",
    "The Berlin Wall fell in 1989, marking the end of the Cold War",
    
    # Technology (10)
    "Artificial intelligence is the simulation of human intelligence by machines",
    "Machine learning is a subset of AI that learns from data without explicit programming",
    "Neural networks are computing systems inspired by biological brains",
    "Cloud computing provides on-demand computing resources over the internet",
    "Blockchain is a distributed ledger technology underlying cryptocurrencies",
    "The Internet is a global network connecting billions of devices worldwide",
    "Quantum computing uses quantum mechanics to process information",
    "5G is the fifth generation of cellular network technology",
    "Virtual reality creates immersive computer-generated environments",
    "The transistor is a fundamental semiconductor device invented in 1947",
    
    # Nature (10)
    "Dogs are domesticated mammals that belong to the family Canidae",
    "Cats are small carnivorous mammals often kept as pets",
    "The Sun is a star at the center of our solar system",
    "The Moon is Earth's only natural satellite",
    "Mount Everest is the highest mountain on Earth at 8,849 meters",
    "The Amazon rainforest is the world's largest tropical rainforest",
    "Whales are large marine mammals that breathe air",
    "Eagles are large birds of prey with exceptional vision",
    "Coral reefs are underwater ecosystems formed by coral polyps",
    "The Pacific Ocean is the largest and deepest ocean on Earth",
]

# Test queries with expected keywords
TEST_QUERIES = [
    ("Who created Python?", "Guido"),
    ("What is machine learning?", "subset"),
    ("When did World War II end?", "1945"),
    ("What are dogs?", "mammals"),
    ("What is DNA?", "genetic"),
    ("What is the speed of light?", "299"),
    ("What is JavaScript used for?", "web"),
    ("What is artificial intelligence?", "intelligence"),
    ("Tell me about the Sun", "star"),
    ("What is the largest ocean?", "Pacific"),
]

def run_test():
    storage_path = "./knowledge_50_concepts"
    
    print("\n" + "="*70)
    print("50-CONCEPT COMPREHENSIVE TEST")
    print("="*70)
    print("Testing: Learn 50 → Save → Reload → Query 10 → Verify")
    
    # Clean up
    import shutil
    if Path(storage_path).exists():
        shutil.rmtree(storage_path)
    
    # ========================================
    # PHASE 1: LEARNING
    # ========================================
    print("\n" + "="*70)
    print("PHASE 1: LEARNING 50 CONCEPTS")
    print("="*70)
    
    print("\n[1.1] Initializing engine...")
    start_time = time.time()
    config = production_config(storage_path=storage_path)
    engine1 = ReasoningEngine.from_config(config)
    init_time = time.time() - start_time
    print(f"✓ Engine initialized in {init_time:.2f}s")
    
    print("\n[1.2] Learning concepts...")
    learn_start = time.time()
    for i, concept in enumerate(CONCEPTS, 1):
        engine1.learn(concept)
        if i % 10 == 0:
            print(f"  [{i}/50] ✓ Learned {i} concepts...")
    learn_time = time.time() - learn_start
    print(f"\n✓ All 50 concepts learned in {learn_time:.2f}s ({50/learn_time:.1f} concepts/sec)")
    
    print("\n[1.3] Saving to disk...")
    engine1.save()
    print("✓ Saved")
    
    print("\n[1.4] Testing query before closing...")
    result = engine1.ask("Who created Python?")
    print(f"  Query: 'Who created Python?'")
    print(f"  Answer: {result.primary_answer}")
    print(f"  Confidence: {result.confidence:.2f}")
    
    engine1.close()
    print("\n[1.5] Engine closed")
    
    # ========================================
    # PHASE 2: RELOAD
    # ========================================
    print("\n" + "="*70)
    print("PHASE 2: RELOAD FROM DISK")
    print("="*70)
    
    print("\n[2.1] Creating new engine instance (simulating restart)...")
    reload_start = time.time()
    config2 = production_config(storage_path=storage_path)
    engine2 = ReasoningEngine.from_config(config2)
    reload_time = time.time() - reload_start
    print(f"✓ Engine reloaded in {reload_time:.2f}s")
    
    # ========================================
    # PHASE 3: QUERY TESTING
    # ========================================
    print("\n" + "="*70)
    print("PHASE 3: QUERY TESTING (10 QUERIES)")
    print("="*70)
    
    passed = 0
    failed = 0
    total_query_time = 0
    
    for i, (query, expected_keyword) in enumerate(TEST_QUERIES, 1):
        query_start = time.time()
        result = engine2.ask(query)
        query_time = (time.time() - query_start) * 1000  # ms
        total_query_time += query_time
        
        answer_lower = result.primary_answer.lower()
        keyword_lower = expected_keyword.lower()
        match = keyword_lower in answer_lower
        
        status = "✓" if match else "✗"
        passed += 1 if match else 0
        failed += 0 if match else 1
        
        print(f"\n  [{i}/10] {status} Query: '{query}'")
        print(f"       Expected: '{expected_keyword}'")
        print(f"       Answer: {result.primary_answer}")
        print(f"       Confidence: {result.confidence:.2f}")
        print(f"       Time: {query_time:.1f}ms")
    
    avg_query_time = total_query_time / len(TEST_QUERIES)
    
    print("\n" + "="*70)
    print("QUERY PERFORMANCE")
    print("="*70)
    print(f"  Passed: {passed}/{len(TEST_QUERIES)}")
    print(f"  Failed: {failed}/{len(TEST_QUERIES)}")
    print(f"  Success rate: {passed/len(TEST_QUERIES)*100:.1f}%")
    print(f"  Average query time: {avg_query_time:.1f}ms")
    
    # ========================================
    # PHASE 4: PERSISTENCE
    # ========================================
    print("\n" + "="*70)
    print("PHASE 4: PERSISTENCE VERIFICATION")
    print("="*70)
    
    print("\n[4.1] Testing persistence across multiple restarts...")
    
    # First query
    result1 = engine2.ask("What is machine learning?")
    engine2.close()
    
    # Reload and query again
    config3 = production_config(storage_path=storage_path)
    engine3 = ReasoningEngine.from_config(config3)
    result2 = engine3.ask("What is machine learning?")
    
    consistent = result1.primary_answer == result2.primary_answer
    status = "✓" if consistent else "✗"
    print(f"{status} Persistence check: {'PASS' if consistent else 'FAIL'}")
    print(f"  First answer:  {result1.primary_answer}")
    print(f"  Second answer: {result2.primary_answer}")
    
    engine3.close()
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    all_passed = passed == len(TEST_QUERIES) and consistent
    
    print(f"\nLearning: ✓ 50 concepts in {learn_time:.2f}s")
    print(f"Reload: ✓ {reload_time:.2f}s")
    print(f"Queries: {passed}/{len(TEST_QUERIES)} passed")
    print(f"Persistence: {'✓ PASS' if consistent else '✗ FAIL'}")
    print(f"\nOverall: {'✓✓✓ ALL TESTS PASSED ✓✓✓' if all_passed else '⚠ SOME TESTS FAILED'}")
    
    # Cleanup
    print("\n[Cleanup] Removing test data...")
    shutil.rmtree(storage_path)
    print("✓ Cleaned up")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(run_test())
