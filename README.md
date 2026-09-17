# Darukaa.Earth — AI Biodiversity Intelligence (Environmental Reasoning Engine)

> NOT a chatbot. NOT prompt-engineering. An **AI Environmental Scientist** that retrieves evidence,
> reasons across ≥3 environmental dimensions, asks for missing data, and returns measurable impact estimates.

## Quickstart (local, no keys needed)

```bash
# backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000   # seeds KB from knowledge/seed_sources.json on boot

# frontend (new terminal)
cd frontend
npm install && npm run dev                  # http://localhost:3000
```

Try: `Biodiversity is declining on my cropland near Nashik. SOC 0.6%, rainfall 520mm, 34C, heavy pesticide, few bees.`

Vague input (`Biodiversity is declining.`) returns **clarifying questions** before recommendations.

## Architecture

```
Next.js 15 (Vercel) ──▶ FastAPI (Railway) ──▶ LangGraph: input→retrieval→scientist→biodiversity→impact→verify→respond
                                                   │              │                     │
                                              Qdrant/Chroma   Postgres (Supabase)    Redis (memory)
                                              OpenAI/Hash     13 tables              short-term turns
```

See `ARCHITECTURE.md`, `docs/API_SPEC.md`, `docs/DEPLOYMENT.md`, `docs/EVALUATION.md`.

## API

| Method | Path | Purpose |
|---|---|---|
| POST | `/chat` | Full 7-stage reasoning → 10-section response |
| POST | `/analyze` | Assessment + risks + chains + completeness |
| POST | `/recommend` | Ranked interventions (each ≥3 dimensions) |
| POST | `/reasoning`, `/reason` | Causal chains + KG paths + reasoning graph |
| POST | `/impact` | Impact estimate for an intervention |
| POST | `/upload`, `/ingest` | Index a document into the KB (file / JSON) |
| GET | `/conversation/{id}` | Memory + recommendations |
| GET | `/history` | Longitudinal conversation records |
| GET | `/graph` | Knowledge graph (`?src=&dst=` for paths) |
| GET | `/sources` | Evidence catalog (filter `?topic=soil`) |
| GET | `/metrics/{cid}` | Latest metrics per conversation |
| GET | `/health` | Liveness |

Every `/chat` response contains the 10 mandated sections: assessment, risks, recommendations,
reasoning, impacted metrics, estimated improvement, horizon, confidence, sources, data-needed.

## Production env

| Var | Local default | Production |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./darukaa.db` | Supabase Postgres `postgresql+psycopg2://…` (`backend/sql/schema.sql`) |
| `REDIS_URL` | empty (in-memory) | Upstash/Redis `redis://…` |
| `VECTOR_BACKEND` | `local` | `qdrant` (+`QDRANT_URL`) or `chroma` |
| `EMBEDDING_PROVIDER` | `hash` | `openai` (+`OPENAI_API_KEY`) |

## Deploy

- Backend → Railway (`backend/Dockerfile`), Frontend → Vercel (`frontend/`), DB → Supabase, Vector → Qdrant Cloud, Cache → Upstash. Full steps in `docs/DEPLOYMENT.md`.
- `docker-compose up --build` runs backend + frontend + Postgres + Redis + Qdrant locally.

## Tests & eval

```bash
cd backend && pytest -q
python scripts/eval.py   # dimension-compliance, citation-grounding, completeness-gating checks
```
