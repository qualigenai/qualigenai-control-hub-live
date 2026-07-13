import duckdb
import os


def init_governance_vault(db_path=None):
    # Dynamically point to your centralized DuckDB file
    if db_path is None:
        db_path = r"C:\Users\Rambhupal\AI-Portfolio\ai-observability-platform\observability_vault.duckdb"

    print(f"Connecting to DuckDB Vault at: {db_path}")
    conn = duckdb.connect(db_path)

    # 📑 1. Model Asset Registry Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS model_registry (
            model_id VARCHAR PRIMARY KEY,
            model_provider VARCHAR,          -- GPT-5.5, Claude, Gemini, Llama
            model_version VARCHAR,
            business_owner VARCHAR,
            deployment_date TIMESTAMP,
            risk_score DOUBLE DEFAULT 0.0
        );
    """)

    # 📑 2. Prompt Asset Registry Table (Git-style controls)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prompt_registry (
            prompt_hash VARCHAR PRIMARY KEY,
            prompt_name VARCHAR,
            version_tag VARCHAR,             -- v1, v2, v3
            prompt_text TEXT,
            author VARCHAR,
            changed_at TIMESTAMP,
            parent_hash VARCHAR
        );
    """)

    # 📑 3. Gold Evaluation Dataset Inventory Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS evaluation_datasets (
            dataset_id VARCHAR PRIMARY KEY,
            dataset_name VARCHAR,            -- Financial QA, Healthcare Dataset, etc.
            sample_count INTEGER,
            last_used_at TIMESTAMP,
            associated_engine VARCHAR
        );
    """)

    # Seed sample assets for demonstration if table is empty
    count = conn.execute("SELECT COUNT(*) FROM model_registry").fetchone()[0]
    if count == 0:
        conn.execute("""
            INSERT INTO model_registry VALUES 
            ('gpt-5.5-core', 'OpenAI', 'v5.5-beta', 'FinTech-Squad', CURRENT_TIMESTAMP, 0.10),
            ('claude-3.5-sonnet', 'Anthropic', 'v3.5-stable', 'Core RAG Engine', CURRENT_TIMESTAMP, 0.05),
            ('gemini-1.5-pro', 'Google', 'v1.5-localized', 'Pilgrim Bot System', CURRENT_TIMESTAMP, 0.15)
        """)
        print("💡 Seeded mock enterprise model assets successfully.")

    conn.close()
    print("✅ Governance tables cleanly validated/initialized in database.")


if __name__ == "__main__":
    init_governance_vault()