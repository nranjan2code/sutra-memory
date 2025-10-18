from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .templates import select_template

@dataclass
class NLGConfig:
    tone: str = "friendly"  # friendly | formal | concise | regulatory
    moves: List[str] = None  # e.g., ["define", "evidence"]
    seed: Optional[int] = None

@dataclass
class GroundedSentence:
    text: str
    grounded_to: List[str]  # list of concept_ids

class GroundingError(Exception):
    pass

class NLGRealizer:
    """Minimal grounded realizer: deterministic, template-driven.

    Inputs:
      - answer: canonical answer text (from storage)
      - reasoning_paths: list of path objects with concept_ids and concepts
    Outputs:
      - final text + grounding map
    """

    def __init__(self, config: Optional[NLGConfig] = None):
        self.config = config or NLGConfig()
        if self.config.moves is None:
            self.config.moves = ["define", "evidence"]

    def realize(self,
                query: str,
                answer: str,
                reasoning_paths: Optional[List[Dict[str, Any]]] = None) -> Tuple[str, List[GroundedSentence], Dict[str, Any]]:
        template = select_template(self.config.tone, self.config.moves)

        # slots
        lead = self._lead_phrase(self.config.tone)
        because_opt = "Because " if self._has_evidence(reasoning_paths) else ""
        evidence_1_opt, evidence_ids = self._evidence_1(reasoning_paths)

        # render
        rendered = template.pattern
        rendered = rendered.replace("{lead_friendly}", lead)
        rendered = rendered.replace("{lead_formal}", lead)
        rendered = rendered.replace("{answer}", answer.strip())
        rendered = rendered.replace("{because_opt}", because_opt)
        rendered = rendered.replace("{evidence_1_opt}", evidence_1_opt)

        sentences = [s.strip() for s in rendered.split(".") if s.strip()]

        grounded: List[GroundedSentence] = []
        for i, s in enumerate(sentences):
            if i == 0:
                grounded.append(GroundedSentence(text=s + ".", grounded_to=evidence_ids or []))
            else:
                grounded.append(GroundedSentence(text=s + ".", grounded_to=evidence_ids))

        # grounding gate: ensure all tokens come from answer/evidence pool
        self._grounding_gate(grounded, answer, reasoning_paths)

        meta = {
            "template_id": template.id,
            "tone": self.config.tone,
            "moves": self.config.moves,
            "evidence_used": evidence_ids,
        }
        final_text = " ".join([g.text for g in grounded]).strip()
        return final_text, grounded, meta

    def _lead_phrase(self, tone: str) -> str:
        if tone == "friendly":
            return "Here’s what I found:"
        if tone == "formal":
            return "According to the knowledge base,"
        if tone == "regulatory":
            return "Per documented sources,"
        return "Summary:"

    def _has_evidence(self, paths: Optional[List[Dict[str, Any]]]) -> bool:
        return bool(paths)

    def _evidence_1(self, paths: Optional[List[Dict[str, Any]]]) -> Tuple[str, List[str]]:
        if not paths:
            return "", []
        # take first concept from first path as evidence snippet
        p0 = paths[0]
        # expected shape from ExplainableResult.reasoning_paths: dicts with 'concepts' and 'concept_ids'
        concepts = p0.get("concepts") or []
        cids = p0.get("concept_ids") or []
        if concepts:
            snippet = concepts[0]
            return f"{snippet}", cids[:1]
        return "", cids[:1]

    def _grounding_gate(self, grounded: List[GroundedSentence], answer: str, paths: Optional[List[Dict[str, Any]]]):
        allowed_pool = set((answer or "").lower().split())
        if paths:
            for p in paths:
                for text in (p.get("concepts") or []):
                    allowed_pool.update((text or "").lower().split())
        # very permissive initial check: ensure at least half tokens come from pool
        for g in grounded:
            tokens = [t.strip(",;:()[]") for t in g.text.lower().split()]
            if not tokens:
                raise GroundingError("Empty sentence after realization")
            overlap = sum(1 for t in tokens if t in allowed_pool)
            if overlap / max(1, len(tokens)) < 0.5:
                raise GroundingError("Grounding check failed: low lexical overlap")
