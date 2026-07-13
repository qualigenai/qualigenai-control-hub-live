def generate_html_report(results):

    rows = ""

    for r in results:

        rows += f"""
        <tr>
            <td>{r['id']}</td>
            <td>{r['blocked']}</td>
            <td>{r['reason']}</td>
            <td>{r['score']}</td>
        </tr>
        """

    html = f"""
    <html>
    <head>
        <title>AI Guardrails Report</title>
    </head>

    <body>

        <h1>AI Guardrails Platform Report</h1>

        <table border="1" cellpadding="10">

            <tr>
                <th>Test ID</th>
                <th>Blocked</th>
                <th>Reason</th>
                <th>Score</th>
            </tr>

            {rows}

        </table>

    </body>
    </html>
    """

    with open(
        "reports/html/latest_guardrail_report.html",
        "w",
        encoding="utf-8"
    ) as file:

        file.write(html)