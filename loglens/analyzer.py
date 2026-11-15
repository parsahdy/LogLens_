from collections import defaultdict
from typing import Sequence
from loglens.models import LogEntry, LogSummary, EndpointStats, LogLevel


def analyze_logs(
    entries: Sequence[LogEntry],
    total_lines: int,
    parsed_lines: int,
    skipped_lines: int,
) -> LogSummary:
    total_requests = len(entries)

    severity_counts: dict[str, int] = {
        LogLevel.INFO.value: 0,
        LogLevel.WARNING.value: 0,
        LogLevel.ERROR.value: 0,
    }
    status_code_counts: dict[int, int] = {}
    client_error_count = 0
    server_error_count = 0

    endpoint_data = defaultdict(lambda: {"total": 0, "client_err": 0, "server_err": 0})

    for entry in entries:
        level_str = entry.level.value if isinstance(entry.level, LogLevel) else str(entry.level)
        severity_counts[level_str] = severity_counts.get(level_str, 0) + 1

        status_code_counts[entry.status_code] = status_code_counts.get(entry.status_code, 0) + 1

        endpoint_data[entry.endpoint]["total"] += 1

        if 400 <= entry.status_code < 500:
            client_error_count += 1
            endpoint_data[entry.endpoint]["client_err"] += 1
        elif 500 <= entry.status_code < 600:
            server_error_count += 1
            endpoint_data[entry.endpoint]["server_err"] += 1

    total_errors = client_error_count + server_error_count

    overall_error_rate = (total_errors / total_requests) if total_requests > 0 else 0.0
    client_error_rate = (client_error_count / total_requests) if total_requests > 0 else 0.0
    server_error_rate = (server_error_count / total_requests) if total_requests > 0 else 0.0

    problematic_endpoints: list[EndpointStats] = []
    for ep, stats in endpoint_data.items():
        err_cnt = stats["client_err"] + stats["server_err"]
        if err_cnt > 0:
            problematic_endpoints.append(
                EndpointStats(
                    endpoint=ep,
                    total_requests=stats["total"],
                    error_count=err_cnt,
                    client_error_count=stats["client_err"],
                    server_error_count=stats["server_err"],
                )
            )

    problematic_endpoints.sort(key=lambda x: (-x.error_count, -x.total_requests, x.endpoint))

    return LogSummary(
        total_lines=total_lines,
        parsed_lines=parsed_lines,
        skipped_lines=skipped_lines,
        total_requests=total_requests,
        severity_counts=severity_counts,
        status_code_counts=status_code_counts,
        client_error_count=client_error_count,
        server_error_count=server_error_count,
        overall_error_rate=round(overall_error_rate, 4),
        client_error_rate=round(client_error_rate, 4),
        server_error_rate=round(server_error_rate, 4),
        problematic_endpoints=problematic_endpoints,
    )
