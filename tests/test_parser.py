import io
from datetime import datetime
import pytest

from loglens.models import LogLevel
from loglens.parser import parse_log_stream, parse_log_file


def test_parse_log_stream_valid():
    content = (
        "2026-11-15 10:00:01 INFO GET /api/users 200\n"
        "2026-11-15 10:00:02 ERROR GET /api/orders 500\n"
    )
    stream = io.StringIO(content)
    entries, total, parsed, skipped = parse_log_stream(stream)

    assert total == 2
    assert parsed == 2
    assert skipped == 0
    assert len(entries) == 2
    assert entries[0].level == LogLevel.INFO
    assert entries[0].method == "GET"
    assert entries[0].endpoint == "/api/users"
    assert entries[0].status_code == 200


def test_parse_log_stream_with_malformed_and_empty_lines():
    content = (
        "\n"
        "2026-11-15 10:00:01 INFO GET /api/users 200\n"
        "INVALID LOG LINE FORMAT\n"
        "2026-11-15 10:00:02 TRACE GET /api/orders 500\n"  # Invalid log level / method
        "2026-11-15 10:00:03 WARNING POST /api/items 999\n"  # Invalid status code
        "2026-11-15 10:00:04 WARNING POST /api/items 201\n"
    )
    stream = io.StringIO(content)
    entries, total, parsed, skipped = parse_log_stream(stream)

    assert total == 6
    assert parsed == 2
    assert skipped == 4
    assert len(entries) == 2
    assert entries[0].endpoint == "/api/users"
    assert entries[1].endpoint == "/api/items"


def test_parse_log_file_non_existent(tmp_path):
    fake_file = tmp_path / "non_existent.log"
    entries, total, parsed, skipped = parse_log_file(fake_file)
    assert entries == []
    assert total == 0
    assert parsed == 0
    assert skipped == 0


def test_parse_log_file_valid(tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text(
        "2026-11-15 10:00:01 INFO GET /health 200\n"
        "2026-11-15 10:00:02 ERROR POST /api/pay 500\n",
        encoding="utf-8",
    )
    entries, total, parsed, skipped = parse_log_file(log_file)
    assert total == 2
    assert parsed == 2
    assert skipped == 0
    assert len(entries) == 2
