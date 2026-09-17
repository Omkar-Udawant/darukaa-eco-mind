# Evaluation Strategy (`scripts/eval.py`)

| Check | Method | Pass bar |
|---|---|---|
| Dimension compliance | every rec `len(dimensions_used) ≥ 3` over 12-scenario suite | 100% |
| Citation grounding | every source excerpt substring-matches KB chunk | 100% |
| Completeness gating | vague input → ≥2 clarifying questions, completeness < 0.7 | pass |
| Impact boundedness | all gains in (0, 70] | pass |
| Confidence calibration | complete vignette ≥ vague vignette | pass |
| Latency | p50 `/chat` local | < 2 s |

Run: `cd backend && python ../scripts/eval.py` (uses TestClient, no network).
Golden scenarios in `scripts/demo_seed.py`.
