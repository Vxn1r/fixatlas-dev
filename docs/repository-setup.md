# GitHub repository setup checklist

This file records settings that cannot be represented by repository files alone.

## Create the repository

Suggested repository: `Vxn1r/fixatlas-dev`

- Visibility: Public
- Description: `Evidence-first, offline developer error diagnostics for humans and coding agents.`
- Website: leave blank until a real project website exists
- Initialize with README: **No** (this source tree already contains one)
- License: **MIT** (already included)

## Topics

Apply these topics in the repository's About panel:

`ai-agents`, `developer-tools`, `mcp`, `productivity`, `debugging`, `troubleshooting`, `error-diagnostics`, `cli`, `python`, `offline`, `llm`, `open-source`, `developer-experience`.

## Issues, discussions, and pull requests

- Keep Issues enabled.
- Enable Discussions for Announcements, Q&A, Ideas, and Show and tell.
- Keep pull requests enabled and use the included templates.
- Add labels: `bug`, `documentation`, `enhancement`, `good first issue`, `help wanted`, `needs-triage`, `rule:new`, `tests`.

## Branch protection for `main`

After CI has run once, protect `main`:

- Require a pull request before merging.
- Require the CI test jobs to pass.
- Require conversation resolution.
- Disable force pushes and branch deletion.
- Prefer squash merging.

## Security and automation

- Enable Dependabot alerts and security updates.
- Enable the dependency graph and CodeQL code scanning.
- Enable private vulnerability reporting when available.
- Keep GitHub Actions default token permissions read-only; individual workflows request only the permissions they need.

These are setup instructions, not settings already applied to a live repository.
