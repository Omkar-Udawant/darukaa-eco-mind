"""FastAPI entrypoint — Environmental Reasoning Engine (not a chatbot)."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .config import settings
from .database import init_db

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
log = logging.getLogger("darukaa")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # seed KB on first boot if empty
    try:
        from pathlib import Path

        from .rag.ingest import ingest_seed_file
        from .rag.vectorstore import get_vector_store

        store = get_vector_store()
        if store.count() == 0:
            seed = Path(__file__).resolve().parents[2] / ".." / ".." / "knowledge" / "seed_sources.json"
            seed = seed.resolve()
            alt = Path(__file__).resolve().parents[3] / "knowledge" / "seed_sources.json"
            for cand in (seed, alt, Path("knowledge/seed_sources.json"), Path("../knowledge/seed_sources.json")):
                if cand.exists():
                    n = ingest_seed_file(str(cand), store)
                    log.info("Seeded knowledge base: %s chunks from %s", n, cand)
                    break
    except Exception as e:  # never fail boot on KB issues
        log.warning("KB seeding skipped: %s", e)
    yield


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()] or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/")
def root():
    return {"service": settings.APP_NAME, "version": settings.APP_VERSION, "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
