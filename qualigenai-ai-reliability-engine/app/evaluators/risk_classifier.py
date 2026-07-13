class RiskClassifier:
    """
    Converts reliability score into severity and quality gate status.
    """

    def classify_severity(self, score: int) -> str:
        if score >= 85:
            return "low"

        if score >= 75:
            return "medium"

        if score >= 50:
            return "high"

        return "critical"

    def classify_status(self, score: int) -> str:
        if score >= 75:
            return "passed"

        return "failed"

    def classify_gate(self, average_score: float, critical_failures: int) -> str:
        if average_score < 75:
            return "failed"

        if critical_failures > 0:
            return "failed"

        return "passed"