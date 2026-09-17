# Presentation Notes (narrative + anticipated Q&A)

## Narrative arc
1. **Problem:** biodiversity collapse is multi-causal; tools are single-variable or black-box.
2. **Insight:** make shallow answers *structurally impossible* — dimensions asserted in code, gated in eval.
3. **System:** 8 agents, knowledge graph + RAG, memory, quantified impact, honest confidence.
4. **Proof:** live vague→rich demo, claim-to-evidence trace, green test suite.

## Anticipated judge questions
- **"Why not just GPT + RAG?"** — Nondeterminism + citation hallucination. Our deterministic pipeline
  is reproducible and every citation is substring-grounded (tested). An LLM can style the response
  layer later without touching the evidence core.
- **"Rule-based impact numbers?"** — Transparent bounded heuristics from FAO/IPCC ranges, labeled with
  horizons; `reasoning/impact.py` is the documented swap-in point for learned estimators.
- **"Only 8 seed sources?"** — Bootstrap corpus; `/ingest` pipelines per source family scale it, and
  `evidence_strength` tiers mean quality compounds with corpus size.
- **"Does it handle my region/crop?"** — Extraction is keyword + numeric and region-aware; unknown
  inputs lower completeness → clarifying questions instead of confabulation (demo this).
- **"Production readiness?"** — Docker Compose, CI, Supabase schema + migrations, Qdrant/Redis/OpenAI
  via env, health + logs tables for observability.

## One-liners
- "A chatbot answers. A scientist asks for data."
- "Every claim, three clicks to evidence."
- "Shallow answers are unrepresentable here — forbidden by assertion, not by prompt."
