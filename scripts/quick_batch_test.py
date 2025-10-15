#!/usr/bin/env python3
"""
Quick test showing batch learning with queryable knowledge.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "sutra-core"))

from sutra_core.reasoning.engine import ReasoningEngine


def main():
    print("Testing batch learning with rich associations...\n")
    
    # Create engine
    engine = ReasoningEngine(
        storage_path="./test_knowledge",
        enable_batch_embeddings=True,
        use_rust_storage=False,
    )
    
    # Learn knowledge with explicit relationships (better for queries)
    knowledge = [
        ("Machine learning is a subset of artificial intelligence that enables systems to learn from data", None, "AI"),
        ("Deep learning is a type of machine learning that uses neural networks with multiple layers", None, "AI"),
        ("Neural networks are inspired by biological neurons in the brain", None, "AI"),
        ("Supervised learning requires labeled training data to learn patterns", None, "AI"),
        ("Unsupervised learning discovers patterns in unlabeled data automatically", None, "AI"),
        ("Reinforcement learning learns through trial and error with rewards and penalties", None, "AI"),
    ]
    
    print("Learning 6 concepts with batch API...")
    import time
    start = time.time()
    concept_ids = engine.learn_batch(knowledge)
    elapsed = time.time() - start
    print(f"✅ Learned {len(concept_ids)} concepts in {elapsed:.3f}s ({len(concept_ids)/elapsed:.1f} concepts/sec)\n")
    
    # Now query
    print("Querying learned knowledge...")
    result = engine.ask("What is machine learning?", num_reasoning_paths=5)
    
    print(f"\nQuery: 'What is machine learning?'")
    print(f"Primary Answer: {result.primary_answer[:100] if result.primary_answer else 'No specific answer'}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Supporting Paths: {len(result.supporting_paths)}")
    
    if result.supporting_paths:
        print("\nReasoning Path Example:")
        path = result.supporting_paths[0]
        print(f"  Confidence: {path.confidence:.2f}")
        print(f"  Steps: {len(path.steps)}")
    
    # Search concepts
    print("\n\nSearching for 'neural network'...")
    results = engine.search_concepts("neural network", limit=3)
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['content'][:80]}...")
        print(f"   Score: {r.get('relevance_score', 0):.3f}")
    
    # Stats
    if engine.embedding_batch_processor:
        stats = engine.embedding_batch_processor.get_stats()
        print(f"\n📊 Embedding Stats:")
        print(f"   Throughput: {stats['avg_throughput']:.1f} texts/sec")
        print(f"   Cache hits: {stats['cache_hits']}")


if __name__ == "__main__":
    main()
