"""Conversation memory: Redis (short-term) + PostgreSQL (long-term). Falls back to in-memory."""
from __future__ import annotations

import json

_mem: dict[str, list[dict]] = {}


class MemoryManager:
    def __init__(self):
        from ..config import settings

        self._redis = None
        if settings.REDIS_URL:
            try:
                import redis

                self._redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
                self._redis.ping()
            except Exception:
                self._redis = None

    # -- short-term --
    def append_turn(self, conversation_id: str, role: str, content: str, entities: dict | None = None):
        entry = {"role": role, "content": content, "entities": entities or {}}
        if self._redis:
            try:
                self._redis.rpush(f"darukaa:{conversation_id}", json.dumps(entry))
                self._redis.ltrim(f"darukaa:{conversation_id}", -40, -1)
                return
            except Exception:
                pass
        _mem.setdefault(conversation_id, []).append(entry)
        _mem[conversation_id] = _mem[conversation_id][-40:]

    def recent(self, conversation_id: str, n: int = 10) -> list[dict]:
        if self._redis:
            try:
                raw = self._redis.lrange(f"darukaa:{conversation_id}", -n, -1)
                return [json.loads(x) for x in raw]
            except Exception:
                pass
        return _mem.get(conversation_id, [])[-n:]

    # -- long-term (Postgres) --
    def persist(self, conversation_id: str, role: str, content: str, entities: dict | None = None):
        try:
            from ..database import SessionLocal, ConversationMemory

            db = SessionLocal()
            try:
                db.add(ConversationMemory(
                    conversation_id=conversation_id, role=role,
                    content=content[:8000], entities=entities or {},
                ))
                db.commit()
            finally:
                db.close()
        except Exception:
            pass

    def history(self, conversation_id: str, limit: int = 50) -> list[dict]:
        try:
            from ..database import SessionLocal, ConversationMemory

            db = SessionLocal()
            try:
                rows = (
                    db.query(ConversationMemory)
                    .filter(ConversationMemory.conversation_id == conversation_id)
                    .order_by(ConversationMemory.created_at.desc())
                    .limit(limit)
                    .all()
                )
                return [{"role": r.role, "content": r.content, "entities": r.entities} for r in reversed(rows)]
            finally:
                db.close()
        except Exception:
            return self.recent(conversation_id, limit)


memory = MemoryManager()
