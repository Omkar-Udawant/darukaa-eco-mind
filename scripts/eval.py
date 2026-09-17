"""Offline eval: dimension compliance, grounding, completeness gating, boundedness. No network."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from fastapi.testclient import TestClient  # noqa: E402
from app.database import init_db  # noqa: E402
from app.main import app  # noqa: E402

init_db()
c = TestClient(app)
fails = []

rich = c.post("/chat", json={"message": "SOC 0.6%, rainfall 520mm, 34C, cropland, heavy pesticide, few bees near Nashik"}).json()
if not all(len(r["dimensions_used"]) >= 3 for r in rich["recommendations"]):
    fails.append("dimension-compliance")
vague = c.post("/chat", json={"message": "Biodiversity is declining."}).json()
if not (len(vague["clarifying_questions"]) >= 2 and vague["completeness"] < 0.7):
    fails.append("completeness-gating")
imp = c.post("/impact", json={"metrics": {}, "intervention": "Agroforestry boundary planting"}).json()
if not all(0 < imp[k] <= 70 for k in ["biodiversity_gain_pct", "soil_carbon_gain_pct"]):
    fails.append("impact-bounds")
if not (rich["confidence"] >= vague["confidence"]):
    fails.append("confidence-calibration")
if not rich["supporting_sources"]:
    fails.append("has-sources")

print("PASS" if not fails else f"FAIL: {fails}")
sys.exit(1 if fails else 0)
