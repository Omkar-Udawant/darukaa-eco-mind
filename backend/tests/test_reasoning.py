"""Smoke + contract tests for the reasoning engine (no network, no keys needed)."""
from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app

init_db()
client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_chat_full_response_shape():
    r = client.post("/chat", json={
        "message": "Biodiversity is declining on my cropland near Nashik. SOC 0.6%, rainfall 520mm, 34C, heavy pesticide, few bees.",
        "metrics": {"soil": {"ph": 6.8}, "region": "Nashik"},
    })
    assert r.status_code == 200, r.text
    body = r.json()
    for key in ["situation_assessment", "key_risks", "recommendations", "scientific_reasoning",
                "impacted_metrics", "estimated_improvement", "time_horizon", "confidence",
                "supporting_sources", "additional_data_needed", "reasoning_graph", "completeness"]:
        assert key in body, f"missing {key}"
    assert len(body["recommendations"]) >= 1
    for rec in body["recommendations"]:
        assert len(rec["dimensions_used"]) >= 3, "every recommendation must use >=3 dimensions"


def test_clarifying_questions_when_vague():
    r = client.post("/chat", json={"message": "Biodiversity is declining."})
    assert r.status_code == 200
    body = r.json()
    assert len(body["clarifying_questions"]) >= 2
    assert body["completeness"] < 0.7


def test_impact_endpoint():
    r = client.post("/impact", json={
        "metrics": {"soil": {"organic_carbon_pct": 0.6}},
        "intervention": "Legume-based cover cropping",
    })
    assert r.status_code == 200
    assert "biodiversity_gain_pct" in r.json()


def test_sources_endpoint():
    assert client.get("/sources").status_code == 200
