import pytest
from sutra_nlg import NLGRealizer, NLGConfig, GroundingError

def test_realizer_basic_define_evidence():
    r = NLGRealizer(NLGConfig(tone="friendly", moves=["define","evidence"]))
    answer = "Python is a programming language"
    paths = [{
        "concepts": ["Python", "programming language"],
        "concept_ids": ["c1","c2"],
        "association_types": ["semantic"],
        "confidence": 0.9,
        "explanation": "semantic match"
    }]
    text, grounded, meta = r.realize(query="What is Python?", answer=answer, reasoning_paths=paths)
    assert "Python" in text
    assert grounded and grounded[0].grounded_to == ["c1"]
    assert meta["template_id"]


def test_realizer_grounding_gate_blocks_unrelated_text():
    r = NLGRealizer(NLGConfig(tone="friendly", moves=["define"]))
    # Force unrelated answer and no paths; pattern still uses answer so it should pass
    # Now simulate unrelated by passing empty answer and unrelated paths
    with pytest.raises(GroundingError):
        r._grounding_gate(
            grounded=[type("GS", (), {"text": "Unrelated sentence.", "grounded_to": []})()],
            answer="",
            paths=[{"concepts": ["Python"], "concept_ids": ["c1"]}],
        )
