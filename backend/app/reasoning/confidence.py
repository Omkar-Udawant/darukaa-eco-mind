"""Stage 7 — Confidence Assessment."""
from __future__ import annotations

from .extractor import dimensions_present
from ..schemas import EnvMetrics

EVIDENCE_WEIGHTS = {"strong": 1.0, "medium": 0.75, "emerging": 0.5}


def compute_confidence(m: EnvMetrics, completeness: float, sources: list[dict]) -> float:
    dims = len(dimensions_present(m))
    dim_score = min(1.0, dims / 5.0)
    if sources:
        ev = sum(EVIDENCE_WEIGHTS.get(str(s.get("evidence_strength", "medium")).lower(), 0.75) for s in sources)
        ev_score = min(1.0, ev / max(1, len(sources)) * min(1.0, len(sources) / 3.0 + 0.4))
    else:
        ev_score = 0.4
    model_certainty = 0.8 if dims >= 3 else 0.55
    conf = 100 * (0.45 * completeness + 0.30 * ev_score + 0.15 * dim_score + 0.10 * model_certainty)
    return round(max(35.0, min(96.0, conf)), 1)
