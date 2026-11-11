"""Load and validate local FixAtlas rule registries."""

from __future__ import annotations

import json
import re
from importlib.resources import files
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from fixatlas.models import Rule

REGISTRY_VERSION = 1
MAX_REGISTRY_BYTES = 2_000_000
MAX_RULES = 10_000
MAX_FIELD_CHARS = 8_000
_RULE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class RegistryError(ValueError):
    """Raised when a rule registry is malformed or unsafe to load."""


def _non_empty_string(value: Any, field: str, rule_id: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RegistryError(f"Rule {rule_id!r}: {field} must be a non-empty string")
    cleaned = value.strip()
    if len(cleaned) > MAX_FIELD_CHARS:
        raise RegistryError(f"Rule {rule_id!r}: {field} exceeds {MAX_FIELD_CHARS:,} characters")
    return cleaned


def parse_registry(payload: Any) -> tuple[Rule, ...]:
    if not isinstance(payload, dict):
        raise RegistryError("Registry root must be a JSON object")
    schema_version = payload.get("schema_version")
    if (
        not isinstance(schema_version, int)
        or isinstance(schema_version, bool)
        or schema_version != REGISTRY_VERSION
    ):
        raise RegistryError(
            f"Unsupported registry schema_version: {payload.get('schema_version')!r}; "
            f"expected {REGISTRY_VERSION}"
        )
    raw_rules = payload.get("rules")
    if not isinstance(raw_rules, list):
        raise RegistryError("Registry field 'rules' must be a list")
    if len(raw_rules) > MAX_RULES:
        raise RegistryError(f"Registry may contain at most {MAX_RULES:,} rules")

    rules: list[Rule] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(raw_rules):
        if not isinstance(raw, dict):
            raise RegistryError(f"Rule at index {index} must be a JSON object")
        rule_id = _non_empty_string(raw.get("id"), "id", f"index {index}")
        if not _RULE_ID.fullmatch(rule_id):
            raise RegistryError(
                f"Rule ID {rule_id!r} must use lowercase kebab-case letters and digits"
            )
        if rule_id in seen_ids:
            raise RegistryError(f"Duplicate rule id: {rule_id}")
        seen_ids.add(rule_id)

        cleaned = dict(raw)
        cleaned["id"] = rule_id
        for field in ("title", "category", "summary", "root_cause", "verification"):
            cleaned[field] = _non_empty_string(raw.get(field), field, rule_id)
        for field in ("match_any", "match_all", "checks", "actions"):
            values = raw.get(field, [])
            if not isinstance(values, list) or any(
                not isinstance(item, str) or not item.strip() for item in values
            ):
                raise RegistryError(
                    f"Rule {rule_id!r}: {field} must be a list of non-empty strings"
                )
            cleaned[field] = [item.strip() for item in values]
        if not cleaned["match_any"] and not cleaned["match_all"]:
            raise RegistryError(
                f"Rule {rule_id!r}: at least one matching signal is required"
            )
        if not cleaned["checks"]:
            raise RegistryError(
                f"Rule {rule_id!r}: at least one diagnostic check is required"
            )
        if not cleaned["actions"]:
            raise RegistryError(
                f"Rule {rule_id!r}: at least one recommended action is required"
            )
        references = raw.get("references", [])
        if not isinstance(references, list):
            raise RegistryError(f"Rule {rule_id!r}: references must be a list")
        cleaned_references: list[dict[str, str]] = []
        for reference in references:
            if not isinstance(reference, dict):
                raise RegistryError(
                    f"Rule {rule_id!r}: references must contain label/url objects"
                )
            label = reference.get("label")
            url = reference.get("url")
            if not isinstance(label, str) or not label.strip():
                raise RegistryError(f"Rule {rule_id!r}: reference label must be non-empty")
            parsed_url = urlsplit(url.strip()) if isinstance(url, str) else None
            if (
                parsed_url is None
                or parsed_url.scheme != "https"
                or not parsed_url.hostname
            ):
                raise RegistryError(
                    f"Rule {rule_id!r}: reference URL must use HTTPS and include a valid host"
                )
            if (
                len(label.strip()) > MAX_FIELD_CHARS
                or len(url.strip()) > MAX_FIELD_CHARS
            ):
                raise RegistryError(f"Rule {rule_id!r}: reference fields are too long")
            cleaned_references.append(
                {"label": label.strip(), "url": url.strip()}
            )
        cleaned["references"] = cleaned_references
        rules.append(Rule.from_dict(cleaned))
    return tuple(rules)


def load_registry(path: str | Path | None = None) -> tuple[Rule, ...]:
    if path is None:
        resource = files("fixatlas.data").joinpath("rules.json")
        raw = resource.read_bytes()
        source = "built-in registry"
    else:
        source_path = Path(path).expanduser()
        try:
            size = source_path.stat().st_size
        except OSError as exc:
            raise RegistryError(f"Cannot read registry {source_path}: {exc}") from exc
        if size > MAX_REGISTRY_BYTES:
            raise RegistryError(f"Registry exceeds the {MAX_REGISTRY_BYTES:,}-byte size limit")
        try:
            raw = source_path.read_bytes()
        except OSError as exc:
            raise RegistryError(f"Cannot read registry {source_path}: {exc}") from exc
        source = str(source_path)

    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RegistryError(f"Invalid JSON in {source}: {exc}") from exc
    return parse_registry(payload)
