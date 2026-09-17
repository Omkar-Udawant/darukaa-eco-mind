"""Stage 1 — Input Analysis: extract metrics, geo + land-use indicators, missing vars."""
from __future__ import annotations

import re
from ..schemas import EnvMetrics

PH_RE = re.compile(r"pH\s*(?:of\s*)?(?P<v>\d(?:\.\d+)?)", re.I)
SOC_RE = re.compile(r"(?:organic\s*carbon|soc)\D{0,12}(?P<v>\d(?:\.\d+)?)\s*%?", re.I)
MOIST_RE = re.compile(r"moisture\D{0,12}(?P<v>\d+(?:\.\d+)?)\s*%?", re.I)
TEMP_RE = re.compile(r"(?P<v>-?\d+(?:\.\d+)?)\s*°?\s*c\b", re.I)
RAIN_RE = re.compile(r"(?:rainfall|rain|precip)\D{0,15}(?P<v>\d+(?:\.\d+)?)\s*mm", re.I)
RICH_RE = re.compile(r"(?:richness|species)\D{0,15}(?P<v>\d+)", re.I)

LAND_KEYWORDS = {
    "cropland": ["crop", "farm", "agricultur", "paddy", "wheat", "maize"],
    "forest": ["forest", "woodland", "trees", "deforest"],
    "grassland": ["grass", "pasture", "meadow", "savanna"],
    "urban": ["urban", "city", "built", "concrete"],
    "wetlands": ["wetland", "marsh", "swamp", "mangrove", "lake", "pond"],
}
POLL_KEYWORDS = {
    "high": ["heavy pesticide", "high chemical", "severe pollution", "industrial runoff"],
    "medium": ["moderate pesticide", "some pollution", "fertilizer"],
    "low": ["organic", "no pesticide", "pristine", "no chemical"],
}
REGION_RE = re.compile(
    r"\b(?:in|near|around|region of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})"
)


def _kw_hit(text: str, words: list[str]) -> bool:
    t = text.lower()
    return any(w in t for w in words)


def extract_from_text(message: str, base: EnvMetrics | None = None) -> EnvMetrics:
    m = base.model_copy(deep=True) if base else EnvMetrics()
    t = message or ""

    def num(rx):
        mm = rx.search(t)
        return float(mm.group("v")) if mm else None

    v = num(PH_RE)
    if v is not None and m.soil.ph is None:
        m.soil.ph = v
    v = num(SOC_RE)
    if v is not None and m.soil.organic_carbon_pct is None:
        m.soil.organic_carbon_pct = v
    v = num(MOIST_RE)
    if v is not None and m.soil.moisture_pct is None:
        m.soil.moisture_pct = v
    v = num(TEMP_RE)
    if v is not None and m.climate.temperature_c is None:
        m.climate.temperature_c = v
    v = num(RAIN_RE)
    if v is not None and m.climate.rainfall_mm is None:
        m.climate.rainfall_mm = v
    mm = RICH_RE.search(t)
    if mm and m.biodiversity.species_richness is None:
        m.biodiversity.species_richness = int(float(mm.group("v")))

    tl = t.lower()
    for lu, kws in LAND_KEYWORDS.items():
        if _kw_hit(t, kws) and not m.land_use.dominant_type:
            m.land_use.dominant_type = lu
    if "pollinator" in tl:
        if any(w in tl for w in ["no pollinator", "absent", "declin", "loss", "few bees"]):
            m.biodiversity.pollinator_presence = m.biodiversity.pollinator_presence or "low"
        elif "abundant" in tl or "high" in tl:
            m.biodiversity.pollinator_presence = m.biodiversity.pollinator_presence or "high"
    for level, kws in POLL_KEYWORDS.items():
        if _kw_hit(t, kws):
            if not m.human_impact.pollution:
                m.human_impact.pollution = level
            if ("pesticide" in tl or "chemical" in tl or "fertilizer" in tl) and not m.human_impact.chemical_inputs:
                m.human_impact.chemical_inputs = level
    if "deforest" in tl and not m.human_impact.deforestation:
        m.human_impact.deforestation = "high" if "severe" in tl or "heavy" in tl else "medium"
    if "fragment" in tl and not m.human_impact.fragmentation:
        m.human_impact.fragmentation = "medium"
    if "drought" in tl or "erratic" in tl:
        m.climate.seasonal_variability = m.climate.seasonal_variability or "high"
    if "monsoon" in tl:
        m.climate.seasonal_variability = m.climate.seasonal_variability or "seasonal-monsoon"
    rm = REGION_RE.search(t)
    if rm and not m.region:
        m.region = rm.group(1)
    if not m.notes:
        m.notes = message[:500]
    return m


def dimensions_present(m: EnvMetrics) -> list[str]:
    dims: list[str] = []
    s = m.soil
    if any([s.ph is not None, s.organic_carbon_pct is not None, s.moisture_pct is not None, s.nutrient_quality]):
        dims.append("soil")
    c = m.climate
    if any([c.temperature_c is not None, c.rainfall_mm is not None, c.seasonal_variability]):
        dims.append("climate")
    b = m.biodiversity
    if any([b.species_richness is not None, b.habitat_diversity, b.pollinator_presence]):
        dims.append("biodiversity")
    l = m.land_use
    if any([l.cropland_pct is not None, l.forest_pct is not None, l.grassland_pct is not None,
            l.urban_pct is not None, l.wetlands_pct is not None, l.dominant_type]):
        dims.append("land_use")
    h = m.human_impact
    if any([h.pollution, h.deforestation, h.fragmentation, h.chemical_inputs]):
        dims.append("human_impact")
    return dims
