from datetime import datetime
import pytest
from pydantic import ValidationError
from loglens.models import LogLevel, LogEntry, EndpointStats, LogSummary


def test_valid_log_entry():
    entry = LogEntry(
        timestamp=datetime(2026, 11, 15, 10, 0, 1),
        level=LogLevel.INFO,
        method="GET",
        endpoint="/api/users",
        status_code=200,
    )
    assert entry.level == LogLevel.INFO
    assert entry.method == "GET"
    assert entry.endpoint == "/api/users"
    assert entry.status_code == 200


def test_invalid_log_level():
    with pytest.raises(ValidationError):
        LogEntry(
            timestamp=datetime(2026, 11, 15, 10, 0, 1),
            level="INVALID",  # type: ignore
            method="GET",
            endpoint="/api/users",
            status_code=200,
        )


def test_invalid_http_method():
    with pytest.raises(ValidationError) as exc_info:
        LogEntry(
            timestamp=datetime(2026, 11, 15, 10, 0, 1),
            level=LogLevel.INFO,
            method="TRACE",
            endpoint="/api/users",
            status_code=200,
        )
    assert "Invalid HTTP method" in str(exc_info.value)


def test_invalid_status_code():
    with pytest.raises(ValidationError):
        LogEntry(
            timestamp=datetime(2026, 11, 15, 10, 0, 1),
            level=LogLevel.INFO,
            method="GET",
            endpoint="/api/users",
            status_code=99,
        )

    with pytest.raises(ValidationError):
        LogEntry(
            timestamp=datetime(2026, 11, 15, 10, 0, 1),
            level=LogLevel.INFO,
            method="GET",
            endpoint="/api/users",
            status_code=600,
        )


def test_empty_endpoint():
    with pytest.raises(ValidationError) as exc_info:
        LogEntry(
            timestamp=datetime(2026, 11, 15, 10, 0, 1),
            level=LogLevel.INFO,
            method="GET",
            endpoint="   ",
            status_code=200,
        )
    assert "Endpoint cannot be empty" in str(exc_info.value)


def test_valid_log_summary():
    summary = LogSummary(
        total_lines=10,
        parsed_lines=10,
        skipped_lines=0,
        total_requests=10,
        severity_counts={"INFO": 8, "WARNING": 1, "ERROR": 1},
        status_code_counts={200: 8, 400: 1, 500: 1},
        client_error_count=1,
        server_error_count=1,
        overall_error_rate=0.2,
        client_error_rate=0.1,
        server_error_rate=0.1,
        problematic_endpoints=[
            EndpointStats(
                endpoint="/api/orders",
                total_requests=2,
                error_count=2,
                client_error_count=1,
                server_error_count=1,
            )
        ],
    )
    assert summary.total_lines == 10
    assert summary.overall_error_rate == 0.2
    assert len(summary.problematic_endpoints) == 1


def test_empty_summary_zero_error_rates():
    summary = LogSummary()
    assert summary.total_lines == 0
    assert summary.overall_error_rate == 0.0
    assert summary.client_error_rate == 0.0
    assert summary.server_error_rate == 0.0
    assert summary.problematic_endpoints == []
