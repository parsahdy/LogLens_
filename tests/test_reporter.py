import json
from loglens.models import LogSummary, EndpointStats
from loglens.reporter import generate_json, generate_markdown


def test_generate_json():
    summary = LogSummary(
        total_lines=5,
        parsed_lines=4,
        skipped_lines=1,
        total_requests=4,
        severity_counts={"INFO": 3, "WARNING": 0, "ERROR": 1},
        status_code_counts={200: 3, 500: 1},
        client_error_count=0,
        server_error_count=1,
        overall_error_rate=0.25,
        client_error_rate=0.0,
        server_error_rate=0.25,
        problematic_endpoints=[
            EndpointStats(
                endpoint="/api/orders",
                total_requests=1,
                error_count=1,
                client_error_count=0,
                server_error_count=1,
            )
        ],
    )

    json_str = generate_json(summary)
    data = json.loads(json_str)

    assert data["total_lines"] == 5
    assert data["parsed_lines"] == 4
    assert data["overall_error_rate"] == 0.25
    assert len(data["problematic_endpoints"]) == 1


def test_generate_markdown_normal():
    summary = LogSummary(
        total_lines=2,
        parsed_lines=2,
        skipped_lines=0,
        total_requests=2,
        severity_counts={"INFO": 1, "WARNING": 0, "ERROR": 1},
        status_code_counts={200: 1, 500: 1},
        client_error_count=0,
        server_error_count=1,
        overall_error_rate=0.5,
        client_error_rate=0.0,
        server_error_rate=0.5,
        problematic_endpoints=[
            EndpointStats(
                endpoint="/api/orders",
                total_requests=1,
                error_count=1,
                client_error_count=0,
                server_error_count=1,
            )
        ],
    )

    md = generate_markdown(summary)
    assert "# LogLens Analysis Report" in md
    assert "Total Lines:** 2" in md
    assert "/api/orders" in md
    assert "50.00%" in md


def test_generate_markdown_empty():
    summary = LogSummary()
    md = generate_markdown(summary)
    assert "# LogLens Analysis Report" in md
    assert "No status codes recorded." in md
    assert "No problematic endpoints identified." in md
