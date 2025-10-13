# Testing

Run tests:
- pytest -q

What’s covered:
- Deduplication and strengthening (sentence concepts)
- Temporal associations across successive texts
- Retrieval propagation via associations (one-hop and multi-hop)
- Association de-duplication (no duplicate edges for same key)
- Persistence roundtrip (counts and retrieval overlap)
- Post-load token index rebuild
- Atomic PBSS writes (no leftover .tmp files)

Test locations:
- tests/test_biological_trainer.py
- tests/test_persistence.py
