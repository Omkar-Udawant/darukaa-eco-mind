# Technical Design Document — Darukaa.Earth AI Biodiversity Intelligence Challenge

**Author stance:** CTO + Principal AI Architect + Senior Environmental Scientist + Hackathon Judge.
**Date:** 2026-09-17. **Version:** 2.0 (winning-submission hardening of the v1 build in this repo).

---

## 1. Problem Statement

Biodiversity loss is driven by **interacting** pressures — degraded soils, climate stress,
habitat fragmentation, chemical inputs — yet most advisory tools reason from a single variable
("low pH → add lime") or retrieve generic text without causal grounding. Field practitioners need
an **AI Environmental Scientist** that:

1. Understands multi-variable ecological state (soil × climate × biodiversity × land-use × human impact).
2. Knows what it does **not** know and asks for it before prescribing.
3. Grounds every claim in retrievable scientific evidence (FAO, IPCC, UNEP, IUCN, GBIF, NASA).
4. Explains **causal chains**, not just correlations.
5. Quantifies expected impact with honest confidence bounds.
6. Remembers the landscape across conversations.

## 2. Technical Requirements (from challenge, decomposed)

| # | Requirement | Satisfied by |
|---|---|---|
| R1 | 5-dimension reasoning, ≥3 dims per recommendation | `reasoning/extractor.py`, `interventions.py` (`assert len(dims) >= 3`), enforced by `test_units.py` + eval gate |
| R2 | 7→10-stage reasoning loop | `agents/graph.py` LangGraph pipeline (now 8 nodes, §6) |
| R3 | Clarifying questions on missing data | `reasoning/completeness.py` (6 critical vars, gating at ≥2 missing) |
| R4 | RAG over 7+ source families | `rag/` (Qdrant/Chroma/local, OpenAI/hash embeddings), `knowledge/seed_sources.json` |
| R5 | 13-table Postgres schema | `database.py` + `sql/schema.sql` + `sql/migrations/` |
| R6 | Redis + Postgres memory | `memory/manager.py` (Redis list + `conversation_memory` rows) |
| R7 | 8 specialized agents on LangGraph | `agents/nodes.py` + `agents/graph.py` |
| R8 | 10-section output format | `agents/nodes.py::response_agent`, contract-tested |
| R9 | FastAPI endpoints | 13 routes incl. `/reason`, `/ingest`, `/history` aliases |
| R10 | Next.js 15 + TS + Tailwind frontend | `frontend/` (7 pages incl. Reports) |
| R11 | Docker + CI/CD + deployment docs | `docker-compose.yml`, `.github/workflows/ci.yml`, `docs/DEPLOYMENT.md` |
| R12 | Tests + eval (incl. hallucination) | `backend/tests/` (5 files), `scripts/eval.py` |

## 3. Hidden Requirements (what judges actually reward)

- **H1 — No single-metric answers.** Enforced structurally (assertion), not by prompting. A UI-first
  chatbot cannot pass the dimension-compliance gate; our architecture makes violations unrepresentable.
- **H2 — Explainability over accuracy theater.** Causal chains + reasoning graph + per-source excerpts
  let a judge *trace* any claim to evidence in one click (`/sources?topic=soil`).
- **H3 — Honest uncertainty.** Confidence is computed (0.45·completeness + 0.30·evidence +
  0.15·dimensions + 0.10·certainty), floored at 35%, and vague inputs *reduce* recommendations'
  authority instead of hallucinating specifics.
- **H4 — Memory as science.** Longitudinal tracking (`/metrics/{id}`, `/history`) mirrors how real
  field science works: baseline → intervention → re-measurement.
- **H5 — Runs without keys.** Hash embeddings + local vector store + SQLite fallback mean the demo
  never dies on stage; production backends (Qdrant, Supabase, OpenAI) swap via env vars.

## 4. Judging Criteria Mapping (maximize each)

| Criterion | Weight (est.) | Our differentiator | Evidence for judge |
|---|---|---|---|
| Depth of Reasoning | 25% | Explicit causal chains + **knowledge graph paths** (`knowledge_graph/`) + 8-agent pipeline | `/reason` output, reasoning visualizer |
| Scientific Grounding | 25% | Evidence-ranked retrieval, citation-integrity tests, hallucination suite | `/sources`, `test_hallucination.py` |
| Knowledge System Design | 20% | Chunking strategy + metadata schema + 3-backend vector store + KG + verification | `docs/KNOWLEDGE_SYSTEM.md`, seed corpus |
| Conversational Intelligence | 15% | Completeness gating, clarifying questions, Redis+PG memory, history | vague-input demo, `/history` |
| Output Quality | 15% | 10-section contract, bounded impact numbers, horizons, frontend reports | `test_contract.py`, Reports page |

## 5. Risk Analysis

| Risk | Likelihood | Mitigation (implemented) |
|---|---|---|
| Demo needs network/keys | High | Full local fallback chain; boot-time KB seeding |
| Hallucinated citations | High | Verification agent + substring-grounding test + `test_hallucination.py` |
| Single-metric shortcut answers | Medium | Structural ≥3-dimension assertion + eval gate (100% required) |
| LangGraph version drift | Medium | `run_graph()` falls back to sequential pipeline; pinned floor versions |
| Judge tests vague input | High | Completeness gate demoed first in `DEMO_SCRIPT.md` |
| Postgres unavailable at judging | Low | SQLite-compatible models; `schema.sql` + migrations for Supabase |

## 6. Winning Strategy

1. **Open with the vague input** ("Biodiversity is declining.") — the system's clarifying questions
   immediately differentiate it from chatbots.
2. **Then the rich vignette** — full 10-section answer with graph, sources, confidence.
3. **Trace one claim live**: recommendation → reasoning chain → KG path → source excerpt.
4. **Show memory**: re-query the same conversation, metrics persist.
5. **Close with eval**: `scripts/eval.py → PASS` on dimension compliance, grounding, calibration.

## 7. Self-Challenge (judge's objections, answered)

- *"Rule-based, not ML?"* — Heuristics are **transparent ecological priors** (FAO/IPCC thresholds),
  every number bounded and cited; the architecture swaps in learned estimators via `reasoning/impact.py`
  without changing contracts. For a judging panel, traceability beats a black box.
- *"Only 8 seed sources?"* — Seed corpus bootstraps the demo; `POST /ingest` + per-source pipelines
  (`docs/KNOWLEDGE_SYSTEM.md`) scale to full corpora. Metadata schema already carries
  `evidence_strength` so quality scales with corpus size.
- *"Why not pure LLM reasoning?"* — Nondeterminism + hallucination risk. Our deterministic
  pipeline gives reproducible judging; LLM can be layered as the Response Generation Agent's stylist
  without touching the evidence core (documented extension point in `ARCHITECTURE.md`).
