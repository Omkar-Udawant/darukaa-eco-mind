"""Stage 2 — Information Completeness Check."""
from __future__ import annotations

from ..schemas import EnvMetrics
from . import CRITICAL_VARS

QUESTIONS = {
    "soil.organic_carbon_pct": "What is the Soil Organic Carbon (%)? (soil test or estimate; <1% is degraded)",
    "climate.rainfall_mm": "What is the annual rainfall (mm) and is irrigation available?",
    "land_use.dominant_type": "What is the dominant land use — cropland, forest, grassland, urban, or wetlands?",
    "climate.temperature_c": "What is the mean growing-season temperature (°C)?",
    "biodiversity.pollinator_presence": "Are pollinators present (bees/butterflies)? absent / low / medium / high?",
    "soil.ph": "What is the soil pH?",
}


def _get(m: EnvMetrics, path: str):
    scope, attr = path.split(".")
    return getattr(getattr(m, scope), attr)


def check_completeness(m: EnvMetrics) -> dict:
    missing: list[str] = []
    questions: list[str] = []
    for path, label in CRITICAL_VARS:
        v = _get(m, path)
        if v is None or v == "":
            missing.append(label)
            questions.append(QUESTIONS[path])
    completeness = round(1 - len(missing) / len(CRITICAL_VARS), 3)
    needs_clarification = len(missing) >= 2
    return {
        "missing": missing,
        "questions": questions,
        "completeness": completeness,
        "needs_clarification": needs_clarification,
    }
