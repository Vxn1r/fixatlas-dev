# Rule registry format

A registry is a UTF-8 JSON object with `schema_version: 1` and a `rules` array.

Each rule has these fields:

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Stable, unique kebab-case identifier |
| `title` | string | Short human-readable diagnosis |
| `category` | string | Toolchain or ecosystem |
| `summary` | string | What the error usually means |
| `root_cause` | string | Likely cause, stated without overclaiming |
| `match_any` | string array | At least one literal, case-insensitive signal must occur |
| `match_all` | string array | Every literal signal must occur; useful to narrow generic phrases |
| `checks` | non-empty string array | Diagnostic checks to confirm or reject the hypothesis |
| `actions` | non-empty string array | Conservative next steps; never auto-executed |
| `references` | object array | Optional `{ "label": ..., "url": ... }` documentation links |
| `verification` | string | What has and has not been verified |

## Matching semantics

- Matching is case-insensitive literal substring matching; no regular expressions or code execution are used.
- If `match_any` is non-empty, at least one of its entries must appear.
- Every `match_all` entry must appear.
- Rules are ordered by transparent match strength and number of matched signals, then by rule ID.
- `strong signal` means multiple literal signals matched or required context signals were satisfied. It is not a probability.

## Authoring advice

Prefer exact codes and phrases. Avoid generic signatures that could produce noisy diagnoses. Include negative tests so nearby but unrelated errors do not match. Keep the database offline and deterministic.
