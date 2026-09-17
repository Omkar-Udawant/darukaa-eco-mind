"""Vector store with graceful fallback: Qdrant > Chroma > in-memory."""
from __future__ import annotations

import math
import uuid

_docs: list[dict] = []  # in-memory fallback


def _cos(a: list[float], b: list[float]) -> float:
    n = (math.sqrt(sum(x * x for x in a)) or 1.0) * (math.sqrt(sum(x * x for x in b)) or 1.0)
    return sum(x * y for x, y in zip(a, b)) / n


class LocalVectorStore:
    def __init__(self, embeddings):
        self.emb = embeddings

    def upsert(self, docs: list[dict]) -> int:
        global _docs
        vecs = self.emb.embed_documents([d["chunk_text"] for d in docs])
        for d, v in zip(docs, vecs):
            d = {**d, "embedding": v, "embedding_id": d.get("embedding_id") or str(uuid.uuid4())}
            _docs = [x for x in _docs if x.get("embedding_id") != d["embedding_id"]]
            _docs.append(d)
        return len(docs)

    def query(self, text: str, top_k: int = 4, topic: str | None = None) -> list[dict]:
        q = self.emb.embed_query(text)
        pool = [d for d in _docs if (not topic or d.get("topic") == topic or topic.lower() in str(d.get("topic", "")).lower())] or _docs
        ranked = sorted(pool, key=lambda d: _cos(q, d["embedding"]), reverse=True)
        return [{k: v for k, v in d.items() if k != "embedding"} for d in ranked[:top_k]]

    def count(self) -> int:
        return len(_docs)


def get_vector_store():
    from ..config import settings
    from .embeddings import get_embeddings

    emb = get_embeddings()
    # Try Qdrant if configured
    if settings.VECTOR_BACKEND == "qdrant" and settings.QDRANT_URL:
        try:
            from .qdrant_store import QdrantStore

            return QdrantStore(emb)
        except Exception:
            pass
    # Try Chroma if requested and available
    if settings.VECTOR_BACKEND == "chroma":
        try:
            from .chroma_store import ChromaStore

            return ChromaStore(emb, persist_dir=settings.CHROMA_DIR)
        except Exception:
            pass
    return LocalVectorStore(emb)
