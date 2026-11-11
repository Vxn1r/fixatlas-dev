# Architecture

FixAtlas 0.1 is a small offline pipeline:

```text
stdin / UTF-8 file
        |
        v
bounded input reader ----> no persistence / no network
        |
        v
registry loader ---------> bundled or user-supplied JSON
        |
        v
literal signature engine -> deterministic RuleMatch objects
        |
        v
human-readable output OR JSON output
        |
        +--> optional local MCP stdio server (Python 3.11+, official SDK)
        |        |
        |        +--> read-only explain / search / list / capabilities tools
        |
        +--> reusable agent + skill instructions
```

## Design decisions

- **Standard library at runtime:** installation has no runtime dependency chain.
- **Literal matching:** avoids evaluating user-provided regular expressions and keeps rule behavior inspectable.
- **Bounded input:** limits accidental memory use from unexpectedly large logs.
- **No automatic repair:** a future fix executor would introduce command execution, environment mutation, and consent risks. It is deliberately out of scope for 0.1.
- **No network:** current rules are static snapshots. Version-aware remote metadata is a future feature and must remain opt-in if introduced.
- **Optional agent bridge:** the MCP adapter exposes read-only tool functions backed by the same local engine; the SDK is an optional extra so the core CLI stays dependency-free.

## Trust model

A rule is a troubleshooting hypothesis authored by contributors. Its signature can be tested locally, but the actual root cause is specific to the user's environment. The CLI therefore exposes matched strings and recommends verification checks rather than claiming certainty.
