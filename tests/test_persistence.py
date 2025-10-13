import asyncio
import os
import shutil
import tempfile
import pytest

from src.biological_trainer import BiologicalTrainer


@pytest.mark.asyncio
async def test_persistence_roundtrip(tmp_path):
    base = os.path.join(str(tmp_path), "kb")
    t1 = BiologicalTrainer()
    await t1.train_from_stream([
        "Cats chase mice.",
        "Mice eat cheese.",
    ])
    # Save
    t1.save_memory(base)

    # Load into a fresh trainer
    t2 = BiologicalTrainer()
    t2.load_memory(base)

    # Check that we have at least the same number of concepts and associations
    s1 = t1._get_memory_stats()
    s2 = t2._get_memory_stats()
    assert s2['total_concepts'] >= s1['total_concepts']
    assert s2['total_associations'] >= s1['total_associations']

    # Query should surface associated content similarly
    r1 = t1.query_knowledge("cats cheese", max_results=5)
    r2 = t2.query_knowledge("cats cheese", max_results=5)
    assert len(r2) > 0
    # There should be an overlap in top contents
    top1 = {x['content'] for x in r1[:3]}
    top2 = {x['content'] for x in r2[:3]}
    assert top1 & top2

    # Token index should be populated after load
    assert any(tok in t2.memory_system.token_index for tok in {"cats", "cheese"})

    # No temporary files should remain from atomic writes
    node_dir = os.path.join(base, "nodes")
    leftovers = [f for f in os.listdir(node_dir) if f.endswith('.tmp')]
    assert not leftovers, f"Found leftover temp files: {leftovers}"
