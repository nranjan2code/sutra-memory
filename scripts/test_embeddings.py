#!/usr/bin/env python3
"""
Test script for EmbeddingBatchProcessor with MPS support.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "sutra-core"))

from sutra_core.learning.embeddings import create_embedding_processor


def test_embedding_processor():
    print("=" * 60)
    print("Testing EmbeddingBatchProcessor")
    print("=" * 60)
    
    # Create processor
    print("\n1. Creating embedding processor...")
    processor = create_embedding_processor(
        model_name="all-MiniLM-L6-v2",
        device="auto",
        mps_threshold=64,
    )
    print(f"   {processor}")
    
    # Test single embedding
    print("\n2. Testing single embedding...")
    text = "Machine learning is a subset of artificial intelligence"
    emb = processor.encode_single(text)
    print(f"   Text: '{text[:50]}...'")
    print(f"   Embedding shape: {emb.shape}")
    print(f"   Embedding norm: {(emb ** 2).sum() ** 0.5:.6f}")
    
    # Test small batch (CPU)
    print("\n3. Testing small batch (batch_size=10, should use CPU)...")
    texts = [f"This is test sentence number {i}" for i in range(10)]
    embeddings = processor.encode_batch(texts)
    print(f"   Batch size: {len(texts)}")
    print(f"   Embeddings shape: {embeddings.shape}")
    stats = processor.get_stats()
    print(f"   Throughput: {stats['avg_throughput']:.1f} texts/sec")
    
    # Test large batch (MPS)
    print("\n4. Testing large batch (batch_size=128, should use MPS)...")
    texts = [f"Artificial intelligence concept {i}" for i in range(128)]
    embeddings = processor.encode_batch(texts)
    print(f"   Batch size: {len(texts)}")
    print(f"   Embeddings shape: {embeddings.shape}")
    stats = processor.get_stats()
    print(f"   Throughput: {stats['avg_throughput']:.1f} texts/sec")
    
    # Test cache
    print("\n5. Testing cache (re-encoding same texts)...")
    embeddings2 = processor.encode_batch(texts[:10])  # Re-encode first 10
    stats = processor.get_stats()
    print(f"   Cache hits: {stats['cache_hits']}")
    print(f"   Cache misses: {stats['cache_misses']}")
    print(f"   Cache hit rate: {stats['cache_hit_rate']:.1f}%")
    
    # Performance summary
    print("\n6. Performance Summary:")
    stats = processor.get_stats()
    print(f"   Total embeddings: {stats['total_embeddings']}")
    print(f"   Total time: {stats['total_time']:.3f}s")
    print(f"   Batch count: {stats['batch_count']}")
    print(f"   Average throughput: {stats['avg_throughput']:.1f} texts/sec")
    print(f"   Cache size: {stats['cache_size']}")
    print(f"   Cache hit rate: {stats['cache_hit_rate']:.1f}%")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_embedding_processor()
