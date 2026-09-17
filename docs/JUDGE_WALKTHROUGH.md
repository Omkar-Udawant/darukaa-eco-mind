# Judge Walkthrough (self-guided, 10 minutes)

1. **Start vague** — `POST /chat {"message":"Biodiversity is declining."}` → confirm
   `clarifying_questions.length >= 2` and `completeness < 0.7`. (Conversational Intelligence)
2. **Go rich** — add SOC 0.6%, 520mm, 34C, cropland, pesticide, few bees → confirm 3 recommendations,
   each `dimensions_used.length >= 3`. (Depth of Reasoning)
3. **Check grounding** — for each `supporting_sources[]`, confirm `source` ∈ {FAO,IPCC,UNEP,IUCN,GBIF,
   NASA,USER} and the excerpt appears in `GET /sources`. (Scientific Grounding)
4. **Query the graph** — `GET /graph?src=carbon&dst=biodiversity_health` → ≥1 path;
   `POST /reason` → `kg_paths` non-empty. (Knowledge System)
5. **Check memory** — `GET /history` lists the conversation; `GET /conversation/{id}` replays turns;
   Reports page renders the longitudinal record. (Conversational Intelligence)
6. **Check numbers** — `POST /impact` gains in (0,70]; rich-vignette confidence ≥ vague-input
   confidence. (Output Quality)
7. **Run the gates** — `pytest -q` all green; `python scripts/eval.py` → PASS.

Scoring shortcut: if steps 2, 3, and 7 pass, the submission meets every hard requirement.
