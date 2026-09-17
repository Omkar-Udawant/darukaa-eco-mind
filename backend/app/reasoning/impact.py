"""Stage 6 — Impact Estimation (transparent, bounded heuristics)."""
from __future__ import annotations

from ..schemas import EnvMetrics


def _clamp(x: float, lo: float = 2.0, hi: float = 60.0) -> float:
    return max(lo, min(hi, round(x, 1)))


def estimate_impact(m: EnvMetrics, intervention_title: str) -> dict:
    t = (intervention_title or "").lower()
    # baselines modulated by degradation severity
    degraded = 0
    if (m.soil.organic_carbon_pct or 2.0) < 1.0:
        degraded += 1
    if (m.climate.rainfall_mm or 1000) < 600:
        degraded += 1
    if m.biodiversity.pollinator_presence in ("absent", "low"):
        degraded += 1
    if m.human_impact.chemical_inputs in ("high", "medium"):
        degraded += 1
    base = 12.0 + 3.0 * degraded  # more degraded => larger % gains possible

    if "cover crop" in t or "legume" in t:
        return {
            "biodiversity_gain_pct": _clamp(base * 0.8),
            "soil_carbon_gain_pct": _clamp(base * 1.6, hi=25.0) if base * 1.6 <= 25 else 25.0,
            "water_retention_gain_pct": _clamp(base * 1.1),
            "habitat_quality_gain_pct": _clamp(base * 0.9),
            "horizon": "Medium Term",
        }
    if "agroforest" in t:
        return {
            "biodiversity_gain_pct": _clamp(base * 1.5),
            "soil_carbon_gain_pct": _clamp(base * 1.2),
            "water_retention_gain_pct": _clamp(base * 1.0),
            "habitat_quality_gain_pct": _clamp(base * 1.6),
            "horizon": "Long Term",
        }
    if "pollinator" in t:
        return {
            "biodiversity_gain_pct": _clamp(base * 1.8, hi=70.0),
            "soil_carbon_gain_pct": _clamp(base * 0.4),
            "water_retention_gain_pct": _clamp(base * 0.5),
            "habitat_quality_gain_pct": _clamp(base * 1.4),
            "horizon": "Short Term",
        }
    if "wetland" in t or "pond" in t:
        return {
            "biodiversity_gain_pct": _clamp(base * 1.3),
            "soil_carbon_gain_pct": _clamp(base * 0.7),
            "water_retention_gain_pct": _clamp(base * 2.0, hi=45.0),
            "habitat_quality_gain_pct": _clamp(base * 1.5),
            "horizon": "Medium Term",
        }
    if "mixed crop" in t or "ipm" in t:
        return {
            "biodiversity_gain_pct": _clamp(base * 1.1),
            "soil_carbon_gain_pct": _clamp(base * 1.0),
            "water_retention_gain_pct": _clamp(base * 0.8),
            "habitat_quality_gain_pct": _clamp(base * 1.0),
            "horizon": "Short Term",
        }
    return {
        "biodiversity_gain_pct": _clamp(base),
        "soil_carbon_gain_pct": _clamp(base * 0.9),
        "water_retention_gain_pct": _clamp(base * 0.9),
        "habitat_quality_gain_pct": _clamp(base * 1.1),
        "horizon": "Medium Term",
    }
