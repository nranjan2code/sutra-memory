import asyncio
import pytest

from src.biological_trainer import BiologicalTrainer, AssociationType


@pytest.mark.asyncio
async def test_dedup_and_strengthen_sentence_concepts():
    trainer = BiologicalTrainer()
    text = "Cats chase mice."
    await trainer.train_from_stream([text])
    await trainer.train_from_stream([text])

    # Find concepts with exact content match
    matches = [c for c in trainer.memory_system.concepts.values() if c.content == text]
    assert len(matches) == 1, "Sentence concept should be deduplicated"
    concept = matches[0]
    assert concept.access_frequency > 1, "Access frequency should increase on reinforcement"
    assert concept.strength > 0.2, "Strength should increase above initial baseline"
    assert concept.memory_type != concept.memory_type.EPHEMERAL, "Should consolidate beyond ephemeral"


@pytest.mark.asyncio
async def test_temporal_associations_between_texts():
    trainer = BiologicalTrainer()
    texts = [
        "Cats chase mice.",
        "Mice eat cheese.",
    ]
    await trainer.train_from_stream(texts)

    # Count temporal associations
    temporal = [a for a in trainer.memory_system.associations if a.association_type == AssociationType.TEMPORAL]
    # With two single-sentence texts, expect bidirectional links between them (2 edges)
    assert len(temporal) >= 2, "Temporal links should connect successive texts"


@pytest.mark.asyncio
async def test_retrieval_uses_associations():
    trainer = BiologicalTrainer()
    await trainer.train_from_stream([
        "Cats chase mice.",
        "Mice eat cheese.",
    ])
    results = trainer.query_knowledge("cats cheese", max_results=5)
    contents = [r["content"] for r in results]
    assert any("Mice eat cheese." in c for c in contents), "Associated sentence should surface via spreading activation"


@pytest.mark.asyncio
async def test_association_deduplication():
    trainer = BiologicalTrainer()
    text = "Neural networks learn representations."
    # Train multiple times on same text to trigger reinforcement
    for _ in range(3):
        await trainer.train_from_stream([text])

    # Ensure no duplicate association objects exist for same (source,target,type)
    keys = set()
    for a in trainer.memory_system.associations:
        key = (a.source_id, a.target_id, a.association_type)
        assert key not in keys, "Duplicate association detected"
        keys.add(key)


@pytest.mark.asyncio
async def test_multi_hop_retrieval_propagation():
    trainer = BiologicalTrainer()
    # Three texts in sequence; temporal edges link successive sentences
    texts = [
        "Cats chase mice.",
        "Mice eat cheese.",
        "Cheese is dairy.",
    ]
    await trainer.train_from_stream(texts)

    # Query with one hop likely won't reach the third sentence
    res1 = trainer.query_knowledge("cats", max_results=10, hops=1)
    contents1 = [r["content"] for r in res1]
    # Multi-hop (2) should allow propagation to the third sentence via temporal chain
    res2 = trainer.query_knowledge("cats", max_results=10, hops=2)
    contents2 = [r["content"] for r in res2]

    assert any("Cheese is dairy." in c for c in contents2), "Two-hop propagation should reach distant neighbors"
