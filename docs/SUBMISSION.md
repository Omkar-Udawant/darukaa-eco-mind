# Hackathon Submission — Darukaa.Earth AI Biodiversity Intelligence

**Team:** solo build, CTO-to-judge methodology. **Track:** AI Biodiversity Intelligence Challenge.

## What it is (30 seconds)

An **Environmental Reasoning Engine** — an AI Environmental Scientist that reads multi-variable
ecological state, asks for what's missing, retrieves evidence (FAO/IPCC/UNEP/IUCN/GBIF/NASA),
reasons through causal chains **and a knowledge graph**, and returns quantified, cited,
confidence-scored interventions. Not a chatbot: single-metric answers are structurally impossible
(`assert len(dimensions_used) >= 3`, eval-gated at 100%).

## Judging-criteria checklist

- **Depth of Reasoning:** 8-agent LangGraph pipeline + causal chains + 17-entity knowledge graph
  with BFS path queries (`GET /graph?src=carbon&dst=biodiversity_health`).
- **Scientific Grounding:** evidence-ranked RAG, citation allowlist + substring-grounding tests,
  dedicated hallucination suite (`test_hallucination.py`).
- **Knowledge System Design:** chunking/metadata/retrieval/verification documented
  (`docs/KNOWLEDGE_SYSTEM.md`); Qdrant/Chroma/local + OpenAI/hash swappable via env.
- **Conversational Intelligence:** completeness gating (vague → clarifying questions), Redis+Postgres
  memory, `/history` longitudinal records, Reports page.
- **Output Quality:** 10-section contract on every `/chat`, bounded impact %, horizons, 7 frontend pages.

## Run it (2 minutes)

```bash
cd darukaa-earth/backend && pip install -r requirements.txt && uvicorn app.main:app --reload
cd darukaa-earth/frontend && npm install && npm run dev
pytest -q            # 20+ tests, incl. RAG / hallucination / performance
python ../scripts/eval.py   # PASS
```

## Repo map

`backend/app/{agents,reasoning,rag,knowledge_graph,memory,api}` · `backend/sql/{schema.sql,migrations/}` ·
`frontend/app/{chat,metrics,reasoning,sources,recommendations,reports,admin}` ·
`docs/{TECHNICAL_DESIGN,ARCHITECTURE_DIAGRAM,API_SPEC,DEPLOYMENT,EVALUATION,ERD,KNOWLEDGE_SYSTEM,DEMO_SCRIPT,PRESENTATION_NOTES,JUDGE_WALKTHROUGH,SUBMISSION}` ·
`knowledge/{seed_sources.json,demo_dataset.json}`
