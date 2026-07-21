import json

from app.evaluators.guardrail_evaluator import evaluate_guardrail
from app.reports.json_report_generator import generate_json_report
from app.reports.html_report_generator import generate_html_report


def run_guardrail_suite() -> dict:
    """
    Runs the full guardrail suite and returns a result dict.
    Used by both the CLI (below) and the new API service (api.py).
    """
    with open(
        "datasets/guardrail_tests/golden_guardrail_dataset.json",
        encoding="utf-8"
    ) as file:
        test_cases = json.load(file)

    results = []

    for tc in test_cases:
        result = evaluate_guardrail(tc)

        final_result = {
            "id": tc["id"],
            "question": tc["question"],
            "blocked": result["blocked"],
            "reason": result["reason"],
            "score": result["score"]
        }

        results.append(final_result)

        print(f"\n{tc['id']}")
        print("Blocked :", result["blocked"])
        print("Reason  :", result["reason"])
        print("Score   :", result["score"])

    total_tests = len(results)
    blocked_count = sum(1 for r in results if r["blocked"])

    report = {
        "total_tests": total_tests,
        "blocked": blocked_count,
        "results": results,
    }

    return {"ok": True, "report": report}


if __name__ == "__main__":
    print("=" * 50)
    print("AI Guardrails Platform")
    print("=" * 50)

    outcome = run_guardrail_suite()
    results = outcome["report"]["results"]

    generate_json_report(results)
    generate_html_report(results)

    print("\nReports generated successfully.")