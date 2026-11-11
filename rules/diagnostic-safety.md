# FixAtlas diagnostic safety rules

These rules apply to the FixAtlas project and to agent integrations that use its output.

1. Diagnostics are hypotheses. Preserve the evidence and state uncertainty.
2. Prefer read-only checks before any environment-changing command.
3. Never auto-execute a suggested command or silently modify project files.
4. Request explicit user approval before running commands with side effects.
5. Never recommend broad permission changes, force installs, deletion, or security-control disabling as a first-line fix.
6. Keep logs local. Sanitize examples before filing issues or pull requests.
7. Do not collect telemetry or send diagnostic input to remote services.
8. New rules require official references, positive tests, negative tests, and clear verification notes.
