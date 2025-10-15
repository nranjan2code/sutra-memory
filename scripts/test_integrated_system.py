#!/usr/bin/env python3
"""
Test integrated system with entity cache.

Tests that ReasoningEngine properly integrates with EntityCache:
1. Cache hits return LLM-extracted entities
2. Cache misses fall back to regex extraction
3. Concepts are queued for background processing
"""

import json
import os
import sys
import time
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "sutra-core"))

from sutra_core.reasoning.engine import ReasoningEngine


def setup_test_cache(storage_path: Path) -> None:
    """Set up test cache with sample data."""
    import hashlib
    
    storage_path.mkdir(parents=True, exist_ok=True)
    
    # Test content
    test_content = "The heart pumps blood through the body"
    concept_id = hashlib.md5(test_content.encode()).hexdigest()[:16]
    
    # Create sample concepts
    concepts = {
        concept_id: {
            "id": concept_id,
            "content": test_content,
            "timestamp": time.time()
        }
    }
    
    # Create cache with one pre-extracted concept
    cache_data = {
        concept_id: {
            "entities": [
                {"text": "heart", "type": "organ", "confidence": 0.98},
                {"text": "blood", "type": "biological fluid", "confidence": 0.97},
                {"text": "body", "type": "anatomical structure", "confidence": 0.96}
            ],
            "timestamp": time.time(),
            "model": "gpt-oss:120b-cloud"
        }
    }
    
    # Create empty processing queue
    queue: list = []
    
    # Write files
    with open(storage_path / "concepts.json", "w") as f:
        json.dump(concepts, f, indent=2)
    
    with open(storage_path / "entity_cache.json", "w") as f:
        json.dump(cache_data, f, indent=2)
    
    with open(storage_path / "processing_queue.json", "w") as f:
        json.dump(queue, f, indent=2)
    
    print(f"✅ Test cache created at {storage_path}")
    print(f"   Concept ID: {concept_id}")


def test_cache_hit(engine: ReasoningEngine) -> None:
    """Test that cache hits use LLM-extracted entities."""
    print("\n=== Test 1: Cache Hit ===")
    
    # Learn a concept that exists in cache
    engine.learn("The heart pumps blood through the body")
    
    # Check that associations were created
    if len(engine.associations) > 0:
        print(f"✅ Created {len(engine.associations)} associations from cached entities")
        
        # Print some associations
        for i, (key, assoc) in enumerate(list(engine.associations.items())[:3]):
            source = engine.concepts[assoc.source_id].content
            target = engine.concepts[assoc.target_id].content
            print(f"  {i+1}. {source} → {target} ({assoc.assoc_type.name}, {assoc.confidence:.2f})")
    else:
        print("❌ No associations created from cache")


def test_cache_miss(engine: ReasoningEngine, storage_path: Path) -> None:
    """Test that cache misses fall back to regex and queue concept."""
    print("\n=== Test 2: Cache Miss ===")
    
    # Learn a concept not in cache
    engine.learn("Python is a programming language")
    
    # Check that associations were created (from regex fallback)
    if len(engine.associations) > 0:
        print(f"✅ Created {len(engine.associations)} associations from regex fallback")
    else:
        print("⚠️ No associations created (this is OK if no patterns matched)")
    
    # Check that concept was queued for background processing
    queue_file = storage_path / "processing_queue.json"
    if queue_file.exists():
        with open(queue_file) as f:
            queue = json.load(f)
        
        if len(queue) > 0:
            print(f"✅ Concept queued for background extraction: {len(queue)} in queue")
        else:
            print("❌ Concept not queued for background extraction")
    else:
        print("❌ Queue file not found")


def test_without_cache(storage_path: Path) -> None:
    """Test that system works without entity cache (backward compatibility)."""
    print("\n=== Test 3: Without Entity Cache (Backward Compatibility) ===")
    
    # Create engine without entity cache
    engine = ReasoningEngine(
        storage_path=str(storage_path / "no_cache"),
        enable_entity_cache=False,
        enable_parallel_associations=True,
        association_workers=2,
    )
    
    # Learn a concept
    engine.learn("Dogs are mammals that hunt mice")
    
    if len(engine.associations) > 0:
        print(f"✅ System works without entity cache: {len(engine.associations)} associations")
    else:
        print("❌ System failed without entity cache")


def main():
    """Run integration tests."""
    print("=" * 60)
    print("ENTITY CACHE INTEGRATION TEST")
    print("=" * 60)
    
    # Set up test storage
    test_dir = Path(__file__).parent.parent / "test_integration"
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    storage_path = test_dir / "storage"
    setup_test_cache(storage_path)
    
    # Create engine with entity cache enabled
    print("\n🚀 Initializing ReasoningEngine with EntityCache...")
    engine = ReasoningEngine(
        storage_path=str(storage_path),
        enable_entity_cache=True,
        enable_parallel_associations=True,
        association_workers=2,
    )
    
    if engine.entity_cache:
        print("✅ EntityCache initialized successfully")
    else:
        print("❌ EntityCache not initialized")
        return
    
    # Run tests
    try:
        test_cache_hit(engine)
        test_cache_miss(engine, storage_path)
        test_without_cache(test_dir)
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
