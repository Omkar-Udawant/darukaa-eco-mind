"""Environmental Knowledge Graph — entities, causal relationships, graph queries.

Entities: soil, carbon, moisture, ph, rainfall, temperature, species, habitat,
pollution, deforestation, agriculture, water (+ intermediate ecological entities).
Relationship semantics: A -> B means 'A causally influences B' with a mechanism
and the evidence family that supports it.
"""
from __future__ import annotations

from collections import deque

ENTITIES: dict[str, dict] = {
    "soil": {"label": "Soil", "dimension": "soil"},
    "carbon": {"label": "Soil Organic Carbon", "dimension": "soil"},
    "moisture": {"label": "Soil Moisture", "dimension": "soil"},
    "ph": {"label": "Soil pH", "dimension": "soil"},
    "microbial_diversity": {"label": "Microbial Diversity", "dimension": "soil"},
    "plant_diversity": {"label": "Plant Diversity", "dimension": "biodiversity"},
    "pollinator_diversity": {"label": "Pollinator Diversity", "dimension": "biodiversity"},
    "species": {"label": "Species Richness", "dimension": "biodiversity"},
    "habitat": {"label": "Habitat Quality", "dimension": "biodiversity"},
    "biodiversity_health": {"label": "Biodiversity Health", "dimension": "biodiversity"},
    "rainfall": {"label": "Rainfall", "dimension": "climate"},
    "temperature": {"label": "Temperature", "dimension": "climate"},
    "water": {"label": "Surface/Ground Water", "dimension": "climate"},
    "agriculture": {"label": "Agriculture / Cropland", "dimension": "land_use"},
    "deforestation": {"label": "Deforestation", "dimension": "human_impact"},
    "fragmentation": {"label": "Habitat Fragmentation", "dimension": "human_impact"},
    "pollution": {"label": "Pollution / Chemical Inputs", "dimension": "human_impact"},
}

# (source, target, mechanism, evidence)
EDGES: list[tuple[str, str, str, str]] = [
    ("carbon", "microbial_diversity", "organic matter feeds soil biota", "FAO"),
    ("microbial_diversity", "plant_diversity", "nutrient cycling + mycorrhizae support flora", "FAO"),
    ("plant_diversity", "pollinator_diversity", "floral resources + nesting feed pollinators", "UNEP"),
    ("pollinator_diversity", "biodiversity_health", "pollination drives seed set + food webs", "UNEP"),
    ("plant_diversity", "species", "flora richness underpins fauna richness", "IUCN"),
    ("species", "biodiversity_health", "richness stabilizes ecosystem function", "IUCN"),
    ("habitat", "species", "quality habitat sustains populations", "IUCN"),
    ("habitat", "biodiversity_health", "refugia + corridors prevent isolation", "IUCN"),
    ("rainfall", "moisture", "precipitation recharges root-zone water", "NASA"),
    ("rainfall", "water", "runoff + infiltration feed water bodies", "NASA"),
    ("water", "habitat", "ponds/wetlands create amphibian + insect habitat", "NASA"),
    ("moisture", "microbial_diversity", "water availability gates microbial activity", "FAO"),
    ("moisture", "plant_diversity", "drought stress cuts germination + seed set", "IPCC"),
    ("temperature", "pollinator_diversity", "heat shifts phenology, mismatches bloom", "IPCC"),
    ("temperature", "plant_diversity", "heat stress aborts flowers, narrows niches", "IPCC"),
    ("ph", "microbial_diversity", "extreme pH suppresses bacterial/fungal guilds", "FAO"),
    ("soil", "carbon", "management builds or depletes carbon stocks", "FAO"),
    ("deforestation", "fragmentation", "clearing isolates remnant patches", "IUCN"),
    ("deforestation", "habitat", "canopy loss removes niches directly", "IUCN"),
    ("fragmentation", "species", "isolation + edge effects erode richness", "IUCN"),
    ("pollution", "pollinator_diversity", "insecticide exposure kills foragers", "GBIF"),
    ("pollution", "microbial_diversity", "agrochemicals suppress soil biota", "FAO"),
    ("pollution", "water", "runoff degrades aquatic habitat", "UNEP"),
    ("agriculture", "carbon", "tillage + residue removal deplete SOC", "FAO"),
    ("agriculture", "habitat", "monoculture simplifies landscape mosaic", "IPCC"),
    ("agriculture", "pollution", "input-intensive farming loads chemicals", "GBIF"),
    ("carbon", "moisture", "humus raises water-holding capacity", "FAO"),
    ("habitat", "pollinator_diversity", "corridors + strips rebuild networks", "UNEP"),
]

