# Deployment Guide

## Frontend → Vercel
1. Import `frontend/` as project. 2. Set `NEXT_PUBLIC_API_URL=https://<railway-backend>/`. 3. Deploy (Next 15, `npm run build`).

## Backend → Railway
1. New service from `backend/` (`Dockerfile`). 2. Env: `DATABASE_URL` (Supabase pooled), `REDIS_URL` (Upstash), `QDRANT_URL`/`QDRANT_API_KEY` (Qdrant Cloud), `OPENAI_API_KEY`, `EMBEDDING_PROVIDER=openai`, `VECTOR_BACKEND=qdrant`, `CORS_ORIGINS=https://<vercel-app>`. 3. `psql $DATABASE_URL -f backend/sql/schema.sql` once.

## Database → Supabase
Create project → copy pooled connection string → replace `DATABASE_URL`. Schema in `backend/sql/schema.sql`.

## Vector → Qdrant Cloud / Chroma
Qdrant: free cluster → set `QDRANT_URL` + key, `VECTOR_BACKEND=qdrant`. Chroma (simpler, no cloud): `VECTOR_BACKEND=chroma`, `CHROMA_DIR=/data/chroma`.

## Cache → Upstash Redis
Copy `rediss://…` URL into `REDIS_URL`; memory manager auto-detects, else in-memory.

## Local prod-like: `docker-compose up --build` (backend :8000, frontend :3000, pg :5432, redis :6379, qdrant :6333).
