"""Holdout evaluation tests — uses test data NOT seen during development.

These tests verify the schema and compiler generalize to unseen souls,
not just the Linus/Buffett examples used during development.
"""

import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from compiler.compile import compile_soul_md

HOLDOUT_DIR = Path(__file__).resolve().parent / "fixtures" / "holdout"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "soul_schema.json"

REQUIRED_HEADINGS = [
    "Core Identity",
    "Core Beliefs",
    "Values",
    "Knowledge Frameworks",
    "Catchphrases",
    "Response Rules",
    "Blind Spots",
    "Conflict Style",
    "Basic Info",
]


@pytest.fixture(scope="module")
def schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def holdout_souls():
    souls = {}
    for soul_path in sorted(HOLDOUT_DIR.glob("*/soul.yaml")):
        with open(soul_path) as f:
            souls[soul_path.parent.name] = yaml.safe_load(f)
    return souls


class TestHoldoutValidation:
    """Holdout souls must pass schema validation without any special-casing."""

    def test_holdout_dir_has_souls(self, holdout_souls):
        assert len(holdout_souls) >= 1, "Need at least 1 holdout soul"

    def test_all_holdout_souls_validate(self, schema, holdout_souls):
        validator = Draft202012Validator(schema)
        for name, soul in holdout_souls.items():
            errors = list(validator.iter_errors(soul))
            if errors:
                msg = "\n".join(f"  {e.message}" for e in errors[:5])
                pytest.fail(f"Holdout soul '{name}' failed validation:\n{msg}")

    def test_all_holdout_souls_have_abcde(self, holdout_souls):
        for name, soul in holdout_souls.items():
            for layer in "ABCDE":
                assert layer in soul["layers"], f"Holdout {name} missing layer {layer}"


class TestHoldoutCompilation:
    """Holdout souls must compile to valid soul.md."""

    def test_all_holdout_souls_compile(self, holdout_souls):
        for name, soul in holdout_souls.items():
            md = compile_soul_md(soul)
            assert len(md) > 200, f"Holdout {name} compiled output too short"

    def test_all_sections_present_in_holdout(self, holdout_souls):
        for name, soul in holdout_souls.items():
            md = compile_soul_md(soul)
            for heading in REQUIRED_HEADINGS:
                assert heading in md, f"Holdout {name} missing '{heading}'"

    def test_holdout_name_in_output(self, holdout_souls):
        for name, soul in holdout_souls.items():
            md = compile_soul_md(soul)
            assert soul["metadata"]["name"] in md