_ADJ: dict[str, list[tuple[str, str, str]]] = {}
for _s, _t, _mech, _ev in EDGES:
    _ADJ.setdefault(_s, []).append((_t, _mech, _ev))


def neighbors(entity: str, direction: str = "out") -> list[dict]:
    """Graph query: 1-hop neighborhood of an entity."""
    if direction == "out":
        return [{"entity": t, "mechanism": m, "evidence": e} for t, m, e in _ADJ.get(entity, [])]
    return [
        {"entity": s, "mechanism": m, "evidence": e}
        for s, t, m, e in EDGES
        if t == entity
    ]


def find_paths(src: str, dst: str, max_depth: int = 4) -> list[list[str]]:
    """Graph query: all directed paths src -> dst up to max_depth (BFS)."""
    if src not in ENTITIES or dst not in ENTITIES:
        return []
    paths: list[list[str]] = []
    queue: deque[list[str]] = deque([[src]])
    while queue:
        path = queue.popleft()
        if len(path) > max_depth + 1:
            continue
        last = path[-1]
        if last == dst and len(path) > 1:
            paths.append(path)
            continue
        for nxt, _, _ in _ADJ.get(last, []):
            if nxt not in path:
                queue.append(path + [nxt])
    return paths


def _describe_path(path: list[str]) -> str:
    mechs = []
    for a, b in zip(path, path[1:]):
        for t, mech, _ in _ADJ.get(a, []):
            if t == b:
                mechs.append(mech)
                break
    labels = [ENTITIES[n]["label"] for n in path]
    return " -> ".join(labels) + (f"  [{'; '.join(mechs)}]" if mechs else "")


def reasoning_paths_for_metrics(metrics) -> list[str]:
    """Select KG paths activated by the observed multi-metric state."""
    s, c, b, lu, h = metrics.soil, metrics.climate, metrics.biodiversity, metrics.land_use, metrics.human_impact
    queries: list[tuple[str, str]] = []
    if (s.organic_carbon_pct or 99) < 1.5:
        queries.append(("carbon", "biodiversity_health"))
    if (c.rainfall_mm or 9999) < 800:
        queries.append(("rainfall", "plant_diversity"))
    if (c.temperature_c or 0) > 32:
        queries.append(("temperature", "biodiversity_health"))
    if b.pollinator_presence in ("absent", "low"):
        queries.append(("plant_diversity", "biodiversity_health"))
    if h.deforestation in ("medium", "high"):
        queries.append(("deforestation", "species"))
    if h.pollution in ("medium", "high") or h.chemical_inputs in ("medium", "high"):
        queries.append(("pollution", "pollinator_diversity"))
    if lu.dominant_type == "cropland" or not queries:
        queries.append(("agriculture", "biodiversity_health"))
    out: list[str] = []
    for src, dst in queries:
        for p in find_paths(src, dst)[:2]:
            out.append("KG path: " + _describe_path(p))
    return out


def full_graph() -> dict:
    return {
        "entities": [{"id": k, **v} for k, v in ENTITIES.items()],
        "relationships": [
            {"from": s, "to": t, "mechanism": m, "evidence": e} for s, t, m, e in EDGES
        ],
    }
