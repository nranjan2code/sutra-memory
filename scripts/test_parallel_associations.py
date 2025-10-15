#!/usr/bin/env python3
"""
Test parallel association extraction performance.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "sutra-core"))

from sutra_core.reasoning.engine import ReasoningEngine


def main():
    print("=" * 70)
    print("Testing Parallel Association Extraction (Phase 8A+)")
    print("=" * 70)
    
    # Test data
    knowledge = [
        ("Machine learning is a subset of artificial intelligence that enables systems to learn", None, "AI"),
        ("Deep learning is a type of machine learning using neural networks", None, "AI"),
        ("Python is a high-level programming language used for AI development", None, "Programming"),
        ("TensorFlow is a machine learning framework developed by Google", None, "AI"),
        ("Natural language processing enables computers to understand human language", None, "AI"),
        ("Computer vision allows machines to interpret visual information from images", None, "AI"),
        ("Reinforcement learning trains agents through trial and error with rewards", None, "AI"),
        ("Supervised learning requires labeled training data for model training", None, "AI"),
        ("Unsupervised learning discovers patterns in unlabeled data automatically", None, "AI"),
        ("Transfer learning reuses pretrained models for new tasks", None, "AI"),
    ] * 10  # 100 concepts total
    
    print(f"\nTest dataset: {len(knowledge)} concepts\n")
    
    # Test 1: Without parallel associations (Phase 8A baseline)
    print("Test 1: Sequential association extraction (Phase 8A)")
    print("-" * 70)
    
    engine_seq = ReasoningEngine(
        storage_path="./test_seq",
        enable_batch_embeddings=True,
        enable_parallel_associations=False,  # Sequential
        use_rust_storage=False,
    )
    
    start = time.time()
    concept_ids = engine_seq.learn_batch(knowledge)
    seq_time = time.time() - start
    seq_throughput = len(concept_ids) / seq_time
    
    print(f"Time: {seq_time:.3f}s")
    print(f"Throughput: {seq_throughput:.1f} concepts/sec")
    print(f"Concepts learned: {len(concept_ids)}")
    
    # Test 2: With parallel associations (Phase 8A+)
    print("\nTest 2: Parallel association extraction (Phase 8A+)")
    print("-" * 70)
    
    engine_par = ReasoningEngine(
        storage_path="./test_par",
        enable_batch_embeddings=True,
        enable_parallel_associations=True,  # Parallel!
        association_workers=4,
        use_rust_storage=False,
    )
    
    start = time.time()
    concept_ids = engine_par.learn_batch(knowledge)
    par_time = time.time() - start
    par_throughput = len(concept_ids) / par_time
    
    print(f"Time: {par_time:.3f}s")
    print(f"Throughput: {par_throughput:.1f} concepts/sec")
    print(f"Concepts learned: {len(concept_ids)}")
    
    # Comparison
    print("\n" + "=" * 70)
    print("Performance Comparison")
    print("=" * 70)
    speedup = seq_time / par_time if par_time > 0 else 0
    improvement = ((par_throughput - seq_throughput) / seq_throughput * 100) if seq_throughput > 0 else 0
    
    print(f"Sequential (Phase 8A):     {seq_throughput:.1f} concepts/sec")
    print(f"Parallel (Phase 8A+):      {par_throughput:.1f} concepts/sec")
    print(f"Speedup:                   {speedup:.2f}x")
    print(f"Improvement:               +{improvement:.1f}%")
    
    # Time saved
    time_saved = seq_time - par_time
    time_saved_pct = (time_saved / seq_time * 100) if seq_time > 0 else 0
    print(f"\nTime saved: {time_saved:.2f}s ({time_saved_pct:.1f}%)")
    
    # Query test
    print("\n" + "=" * 70)
    print("Quality Verification")
    print("=" * 70)
    
    result = engine_par.ask("What is machine learning?", num_reasoning_paths=3)
    print(f"Query: 'What is machine learning?'")
    print(f"Answer: {result.primary_answer[:80] if result.primary_answer else 'No answer'}...")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Paths: {len(result.supporting_paths)}")
    
    print("\n" + "=" * 70)
    print("✅ Phase 8A+ Test Complete!")
    print("=" * 70)
    
    if speedup >= 1.3:
        print(f"🎉 SUCCESS: {speedup:.2f}x speedup achieved!")
    else:
        print(f"⚠️  Speedup lower than expected: {speedup:.2f}x")
        print("   (Expected: ≥1.3x for 100 concepts)")


if __name__ == "__main__":
    main()
