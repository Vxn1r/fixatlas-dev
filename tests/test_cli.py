from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def run_cli(*args: str, input_text: str | None = None):
    return subprocess.run(
        [sys.executable, "-m", "fixatlas", *args],
        input=input_text,
        text=True,
        capture_output=True,
        cwd=ROOT,
        env=ENV,
        check=False,
    )


def test_explain_reads_stdin_and_matches_rule():
    result = run_cli("explain", input_text="npm ERR! code EBADPLATFORM")
    assert result.returncode == 0
    assert "npm-ebadplatform" in result.stdout
    assert "offline analysis" in result.stdout


def test_explain_json_is_machine_readable():
    result = run_cli("explain", "--json", input_text="ModuleNotFoundError: No module named 'x'")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["network_access"] is False
    assert payload["matches"][0]["id"] == "python-module-not-found"


def test_explain_returns_one_for_unknown_error():
    result = run_cli("explain", input_text="A made-up error with no known signature")
    assert result.returncode == 1
    assert "No matching rule found" in result.stdout


def test_list_and_search():
    listed = run_cli("list")
    searched = run_cli("search", "platform")
    assert listed.returncode == 0
    assert "npm-ebadplatform" in listed.stdout
    assert searched.returncode == 0
    assert "npm-ebadplatform" in searched.stdout


def test_doctor_json_has_no_network_claim():
    result = run_cli("doctor", "--json")
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["network_checks"] == "not performed"
    assert payload["telemetry"] == "disabled"


def test_missing_input_file_is_a_clear_error():
    result = run_cli("explain", "does-not-exist.log")
    assert result.returncode == 2
    assert "Cannot access input file" in result.stderr


def test_version_flag():
    result = run_cli("--version")
    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_validate_registry_command():
    result = run_cli("validate-registry", "src/fixatlas/data/rules.json")
    assert result.returncode == 0
    assert "9 rules" in result.stdout


def test_explain_reads_file(tmp_path):
    log = tmp_path / "build.log"
    log.write_text("fatal: not a git repository", encoding="utf-8")
    result = run_cli("explain", str(log))
    assert result.returncode == 0
    assert "git-not-repository" in result.stdout
