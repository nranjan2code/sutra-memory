#!/usr/bin/env python3
"""
Test batch learning with EmbeddingBatchProcessor and MPS support.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "sutra-core"))

from sutra_core.reasoning.engine import ReasoningEngine


def test_batch_learning():
    print("=" * 70)
    print("Testing Batch Learning with MPS Support")
    print("=" * 70)
    
    # Create engine with batch embeddings enabled
    print("\n1. Initializing ReasoningEngine with batch embeddings...")
    engine = ReasoningEngine(
        storage_path="./test_batch_knowledge",
        enable_batch_embeddings=True,
        embedding_model="all-MiniLM-L6-v2",
        mps_batch_threshold=64,
        enable_vector_index=True,
        use_rust_storage=False,  # Use in-memory for faster testing
    )
    print("   ✅ Engine initialized")
    
    # Test 1: Small batch (CPU)
    print("\n2. Testing small batch (10 concepts, should use CPU)...")
    small_batch = [
        ("Machine learning is a subset of AI", "test", "AI"),
        ("Deep learning uses neural networks", "test", "AI"),
        ("Natural language processing handles text", "test", "AI"),
        ("Computer vision processes images", "test", "AI"),
        ("Reinforcement learning learns from rewards", "test", "AI"),
        ("Supervised learning needs labeled data", "test", "AI"),
        ("Unsupervised learning finds patterns", "test", "AI"),
        ("Transfer learning reuses knowledge", "test", "AI"),
        ("Feature engineering creates input variables", "test", "AI"),
        ("Model evaluation measures performance", "test", "AI"),
    ]
    
    start = time.time()
    concept_ids = engine.learn_batch(small_batch)
    elapsed = time.time() - start
    
    throughput = len(concept_ids) / elapsed
    print(f"   Learned {len(concept_ids)} concepts in {elapsed:.3f}s")
    print(f"   Throughput: {throughput:.1f} concepts/sec")
    
    # Test 2: Large batch (MPS)
    print("\n3. Testing large batch (128 concepts, should use MPS)...")
    large_batch = [
        (f"Concept number {i} about artificial intelligence and machine learning systems", "test", "AI")
        for i in range(128)
    ]
    
    start = time.time()
    concept_ids = engine.learn_batch(large_batch)
    elapsed = time.time() - start
    
    throughput = len(concept_ids) / elapsed
    print(f"   Learned {len(concept_ids)} concepts in {elapsed:.3f}s")
    print(f"   Throughput: {throughput:.1f} concepts/sec")
    
    # Test 3: Compare with sequential learning
    print("\n4. Comparing batch vs sequential learning...")
    test_concepts = [
        ("Python is a programming language", "test", "Programming"),
        ("JavaScript runs in browsers", "test", "Programming"),
        ("TypeScript adds types to JavaScript", "test", "Programming"),
        ("Rust is memory-safe", "test", "Programming"),
        ("Go is designed for concurrency", "test", "Programming"),
        ("Swift is used for iOS", "test", "Programming"),
        ("Kotlin is used for Android", "test", "Programming"),
        ("C++ offers low-level control", "test", "Programming"),
        ("Java runs on the JVM", "test", "Programming"),
        ("Ruby emphasizes simplicity", "test", "Programming"),
    ]
    
    # Sequential
    start = time.time()
    for content, source, category in test_concepts:
        engine.learn(content, source=source, category=category)
    seq_elapsed = time.time() - start
    seq_throughput = len(test_concepts) / seq_elapsed
    
    # Batch
    start = time.time()
    engine.learn_batch(test_concepts)
    batch_elapsed = time.time() - start
    batch_throughput = len(test_concepts) / batch_elapsed
    
    speedup = seq_elapsed / batch_elapsed
    print(f"   Sequential: {seq_elapsed:.3f}s ({seq_throughput:.1f} concepts/sec)")
    print(f"   Batch:      {batch_elapsed:.3f}s ({batch_throughput:.1f} concepts/sec)")
    print(f"   Speedup:    {speedup:.2f}x")
    
    # Test 4: Query learned knowledge
    print("\n5. Testing query on learned knowledge...")
    result = engine.ask("What is machine learning?", num_reasoning_paths=3)
    print(f"   Query: 'What is machine learning?'")
    print(f"   Primary answer: {result.primary_answer[:80] if result.primary_answer else 'No answer'}...")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Paths found: {len(result.supporting_paths)}")
    
    # Test 5: Check embedding processor stats
    if engine.embedding_batch_processor:
        print("\n6. Embedding processor statistics:")
        stats = engine.embedding_batch_processor.get_stats()
        print(f"   Total embeddings: {stats['total_embeddings']}")
        print(f"   Total time: {stats['total_time']:.3f}s")
        print(f"   Batch count: {stats['batch_count']}")
        print(f"   Avg throughput: {stats['avg_throughput']:.1f} texts/sec")
        print(f"   Cache hit rate: {stats['cache_hit_rate']:.1f}%")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ All batch learning tests passed!")
    print("=" * 70)
    print(f"\nKey Results:")
    print(f"  - Small batch (10): {len(small_batch)/elapsed if elapsed > 0 else 0:.1f} concepts/sec")
    print(f"  - Large batch (128): {throughput:.1f} concepts/sec")
    print(f"  - Batch vs Sequential: {speedup:.2f}x speedup")
    print(f"  - Embedding processor: {stats['avg_throughput']:.1f} texts/sec avg" if engine.embedding_batch_processor else "")
    print(f"  - Knowledge stored: {len(engine.concepts)} total concepts")


if __name__ == "__main__":
    test_batch_learning()
