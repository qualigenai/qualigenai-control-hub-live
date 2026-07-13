from app.evaluators.hallucination_classifier import HallucinationClassifier
from app.evaluators.remediation_engine import RemediationEngine
from app.evaluators.scoring_engine import ScoringEngine
from app.evaluators.risk_classifier import RiskClassifier


class BasicResponseEvaluator:
    """
    Evaluates RAG responses for reliability, hallucination risk,
    citation quality, grounding, retrieval and safety.
    """

    def __init__(self):
        self.classifier = HallucinationClassifier()
        self.remediation_engine = RemediationEngine()
        self.scoring_engine = ScoringEngine()
        self.risk_classifier = RiskClassifier()

    def evaluate(self, test_case: dict, rag_response: dict) -> dict:
        test_id = test_case.get("id")
        question = test_case.get("question", "")
        expected_source = test_case.get("expected_source", "")
        validation_type = test_case.get("validation_type", "")
        risk = test_case.get("risk", "medium")

        if rag_response.get("status") == "failed":
            hallucination_type = "API / Connector Failure"

            return {
                "test_id": test_id,
                "question": question,
                "validation_type": validation_type,
                "risk": risk,
                "severity": "critical",
                "status": "failed",
                "score": 0,
                "component_scores": {
                    "answer_availability": 0,
                    "source_citation": 0,
                    "context_grounding": 0,
                    "retrieval_quality": 0,
                    "safety_behavior": 0
                },
                "hallucination_type": hallucination_type,
                "reason": rag_response.get("error", "RAG response failed"),
                "remediation": "Check API availability, authentication, endpoint path, request payload, timeout, and response format.",
                "answer_preview": "",
                "sources": []
            }

        data = rag_response.get("data", {})

        answer = data.get("answer", "")
        sources = data.get("sources", [])
        retrieved_context = data.get("retrieved_context", "")
        raw_response = data.get("raw_response", {})

        chunks_used = 0
        if isinstance(raw_response, dict):
            chunks_used = raw_response.get("chunks_used", 0)

        component_scores = {
            "answer_availability": self.scoring_engine.score_answer_availability(answer),
            "source_citation": self.scoring_engine.score_source_citation(sources, expected_source),
            "context_grounding": self.scoring_engine.score_context_grounding(answer, sources),
            "retrieval_quality": self.scoring_engine.score_retrieval_quality(sources, chunks_used),
            "safety_behavior": self.scoring_engine.score_safety_behavior(question, answer)
        }

        overall_score = self.scoring_engine.calculate_overall_score(component_scores)

        issues = []

        if component_scores["answer_availability"] < 75:
            issues.append("Answer is missing, weak, or says information is unavailable")

        if component_scores["source_citation"] < 75:
            issues.append("Expected source citation is missing or mismatched")

        if component_scores["context_grounding"] < 75:
            issues.append("Answer may not be sufficiently grounded in retrieved sources")

        if component_scores["retrieval_quality"] < 75:
            issues.append("Retrieval quality is low or no chunks were used")

        if component_scores["safety_behavior"] < 75:
            issues.append("Safety behavior check failed")

        severity = self.risk_classifier.classify_severity(overall_score)
        status = self.risk_classifier.classify_status(overall_score)

        #hallucination_type = self.classifier.classify(validation_type, issues)
        hallucination_type = "No Issue Detected" if not issues else self.classifier.classify(validation_type, issues)
        remediation = self.remediation_engine.suggest(hallucination_type)

        return {
            "test_id": test_id,
            "question": question,
            "validation_type": validation_type,
            "risk": risk,
            "severity": severity,
            "status": status,
            "score": overall_score,
            "component_scores": component_scores,
            "hallucination_type": hallucination_type,
            "reason": "Passed validation" if not issues else "; ".join(issues),
            "remediation": remediation,
            "answer_preview": answer[:300],
            "sources": sources
        }