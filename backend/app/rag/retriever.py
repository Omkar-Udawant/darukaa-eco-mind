"""Stage 3 — Knowledge Retrieval (topic-routed, evidence-ranked)."""
from __future__ import annotations

import time

TOPIC_HINTS = {
    "soil": ["soil", "carbon", "ph", "nutrient", "microb"],
    "pollinator": ["pollinat", "bee", "butterfly"],
    "agroforestry": ["agroforest", "tree", "boundary"],
    "wetland": ["wetland", "pond", "water"],
    "climate": ["climate", "rainfall", "temperature", "ipcc"],
    "restoration": ["restor", "habitat", "diversity"],
}


def infer_topics(query: str, metrics_text: str = "") -> list[str]:
    t = f"{query} {metrics_text}".lower()
    return [topic for topic, kws in TOPIC_HINTS.items() if any(k in t for k in kws)] or ["soil", "restoration"]


def retrieve(query: str, metrics_text: str = "", top_k: int = 4) -> tuple[list[dict], dict]:
    from .vectorstore import get_vector_store

    t0 = time.time()
    store = get_vector_store()
    topics = infer_topics(query, metrics_text)
    seen: dict[str, dict] = {}
    per = max(2, top_k // max(1, len(topics)))
    for topic in topics:
        try:
            for d in store.query(query, top_k=per, topic=topic):
                seen[d.get("chunk_text", "")[:200]] = d
        except Exception:
            continue
    if not seen:
        try:
            for d in store.query(query, top_k=top_k):
                seen[d.get("chunk_text", "")[:200]] = d
        except Exception:
            pass
    rank = {"strong": 0, "medium": 1, "emerging": 2}
    docs = sorted(seen.values(), key=lambda d: rank.get(str(d.get("evidence_strength", "medium")).lower(), 1))[:top_k]
    meta = {"topics": topics, "latency_ms": int((time.time() - t0) * 1000), "count": len(docs)}
    return docs, meta
