import json
from datetime import datetime
from collections import Counter

from app.config import Settings
from app.connectors.rag_v1_5_connector import RAGV15Connector
from app.evaluators.basic_response_evaluator import BasicResponseEvaluator
from app.reports.html_report_generator import HTMLReportGenerator


def load_test_cases():
    with open(Settings.DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json_report(report: dict):
    Settings.JSON_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(Settings.JSON_REPORT_PATH, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)


def build_summary(results: list) -> dict:
    total_tests = len(results)

    passed = len([
        item for item in results
        if item.get("status") == "passed"
    ])

    failed = total_tests - passed

    average_score = round(
        sum(item.get("score", 0) for item in results) / total_tests,
        2
    ) if total_tests else 0

    critical_failures = [
        item for item in results
        if item.get("severity") == "critical"
        or (item.get("risk") == "critical" and item.get("status") == "failed")
    ]

    high_failures = [
        item for item in results
        if item.get("severity") == "high"
    ]

    hallucination_breakdown = dict(
        Counter(item.get("hallucination_type", "Unknown") for item in results)
    )

    quality_gate = "passed"

    if average_score < Settings.QUALITY_GATE_MIN_SCORE:
        quality_gate = "failed"

    if critical_failures:
        quality_gate = "failed"

    return {
        "total_tests": total_tests,
        "passed": passed,
        "failed": failed,
        "average_score": average_score,
        "critical_failures": len(critical_failures),
        "high_failures": len(high_failures),
        "hallucination_breakdown": hallucination_breakdown,
        "quality_gate": quality_gate
    }


def main():
    print("====================================================")
    print(Settings.PROJECT_NAME)
    print("====================================================")
    print(f"System Under Test: {Settings.SYSTEM_UNDER_TEST}")
    print(f"Execution Mode   : {Settings.EXECUTION_MODE}")
    print(f"Base URL         : {Settings.get_base_url()}")
    print(f"Query Endpoint   : {Settings.RAG_QUERY_ENDPOINT}")

    connector = RAGV15Connector()
    evaluator = BasicResponseEvaluator()
    html_generator = HTMLReportGenerator()

    print("\nChecking connector health...")
    health = connector.health_check()
    print(json.dumps(health, indent=2))

    if health.get("status") == "failed":
        print("\nWARNING: Health check failed.")
        print("Check whether your local RAG app is running at:")
        print(Settings.get_base_url())
        return

    test_cases = load_test_cases()
    results = []

    print(f"\nLoaded {len(test_cases)} test cases.")

    for test_case in test_cases:
        print(f"\nRunning {test_case['id']}: {test_case['question']}")

        rag_response = connector.ask_question(
            test_id=test_case["id"],
            question=test_case["question"]
        )

        evaluation = evaluator.evaluate(test_case, rag_response)

        print(f"Result: {evaluation['status']} | Score: {evaluation['score']}")
        print(f"Type  : {evaluation['hallucination_type']}")
        print(f"Reason: {evaluation['reason']}")

        results.append(evaluation)

    summary = build_summary(results)

    report = {
        "project": Settings.PROJECT_NAME,
        "system_under_test": Settings.SYSTEM_UNDER_TEST,
        "execution_mode": Settings.EXECUTION_MODE,
        "base_url": Settings.get_base_url(),
        "query_endpoint": Settings.RAG_QUERY_ENDPOINT,
        "run_timestamp": datetime.now().isoformat(),
        "summary": summary,
        "health_check": health,
        "results": results
    }

    save_json_report(report)
    html_generator.generate(report, str(Settings.HTML_REPORT_PATH))

    print("\n====================================================")
    print("Test Run Completed")
    print("====================================================")
    print(f"Total Tests       : {summary['total_tests']}")
    print(f"Passed            : {summary['passed']}")
    print(f"Failed            : {summary['failed']}")
    print(f"Avg Score         : {summary['average_score']}")
    print(f"Critical Failures : {summary['critical_failures']}")
    print(f"High Failures     : {summary['high_failures']}")
    print(f"Quality Gate      : {summary['quality_gate'].upper()}")
    print(f"JSON Report       : {Settings.JSON_REPORT_PATH}")
    print(f"HTML Report       : {Settings.HTML_REPORT_PATH}")


if __name__ == "__main__":
    main()