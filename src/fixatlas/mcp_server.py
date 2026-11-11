"""Optional MCP server exposing FixAtlas diagnostics to coding agents.

This module imports the MCP SDK lazily so the base FixAtlas installation remains
zero-dependency. Install ``fixatlas-cli[mcp]`` on Python 3.11+ to enable it.
"""

from __future__ import annotations

from fixatlas import __version__
from fixatlas.agent_tools import explain_error, list_rules, search_rules, tool_capabilities


def create_server():
    """Create the official-SDK MCP server and register read-only tools."""
    try:
        from mcp.server import MCPServer
    except ImportError as exc:
        raise RuntimeError(
            "The optional MCP integration is not installed. On Python 3.11+, run "
            "`python -m pip install 'fixatlas-cli[mcp]'`."
        ) from exc

    server = MCPServer(
        "FixAtlas",
        title="FixAtlas Developer Diagnostics",
        description="Offline, evidence-first diagnostics for common developer errors.",
        instructions=(
            "Use FixAtlas to identify known developer error signatures. Explain that matches "
            "are diagnostic leads, not guaranteed fixes. Never claim a command was run. "
            "FixAtlas tools are read-only: they do not execute commands, access the network, "
            "or transmit the user's log text. Ask the user before recommending any "
            "destructive change."
        ),
        version=__version__,
    )
    server.tool(
        name="fixatlas_explain",
        title="Explain a developer error",
        description=(
            "Analyze pasted error text against FixAtlas's local rule database. Returns matched "
            "signals, likely causes, diagnostic checks, conservative next steps, and references. "
            "Never executes commands or sends the text over the network."
        ),
    )(explain_error)
    server.tool(
        name="fixatlas_search_rules",
        title="Search diagnostic rules",
        description="Search local FixAtlas rules by ID, title, category, or summary.",
    )(search_rules)
    server.tool(
        name="fixatlas_list_rules",
        title="List diagnostic rules",
        description="List local FixAtlas rules, optionally filtered by category.",
    )(list_rules)
    server.tool(
        name="fixatlas_capabilities",
        title="Describe FixAtlas capabilities",
        description="Return FixAtlas version, limits, privacy properties, and available tools.",
    )(tool_capabilities)
    return server


def run_server() -> None:
    """Run the MCP server over standard input/output."""
    create_server().run()
