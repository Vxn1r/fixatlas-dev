from __future__ import annotations

import json

import pytest

from fixatlas.engine import InputTooLargeError, analyze
from fixatlas.registry import RegistryError, load_registry, parse_registry


@pytest.fixture(scope="module")
def rules():
    return load_registry()


def test_registry_has_unique_ids_and_expected_seed_coverage(rules):
    ids = [rule.id for rule in rules]
    assert len(ids) == len(set(ids))
    assert {
        "npm-ebadplatform",
        "npm-eresolve",
        "python-module-not-found",
        "git-not-repository",
    }.issubset(ids)


def test_matches_npm_platform_error(rules):
    matches = analyze("npm ERR! code EBADPLATFORM\nnpm ERR! not compatible with your OS", rules)
    assert matches
    assert matches[0].rule.id == "npm-ebadplatform"
    assert matches[0].matched_signals == ("EBADPLATFORM",)


def test_matches_python_import_error(rules):
    matches = analyze("ModuleNotFoundError: No module named 'dnspython'", rules)
    assert matches[0].rule.id == "python-module-not-found"


def test_gradle_rule_requires_both_signals(rules):
    assert analyze("Could not resolve all files for configuration", rules) == []
    matches = analyze("Gradle: Could not resolve all files for configuration ':app'", rules)
    assert matches[0].rule.id == "gradle-dependency-resolution"


def test_no_match_is_not_a_crash(rules):
    assert analyze("Everything completed successfully", rules) == []


def test_match_is_case_insensitive(rules):
    matches = analyze("FATAL: NOT A GIT REPOSITORY", rules)
    assert matches[0].rule.id == "git-not-repository"


def test_input_size_is_bounded(rules):
    with pytest.raises(InputTooLargeError):
        analyze("x" * 200_001, rules)


def test_registry_rejects_duplicate_ids():
    item = {
        "id": "sample",
        "title": "Sample rule",
        "category": "test",
        "summary": "A sample.",
        "root_cause": "Test data.",
        "match_any": ["sample error"],
        "match_all": [],
        "checks": ["Check the sample."],
        "actions": ["Fix the sample."],
        "references": [],
        "verification": "Unit-tested signature.",
    }
    with pytest.raises(RegistryError, match="Duplicate rule id"):
        parse_registry({"schema_version": 1, "rules": [item, item]})


def test_registry_rejects_unknown_schema():
    with pytest.raises(RegistryError, match="Unsupported registry schema_version"):
        parse_registry({"schema_version": 99, "rules": []})


def test_registry_rejects_rule_without_match_signals():
    item = {
        "id": "sample",
        "title": "Sample rule",
        "category": "test",
        "summary": "A sample.",
        "root_cause": "Test data.",
        "match_any": [],
        "match_all": [],
        "checks": ["Check the sample."],
        "actions": ["Fix the sample."],
        "references": [],
        "verification": "Unit-tested signature.",
    }
    with pytest.raises(RegistryError, match="matching signal"):
        parse_registry({"schema_version": 1, "rules": [item]})


def test_bundled_registry_is_valid_json():
    # A separate JSON parse catches malformed package-data before resource loading.
    from importlib.resources import files

    payload = json.loads(files("fixatlas.data").joinpath("rules.json").read_text())
    assert payload["schema_version"] == 1
    assert len(payload["rules"]) >= 8


@pytest.mark.parametrize(
    ("message", "expected_id"),
    [
        ("npm ERR! ERESOLVE unable to resolve dependency tree", "npm-eresolve"),
        ("pip ERROR: ResolutionImpossible", "pip-resolution-impossible"),
        ("error: externally-managed-environment", "python-pep668"),
        ("git@github.com: Permission denied (publickey)", "git-ssh-publickey"),
        ("main.c:(.text+0x12): undefined reference to `helper'", "gcc-undefined-reference"),
    ],
)
def test_each_additional_seed_rule_matches(message, expected_id, rules):
    matches = analyze(message, rules)
    assert matches
    assert matches[0].rule.id == expected_id


def test_registry_rejects_non_integer_schema_version():
    with pytest.raises(RegistryError, match="Unsupported registry schema_version"):
        parse_registry({"schema_version": True, "rules": []})


def test_registry_rejects_non_https_reference():
    item = {
        "id": "sample",
        "title": "Sample rule",
        "category": "test",
        "summary": "A sample.",
        "root_cause": "Test data.",
        "match_any": ["sample error"],
        "match_all": [],
        "checks": ["Check the sample."],
        "actions": ["Fix the sample."],
        "references": [{"label": "Unsafe", "url": "javascript:alert(1)"}],
        "verification": "Unit-tested signature.",
    }
    with pytest.raises(RegistryError, match="must use HTTPS"):
        parse_registry({"schema_version": 1, "rules": [item]})


def test_every_seed_rule_has_usable_content(rules):
    assert len(rules) == 9
    for rule in rules:
        assert rule.title
        assert rule.summary
        assert rule.root_cause
        assert rule.match_any or rule.match_all
        assert rule.checks
        assert rule.actions
        assert rule.verification
        assert all(ref["url"].startswith("https://") for ref in rule.references)


def test_generic_platform_phrase_does_not_trigger_npm_rule(rules):
    assert analyze("The documentation discusses an unsupported platform for testing", rules) == []


def test_generic_could_not_resolve_phrase_does_not_trigger_gradle_rule(rules):
    assert analyze("Could not resolve the conflict in this explanation", rules) == []


def test_registry_rejects_malformed_rule_id():
    item = {
        "id": "Not Valid!",
        "title": "Sample rule",
        "category": "test",
        "summary": "A sample.",
        "root_cause": "Test data.",
        "match_any": ["sample error"],
        "match_all": [],
        "checks": ["Check the sample."],
        "actions": ["Fix the sample."],
        "references": [],
        "verification": "Unit-tested signature.",
    }
    with pytest.raises(RegistryError, match="lowercase kebab-case"):
        parse_registry({"schema_version": 1, "rules": [item]})


def test_registry_rejects_https_url_without_host():
    item = {
        "id": "sample",
        "title": "Sample rule",
        "category": "test",
        "summary": "A sample.",
        "root_cause": "Test data.",
        "match_any": ["sample error"],
        "match_all": [],
        "checks": ["Check the sample."],
        "actions": ["Fix the sample."],
        "references": [{"label": "Broken", "url": "https:///not-a-host"}],
        "verification": "Unit-tested signature.",
    }
    with pytest.raises(RegistryError, match="must use HTTPS"):
        parse_registry({"schema_version": 1, "rules": [item]})
