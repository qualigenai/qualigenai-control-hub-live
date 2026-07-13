class HallucinationClassifier:
    """
    Classifies the type of hallucination or validation issue
    based on the validation type and detected issues.
    """

    def classify(self, validation_type: str, issues: list) -> str:
        issue_text = " ".join(issues).lower()

        if validation_type == "prompt_injection":
            return "Prompt Injection Failure"

        if validation_type == "fake_citation_detection":
            return "Citation Hallucination"

        if validation_type == "unsupported_answer":
            return "Unsupported Answer"

        if validation_type == "retrieval_quality":
            return "Retrieval Hallucination"

        if validation_type == "citation_validation":
            return "Citation Hallucination"

        if validation_type == "factual_correctness":
            return "Factual Hallucination"

        if validation_type == "groundedness":
            return "Contextual Hallucination"

        if validation_type == "overclaim_detection":
            return "Overclaim / Confidence Hallucination"

        if "source" in issue_text or "citation" in issue_text:
            return "Citation Hallucination"

        if "context" in issue_text:
            return "Contextual Hallucination"

        if "too short" in issue_text:
            return "Incomplete Answer"

        return "General Reliability Issue"