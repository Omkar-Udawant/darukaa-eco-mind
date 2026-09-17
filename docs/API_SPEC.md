# API Specification — base URL `http://localhost:8000`

## POST /chat → ChatResponse (10 sections + graph + completeness)
Request: `{ message, conversation_id?, metrics?: EnvMetrics, user_email? }`
Response keys: `conversation_id, situation_assessment, key_risks, recommendations[],
scientific_reasoning, impacted_metrics, estimated_improvement, time_horizon,
confidence, supporting_sources[], additional_data_needed, clarifying_questions[],
reasoning_graph{nodes[], edges[]}, completeness`.

Example:
```bash
curl -X POST localhost:8000/chat -H 'Content-Type: application/json' -d '{
  "message": "Biodiversity is declining on my cropland. SOC 0.6%, rainfall 520mm, 34C, heavy pesticide, few bees."}'
```

## POST /analyze `{ conversation_id?, metrics }` → `{ assessment, risks, chains, graph, completeness, missing }`
## POST /recommend `{ conversation_id?, metrics, top_k=3 }` → `{ recommendations, confidence }`
## POST /reasoning, POST /reason (same as Analyze) → `{ chains, kg_paths, graph, dimensions, scientific_reasoning }`
## POST /impact `{ metrics, intervention }` → `{ biodiversity_gain_pct, soil_carbon_gain_pct, water_retention_gain_pct, habitat_quality_gain_pct, horizon }`
## POST /upload (multipart `file`, query `source`) → `{ filename, chunks_indexed, source }`
## POST /ingest (JSON `{ text, source, publication, year, topic, evidence_strength }`) → `{ chunks_indexed, source, topic }`
## GET /history?user_email=&limit=20 → `[{ id, title, region, turns }]`
## GET /graph / GET /graph?src=carbon&dst=biodiversity_health → `{ entities[], relationships[] }` or `{ paths[] }` / `{ entity, out[], in[] }`
## GET /conversation/{id} → `{ conversation, memory[], recommendations[] }`
## GET /sources?topic=soil → `[{ source, publication, year, topic, evidence_strength, excerpt }]`
## GET /metrics/{conversation_id} → latest soil/climate/biodiversity/land_use/human_impact snapshots
## GET /health → `{ status: ok }`

All errors use FastAPI detail format; recommendation objects always carry `dimensions_used` (len ≥ 3).
