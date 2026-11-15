import json
from pathlib import Path
from loglens.parser import parse_log_file
from loglens.analyzer import analyze_logs
from loglens.reporter import generate_json, generate_markdown
from loglens.cli import main


def test_end_to_end_pipeline(tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text(
        "2026-11-15 10:00:01 INFO GET /api/users 200\n"
        "2026-11-15 10:00:02 WARNING GET /api/users 404\n"
        "2026-11-15 10:00:03 ERROR POST /api/orders 500\n"
        "INVALID LINE\n"
        "2026-11-15 10:00:04 ERROR POST /api/orders 502\n",
        encoding="utf-8",
    )

    # 1. Parse
    entries, total_lines, parsed_lines, skipped_lines = parse_log_file(log_file)
    assert total_lines == 5
    assert parsed_lines == 4
    assert skipped_lines == 1

    # 2. Analyze
    summary = analyze_logs(entries, total_lines, parsed_lines, skipped_lines)
    assert summary.total_requests == 4
    assert summary.severity_counts == {"INFO": 1, "WARNING": 1, "ERROR": 2}
    assert summary.client_error_count == 1
    assert summary.server_error_count == 2
    assert summary.overall_error_rate == 0.75

    # 3. Report
    json_rep = generate_json(summary)
    md_rep = generate_markdown(summary)

    parsed_json = json.loads(json_rep)
    assert parsed_json["total_requests"] == 4
    assert "# LogLens Analysis Report" in md_rep
    assert "/api/orders" in md_rep


def test_cli_execution(tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text(
        "2026-11-15 10:00:01 INFO GET /api/users 200\n"
        "2026-11-15 10:00:02 ERROR GET /api/orders 500\n",
        encoding="utf-8",
    )
    json_out = tmp_path / "report.json"
    md_out = tmp_path / "report.md"

    main([str(log_file), "--json", str(json_out), "--markdown", str(md_out)])

    assert json_out.exists()
    assert md_out.exists()

    data = json.loads(json_out.read_text(encoding="utf-8"))
    assert data["total_requests"] == 2
    assert data["server_error_count"] == 1

    md_content = md_out.read_text(encoding="utf-8")
    assert "# LogLens Analysis Report" in md_content
    assert "/api/orders" in md_content
