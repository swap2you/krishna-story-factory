"""Governed Knowledge search: SQLite FTS for local, PostgreSQL-ready SQL."""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from ..config import get_settings

PUBLIC_LIFECYCLES = frozenset({"approved", "published"})


def _roadmap_path() -> Path:
    return get_settings().repository_root / "content" / "knowledge" / "roadmap" / "records.json"


def _fts_db_path() -> Path:
    settings = get_settings()
    path = settings.repository_root / "data" / "catalog" / "knowledge_fts.sqlite"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def ensure_fts_index() -> Path:
    db_path = _fts_db_path()
    records = json.loads(_roadmap_path().read_text(encoding="utf-8"))
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("DROP TABLE IF EXISTS knowledge_fts")
        conn.execute(
            """
            CREATE VIRTUAL TABLE knowledge_fts USING fts5(
              id UNINDEXED,
              title,
              pillar,
              cluster,
              content_type,
              audience,
              level,
              lifecycle UNINDEXED,
              visibility UNINDEXED,
              source_tier,
              aliases,
              transliteration,
              summary,
              body,
              scripture,
              topic,
              tokenize = 'porter unicode61'
            )
            """
        )
        for row in records:
            conn.execute(
                """
                INSERT INTO knowledge_fts(
                  id, title, pillar, cluster, content_type, audience, level,
                  lifecycle, visibility, source_tier, aliases, transliteration,
                  summary, body, scripture, topic
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', '', '', '', '', ?)
                """,
                (
                    row.get("id"),
                    row.get("title"),
                    row.get("pillar"),
                    row.get("cluster"),
                    row.get("content_type"),
                    row.get("audience"),
                    row.get("level"),
                    row.get("lifecycle"),
                    row.get("visibility"),
                    row.get("source_tier_required"),
                    row.get("cluster"),
                ),
            )
        conn.commit()
    finally:
        conn.close()
    return db_path


def search_knowledge(
    query: str,
    *,
    include_private: bool = False,
    limit: int = 50,
    facet_lifecycle: str | None = None,
    facet_type: str | None = None,
) -> dict:
    ensure_fts_index()
    q = (query or "").strip()
    conn = sqlite3.connect(_fts_db_path())
    conn.row_factory = sqlite3.Row
    try:
        if q:
            # Phrase + keyword tolerant: quote tokens for FTS5.
            tokens = re.findall(r"[\w\-]+", q, flags=re.UNICODE)
            if not tokens:
                match = q.replace('"', "")
            else:
                match = " ".join(f'"{t}"' for t in tokens)
            sql = """
              SELECT id, title, pillar, cluster, content_type, audience, level,
                     lifecycle, visibility, source_tier, bm25(knowledge_fts) AS rank
              FROM knowledge_fts
              WHERE knowledge_fts MATCH ?
            """
            params: list = [match]
        else:
            sql = """
              SELECT id, title, pillar, cluster, content_type, audience, level,
                     lifecycle, visibility, source_tier, 0 AS rank
              FROM knowledge_fts
              WHERE 1=1
            """
            params = []
        if not include_private:
            sql += " AND visibility = 'public' AND lifecycle IN ('approved','published')"
        if facet_lifecycle:
            sql += " AND lifecycle = ?"
            params.append(facet_lifecycle)
        if facet_type:
            sql += " AND content_type = ?"
            params.append(facet_type)
        sql += " ORDER BY rank LIMIT ?"
        params.append(max(1, min(limit, 200)))
        try:
            rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
        except sqlite3.OperationalError:
            rows = []
        suggestions = []
        if not rows and q:
            suggestions = ["bhakti", "Prabhupāda", "Bhagavad-gītā", "Sunday School", "deity worship"]
        return {
            "query": q,
            "include_private": include_private,
            "count": len(rows),
            "results": rows,
            "zero_result_suggestions": suggestions,
            "engine": "sqlite_fts5",
            "postgres_ready": True,
        }
    finally:
        conn.close()


# PostgreSQL-ready DDL kept beside the SQLite implementation for migrations/adapters.
POSTGRES_DDL = """
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
  cluster TEXT
);
CREATE INDEX IF NOT EXISTS idx_knowledge_lifecycle ON knowledge_documents (lifecycle, visibility);
-- Application adapters should also create a tsvector column + GIN index:
-- ALTER TABLE knowledge_documents ADD COLUMN search_vector tsvector;
-- CREATE INDEX idx_knowledge_fts ON knowledge_documents USING GIN (search_vector);
"""
