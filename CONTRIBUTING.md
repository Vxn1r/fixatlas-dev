# Contributing to FixAtlas

Thank you for helping make developer troubleshooting more accurate and reproducible.

## Ground rules

- Be respectful, specific, and constructive.
- Do not submit secrets, credentials, private logs, or personal data.
- Do not add a rule that recommends destructive commands as a default fix.
- Never describe a signature match as proof that a diagnosis is correct.

## Development setup

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
pytest
ruff check .
ruff format --check .
```

## Adding a diagnostic rule

1. Find a narrowly identifying error signature and an official reference.
2. Add the rule to `src/fixatlas/data/rules.json`.
3. Include diagnostic checks that help distinguish similar causes.
4. Recommend the least risky next steps first. Do not suggest bypass flags as the default.
5. Add positive and negative tests. A vague message must not trigger the rule.
6. Run `fixatlas validate-registry src/fixatlas/data/rules.json` and the full test suite.

Rules must not require network access to match. Avoid broad strings such as `error`, `failed`, or `not found` unless paired with more specific signals.

## Pull requests

- Keep changes focused and explain the user problem being solved.
- Include tests and documentation for behavior changes.
- Do not commit generated build artifacts, local environments, or real logs.
- Use clear commit messages (for example, `feat: add pip resolver rule`).

## Security issues

Do not report vulnerabilities in public issues. Follow [SECURITY.md](SECURITY.md).
