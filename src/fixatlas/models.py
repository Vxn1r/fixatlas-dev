"""Typed, dependency-free models used by the FixAtlas rule engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Rule:
    id: str
    title: str
    category: str
    summary: str
    root_cause: str
    match_any: tuple[str, ...]
    match_all: tuple[str, ...]
    checks: tuple[str, ...]
    actions: tuple[str, ...]
    references: tuple[dict[str, str], ...]
    verification: str

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Rule:
        return cls(
            id=value["id"],
            title=value["title"],
            category=value["category"],
            summary=value["summary"],
            root_cause=value["root_cause"],
            match_any=tuple(value.get("match_any", [])),
            match_all=tuple(value.get("match_all", [])),
            checks=tuple(value["checks"]),
            actions=tuple(value["actions"]),
            references=tuple(value.get("references", [])),
            verification=value["verification"],
        )


@dataclass(frozen=True, slots=True)
class RuleMatch:
    rule: Rule
    matched_signals: tuple[str, ...]
    missing_required_signals: tuple[str, ...]
    strength: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.rule.id,
            "title": self.rule.title,
            "category": self.rule.category,
            "summary": self.rule.summary,
            "root_cause": self.rule.root_cause,
            "matched_signals": list(self.matched_signals),
            "missing_required_signals": list(self.missing_required_signals),
            "match_strength": self.strength,
            "checks": list(self.rule.checks),
            "actions": list(self.rule.actions),
            "references": list(self.rule.references),
            "verification": self.rule.verification,
        }
