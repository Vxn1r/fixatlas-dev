from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_mcp_configuration_example_is_valid_and_uses_local_stdio():
    payload = json.loads((ROOT / "mcp-configs" / "local-stdio.example.json").read_text())
    entry = payload["mcpServers"]["fixatlas"]
    assert entry["command"] == "fixatlas"
    assert entry["args"] == ["mcp"]


def test_agent_skill_has_required_frontmatter_and_workflow():
    content = (ROOT / "skills" / "diagnose-error" / "SKILL.md").read_text()
    assert content.startswith("---\n")
    frontmatter = content.split("---\n", 2)[1]
    assert "name: fixatlas-diagnose-error" in frontmatter
    assert "description:" in frontmatter
    assert "## Workflow" in content
    assert "Wait for approval" in content


def test_diagnostician_agent_preserves_privacy_and_user_control():
    content = (ROOT / "agents" / "fixatlas-diagnostician.md").read_text()
    assert "Never claim FixAtlas ran a command" in content
    assert "Do not upload, persist, or repeat raw logs" in content
    assert "request user approval" in content


def test_github_bootstrap_script_is_safe_and_repeatable():
    content = (ROOT / "scripts" / "bootstrap_github.sh").read_text()
    assert "gh auth status" in content
    assert "git remote get-url origin" in content
    assert "git push origin v0.1.0" in content
    assert "--add-topic ai-agents" in content
    assert 'gh label create "$name"' in content
    assert 'fail "origin points to' in content
