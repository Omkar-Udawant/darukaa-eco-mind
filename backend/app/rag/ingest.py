"""Chunking + ingest pipeline. Stores chunk_text/source/publication/year/evidence_strength/topic."""
from __future__ import annotations

import json
import re
import uuid


def chunk_text(text: str, size: int = 800, overlap: int = 120) -> list[str]:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return []
    chunks, i = [], 0
    while i < len(text):
        chunks.append(text[i : i + size])
        i += max(1, size - overlap)
    return chunks


def build_records(source: str, publication: str, year: int, topic: str,
                  evidence_strength: str, text: str) -> list[dict]:
    return [
        {
            "chunk_text": c,
            "source": source,
            "publication": publication,
            "year": int(year),
            "evidence_strength": evidence_strength,
            "topic": topic,
            "embedding_id": uuid.uuid4().hex,
        }
        for c in chunk_text(text)
    ]


def ingest_seed_file(path: str, store=None) -> int:
    from .vectorstore import get_vector_store

    store = store or get_vector_store()
    with open(path, encoding="utf-8") as f:
        items = json.load(f)
    docs: list[dict] = []
    for it in items:
        docs.extend(
            build_records(
                it["source"], it["publication"], it.get("year", 2020),
                it.get("topic", "general"), it.get("evidence_strength", "medium"),
                it.get("text", ""),
            )
        )
    # also persist to SQL for /sources endpoint
    try:
        from ..database import SessionLocal, ScientificSource

        db = SessionLocal()
        try:
            for d in docs:
                db.add(ScientificSource(
                    source=d["source"], publication=d["publication"], year=d["year"],
                    topic=d["topic"], evidence_strength=d["evidence_strength"],
                    chunk_text=d["chunk_text"][:4000], embedding_id=d["embedding_id"],
                ))
            db.commit()
        finally:
            db.close()
    except Exception:
        pass
    return store.upsert(docs)
