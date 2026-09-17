"""Optional Chroma backend (used when VECTOR_BACKEND=chroma)."""
from __future__ import annotations


class ChromaStore:
    def __init__(self, embeddings, persist_dir: str = "./chroma_db"):
        import chromadb

        self.client = chromadb.PersistentClient(path=persist_dir)
        self.col = self.client.get_or_create_collection("darukaa_knowledge")
        self.emb = embeddings

    def upsert(self, docs: list[dict]) -> int:
        texts = [d["chunk_text"] for d in docs]
        vecs = self.emb.embed_documents(texts)
        ids = [d.get("embedding_id") or __import__("uuid").uuid4().hex for d in docs]
        metas = [{k: str(v)[:800] for k, v in d.items() if k not in ("chunk_text", "embedding")} for d in docs]
        self.col.upsert(ids=ids, documents=texts, embeddings=vecs, metadatas=metas)
        return len(docs)

    def query(self, text: str, top_k: int = 4, topic: str | None = None) -> list[dict]:
        q = self.emb.embed_query(text)
        res = self.col.query(query_embeddings=[q], n_results=top_k)
        out = []
        for i, doc in enumerate(res.get("documents", [[]])[0]):
            meta = res.get("metadatas", [[{}]])[0][i] if res.get("metadatas") else {}
            out.append({"chunk_text": doc, **meta})
        return out

    def count(self) -> int:
        return self.col.count()
