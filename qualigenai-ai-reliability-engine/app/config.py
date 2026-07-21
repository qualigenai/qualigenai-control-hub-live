import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


class Settings:
    PROJECT_NAME = "QualiGenAI AI Reliability Engine"

    SYSTEM_UNDER_TEST = "Hybrid RAG v1.5"

    EXECUTION_MODE = os.getenv("EXECUTION_MODE", "local_api")

    LOCAL_RAG_BASE_URL = "http://127.0.0.1:8000"

    PRODUCTION_RAG_BASE_URL = "https://rag-system-api-v2.onrender.com"

    RAG_HEALTH_ENDPOINT = "/health"

    RAG_QUERY_ENDPOINT = "/query"

    RAG_LOGIN_ENDPOINT = "/api/auth/login"

    DATASET_PATH = Path("datasets/rag_v1_5_tests/golden_dataset.json")

    JSON_REPORT_PATH = Path("reports/json/latest_report.json")

    HTML_REPORT_PATH = Path("reports/html/latest_report.html")

    REQUEST_TIMEOUT_SECONDS = 60

    QUALITY_GATE_MIN_SCORE = 75

    RAG_API_AUTH_TYPE = os.getenv("RAG_API_AUTH_TYPE", "none")

    RAG_API_KEY = os.getenv("RAG_API_KEY", "")

    RAG_LOGIN_EMAIL = os.getenv("RAG_LOGIN_EMAIL", "")

    RAG_LOGIN_PASSWORD = os.getenv("RAG_LOGIN_PASSWORD", "")

    @classmethod
    def get_base_url(cls):
        if cls.EXECUTION_MODE == "local_api":
            return cls.LOCAL_RAG_BASE_URL

        if cls.EXECUTION_MODE == "production_api":
            return cls.PRODUCTION_RAG_BASE_URL

        if cls.EXECUTION_MODE == "github_ci":
            return cls.LOCAL_RAG_BASE_URL

        raise ValueError(f"Unsupported EXECUTION_MODE: {cls.EXECUTION_MODE}")

    @classmethod
    def get_auth_headers(cls):
        if cls.RAG_API_AUTH_TYPE == "bearer" and cls.RAG_API_KEY:
            return {
                "Authorization": f"Bearer {cls.RAG_API_KEY}"
            }

        return {}
