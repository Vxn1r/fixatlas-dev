---
name: fixatlas-diagnose-error
description: Diagnose compiler, package-manager, runtime, Git, and build errors with FixAtlas evidence. Use when a developer shares an error message, build log, stack trace, or failed command output.
---

# Diagnose a developer error with FixAtlas

## Goal

Use the local FixAtlas rule registry to produce a short, evidence-backed diagnosis without automatically executing a repair.

## Workflow

1. **Minimize the input.** Use the smallest relevant error excerpt. Ask the user to remove tokens, passwords, private URLs, usernames, and unrelated log output before sharing it.
2. **Prefer MCP.** If the FixAtlas MCP server is connected, call `fixatlas_explain` with the excerpt. Otherwise, explain how the user can run `fixatlas explain <log-file> --json` locally. Do not assume the CLI is installed.
3. **Read the evidence.** Inspect `matched_signals`, `match_strength`, `root_cause`, `checks`, `actions`, `references`, and `verification`.
4. **Check context.** Ask for the relevant OS, architecture, runtime, package-manager, and version information only when it changes the diagnosis.
5. **Explain uncertainty.** A match is not a confirmed root cause. If no rule matches, say coverage is missing and do not guess a fix.
6. **Propose safe next steps.** Start with read-only inspection and reversible changes. Explain what every proposed command does.
7. **Wait for approval.** Do not run commands, edit files, upgrade/downgrade packages, or alter permissions without explicit user approval.
8. **Verify.** After the user approves and performs a change, ask for the relevant result and distinguish a passing test from an assumed resolution.

## Output format

- **Likely cause:** one or two sentences, qualified by the evidence.
- **Why:** the exact signal(s) that matched.
- **Check first:** a short list of diagnostic checks.
- **Suggested next step:** the least invasive action first, with risks noted.
- **Verification:** the test or command output that would confirm the result.

## Constraints

- Never claim a command was executed unless the host confirms it.
- Never describe a match label as a probability.
- Never recommend disabling security protections, bypassing dependency constraints, or force-changing package state as the default.
- Never repeat or store the raw log beyond the current diagnostic task.
