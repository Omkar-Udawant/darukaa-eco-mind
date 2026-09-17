"""Hallucination testing: citations must be allowlisted + substring-grounded in the KB."""
from fastapi.testclient import TestClient

from app.database import SessionLocal, ScientificSource, init_db
from app.main import app

init_db()
client = TestClient(app)
ALLOWLIST = {"FAO", "IPCC", "UNEP", "IUCN", "GBIF", "NASA", "USER"}

VIGNETTES = [
    "SOC 0.6%, rainfall 520mm, 34C, cropland, heavy pesticide, few bees near Nashik",
    "Forest patch near Coorg, deforestation medium, fragmentation high, rainfall 1400mm, 26C.",
    "Urban wetland in Chennai, pollution high, rainfall 900mm, 33C, birds declining.",
    "Biodiversity is declining.",
]


def _catalog() -> list[str]:
    db = SessionLocal()
    try:
        return [r.chunk_text for r in db.query(ScientificSource).all()]
    finally:
        db.close()


def test_no_fabricated_sources():
    catalog = _catalog()
    assert len(catalog) >= 8, "KB must be seeded before hallucination tests"
    for v in VIGNETTES:
        body = client.post("/chat", json={"message": v}).json()
        assert body["supporting_sources"], f"no sources for vignette: {v[:40]}"
        for s in body["supporting_sources"]:
            assert s["source"] in ALLOWLIST, f"fabricated source: {s['source']}"
            if s["publication"].endswith("(fallback)"):
                continue
            assert any(s["excerpt"][:80] in c for c in catalog), (
                f"ungrounded excerpt: {s['excerpt'][:80]}"
            )


def test_no_single_metric_answers():
    for v in VIGNETTES:
        body = client.post("/chat", json={"message": v}).json()
        for rec in body["recommendations"]:
            assert len(rec["dimensions_used"]) >= 3
            assert rec["scientific_reasoning"].strip(), "empty reasoning = hand-waving"
