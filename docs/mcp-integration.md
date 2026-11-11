# MCP integration

FixAtlas can expose read-only diagnostic tools to MCP-compatible coding agents through the official MCP Python SDK (v2). The core CLI remains dependency-free; MCP is an optional extra and requires Python 3.11 or newer.

## Install

```bash
python -m pip install 'fixatlas-cli[mcp]'
```

## Run over stdio

```bash
fixatlas mcp
```

Configure your MCP host to launch the command as a local stdio server. Stdio is the SDK default for local subprocess servers. A common configuration shape is:

```json
{
  "mcpServers": {
    "fixatlas": {
      "command": "fixatlas",
      "args": ["mcp"]
    }
  }
}
```

Restart the MCP host after saving its configuration. The exact config-file location depends on the host; follow its official documentation.

## Exposed tools

| Tool | Purpose |
|---|---|
| `fixatlas_explain` | Match error text against local rules and return signals, explanations, checks, next steps, and references |
| `fixatlas_search_rules` | Search rule IDs, titles, categories, and summaries |
| `fixatlas_list_rules` | List rules, optionally filtered by category |
| `fixatlas_capabilities` | Report version, limits, and privacy properties |

## Trust and safety model

- Tools are read-only and deterministic; they do not execute shell commands.
- Error text is analyzed in-process. The FixAtlas server does not make network requests or send logs to a remote service.
- The server does not access the project filesystem beyond its bundled rule database.
- A match is a diagnostic lead, not a verified root cause or guaranteed repair.
- Coding agents should show proposed commands to the user and obtain approval before running them, especially for destructive or environment-changing operations.

The MCP SDK uses stdio transport by default for local server processes. This integration does not expose an HTTP endpoint.
