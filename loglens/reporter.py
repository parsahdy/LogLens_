from loglens.models import LogSummary


def generate_json(summary: LogSummary) -> str:
    return summary.model_dump_json(indent=2)


def generate_markdown(summary: LogSummary) -> str:
    lines = [
        "# LogLens Analysis Report",
        "",
        "## Overview",
        f"- **Total Lines:** {summary.total_lines}",
        f"- **Parsed Lines:** {summary.parsed_lines}",
        f"- **Skipped Lines:** {summary.skipped_lines}",
        f"- **Total Requests:** {summary.total_requests}",
        "",
        "## Severity Breakdown",
        f"- **INFO:** {summary.severity_counts.get('INFO', 0)}",
        f"- **WARNING:** {summary.severity_counts.get('WARNING', 0)}",
        f"- **ERROR:** {summary.severity_counts.get('ERROR', 0)}",
        "",
        "## Error Rates",
        f"- **Overall Error Rate (4xx + 5xx):** {summary.overall_error_rate * 100:.2f}% ({summary.client_error_count + summary.server_error_count}/{summary.total_requests})",
        f"- **Client Error Rate (4xx):** {summary.client_error_rate * 100:.2f}% ({summary.client_error_count}/{summary.total_requests})",
        f"- **Server Error Rate (5xx):** {summary.server_error_rate * 100:.2f}% ({summary.server_error_count}/{summary.total_requests})",
        "",
        "## HTTP Status Codes",
    ]

    if summary.status_code_counts:
        lines.append("| Status Code | Count |")
        lines.append("| --- | --- |")
        for code, count in sorted(summary.status_code_counts.items()):
            lines.append(f"| {code} | {count} |")
    else:
        lines.append("No status codes recorded.")

    lines.extend([
        "",
        "## Problematic Endpoints",
    ])

    if summary.problematic_endpoints:
        lines.append("| Endpoint | Total Requests | Errors | 4xx | 5xx |")
        lines.append("| --- | --- | --- | --- | --- |")
        for ep in summary.problematic_endpoints:
            lines.append(
                f"| {ep.endpoint} | {ep.total_requests} | {ep.error_count} | {ep.client_error_count} | {ep.server_error_count} |"
            )
    else:
        lines.append("No problematic endpoints identified.")

    return "\n".join(lines) + "\n"
