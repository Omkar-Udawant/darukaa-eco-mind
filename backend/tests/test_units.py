"""Unit tests for extractor / completeness / impact / confidence."""
from app.reasoning.completeness import check_completeness
from app.reasoning.confidence import compute_confidence
from app.reasoning.extractor import dimensions_present, extract_from_text
from app.reasoning.impact import estimate_impact
from app.reasoning.interventions import select_interventions
from app.schemas import EnvMetrics


def test_extractor_finds_metrics():
    m = extract_from_text("SOC 0.6%, rainfall 520mm, 34C, cropland, few bees, heavy pesticide near Nashik")
    assert m.soil.organic_carbon_pct == 0.6
    assert m.climate.rainfall_mm == 520
    assert m.land_use.dominant_type == "cropland"
    assert "soil" in dimensions_present(m)


def test_completeness_flags_missing():
    c = check_completeness(EnvMetrics())
    assert c["needs_clarification"] is True
    assert len(c["questions"]) >= 4


def test_interventions_use_3_dimensions():
    for it in select_interventions(EnvMetrics(), top_k=4):
        assert len(it["dimensions"]) >= 3


def test_impact_bounded():
    imp = estimate_impact(EnvMetrics(), "Legume-based cover cropping")
    for k in ["biodiversity_gain_pct", "soil_carbon_gain_pct"]:
        assert 0 < imp[k] <= 70


def test_confidence_range():
    m = extract_from_text("SOC 0.6%, rainfall 520mm, 34C, cropland, few bees")
    c = compute_confidence(m, 0.5, [{"evidence_strength": "strong"}])
    assert 35 <= c <= 96
