-- Darukaa.Earth PostgreSQL schema (Supabase-compatible). Generated from SQLAlchemy models.
-- Run: psql $DATABASE_URL -f schema.sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  email TEXT UNIQUE NOT NULL, name TEXT DEFAULT '', created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS conversations (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  user_id TEXT REFERENCES users(id), title TEXT DEFAULT 'New assessment',
  region TEXT DEFAULT '', created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS conversation_memory (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  conversation_id TEXT REFERENCES conversations(id), role TEXT NOT NULL,
  content TEXT NOT NULL, entities JSONB DEFAULT '{}', created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_memory_conv ON conversation_memory(conversation_id);
CREATE TABLE IF NOT EXISTS soil_metrics (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text, conversation_id TEXT REFERENCES conversations(id),
  ph DOUBLE PRECISION, organic_carbon_pct DOUBLE PRECISION, moisture_pct DOUBLE PRECISION,
  nutrient_quality TEXT DEFAULT '', created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS climate_metrics (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text, conversation_id TEXT REFERENCES conversations(id),
  temperature_c DOUBLE PRECISION, rainfall_mm DOUBLE PRECISION,
  seasonal_variability TEXT DEFAULT '', created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS biodiversity_metrics (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text, conversation_id TEXT REFERENCES conversations(id),
  species_richness INTEGER, habitat_diversity TEXT DEFAULT '',
  pollinator_presence TEXT DEFAULT '', created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS land_use_metrics (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text, conversation_id TEXT REFERENCES conversations(id),
  cropland_pct DOUBLE PRECISION, forest_pct DOUBLE PRECISION, grassland_pct DOUBLE PRECISION,
  urban_pct DOUBLE PRECISION, wetlands_pct DOUBLE PRECISION, dominant_type TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS human_impact_metrics (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text, conversation_id TEXT REFERENCES conversations(id),
  pollution TEXT DEFAULT '', deforestation TEXT DEFAULT '', fragmentation TEXT DEFAULT '',
  chemical_inputs TEXT DEFAULT '', created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS recommendations (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text, conversation_id TEXT REFERENCES conversations(id),
  title TEXT NOT NULL, detail TEXT DEFAULT '', reasoning TEXT DEFAULT '',
  impacted_metrics JSONB DEFAULT '[]', estimated_improvement TEXT DEFAULT '',
  time_horizon TEXT DEFAULT '', confidence DOUBLE PRECISION DEFAULT 0,
  dimensions_used JSONB DEFAULT '[]', created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS scientific_sources (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text, source TEXT NOT NULL,
  publication TEXT NOT NULL, year INTEGER DEFAULT 2020, topic TEXT DEFAULT '',
  evidence_strength TEXT DEFAULT 'medium', chunk_text TEXT NOT NULL, embedding_id TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_sources_source ON scientific_sources(source);
CREATE TABLE IF NOT EXISTS retrieval_logs (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text, conversation_id TEXT REFERENCES conversations(id),
  query TEXT NOT NULL, topics JSONB DEFAULT '[]', doc_ids JSONB DEFAULT '[]',
  latency_ms INTEGER DEFAULT 0, created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS reasoning_logs (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text, conversation_id TEXT REFERENCES conversations(id),
  stage TEXT NOT NULL, payload JSONB DEFAULT '{}', created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS impact_predictions (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text, recommendation_id TEXT REFERENCES recommendations(id),
  biodiversity_gain_pct DOUBLE PRECISION DEFAULT 0, soil_carbon_gain_pct DOUBLE PRECISION DEFAULT 0,
  water_retention_gain_pct DOUBLE PRECISION DEFAULT 0, habitat_quality_gain_pct DOUBLE PRECISION DEFAULT 0,
  horizon TEXT DEFAULT 'Medium Term', created_at TIMESTAMPTZ DEFAULT now()
);
