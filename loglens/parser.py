import re
from datetime import datetime
from pathlib import Path
from typing import TextIO, Union
from pydantic import ValidationError

from loglens.models import LogEntry, LogLevel

LOG_REGEX = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(\w+)\s+(\w+)\s+(\S+)\s+(\d{3})$"
)


def parse_log_stream(stream: TextIO) -> tuple[list[LogEntry], int, int, int]:
    entries: list[LogEntry] = []
    total_lines = 0
    parsed_lines = 0
    skipped_lines = 0

    for line in stream:
        total_lines += 1
        line_str = line.strip()
        if not line_str:
            skipped_lines += 1
            continue

        match = LOG_REGEX.match(line_str)
        if not match:
            skipped_lines += 1
            continue

        timestamp_str, level_str, method_str, endpoint_str, status_code_str = match.groups()

        try:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            entry = LogEntry(
                timestamp=timestamp,
                level=LogLevel(level_str),
                method=method_str,
                endpoint=endpoint_str,
                status_code=int(status_code_str),
            )
            entries.append(entry)
            parsed_lines += 1
        except (ValueError, ValidationError):
            skipped_lines += 1

    return entries, total_lines, parsed_lines, skipped_lines


def parse_log_file(file_path: Union[str, Path]) -> tuple[list[LogEntry], int, int, int]:
    path = Path(file_path)
    if not path.exists():
        return [], 0, 0, 0

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return parse_log_stream(f)
