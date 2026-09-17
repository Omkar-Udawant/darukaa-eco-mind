# Architecture — Darukaa.Earth Environmental Reasoning Engine

## Reasoning loop (LangGraph `StateGraph`, sequential fallback in `backend/app/agents/graph.py`)

1. **Input Agent** (`agents/nodes.py::input_agent`) — merges `EnvMetrics` + regex/KW extraction (`reasoning/extractor.py`); outputs `dimensions_present`.
2. **Missing Information Agent** (`missing_info_agent`) — runs `reasoning/completeness.py` FIRST (6 critical
   vars; ≥2 missing → `clarifying_questions`), so downstream agents know what is unknown.
3. **Retrieval Agent** — topic-routed (`rag/retriever.py`) over Qdrant/Chroma/local; evidence-ranked (strong > medium > emerging); logs to `retrieval_logs`.
4. **Scientist Agent** — `reasoning/causal.py` chains **plus `knowledge_graph/` BFS paths**
   (e.g. carbon → microbial → plant → pollinator → biodiversity health); risk list from thresholds.
5. **Biodiversity Agent** — `reasoning/interventions.py` catalog of 6; `assert len(dimensions) >= 3` enforced; scored by applicability.
6. **Impact Agent** — `reasoning/impact.py` bounded heuristics per intervention class.
7. **Evidence Validation Agent** — citation integrity (allowlist + grounding), `reasoning/confidence.py` (0.45·completeness + 0.30·evidence + 0.15·dimensions + 0.10·certainty), 10-section assembly.
8. **Response Generation Agent** — assembles the mandated 10-section contract.

## Knowledge graph (`backend/app/knowledge_graph/`)

17 entities (soil, carbon, moisture, pH, rainfall, temperature, species, habitat, pollution,
deforestation, agriculture, water, + intermediates), 28 causal edges with mechanism + evidence family.
Queries: `neighbors()`, `find_paths(src, dst)` (BFS), `reasoning_paths_for_metrics()` (state-activated),
exposed via `GET /graph`. See `docs/ERD.md` for the SQL ERD.

## RAG

`rag/ingest.py` chunks (800/120) → `vectorstore.py` (Qdrant → Chroma → local) with metadata
`chunk_text/source/publication/year/evidence_strength/topic`; `embeddings.py` OpenAI or deterministic hash.
Seed: `knowledge/seed_sources.json` (FAO, IPCC, UNEP, IUCN, GBIF, NASA).

## Memory

`memory/manager.py`: Redis list `darukaa:{cid}` (last 40 turns) + `conversation_memory` rows for long-term;
`GET /conversation/{id}` replays both.

## Data

13 tables in `backend/app/database.py` (+ `backend/sql/schema.sql` for Supabase): users, conversations,
conversation_memory, soil/climate/biodiversity/land_use/human_impact _metrics, recommendations,
scientific_sources, retrieval_logs, reasoning_logs, impact_predictions.

## Observability

Every `/chat` writes metric rows ×5, recommendation + impact rows, one retrieval log, one reasoning log.
