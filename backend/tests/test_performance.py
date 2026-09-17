"""Performance: local latency bounds for the demo-critical paths."""
import time

from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app

init_db()
client = TestClient(app)


def _p50(samples: list[float]) -> float:
    return sorted(samples)[len(samples) // 2]


def test_chat_latency_bound():
    ts = []
    for _ in range(3):
        t0 = time.time()
        r = client.post("/chat", json={"message": "SOC 0.8%, rainfall 700mm, 30C, grassland."})
        ts.append(time.time() - t0)
        assert r.status_code == 200
    assert _p50(ts) < 5.0, f"p50 chat latency too high: {_p50(ts):.2f}s"


def test_aux_endpoints_fast():
    for method, path, payload in [
        ("GET", "/health", None),
        ("GET", "/sources", None),
        ("GET", "/graph", None),
        ("POST", "/impact", {"metrics": {}, "intervention": "Agroforestry boundary planting"}),
    ]:
        t0 = time.time()
        r = client.request(method, path, json=payload) if payload else client.request(method, path)
        dt = time.time() - t0
        assert r.status_code == 200 and dt < 3.0, f"{path} slow: {dt:.2f}s"
