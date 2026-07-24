-- PostgreSQL-ready Knowledge search migration (adapter target).
-- Applied by operators when PostgreSQL is provisioned; SQLite FTS remains local default.

CREATE TABLE IF NOT EXISTS knowledge_documents (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  summary TEXT,
  body TEXT,
  aliases TEXT[],
  transliteration TEXT,
  scripture TEXT,
  chapter_verse TEXT,
  topic TEXT,
  audience TEXT,
  age TEXT,
  content_type TEXT,
  lifecycle TEXT NOT NULL,
  visibility TEXT NOT NULL,
  pillar TEXT,
  cluster TEXT,
  source_tier TEXT,
  rights_status TEXT,
  confidentiality TEXT,
  updated_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE knowledge_documents
  ADD COLUMN IF NOT EXISTS search_vector tsvector;

CREATE INDEX IF NOT EXISTS idx_knowledge_lifecycle
  ON knowledge_documents (lifecycle, visibility);

CREATE INDEX IF NOT EXISTS idx_knowledge_fts
  ON knowledge_documents USING GIN (search_vector);
