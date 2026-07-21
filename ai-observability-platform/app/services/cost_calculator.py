# app/services/cost_calculator.py
import tiktoken
from typing import Dict, Any
from app.core.config import settings


class CostCalculatorService:
    @staticmethod
    def get_encoder_for_model(model_name: str):
        """
        Safely acquires the correct tiktoken encoding format structure
        based on the target LLM provider mapping context.
        """
        try:
            if "gpt" in model_name:
                return tiktoken.encoding_for_model(model_name)
            elif "claude" in model_name:
                return tiktoken.get_encoding("cl100k_base")
            else:
                return tiktoken.get_encoding("cl100k_base")
        except Exception:
            return tiktoken.get_encoding("cl100k_base")

    @classmethod
    def calculate_token_count(cls, text: str, model_name: str) -> int:
        """
        Calculates local token usage counts from raw string lengths
        if token counts aren't provided by upstream trackers.
        """
        if not text:
            return 0
        encoder = cls.get_encoder_for_model(model_name)
        return len(encoder.encode(text))

    @staticmethod
    def evaluate_financial_cost(model_name: str, prompt_tokens: int, completion_tokens: int) -> Dict[str, Any]:
        """
        Calculates the financial cost of an LLM call based on the pricing matrix.
        Calculations are based on price per million tokens.
        """
        pricing = settings.PRICING_MATRIX.get(model_name, settings.PRICING_MATRIX.get("default"))

        input_rate = pricing.get("input_cost_per_million", 2.00)
        output_rate = pricing.get("output_cost_per_million", 10.00)

        prompt_cost = (prompt_tokens / 1_000_000) * input_rate
        completion_cost = (completion_tokens / 1_000_000) * output_rate
        total_cost = prompt_cost + completion_cost

        return {
            "model_name": model_name,
            "prompt_cost": round(prompt_cost, 6),
            "completion_cost": round(completion_cost, 6),
            "total_cost": round(total_cost, 6)
        }