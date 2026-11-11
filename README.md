<div align="center">

# FixAtlas

### Evidence-first diagnostics for developer errors.

**Understand the failure. Check the evidence. Choose the fix.**

[![CI](https://github.com/Vxn1r/fixatlas-dev/actions/workflows/ci.yml/badge.svg)](https://github.com/Vxn1r/fixatlas-dev/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Stars](https://img.shields.io/github/stars/Vxn1r/fixatlas-dev?style=social)](https://github.com/Vxn1r/fixatlas-dev/stargazers)
[![Forks](https://img.shields.io/github/forks/Vxn1r/fixatlas-dev?style=social)](https://github.com/Vxn1r/fixatlas-dev/network/members)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Offline](https://img.shields.io/badge/network-offline-brightgreen)](#privacy-first-by-design)
[![No telemetry](https://img.shields.io/badge/telemetry-none-brightgreen)](#privacy-first-by-design)
[![MCP](https://img.shields.io/badge/MCP-compatible-blueviolet)](docs/mcp-integration.md)

</div>

FixAtlas is an open-source, offline-first developer troubleshooting CLI. It recognizes known error signatures, explains likely causes, and gives diagnostic checks and carefully scoped next steps. It does **not** execute commands, upload logs, or pretend that a pattern match is a guaranteed fix.

> **Status:** 0.1.0 alpha. The initial rules are deliberately small and transparent. A matching rule is a lead to investigate—not proof that the root cause is confirmed.

## Why FixAtlas?

Debugging often means searching the same error across issue trackers, old forum answers, package docs, and AI chats. Those sources can be stale or mismatched to the current operating system, runtime, or package version.

FixAtlas is designed around four principles:

- **Evidence over guesses:** every diagnosis exposes the literal signals that matched.
- **Reproducibility:** rules are versioned JSON and can be reviewed, tested, and contributed to.
- **Local by default:** error text stays on your machine; the CLI makes no network calls.
- **Human-controlled changes:** FixAtlas recommends checks and next steps, but never runs shell commands for you.

## Quick start

Requires Python 3.10 or newer.

```bash
# From a source checkout
python -m pip install .

# Or install development dependencies while contributing
python -m pip install -e '.[dev]'
```

Pipe an error directly into FixAtlas:

```bash
npm install 2>&1 | fixatlas explain
```

Analyze a saved log:

```bash
fixatlas explain build.log
```

Get JSON for scripts and coding agents:

```bash
fixatlas explain build.log --json
```

Connect an MCP-compatible coding agent (optional; Python 3.11+):

```bash
python -m pip install 'fixatlas-cli[mcp]'
fixatlas mcp
```

See [MCP integration](docs/mcp-integration.md) for host configuration and tool details.

See available rules and search them:

```bash
fixatlas list
fixatlas search python
fixatlas search platform
```

Inspect the local runtime without network checks:

```bash
fixatlas doctor
fixatlas doctor --json
```

## Example

Input:

```text
npm ERR! code EBADPLATFORM
npm ERR! notsup Unsupported platform for example-native-addon
```

Output (abridged):

```text
[1] npm package is incompatible with this platform (npm-ebadplatform)
    Category: javascript / npm | Match: candidate
    What it means: npm rejected a package because its declared platform constraints...
    Likely cause: The package (or one of its dependencies) declares platform constraints...
    Matched signals: EBADPLATFORM
    Check:
      - Confirm the environment with node --version, npm --version, ...
      - Identify the exact package named near the EBADPLATFORM message...
    Suggested next steps:
      - Choose a package release that explicitly supports this operating system...
      - Avoid using --force as a first response...
```

The `candidate` label describes the number/type of literal signals matched. It is **not** a statistical confidence score.

## Built-in coverage (v0.1.0)

| Area | Initial signatures |
|---|---|
| npm | `EBADPLATFORM`, `ERESOLVE` |
| Python | `ModuleNotFoundError`, `ResolutionImpossible`, PEP 668 externally-managed environment |
| Git | not-a-repository, SSH public-key rejection |
| C / C++ | linker `undefined reference` |
| Gradle | dependency-resolution failure |

This is an intentionally modest starter set. It is not a complete database of developer errors.

## Commands

| Command | Purpose |
|---|---|
| `fixatlas explain [FILE]` | Analyze a UTF-8 file; omit FILE or use `-` for stdin |
| `fixatlas explain FILE --json` | Emit structured JSON |
| `fixatlas list` | List the available rules |
| `fixatlas search WORDS...` | Search rule IDs, titles, categories, and summaries |
| `fixatlas validate-registry FILE` | Validate a custom rule database |
| `fixatlas doctor` | Show local runtime details; no network diagnostics |
| `fixatlas mcp` | Start the optional local MCP stdio server (Python 3.11+) |
| `fixatlas --version` | Print the installed version |

Exit codes: `0` means analysis completed with at least one match; `1` means no rule matched or a search returned no result; `2` means invalid input or a registry/IO error.

## Custom rule registries

A custom registry can be passed to `explain`, `list`, or `search`:

```bash
fixatlas validate-registry ./my-rules.json
fixatlas explain build.log --registry ./my-rules.json
```

The format is documented in [docs/rule-format.md](docs/rule-format.md). Keep rules specific. Prefer exact error strings and multiple required signals over vague words such as `error` or `failed`.

## Privacy-first by design

- No telemetry, analytics, background services, or automatic updates.
- No network requests are made by the CLI.
- Input logs are analyzed in memory and are not written to disk.
- JSON output contains match metadata and input length, not the original log contents.
- The CLI enforces a 200,000-character input limit.

Logs can contain access tokens, private URLs, usernames, file paths, and other sensitive data. Sanitize logs before sharing them in public issues. Do not paste private keys, credentials, or production secrets into bug reports.

## Agent ecosystem

FixAtlas ships reusable instructions alongside the CLI and MCP server:

- [Diagnostician agent](agents/fixatlas-diagnostician.md): a focused diagnostic role with evidence, verification, and privacy boundaries.
- [Diagnose-error skill](skills/diagnose-error/SKILL.md): a reusable workflow for coding agents.
- [Diagnostic safety rules](rules/diagnostic-safety.md): project-wide principles for safe troubleshooting.
- [Local stdio MCP config](mcp-configs/local-stdio.example.json): a generic example for MCP hosts.

These are instructions and configuration examples, not autonomous repair hooks. FixAtlas deliberately does not capture logs or run suggested commands automatically.

## Roadmap

- [x] Offline CLI and deterministic rule engine
- [x] JSON output for tools and agent integrations
- [x] Custom rule registry and validation
- [x] Unit and command-line tests
- [x] Cross-platform CI workflow
- [ ] Community-reviewed rule submissions with reproducible test fixtures
- [x] Optional SDK-backed MCP server for coding-agent clients (stdio)
- [ ] IDE/editor integrations
- [ ] Version-aware diagnosis and package metadata snapshots
- [ ] Optional local project context (lockfiles, runtimes, build manifests)

Roadmap items are plans, not current capabilities. See [CHANGELOG.md](CHANGELOG.md) for shipped changes.

## Contributing

We welcome focused, reproducible rules and fixes. Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Every new rule should include:

1. A narrow signature (not a generic error word).
2. A minimal, sanitized example fixture.
3. A plain-language explanation and diagnostic checks.
4. Conservative next steps that do not hide the underlying problem.
5. Official documentation references where available.
6. Automated tests for positive and negative matches.

## Project metadata

Suggested GitHub repository topics for the current feature set: `ai-agents`, `developer-tools`, `mcp`, `productivity`, `debugging`, `troubleshooting`, `error-diagnostics`, `cli`, `python`, `offline`, `llm`, `open-source`, `developer-experience`. These are suggested metadata values; they must still be applied in GitHub repository settings.

See [docs/project-governance.md](docs/project-governance.md) for repository conventions and release policy. Maintainers can bootstrap GitHub topics, labels, and repository settings with [scripts/bootstrap_github.sh](scripts/bootstrap_github.sh); see [the publishing guide](docs/publish-to-github.md).

## License

MIT. See [LICENSE](LICENSE).
