from datetime import datetime
import pytest

from loglens.models import LogEntry, LogLevel
from loglens.analyzer import analyze_logs


def test_analyze_logs_normal():
    entries = [
        LogEntry(
            timestamp=datetime(2026, 11, 15, 10, 0, 1),
            level=LogLevel.INFO,
            method="GET",
            endpoint="/api/users",
            status_code=200,
        ),
        LogEntry(
            timestamp=datetime(2026, 11, 15, 10, 0, 2),
            level=LogLevel.WARNING,
            method="GET",
            endpoint="/api/users",
            status_code=404,
        ),
        LogEntry(
            timestamp=datetime(2026, 11, 15, 10, 0, 3),
            level=LogLevel.ERROR,
            method="POST",
            endpoint="/api/orders",
            status_code=500,
        ),
        LogEntry(
            timestamp=datetime(2026, 11, 15, 10, 0, 4),
            level=LogLevel.ERROR,
            method="POST",
            endpoint="/api/orders",
            status_code=500,
        ),
    ]

    summary = analyze_logs(entries, total_lines=5, parsed_lines=4, skipped_lines=1)

    assert summary.total_lines == 5
    assert summary.parsed_lines == 4
    assert summary.skipped_lines == 1
    assert summary.total_requests == 4

    assert summary.severity_counts == {"INFO": 1, "WARNING": 1, "ERROR": 2}
    assert summary.status_code_counts == {200: 1, 404: 1, 500: 2}

    assert summary.client_error_count == 1
    assert summary.server_error_count == 2
    assert summary.overall_error_rate == 0.75  # 3 errors out of 4 requests
    assert summary.client_error_rate == 0.25
    assert summary.server_error_rate == 0.50

    assert len(summary.problematic_endpoints) == 2
    # /api/orders has 2 errors, /api/users has 1 error -> orders first
    assert summary.problematic_endpoints[0].endpoint == "/api/orders"
    assert summary.problematic_endpoints[0].error_count == 2
    assert summary.problematic_endpoints[1].endpoint == "/api/users"
    assert summary.problematic_endpoints[1].error_count == 1


def test_analyze_logs_empty():
    summary = analyze_logs([], total_lines=0, parsed_lines=0, skipped_lines=0)
    assert summary.total_lines == 0
    assert summary.total_requests == 0
    assert summary.overall_error_rate == 0.0
    assert summary.client_error_rate == 0.0
    assert summary.server_error_rate == 0.0
    assert summary.problematic_endpoints == []
