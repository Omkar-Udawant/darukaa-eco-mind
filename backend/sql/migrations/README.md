# Migrations

**001 baseline = `../schema.sql`** (canonical 13-table schema; run first on Supabase/Railway):
```bash
psql $DATABASE_URL -f backend/sql/schema.sql
```
Subsequent migrations below run in lexicographic order and are idempotent.

- `002_perf_indexes.sql` — query-performance indexes for judge-facing reads
  (`/history` ordering, `/sources` topic filter, memory replay).
