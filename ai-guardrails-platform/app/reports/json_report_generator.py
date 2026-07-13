import json
from datetime import datetime

def generate_json_report(results):

    report = {
        "generated_at": str(datetime.now()),
        "total_tests": len(results),
        "blocked": sum(r["blocked"] for r in results),
        "results": results
    }

    with open(
        "reports/json/latest_guardrail_report.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(report, file, indent=2)