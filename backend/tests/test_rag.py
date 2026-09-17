"""RAG evaluation: topic routing, evidence ranking, grounding recall."""
from app.database import SessionLocal, ScientificSource
from app.rag.retriever import infer_topics, retrieve


def test_topic_routing():
    assert "pollinator" in infer_topics("bees are declining on my farm")
    assert "soil" in infer_topics("soil carbon is low", "soc 0.5%")
    assert "wetland" in infer_topics("farm pond dried up")


def test_retrieval_returns_grounded_docs():
    docs, meta = retrieve("legume cover crops soil carbon nitrogen", "", top_k=3)
    assert len(docs) >= 1
    assert all(d.get("chunk_text") and d.get("source") for d in docs)
    assert "latency_ms" in meta and meta["latency_ms"] >= 0


def test_evidence_ranking_strong_first():
    docs, _ = retrieve("soil carbon microbial diversity", "", top_k=4)
    rank = {"strong": 0, "medium": 1, "emerging": 2}
    keys = [rank.get(str(d.get("evidence_strength", "medium")).lower(), 1) for d in docs]
    assert keys == sorted(keys), "retrieval must rank strong evidence first"


def test_excerpts_match_sql_catalog():
    docs, _ = retrieve("pollinator flower strips", "", top_k=2)
    db = SessionLocal()
    try:
        catalog = [r.chunk_text for r in db.query(ScientificSource).all()]
    finally:
        db.close()
    for d in docs:
        if d.get("publication", "").endswith("(fallback)"):
            continue
        assert any(d["chunk_text"][:100] in c for c in catalog), "vector hit must exist in SQL catalog"
