# Knowledge System Design (Phase 3) — production-grade RAG

## Chunking strategy (`rag/ingest.py`)

- **800 chars / 120 overlap**, whitespace-normalized. Rationale: FAO/IPCC paragraphs carry one
  claim each; 800 chars ≈ 1–2 claims, small enough for precise citation excerpts (400-char caps in
  responses), overlap preserves sentence boundaries. Trade-off vs 512-token semantic chunks: ours is
  deterministic, dependency-free, and citation-friendly; upgrade path is sentence-aware splitting
  without changing the metadata contract.

## Metadata schema (every vector + SQL row)

`chunk_text, source, publication, year, evidence_strength (strong|medium|emerging), topic,
embedding_id`. `embedding_id` is the join key between Qdrant/Chroma and `scientific_sources`.

## Per-source ingestion pipelines

| Source | Pipeline | Topic tags |
|---|---|---|
| FAO reports | `POST /ingest` w/ `source=FAO`, soil/SOC texts | soil, agroforestry |
| IPCC AR6 | `source=IPCC`, restoration + phenology | agroforestry, climate, restoration |
| UNEP | `source=UNEP`, pollinator assessments | pollinator |
| IUCN | `source=IUCN`, fragmentation guidelines | restoration |
| GBIF | `source=GBIF`, occurrence syntheses | pollinator |
| NASA Earth Data | `source=NASA`, SMAP/MODIS moisture analyses | wetland, climate |
| Papers / soil / climate reports | `POST /upload` (file) or `/ingest` (JSON), default `emerging` | general → re-tagged |

`evidence_strength` defaults: UN assessments = strong, syntheses = medium, uploads = emerging
until corroborated. Retrieval ranks strong > medium > emerging.

## Retrieval strategy (`rag/retriever.py`)

1. **Topic routing**: keyword hints map query+metrics to topics (soil, pollinator, agroforestry,
   wetland, climate, restoration); per-topic quota prevents one topic drowning others.
2. **Evidence ranking**: deterministic tier sort after vector similarity.
3. **Graceful degradation**: topic miss → global top-k; empty KB → honest fallback provenance
   (labeled as such, never fabricated).

## Source verification (`agents/nodes.py::verification_agent` + tests)

- Drops docs lacking `chunk_text`/`source`; caps at 4 citations.
- `test_hallucination.py` enforces: every excerpt is a substring of a KB chunk AND every cited
  `source` is in the allowlist {FAO, IPCC, UNEP, IUCN, GBIF, NASA, USER}.
- Vector-backend choice (Qdrant/Chroma/local) and embedding choice (OpenAI/hash) are env-swappable
  with zero code change — demo survives without keys, production scales with them.
