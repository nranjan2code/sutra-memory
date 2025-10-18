from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Template:
    id: str
    tone: str  # friendly | formal | concise | regulatory
    moves: List[str]  # e.g., ["define", "evidence"]
    pattern: str  # e.g., "{lead} {answer}. {because} {evidence_1}"

# Minimal built-in templates (extensible via storage later)
BUILTIN_TEMPLATES: List[Template] = [
    Template(
        id="friendly_define_ev1",
        tone="friendly",
        moves=["define", "evidence"],
        pattern=(
            "{lead_friendly} {answer}. "
            "{because_opt}{evidence_1_opt}"
        ),
    ),
    Template(
        id="formal_define_ev1",
        tone="formal",
        moves=["define", "evidence"],
        pattern=(
            "{lead_formal} {answer}. "
            "{because_opt}{evidence_1_opt}"
        ),
    ),
    Template(
        id="concise_define",
        tone="concise",
        moves=["define"],
        pattern="{answer}.",
    ),
]


def select_template(tone: str, moves: List[str]) -> Template:
    # simple selection: exact tone match and covers requested moves
    for t in BUILTIN_TEMPLATES:
        if t.tone == tone and all(m in t.moves for m in moves):
            return t
    # fallback: concise
    return BUILTIN_TEMPLATES[-1]
