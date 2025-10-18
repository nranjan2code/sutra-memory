# Sutra NLG (No-LLM Natural Language Generation)

Grounded, explainable response generation for Sutra Hybrid without using LLMs.

Features (initial version):
- Template-driven generation with tone support (friendly, formal, concise, regulatory)
- Micro-planning moves: define, evidence (extensible)
- Grounding gate: every sentence built from retrieved answer/evidence
- Deterministic output with optional seed

Usage:
- Import from sutra-hybrid API layer and post-process ExplainableResult
- Never invent facts: all slots come from answer/reasoning paths

Extensibility:
- Add paraphrase bank, clarifiers, analogy/blending engines later
