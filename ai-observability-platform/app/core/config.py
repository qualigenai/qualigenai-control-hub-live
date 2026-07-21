# app/core/config.py
import os
import json
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME: str = "QualiGenAI Observability Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    DB_FILE: str = os.getenv("DB_FILE", "observability_vault.duckdb")

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))

    # New Target: Load static token pricing structures
    PRICING_FILE_PATH: Path = Path(__file__).resolve().parent.parent.parent / 'config' / 'pricing.json'
    PRICING_MATRIX: dict = {}

    def __init__(self):
        self.load_pricing_matrix()

    def load_pricing_matrix(self):
        try:
            if self.PRICING_FILE_PATH.exists():
                with open(self.PRICING_FILE_PATH, 'r') as file:
                    self.PRICING_MATRIX = json.load(file)
            else:
                # Safe fallback configuration if pricing file is isolated
                self.PRICING_MATRIX = {
                    "default": {"input_cost_per_million": 2.00, "output_cost_per_million": 10.00}
                }
        except Exception:
            self.PRICING_MATRIX = {
                "default": {"input_cost_per_million": 2.00, "output_cost_per_million": 10.00}
            }


settings = Settings()