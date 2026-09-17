"""Stage 5 — Intervention Generation. Every intervention uses >=3 dimensions."""
from __future__ import annotations

from ..schemas import EnvMetrics

CATALOG = [
    {
        "title": "Legume-based cover cropping",
        "detail": "Sow nitrogen-fixing legumes (e.g., clover, vetch, cowpea) in off-season; terminate as mulch, zero-till where possible.",
        "reasoning": "Legumes fix atmospheric nitrogen, raise soil organic carbon, feed microbial diversity and provide floral resources for pollinators — linking soil × biodiversity × human-input reduction.",
        "impacted": ["Soil Organic Carbon", "Microbial Diversity", "Pollinator Presence", "Chemical Input Load"],
        "improvement": "15–25% increase in soil carbon over 2–3 years; ~30% less synthetic N needed.",
        "horizon": "Medium Term",
        "dimensions": ["soil", "biodiversity", "human_impact", "climate"],
        "when": lambda m: True,  # broadly applicable
    },
    {
        "title": "Agroforestry boundary planting",
        "detail": "Plant native multi-purpose trees/shrubs on field bunds at 20–30% boundary cover; protect from grazing for 2 years.",
        "reasoning": "Trees buffer temperature extremes, add litter carbon, create nesting habitat and corridors — linking land-use × climate × biodiversity × soil.",
        "impacted": ["Habitat Diversity", "Species Richness", "Soil Organic Carbon", "Microbial Diversity"],
        "improvement": "20–35% habitat-quality gain in 3–5 years; 0.3–0.6 tC/ha/yr sequestration.",
        "horizon": "Long Term",
        "dimensions": ["land_use", "climate", "biodiversity", "soil"],
        "when": lambda m: (m.land_use.dominant_type in ("", "cropland", "grassland") or (m.land_use.forest_pct or 100) < 20),
    },
    {
        "title": "Native pollinator corridors",
        "detail": "Restore 3–5 m native forb/grass strips every ~200 m; no-spray buffers; staggered bloom calendar.",
        "reasoning": "Continuous bloom + nesting substrate rebuilds pollinator networks, which restores seed set of native plants — biodiversity × land-use × human-impact × soil linkage.",
        "impacted": ["Pollinator Presence", "Species Richness", "Habitat Diversity"],
        "improvement": "40–70% pollinator visitation increase in 1–2 seasons.",
        "horizon": "Short Term",
        "dimensions": ["biodiversity", "land_use", "human_impact", "soil"],
        "when": lambda m: m.biodiversity.pollinator_presence in ("", "absent", "low"),
    },
    {
        "title": "Wetland / farm-pond regeneration",
        "detail": "Desilt and re-profile seasonal water body, plant native littoral vegetation, fence 10 m buffer.",
        "reasoning": "Standing water raises landscape moisture, recharges groundwater and supports amphibian/insect food webs — water × habitat × climate-resilience linkage.",
        "impacted": ["Water Retention", "Habitat Diversity", "Species Richness"],
        "improvement": "25–40% dry-season water retention gain; amphibian richness +30–50%.",
        "horizon": "Medium Term",
        "dimensions": ["land_use", "climate", "biodiversity", "soil"],
        "when": lambda m: (m.climate.rainfall_mm or 9999) < 900 or m.land_use.dominant_type in ("cropland", "grassland", ""),
    },
    {
        "title": "Mixed cropping + reduced chemicals (IPM)",
        "detail": "Intercrop cereals with legumes/oilseeds; replace calendar sprays with IPM thresholds; compost 2–3 t/ha.",
        "reasoning": "Crop diversity breaks pest cycles and feeds soil biota while IPM cuts pollinator exposure — soil × biodiversity × human-impact linkage.",
        "impacted": ["Soil Organic Carbon", "Pollinator Presence", "Chemical Input Load", "Species Richness"],
        "improvement": "20–40% pesticide reduction year one; SOC +10–20% in 2 years.",
        "horizon": "Short Term",
        "dimensions": ["soil", "biodiversity", "human_impact", "land_use"],
        "when": lambda m: m.human_impact.chemical_inputs in ("medium", "high", "") and (m.land_use.dominant_type in ("cropland", "")),
    },
    {
        "title": "Community forest-patch restoration",
        "detail": "Protect and enrich 0.5–2 ha native patch per village; assisted natural regeneration + invasive removal.",
        "reasoning": "Core habitat patches reduce fragmentation, provide refugia and seed sources — land-use × biodiversity × climate linkage with soil co-benefits.",
        "impacted": ["Habitat Diversity", "Species Richness", "Soil Organic Carbon"],
        "improvement": "Native richness +25–45% in 3–5 years within 500 m of patch.",
        "horizon": "Long Term",
        "dimensions": ["land_use", "biodiversity", "climate", "soil"],
        "when": lambda m: (m.human_impact.deforestation in ("medium", "high") or m.human_impact.fragmentation in ("medium", "high", "")),
    },
]


def select_interventions(m: EnvMetrics, top_k: int = 3) -> list[dict]:
    scored: list[tuple[int, dict]] = []
    for item in CATALOG:
        try:
            applicable = bool(item["when"](m))
        except Exception:
            applicable = True
        # score: applicable first, then dimension breadth
        score = (10 if applicable else 0) + len(item["dimensions"])
        if item["title"] == "Native pollinator corridors" and m.biodiversity.pollinator_presence in ("absent", "low"):
            score += 5
        if item["title"] == "Legume-based cover cropping" and (m.soil.organic_carbon_pct or 99) < 1.5:
            score += 5
        scored.append((score, item))
    scored.sort(key=lambda t: t[0], reverse=True)
    out = []
    for _, item in scored[: max(1, top_k)]:
        assert len(item["dimensions"]) >= 3, "Every recommendation must use >=3 dimensions"
        out.append(item)
    return out
