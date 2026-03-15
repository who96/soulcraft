"""Schema validation tests for SoulCraft souls."""

import copy

import pytest
from jsonschema import Draft202012Validator, ValidationError

ABCDE_LAYERS = ["A", "B", "C", "D", "E"]


class TestSchemaIntegrity:
    """Test that the schema itself is well-formed."""

    def test_schema_is_valid_json_schema(self, schema):
        Draft202012Validator.check_schema(schema)

    def test_schema_requires_metadata(self, schema):
        assert "metadata" in schema["properties"]
        assert "metadata" in schema["required"]

    def test_schema_requires_all_abcde_layers(self, schema):
        layers = schema["properties"]["layers"]
        for layer in ABCDE_LAYERS:
            assert layer in layers["properties"], f"Layer {layer} missing from schema"
            assert layer in layers["required"], f"Layer {layer} not required"


class TestLinusSoul:
    """Validate Linus Torvalds soul against schema."""

    def test_validates_against_schema(self, schema, linus_soul):
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(linus_soul))
        if errors:
            msg = "\n".join(f"  {'.'.join(str(p) for p in e.absolute_path)}: {e.message}" for e in errors)
            pytest.fail(f"Schema validation failed:\n{msg}")

    def test_has_all_layers(self, linus_soul):
        for layer in ABCDE_LAYERS:
            assert layer in linus_soul["layers"], f"Layer {layer} missing"

    def test_worldview_has_minimum_entries(self, linus_soul):
        assert len(linus_soul["layers"]["A"]["worldview"]) >= 3

    def test_catchphrases_have_provenance(self, linus_soul):
        for cp in linus_soul["layers"]["C"]["catchphrases"]:
            assert "provenance" in cp
            assert cp["provenance"]["source_file"]
            assert cp["provenance"]["quote"]

    def test_metadata_id_is_slug(self, linus_soul):
        soul_id = linus_soul["metadata"]["id"]
        assert soul_id == "linus-torvalds"
        assert all(c.isalnum() or c == "-" for c in soul_id)


class TestBuffettSoul:
    """Validate Warren Buffett soul against schema."""

    def test_validates_against_schema(self, schema, buffett_soul):
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(buffett_soul))
        if errors:
            msg = "\n".join(f"  {'.'.join(str(p) for p in e.absolute_path)}: {e.message}" for e in errors)
            pytest.fail(f"Schema validation failed:\n{msg}")

    def test_has_all_layers(self, buffett_soul):
        for layer in ABCDE_LAYERS:
            assert layer in buffett_soul["layers"], f"Layer {layer} missing"

    def test_values_have_stance(self, buffett_soul):
        for v in buffett_soul["layers"]["A"]["values"]:
            assert v["stance"] in ("affirm", "reject")

    def test_blind_spots_have_explicit(self, buffett_soul):
        bs = buffett_soul["layers"]["E"]["blind_spots"]
        assert len(bs["explicit"]) >= 1

    def test_metadata_id_is_slug(self, buffett_soul):
        soul_id = buffett_soul["metadata"]["id"]
        assert soul_id == "warren-buffett"


class TestInvalidSoulRejects:
    """Ensure schema rejects invalid souls."""

    def test_missing_metadata_fails(self, schema):
        bad = {"layers": {"A": {}, "B": {}, "C": {}, "D": {}, "E": {}}}
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(bad))
        assert len(errors) > 0, "Should reject soul without proper metadata"

    def test_missing_layer_fails(self, schema, linus_soul):
        bad = copy.deepcopy(linus_soul)
        del bad["layers"]["E"]
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(bad))
        assert any("E" in str(e.message) or "required" in str(e.message) for e in errors)

    def test_bad_version_format_fails(self, schema, linus_soul):
        bad = copy.deepcopy(linus_soul)
        bad["metadata"]["version"] = "not-a-version"
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(bad))
        assert len(errors) > 0, "Should reject bad version format"

    def test_invalid_stance_fails(self, schema, linus_soul):
        bad = copy.deepcopy(linus_soul)
        bad["layers"]["A"]["values"][0]["stance"] = "maybe"
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(bad))
        assert len(errors) > 0, "Should reject invalid stance"
