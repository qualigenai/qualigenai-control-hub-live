import json

from app.evaluators.guardrail_evaluator import evaluate_guardrail

from app.reports.json_report_generator import generate_json_report
from app.reports.html_report_generator import generate_html_report

with open(
    "datasets/guardrail_tests/golden_guardrail_dataset.json",
    encoding="utf-8"
) as file:

    test_cases = json.load(file)

print("=" * 50)
print("AI Guardrails Platform")
print("=" * 50)

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

generate_json_report(results)
generate_html_report(results)

print("\nReports generated successfully.")