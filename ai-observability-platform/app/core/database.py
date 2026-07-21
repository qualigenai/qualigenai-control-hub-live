# app/core/database.py
import duckdb
import os
from contextlib import contextmanager
from app.core.config import settings


def init_db():
    """
    Initializes the DuckDB database file and provisions the core analytical tables.
    Ensures the metadata JSON column is explicitly registered.
    """
    conn = duckdb.connect(settings.DB_FILE)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS traces (
                trace_id VARCHAR PRIMARY KEY,
                model_name VARCHAR,
                prompt_text VARCHAR,
                response_text VARCHAR,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                latency_ms DOUBLE,
                timestamp TIMESTAMP,
                policy_violated BOOLEAN DEFAULT FALSE,
                violation_type VARCHAR,
                action_taken VARCHAR,
                hallucination_score DOUBLE,
                groundedness_score DOUBLE,
                retrieval_precision DOUBLE,
                metadata VARCHAR
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS model_registry (
                model_id VARCHAR PRIMARY KEY,
                model_provider VARCHAR,
                model_version VARCHAR,
                business_owner VARCHAR,
                risk_score DOUBLE
            );
        """)

        existing_count = conn.execute("SELECT COUNT(*) FROM model_registry").fetchone()[0]
        if existing_count == 0:
            conn.execute("""
                INSERT INTO model_registry (model_id, model_provider, model_version, business_owner, risk_score)
                VALUES
                    ('gpt-5.5-core', 'OpenAI', 'v5.5-beta', 'FinTech-Squad', 0.10),
                    ('claude-3.5-sonnet', 'Anthropic', 'v3.5-stable', 'Core RAG Engine', 0.05),
                    ('gemini-1.5-pro', 'Google', 'v1.5-localized', 'Pilgrim Bot System', 0.15);
            """)
            print("[DuckDB] model_registry table seeded with baseline entries.")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS prompt_registry (
                prompt_hash VARCHAR PRIMARY KEY,
                prompt_name VARCHAR,
                version_tag VARCHAR,
                prompt_text VARCHAR,
                author VARCHAR,
                changed_at TIMESTAMP,
                parent_hash VARCHAR
            );
        """)

        print(f"[DuckDB] Database storage cluster verified and active at: {settings.DB_FILE}")
    finally:
        conn.close()


@contextmanager
def get_db_connection():
    """
    Context manager to yield a clean database connection context.
    """
    conn = duckdb.connect(settings.DB_FILE)
    try:
        yield conn
    finally:
        conn.close()
