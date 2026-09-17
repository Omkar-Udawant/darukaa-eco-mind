# Entity-Relationship Diagram (13 tables)

```mermaid
erDiagram
    users ||--o{ conversations : "has"
    conversations ||--o{ conversation_memory : "remembers"
    conversations ||--o{ soil_metrics : "measures"
    conversations ||--o{ climate_metrics : "measures"
    conversations ||--o{ biodiversity_metrics : "measures"
    conversations ||--o{ land_use_metrics : "measures"
    conversations ||--o{ human_impact_metrics : "measures"
    conversations ||--o{ recommendations : "produces"
    conversations ||--o{ retrieval_logs : "logs"
    conversations ||--o{ reasoning_logs : "logs"
    recommendations ||--o{ impact_predictions : "quantifies"
    scientific_sources ||--o{ retrieval_logs : "cited-by"

    users { text id PK "uuid" }
    users { text email UK }
    conversations { text id PK }
    conversations { text user_id FK }
    conversation_memory { text id PK }
    conversation_memory { text conversation_id FK }
    recommendations { text id PK }
    recommendations { text conversation_id FK }
    impact_predictions { text recommendation_id FK }
    scientific_sources { text source "FAO/IPCC/UNEP/..." }
    retrieval_logs { text query }
    reasoning_logs { text stage }
```

**Design decisions (judge-ready answers):**
- One `conversation_id` fans out to all five metric tables → a conversation IS a longitudinal
  landscape record; re-measuring appends rows, never overwrites (audit trail for science).
- `recommendations.dimensions_used` (JSON) makes the ≥3-dimension rule queryable for eval.
- `retrieval_logs` + `reasoning_logs` give full observability: every claim traces to query → docs → chains.
- `scientific_sources.embedding_id` joins the SQL catalog to the vector store for citation-integrity checks.
```
