import argparse
import sys
from pathlib import Path
from loglens.parser import parse_log_file
from loglens.analyzer import analyze_logs
from loglens.reporter import generate_json, generate_markdown


def main(argv=None):
    parser = argparse.ArgumentParser(description="LogLens: Lightweight application log analyzer")
    parser.add_argument("logfile", type=Path, help="Path to the log file to analyze")
    parser.add_argument("--json", type=Path, help="Path to write JSON report")
    parser.add_argument("--markdown", "--md", type=Path, help="Path to write Markdown report")

    args = parser.parse_args(argv)

    if not args.logfile.exists():
        print(f"Error: Log file not found: {args.logfile}", file=sys.stderr)
        sys.exit(1)

    entries, total_lines, parsed_lines, skipped_lines = parse_log_file(args.logfile)
    summary = analyze_logs(entries, total_lines, parsed_lines, skipped_lines)

    json_report = generate_json(summary)
    md_report = generate_markdown(summary)

    if args.json:
        args.json.write_text(json_report, encoding="utf-8")
        print(f"JSON report written to {args.json}")

    if args.markdown:
        args.markdown.write_text(md_report, encoding="utf-8")
        print(f"Markdown report written to {args.markdown}")

    if not args.json and not args.markdown:
        print(md_report)


if __name__ == "__main__":
    main()
