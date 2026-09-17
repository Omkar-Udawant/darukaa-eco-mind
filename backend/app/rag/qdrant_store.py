"""Optional Qdrant backend (used when VECTOR_BACKEND=qdrant + QDRANT_URL set)."""
from __future__ import annotations


class QdrantStore:
    def __init__(self, embeddings):
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams
        from ..config import settings

        self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY or None)
        self.col = "darukaa_knowledge"
        self.emb = embeddings
        try:
            self.client.get_collection(self.col)
        except Exception:
            dim = getattr(embeddings, "dim", 256)
            if hasattr(embeddings, "embed_query"):
                try:
                    dim = len(embeddings.embed_query("probe"))
                except Exception:
                    pass
            self.client.create_collection(
                collection_name=self.col, vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
            )

    def upsert(self, docs: list[dict]) -> int:
        from qdrant_client.models import PointStruct

        vecs = self.emb.embed_documents([d["chunk_text"] for d in docs])
        pts = [
            PointStruct(id=__import__("uuid").uuid4().hex, vector=v, payload=d)
            for d, v in zip(docs, vecs)
        ]
        self.client.upsert(collection_name=self.col, points=pts)
        return len(docs)

    def query(self, text: str, top_k: int = 4, topic: str | None = None) -> list[dict]:
        q = self.emb.embed_query(text)
        hits = self.client.search(collection_name=self.col, query_vector=q, limit=top_k)
        return [h.payload for h in hits]

    def count(self) -> int:
        return self.client.count(collection_name=self.col).count
