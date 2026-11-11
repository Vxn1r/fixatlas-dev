from __future__ import annotations

import sys

import pytest

from fixatlas.agent_tools import explain_error, list_rules, search_rules, tool_capabilities


def test_agent_explain_returns_evidence_without_echoing_input():
    secret_like_log = "npm ERR! code EBADPLATFORM\nTOKEN=do-not-repeat-this"
    result = explain_error(secret_like_log)
    assert result["network_access"] is False
    assert result["input_characters"] == len(secret_like_log)
    assert result["matches"][0]["id"] == "npm-ebadplatform"
    assert "do-not-repeat-this" not in repr(result)


def test_agent_explain_returns_explicit_no_match_result():
    result = explain_error("unrecognized sample error")
    assert result["matches"] == []
    assert "No bundled rule matched" in result["message"]


def test_agent_search_is_case_insensitive():
    result = search_rules("PYTHON")
    assert result["count"] >= 2
    assert all("python" in rule["category"] for rule in result["rules"])


def test_agent_search_rejects_empty_query():
    with pytest.raises(ValueError, match="non-empty"):
        search_rules("  ")


def test_agent_list_can_filter_by_category():
    result = list_rules("git")
    assert result["count"] == 2
    assert all("git" in rule["category"].casefold() for rule in result["rules"])


def test_agent_capabilities_are_read_only_and_offline():
    result = tool_capabilities()
    assert result["network_access"] is False
    assert result["telemetry"] is False
    assert result["executes_commands"] is False
    assert "fixatlas_explain" in result["tools"]


def test_mcp_server_registers_tools_when_optional_sdk_is_installed():
    pytest.importorskip("mcp")
    from fixatlas.mcp_server import create_server

    server = create_server()
    assert server.name == "FixAtlas"
    assert server.version


def test_mcp_server_gives_install_instructions_when_sdk_is_missing(monkeypatch):
    monkeypatch.setitem(sys.modules, "mcp.server", None)
    from fixatlas.mcp_server import create_server

    with pytest.raises(RuntimeError, match="optional MCP integration is not installed"):
        create_server()
