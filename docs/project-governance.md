# Project governance and repository conventions

## Repository identity

- Product: FixAtlas
- Suggested repository: `Vxn1r/fixatlas-dev`
- Package name: `fixatlas-cli`
- Command: `fixatlas`
- License: MIT

## Suggested GitHub topics

`ai-agents`, `developer-tools`, `mcp`, `productivity`, `debugging`, `troubleshooting`, `error-diagnostics`, `cli`, `python`, `offline`, `llm`, `open-source`, `developer-experience`.

Topics are metadata to apply in GitHub repository settings after the repository is created; listing them here does not apply them automatically.

## Branch and review policy

- `main` is the stable default branch.
- Use short-lived branches for changes.
- Require CI to pass before merging.
- Prefer small PRs with tests and documentation.
- Tag releases as `vMAJOR.MINOR.PATCH`.

## Release policy

- Keep `CHANGELOG.md` updated.
- Run the full test and lint suite.
- Build both wheel and source distribution.
- Publish a release only after reviewing generated artifacts and version metadata.
- Do not claim PyPI publication until a release workflow has actually completed.
