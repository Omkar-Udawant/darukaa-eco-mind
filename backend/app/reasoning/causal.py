"""Stage 4 — Ecological Reasoning: causal chains + reasoning graph."""
from __future__ import annotations

from ..config import settings
from ..schemas import EnvMetrics


def build_causal_chains(m: EnvMetrics) -> list[str]:
    chains: list[str] = []
    s, c, b, lu, h = m.soil, m.climate, m.biodiversity, m.land_use, m.human_impact
    if s.organic_carbon_pct is not None and s.organic_carbon_pct < settings.LOW_SOC_THRESHOLD:
        chains.append(
            "Low Soil Carbon (<1%) → reduced microbial activity → lower plant diversity → "
            "reduced pollinator population → biodiversity loss"
        )
    if c.rainfall_mm is not None and c.rainfall_mm < settings.LOW_RAINFALL_THRESHOLD_MM:
        chains.append(
            "Low rainfall (<600mm) + high evaporative demand → soil moisture stress → "
            "poor seed set → fragmented habitat → pollinator decline"
        )
    if c.temperature_c is not None and c.temperature_c > settings.HIGH_TEMP_THRESHOLD_C:
        chains.append(
            "Heat stress (>32°C) → phenology mismatch (flowers vs pollinators) → "
            "lower fruit set → food-web simplification"
        )
    if (lu.dominant_type == "cropland" and (h.chemical_inputs in ("medium", "high")
                                            or h.pollution in ("medium", "high"))):
        chains.append(
            "Intensive cropland + chemical inputs → soil biota suppression → "
            "loss of floral resources → pollinator exposure → biodiversity loss"
        )
    if h.deforestation in ("medium", "high") or (lu.forest_pct is not None and lu.forest_pct < 10):
        chains.append(
            "Deforestation / low forest cover → habitat fragmentation → edge effects → "
            "species isolation → richness decline"
        )
    if lu.dominant_type == "urban" or (lu.urban_pct is not None and lu.urban_pct > 30):
        chains.append(
            "Urban expansion → impervious surfaces → runoff + heat island → "
            "wetland desiccation → habitat-quality collapse"
        )
    if (b.pollinator_presence in ("absent", "low")) and not chains:
        chains.append(
            "Pollinator scarcity → pollination deficit → reduced native seed regeneration → "
            "long-term richness erosion"
        )
    if not chains:
        chains.append(
            "Interacting stressors (soil x climate x land-use) -> cumulative pressure on "
            "habitat quality → gradual biodiversity erosion without intervention"
        )
    return chains


def build_reasoning_graph(m: EnvMetrics, chains: list[str]) -> dict:
    soc = f"{m.soil.organic_carbon_pct}%" if m.soil.organic_carbon_pct is not None else "?%"
    temp = f"{m.climate.temperature_c}C" if m.climate.temperature_c is not None else "?C"
    rain = f"{m.climate.rainfall_mm}mm" if m.climate.rainfall_mm is not None else "?mm"
    nodes = [
        {"id": "soc", "label": f"Soil Carbon: {soc}"},
        {"id": "climate", "label": f"Climate: {temp} / {rain}"},
        {"id": "landuse", "label": f"Land use: {m.land_use.dominant_type or '?'}"},
        {"id": "human", "label": f"Human impact: {m.human_impact.pollution or '?'} pollution"},
        {"id": "microbial", "label": "Microbial activity"},
        {"id": "plants", "label": "Plant diversity"},
        {"id": "pollinators", "label": f"Pollinators: {m.biodiversity.pollinator_presence or '?'}"},
        {"id": "biodiversity", "label": "Biodiversity outcome"},
    ]
    edges = [
        {"from": "soc", "to": "microbial", "label": "drives"},
        {"from": "climate", "to": "microbial", "label": "modulates"},
        {"from": "microbial", "to": "plants", "label": "supports"},
        {"from": "landuse", "to": "plants", "label": "constrains"},
        {"from": "human", "to": "plants", "label": "pressures"},
        {"from": "plants", "to": "pollinators", "label": "feeds"},
        {"from": "climate", "to": "pollinators", "label": "phenology"},
        {"from": "pollinators", "to": "biodiversity", "label": "determines"},
    ]
    return {"nodes": nodes, "edges": edges, "chains": chains}
