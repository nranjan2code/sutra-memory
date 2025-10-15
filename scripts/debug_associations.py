#!/usr/bin/env python3
"""
Debug script to check if parallel associations are being created.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "sutra-core"))

from sutra_core.reasoning.engine import ReasoningEngine


def main():
    print("=" * 70)
    print("DEBUGGING PARALLEL ASSOCIATION EXTRACTION")
    print("=" * 70)
    
    # Test with simple knowledge
    engine = ReasoningEngine(
        storage_path="./debug_associations",
        enable_batch_embeddings=True,
        enable_parallel_associations=True,
        association_workers=4,
        use_rust_storage=False,
    )
    
    knowledge = [
        ("A dog is a mammal", None, "Animals"),
        ("A cat is a mammal", None, "Animals"),
        ("A mammal is an animal", None, "Biology"),
        ("Training causes good behavior in dogs", None, "Training"),
    ]
    
    print(f"\nTeaching {len(knowledge)} concepts...")
    concept_ids = engine.learn_batch(knowledge)
    
    print(f"\n📊 Knowledge Base Stats:")
    print(f"  Concepts: {len(engine.concepts)}")
    print(f"  Associations: {len(engine.associations)}")
    print(f"  Concept neighbors: {sum(len(v) for v in engine.concept_neighbors.values())}")
    
    print(f"\n📝 Concepts:")
    for cid, concept in engine.concepts.items():
        print(f"  {cid[:8]}...: {concept.content}")
    
    print(f"\n🔗 Associations:")
    for (src, tgt), assoc in engine.associations.items():
        src_content = engine.concepts[src].content if src in engine.concepts else src[:8]
        tgt_content = engine.concepts[tgt].content if tgt in engine.concepts else tgt[:8]
        print(f"  {src_content} --[{assoc.assoc_type.name}]--> {tgt_content}")
    
    print(f"\n🔍 Testing Query...")
    result = engine.ask("What are dogs?", num_reasoning_paths=5)
    print(f"  Answer: {result.primary_answer or 'No answer'}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Paths: {len(result.supporting_paths)}")
    
    if result.supporting_paths:
        print(f"\n  Reasoning paths:")
        for i, path in enumerate(result.supporting_paths, 1):
            print(f"    {i}. {path.query} → {path.answer} (conf: {path.confidence:.2f})")
            for step in path.steps:
                print(f"       - {step.explanation}")


if __name__ == "__main__":
    main()
