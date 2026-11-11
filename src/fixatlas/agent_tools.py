"""Small, dependency-free tool functions for coding-agent integrations."""

from __future__ import annotations

from typing import Any

from fixatlas import __version__
from fixatlas.engine import MAX_INPUT_CHARS, analyze
from fixatlas.registry import load_registry


def explain_error(error_text: str) -> dict[str, Any]:
    """Diagnose an error message and return evidence-backed matching rules.

    The input is analyzed locally. The function never executes commands, performs
    network requests, or includes the original error text in its response.
    """
    if not isinstance(error_text, str):
        raise TypeError("error_text must be a string")
    matches = analyze(error_text, load_registry())
    return {
        "tool": "fixatlas",
        "version": __version__,
        "input_characters": len(error_text),
        "network_access": False,
        "matches": [match.to_dict() for match in matches],
        "message": (
            "Review the checks and references; a rule match is a diagnostic lead, "
            "not a guaranteed fix."
            if matches
            else "No bundled rule matched. This does not prove the error is harmless "
            "or unsupported."
        ),
    }


def search_rules(query: str) -> dict[str, Any]:
    """Search the bundled rule catalogue by ID, title, category, or summary."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    if len(query) > 500:
        raise ValueError("query must be 500 characters or fewer")
    needle = query.strip().casefold()
    found = [
        rule
        for rule in load_registry()
        if needle in " ".join((rule.id, rule.title, rule.category, rule.summary)).casefold()
    ]
    return {
        "query": query,
        "count": len(found),
        "rules": [
            {
                "id": rule.id,
                "title": rule.title,
                "category": rule.category,
                "summary": rule.summary,
            }
            for rule in found
        ],
    }


def list_rules(category: str | None = None) -> dict[str, Any]:
    """List available rules, optionally restricted to a category substring."""
    if category is not None and not isinstance(category, str):
        raise TypeError("category must be a string or None")
    if category is not None and len(category) > 500:
        raise ValueError("category must be 500 characters or fewer")
    needle = category.strip().casefold() if category is not None else ""
    rules = [
        rule
        for rule in load_registry()
        if not needle or needle in rule.category.casefold()
    ]
    return {
        "count": len(rules),
        "rules": [
            {
                "id": rule.id,
                "title": rule.title,
                "category": rule.category,
                "summary": rule.summary,
            }
            for rule in rules
        ],
    }


def tool_capabilities() -> dict[str, Any]:
    """Describe safe integration capabilities without exposing user data."""
    return {
        "name": "FixAtlas",
        "version": __version__,
        "input_limit_characters": MAX_INPUT_CHARS,
        "network_access": False,
        "telemetry": False,
        "executes_commands": False,
        "tools": ["fixatlas_explain", "fixatlas_search_rules", "fixatlas_list_rules"],
    }
