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
        # Create core traces storage table
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

                -- Project 2 Guardrails Intersections
                policy_violated BOOLEAN DEFAULT FALSE,
                violation_type VARCHAR,
                action_taken VARCHAR,

                -- Project 1 Reliability Intersections
                hallucination_score DOUBLE,
                groundedness_score DOUBLE,
                retrieval_precision DOUBLE,

                -- CRITICAL FIX: Explicit storage for unstructured payload contextual links
                metadata VARCHAR
            );
        """)
        print(f"[DuckDB] Database storage cluster verified and active at: {settings.DB_FILE}")
    finally:
        conn.close()


@contextmanager
def get_db_connection():
    """
    Context manager to yield a clean database connection context.
    Safely wraps database connection lifecycles to prevent access locks.
    """
    conn = duckdb.connect(settings.DB_FILE)
    try:
        yield conn
    finally:
        conn.close()