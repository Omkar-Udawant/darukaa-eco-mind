"""Embeddings: OpenAI when key present, else deterministic hash embeddings (no network)."""
from __future__ import annotations

import hashlib
import math


class HashEmbeddings:
    dim: int = 256

    def _vec(self, text: str) -> list[float]:
        v = [0.0] * self.dim
        for tok in text.lower().split():
            h = int(hashlib.sha256(tok.encode()).hexdigest(), 16)
            v[h % self.dim] += 1.0
        n = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / n for x in v]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vec(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vec(text)


def get_embeddings():
    from ..config import settings

    if settings.EMBEDDING_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        try:
            from langchain_openai import OpenAIEmbeddings

            return OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
        except Exception:
            pass
    return HashEmbeddings()
