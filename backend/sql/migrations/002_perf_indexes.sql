-- 002: performance indexes for judge-facing reads. Idempotent.
CREATE INDEX IF NOT EXISTS idx_conv_updated ON conversations(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_conv_user ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_conv_created ON conversation_memory(conversation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_sources_topic_year ON scientific_sources(topic, year DESC);
CREATE INDEX IF NOT EXISTS idx_reco_conv ON recommendations(conversation_id);
CREATE INDEX IF NOT EXISTS idx_reasoning_conv_stage ON reasoning_logs(conversation_id, stage);
