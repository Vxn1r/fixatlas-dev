# Instructions for AI coding agents working on FixAtlas

## Non-negotiable project principles

- Keep the CLI deterministic and offline by default.
- Never upload raw logs, add telemetry, or persist supplied error text without explicit design review.
- Never execute a suggested shell command or modify a user's environment automatically.
- Treat every diagnosis as a hypothesis; preserve matched evidence and recommend checks that can disprove it.
- Prefer literal, specific signatures. Add negative tests for nearby errors.
- Do not invent verification claims or present a signature match as a probability.

## Before changing code

1. Read `docs/architecture.md` and `docs/rule-format.md`.
2. Identify compatibility requirements (Python 3.10+ core; optional MCP extra on Python 3.11+).
3. Add or update tests before modifying user-visible behavior.

## Required checks

```bash
python -m pytest
ruff check .
ruff format --check .
fixatlas validate-registry src/fixatlas/data/rules.json
python -m build
```

## Scope control

- Keep core runtime dependencies at zero. Optional integrations must be lazy-loaded and clearly documented.
- Do not add network access to the core engine.
- Do not add automatic remediation in the 0.x series.
- Update README, docs, and CHANGELOG when behavior or interfaces change.
