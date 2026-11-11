"""Deterministic, offline matching for developer error messages."""

from __future__ import annotations

from fixatlas.models import Rule, RuleMatch

MAX_INPUT_CHARS = 200_000


class InputTooLargeError(ValueError):
    """Raised when an error log exceeds the documented analysis limit."""


def analyze(text: str, rules: tuple[Rule, ...]) -> list[RuleMatch]:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if len(text) > MAX_INPUT_CHARS:
        raise InputTooLargeError(
            f"Input is {len(text):,} characters; maximum supported size is {MAX_INPUT_CHARS:,}"
        )

    haystack = text.casefold()
    matches: list[RuleMatch] = []
    for rule in rules:
        hits = tuple(signal for signal in rule.match_any if signal.casefold() in haystack)
        missing = tuple(signal for signal in rule.match_all if signal.casefold() not in haystack)
        if missing or (rule.match_any and not hits):
            continue
        # This is a transparent rule-hit strength, not a probability or AI confidence score.
        strength = "strong signal" if (len(hits) >= 2 or rule.match_all) else "candidate"
        matches.append(
            RuleMatch(
                rule=rule,
                matched_signals=hits + rule.match_all,
                missing_required_signals=(),
                strength=strength,
            )
        )

    matches.sort(
        key=lambda item: (
            item.strength != "strong signal",
            -len(item.matched_signals),
            item.rule.id,
        )
    )
    return matches
