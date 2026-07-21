# app/services/drift_detector.py
import math
from typing import List, Dict, Any, Optional


class DriftDetectorService:
    @staticmethod
    def calculate_moving_average(scores: List[float]) -> float:
        """Calculates standard trailing moving average metrics."""
        if not scores:
            return 0.0
        return sum(scores) / len(scores)

    @staticmethod
    def calculate_z_score(current_score: float, history: List[float]) -> float:
        """
        Calculates the Z-score of a metric relative to its historical baseline population.
        Helps flag mathematical anomalies when a score deviates by N standard deviations.
        """
        if not history or len(history) < 2:
            return 0.0

        n = len(history)
        mean = sum(history) / n

        # Calculate Variance and Standard Deviation
        variance = sum((x - mean) ** 2 for x in history) / (n - 1)
        std_dev = math.sqrt(variance)

        if std_dev == 0:
            return 0.0

        # Z-Score formula: (X - μ) / σ
        return (current_score - mean) / std_dev

    @classmethod
    def analyze_metric_degradation(cls, current_window: List[float], historical_baseline: List[float],
                                   threshold_z: float = 2.0) -> Dict[str, Any]:
        """
        Compares recent runtime evaluation windows against an established baseline
        to track structural model or retrieval degradation profiles.
        """
        if not current_window or not historical_baseline:
            return {"drift_detected": False, "status": "insufficient_data"}

        current_avg = cls.calculate_moving_average(current_window)
        baseline_avg = cls.calculate_moving_average(historical_baseline)

        # Calculate statistical variance using the final data point of current window
        z_score = cls.calculate_z_score(current_window[-1], historical_baseline)

        # Detect true system performance drift
        drift_detected = abs(z_score) >= threshold_z

        status = "nominal"
        if drift_detected:
            status = "anomalous_degradation" if z_score > 0 else "anomalous_improvement"

        return {
            "drift_detected": drift_detected,
            "status": status,
            "current_window_average": round(current_avg, 4),
            "baseline_average": round(baseline_avg, 4),
            "calculated_z_score": round(z_score, 4)
        }