class RemediationEngine:
    """
    Suggests practical remediation steps based on the hallucination type.
    """

    def suggest(self, hallucination_type: str) -> str:
        suggestions = {
            "Prompt Injection Failure": "Strengthen system prompt, add input filtering, and reject instructions that ask the model to ignore trusted context.",
            "Citation Hallucination": "Enforce citation validation. Do not allow the model to generate document names unless they exist in retrieved sources.",
            "Unsupported Answer": "Add a no-context fallback response. The model should say it does not have enough information when source context is missing.",
            "Retrieval Hallucination": "Improve retrieval by tuning top_k, chunk size, hybrid search weights, and metadata filtering.",
            "Factual Hallucination": "Compare generated answers against golden answers and add stricter factual correctness checks.",
            "Contextual Hallucination": "Add groundedness validation to ensure each answer is supported by retrieved context.",
            "Overclaim / Confidence Hallucination": "Prevent absolute claims like 100% accuracy. Add confidence calibration and risk-aware wording.",
            "Incomplete Answer": "Improve answer completeness by checking minimum response length and required key points.",
            "General Reliability Issue": "Review prompt, retrieved context, expected source, and answer generation flow."
        }

        return suggestions.get(
            hallucination_type,
            "Review the response, retrieved context, and source documents."
        )