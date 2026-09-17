"""Integration: full journey chat -> metrics -> conversation -> history -> ingest -> sources."""
from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app

init_db()
client = TestClient(app)
RICH = "SOC 0.6%, rainfall 520mm, 34C, cropland, heavy pesticide, few bees near Nashik"


def test_full_journey():
    r = client.post("/chat", json={"message": RICH})
    assert r.status_code == 200
    cid = r.json()["conversation_id"]

    m = client.get(f"/metrics/{cid}").json()
    assert m["soil"] and m["soil"]["organic_carbon_pct"] == 0.6

    conv = client.get(f"/conversation/{cid}").json()
    assert len(conv["recommendations"]) >= 1 and len(conv["memory"]) >= 2

    hist = client.get("/history").json()
    assert any(h["id"] == cid for h in hist)

    g = client.get("/graph").json()
    assert len(g["entities"]) >= 12 and len(g["relationships"]) >= 10

    paths = client.get("/graph", params={"src": "carbon", "dst": "biodiversity_health"}).json()
    assert len(paths["paths"]) >= 1

    reason = client.post("/reason", json={"metrics": {}}).json()
    assert "kg_paths" in reason and len(reason["kg_paths"]) >= 1


def test_ingest_pipeline():
    r = client.post("/ingest", json={
        "text": "Miyawaki micro-forests restore native insect networks within two seasons in test plots.",
        "source": "USER", "publication": "Field trial note", "year": 2026,
        "topic": "restoration", "evidence_strength": "emerging",
    })
    assert r.status_code == 200 and r.json()["chunks_indexed"] >= 1
    srcs = client.get("/sources", params={"topic": "restoration"}).json()
    assert any("Miyawaki" in s["excerpt"] for s in srcs)
