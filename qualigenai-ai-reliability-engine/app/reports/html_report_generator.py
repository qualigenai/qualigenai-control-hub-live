from pathlib import Path
from collections import Counter


class HTMLReportGenerator:
    """
    Generates a clean HTML reliability report for the
    QualiGenAI AI Reliability Engine.
    """

    def generate(self, report: dict, output_path: str):
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        summary = report.get("summary", {})
        results = report.get("results", [])

        total_tests = summary.get("total_tests", 0)
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        average_score = summary.get("average_score", 0)
        quality_gate = summary.get("quality_gate", "unknown")

        hallucination_counts = Counter(
            item.get("hallucination_type", "Unknown") for item in results
        )

        hallucination_list = ""
        for name, count in hallucination_counts.items():
            hallucination_list += f"""
            <div class="type-card">
                <span>{name}</span>
                <strong>{count}</strong>
            </div>
            """

        component_rows = ""
        for item in results:
            component_scores = item.get("component_scores", {})

            status_class = "status-pass" if item.get("status") == "passed" else "status-fail"

            component_rows += f"""
            <tr>
                <td>{item.get("test_id")}</td>
                <td>{item.get("score")}</td>
                <td>{component_scores.get("answer_availability", "NA")}</td>
                <td>{component_scores.get("source_citation", "NA")}</td>
                <td>{component_scores.get("context_grounding", "NA")}</td>
                <td>{component_scores.get("retrieval_quality", "NA")}</td>
                <td>{component_scores.get("safety_behavior", "NA")}</td>
                <td class="{status_class}">{item.get("status")}</td>
            </tr>
            """

        failed_rows = ""
        for item in results:
            if item.get("status") == "failed":
                failed_rows += f"""
                <tr>
                    <td>{item.get("test_id")}</td>
                    <td>{item.get("question")}</td>
                    <td>{item.get("hallucination_type")}</td>
                    <td>{item.get("risk")}</td>
                    <td>{item.get("severity")}</td>
                    <td>{item.get("score")}</td>
                    <td>{item.get("reason")}</td>
                    <td>{item.get("remediation")}</td>
                </tr>
                """

        if not failed_rows:
            failed_rows = """
            <tr>
                <td colspan="8" class="success-text">No failed scenarios found.</td>
            </tr>
            """

        all_rows = ""
        for item in results:
            status_class = "status-pass" if item.get("status") == "passed" else "status-fail"

            all_rows += f"""
            <tr>
                <td>{item.get("test_id")}</td>
                <td>{item.get("question")}</td>
                <td>{item.get("hallucination_type")}</td>
                <td>{item.get("risk")}</td>
                <td>{item.get("severity")}</td>
                <td>{item.get("score")}</td>
                <td class="{status_class}">{item.get("status")}</td>
                <td>{item.get("reason")}</td>
                <td>{", ".join(item.get("sources", []))}</td>
            </tr>
            """

        gate_class = "gate-pass" if quality_gate == "passed" else "gate-fail"

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>QualiGenAI AI Reliability Report</title>
    <style>
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: #07111f;
            color: #e5e7eb;
        }}

        .container {{
            padding: 30px;
        }}

        .header {{
            background: linear-gradient(135deg, #111827, #1e3a8a);
            border: 1px solid #24324a;
            padding: 30px;
            border-radius: 18px;
            margin-bottom: 24px;
        }}

        .header h1 {{
            margin: 0;
            font-size: 34px;
        }}

        .header p {{
            color: #cbd5e1;
            margin-top: 8px;
        }}

        .cards {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }}

        .card {{
            background: #0f172a;
            border: 1px solid #24324a;
            padding: 20px;
            border-radius: 16px;
        }}

        .card-title {{
            color: #94a3b8;
            font-size: 13px;
            margin-bottom: 10px;
        }}

        .card-value {{
            font-size: 30px;
            font-weight: bold;
        }}

        .gate-pass {{
            color: #22c55e;
        }}

        .gate-fail {{
            color: #ef4444;
        }}

        .status-pass {{
            color: #22c55e;
            font-weight: bold;
            text-transform: uppercase;
        }}

        .status-fail {{
            color: #ef4444;
            font-weight: bold;
            text-transform: uppercase;
        }}

        .section {{
            background: #0f172a;
            border: 1px solid #24324a;
            padding: 24px;
            border-radius: 16px;
            margin-bottom: 24px;
            overflow-x: auto;
        }}

        .section h2 {{
            margin-top: 0;
        }}

        .types {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
        }}

        .type-card {{
            background: #111827;
            border: 1px solid #334155;
            padding: 14px;
            border-radius: 12px;
            display: flex;
            justify-content: space-between;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}

        th {{
            background: #1e293b;
            color: #cbd5e1;
            text-align: left;
            padding: 12px;
            white-space: nowrap;
        }}

        td {{
            border-bottom: 1px solid #24324a;
            padding: 12px;
            vertical-align: top;
        }}

        .success-text {{
            color: #22c55e;
            font-weight: bold;
            text-align: center;
        }}

        .footer {{
            color: #94a3b8;
            font-size: 13px;
            margin-top: 20px;
        }}

        @media (max-width: 900px) {{
            .cards {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .types {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">

        <div class="header">
            <h1>QualiGenAI AI Reliability Engine</h1>
            <p>Hallucination Testing Report for Hybrid RAG v1.5</p>
            <p>Execution Mode: {report.get("execution_mode")} | Run Time: {report.get("run_timestamp")}</p>
        </div>

        <div class="cards">
            <div class="card">
                <div class="card-title">Total Tests</div>
                <div class="card-value">{total_tests}</div>
            </div>

            <div class="card">
                <div class="card-title">Passed</div>
                <div class="card-value">{passed}</div>
            </div>

            <div class="card">
                <div class="card-title">Failed</div>
                <div class="card-value">{failed}</div>
            </div>

            <div class="card">
                <div class="card-title">Average Score</div>
                <div class="card-value">{average_score}</div>
            </div>

            <div class="card">
                <div class="card-title">Quality Gate</div>
                <div class="card-value {gate_class}">{quality_gate.upper()}</div>
            </div>
        </div>

        <div class="section">
            <h2>Hallucination Type Breakdown</h2>
            <div class="types">
                {hallucination_list}
            </div>
        </div>

        <div class="section">
            <h2>Component Score Breakdown</h2>
            <table>
                <thead>
                    <tr>
                        <th>Test ID</th>
                        <th>Overall</th>
                        <th>Answer Availability</th>
                        <th>Source Citation</th>
                        <th>Context Grounding</th>
                        <th>Retrieval Quality</th>
                        <th>Safety Behavior</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {component_rows}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>All Test Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Test ID</th>
                        <th>Question</th>
                        <th>Hallucination Type</th>
                        <th>Risk</th>
                        <th>Severity</th>
                        <th>Score</th>
                        <th>Status</th>
                        <th>Reason</th>
                        <th>Sources</th>
                    </tr>
                </thead>
                <tbody>
                    {all_rows}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>Failed Scenarios and Remediation</h2>
            <table>
                <thead>
                    <tr>
                        <th>Test ID</th>
                        <th>Question</th>
                        <th>Hallucination Type</th>
                        <th>Risk</th>
                        <th>Severity</th>
                        <th>Score</th>
                        <th>Reason</th>
                        <th>Remediation</th>
                    </tr>
                </thead>
                <tbody>
                    {failed_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            Generated by QualiGenAI AI Reliability Engine.
        </div>

    </div>
</body>
</html>
        """

        output_file.write_text(html, encoding="utf-8")