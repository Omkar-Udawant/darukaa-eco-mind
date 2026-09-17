# Demo Script (5 minutes, live, no keys needed)

## 0:00 — The hook: ask a bad question (Conversational Intelligence)
Paste: **`Biodiversity is declining.`** → system refuses to guess; returns 6 clarifying questions
(SOC, rainfall, land use, temperature, pollinators, pH) with completeness 0%.
Say: *"A chatbot would have answered. A scientist asks for data."*

## 1:00 — The rich vignette (Output Quality + Depth)
Paste: **`Biodiversity is declining on my cropland near Nashik. SOC 0.6%, rainfall 520mm, 34C, heavy pesticide, few bees.`**
Walk the 10 sections: assessment → 4 risks → 3 recommendations → reasoning → metrics → improvement →
horizon → confidence (~78%) → 4 cited sources → data still needed.

## 2:30 — Trace one claim (Scientific Grounding)
Pick "Legume-based cover cropping": read its reasoning aloud → show the KG path
(`carbon → microbial → plant → pollinator → biodiversity health`) → open Sources, find the FAO 2017
excerpt it came from. *"Every claim, three clicks to evidence."*

## 3:30 — Memory + Reports (longitudinal science)
Ask a follow-up in the same conversation → open Reports → show turns, persisted metrics
(`GET /metrics/{id}`), recommendations. *"Baseline → intervention → re-measurement."*

## 4:15 — Prove it (trust)
Run `pytest -q` (20+ pass) + `python scripts/eval.py` → **PASS**.
Close: *"Single-metric answers are unrepresentable in this architecture — the assertion and the eval gate forbid them."*

## Backup (no backend?)
Screenshots in order: vague-input questions → rich answer → graph → sources. Frontend degrades with explicit "backend unreachable" states.
