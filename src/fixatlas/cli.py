"""Command-line interface for FixAtlas."""

from __future__ import annotations

import argparse
import json
import platform
import sys
from collections.abc import Sequence
from pathlib import Path

from fixatlas import __version__
from fixatlas.engine import MAX_INPUT_CHARS, InputTooLargeError, analyze
from fixatlas.registry import RegistryError, load_registry


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fixatlas",
        description="Evidence-first, offline diagnostics for common developer errors.",
        epilog="FixAtlas never executes suggested commands or uploads your logs.",
    )
    parser.add_argument("--version", action="version", version=f"FixAtlas {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    explain = subparsers.add_parser("explain", help="Analyze an error log or piped text")
    explain.add_argument(
        "source",
        nargs="?",
        default="-",
        help="Path to a UTF-8 log file; use '-' for stdin (default)",
    )
    explain.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    explain.add_argument("--registry", help="Use a custom local JSON rule registry")

    search = subparsers.add_parser("search", help="Search rule titles, categories and summaries")
    search.add_argument("query", nargs="+", help="Words to search for")
    search.add_argument("--registry", help="Use a custom local JSON rule registry")

    listing = subparsers.add_parser("list", help="List all bundled diagnostic rules")
    listing.add_argument("--registry", help="Use a custom local JSON rule registry")

    validate = subparsers.add_parser("validate-registry", help="Validate a local rule database")
    validate.add_argument("path", help="Path to a FixAtlas registry JSON file")

    doctor = subparsers.add_parser("doctor", help="Show local runtime details (no network checks)")
    doctor.add_argument("--json", action="store_true", help="Print machine-readable JSON")

    subparsers.add_parser(
        "mcp",
        help="Run the optional Model Context Protocol server over stdio (Python 3.11+)",
    )
    return parser


def _read_source(source: str) -> str:
    if source == "-":
        if sys.stdin.isatty():
            raise ValueError(
                "No input received. Pass a log file or pipe text into `fixatlas explain`."
            )
        text = sys.stdin.read(MAX_INPUT_CHARS + 1)
    else:
        path = Path(source).expanduser()
        try:
            size = path.stat().st_size
        except OSError as exc:
            raise ValueError(f"Cannot access input file {path}: {exc}") from exc
        if size > MAX_INPUT_CHARS * 4:
            raise InputTooLargeError("Input file is larger than the 4x byte safety limit")
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise ValueError(f"Cannot read {path} as UTF-8: {exc}") from exc
    if len(text) > MAX_INPUT_CHARS:
        raise InputTooLargeError(
            f"Input exceeds the {MAX_INPUT_CHARS:,}-character analysis limit; "
            "trim the log and retry"
        )
    return text


def _render_explain(matches: list, source_label: str) -> None:
    print(f"FixAtlas {__version__}  |  source: {source_label}  |  offline analysis")
    if not matches:
        print("\nNo matching rule found.")
        print(
            "This does not mean the error is harmless; the current rule set "
            "may not cover it yet."
        )
        print("Contribute a minimal, sanitized example at the project's issue tracker.")
        return
    for number, match in enumerate(matches, start=1):
        rule = match.rule
        print(f"\n[{number}] {rule.title}  ({rule.id})")
        print(f"    Category: {rule.category} | Match: {match.strength}")
        print(f"    What it means: {rule.summary}")
        print(f"    Likely cause: {rule.root_cause}")
        if match.matched_signals:
            print("    Matched signals: " + "; ".join(match.matched_signals))
        print("    Check:")
        for item in rule.checks:
            print(f"      - {item}")
        print("    Suggested next steps:")
        for item in rule.actions:
            print(f"      - {item}")
        print(f"    Verification status: {rule.verification}")
        for reference in rule.references:
            print(f"    Reference: {reference['label']} — {reference['url']}")
    print("\nSafety: suggestions are advisory. Review commands before running them.")


def _run_explain(args: argparse.Namespace) -> int:
    text = _read_source(args.source)
    rules = load_registry(args.registry)
    matches = analyze(text, rules)
    if args.json:
        print(
            json.dumps(
                {
                    "tool": "fixatlas",
                    "version": __version__,
                    "registry_schema_version": 1,
                    "source": "stdin" if args.source == "-" else "file",
                    "input_characters": len(text),
                    "network_access": False,
                    "matches": [match.to_dict() for match in matches],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        _render_explain(matches, "stdin" if args.source == "-" else args.source)
    return 0 if matches else 1


def _run_search(args: argparse.Namespace) -> int:
    rules = load_registry(args.registry)
    query = " ".join(args.query).casefold()
    found = [
        rule
        for rule in rules
        if query in " ".join((rule.id, rule.title, rule.category, rule.summary)).casefold()
    ]
    if not found:
        print(f"No rules found for: {query}")
        return 1
    for rule in found:
        print(f"{rule.id:30} {rule.title} [{rule.category}]")
        print(f"  {rule.summary}")
    return 0


def _run_list(args: argparse.Namespace) -> int:
    rules = load_registry(args.registry)
    print(f"FixAtlas diagnostic rules ({len(rules)})")
    for rule in rules:
        print(f"{rule.id:30} {rule.title} [{rule.category}]")
    return 0


def _run_validate(args: argparse.Namespace) -> int:
    rules = load_registry(args.path)
    print(f"Valid registry: {args.path} ({len(rules)} rules, schema v1)")
    return 0


def _run_doctor(as_json: bool) -> int:
    details = {
        "fixatlas_version": __version__,
        "python_version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "operating_system": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "network_checks": "not performed",
        "telemetry": "disabled",
    }
    if as_json:
        print(json.dumps(details, indent=2))
    else:
        print("FixAtlas local runtime diagnostics")
        for key, value in details.items():
            print(f"{key.replace('_', ' ').title():22} {value}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "explain":
            return _run_explain(args)
        if args.command == "search":
            return _run_search(args)
        if args.command == "list":
            return _run_list(args)
        if args.command == "validate-registry":
            return _run_validate(args)
        if args.command == "doctor":
            return _run_doctor(args.json)
        if args.command == "mcp":
            if sys.version_info < (3, 11):
                raise RuntimeError("The MCP integration requires Python 3.11 or newer")
            from fixatlas.mcp_server import run_server

            run_server()
            return 0
    except (RegistryError, InputTooLargeError, ValueError, RuntimeError) as exc:
        print(f"fixatlas: error: {exc}", file=sys.stderr)
        return 2
    return 2
