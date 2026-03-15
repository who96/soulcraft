"""Compiler tests for SoulCraft soul.md generation."""

import pytest

from compiler.compile import compile_soul_md, load_schema, load_soul, validate

from tests.conftest import ROOT, SOULS_DIR

REQUIRED_HEADINGS = [
    "Core Identity",
    "Core Beliefs",
    "Values",
    "Knowledge Frameworks",
    "Key Influences",
    "Original Ideas",
    "Catchphrases",
    "Expression Style",
    "Emotional Triggers",
    "Response Rules",
    "Blind Spots",
    "Conflict Style",
    "Provenance",
    "Basic Info",
]


class TestCompilation:
    """Test that soul.yaml compiles to valid soul.md."""

    @pytest.fixture(scope="class")
    def schema(self):
        return load_schema()

    @pytest.fixture(scope="class", params=["linus-torvalds", "warren-buffett"])
    def soul_pair(self, request):
        soul_path = SOULS_DIR / request.param / "soul.yaml"
        soul = load_soul(soul_path)
        md = compile_soul_md(soul)
        return request.param, soul, md

    def test_compilation_succeeds(self, soul_pair):
        name, soul, md = soul_pair
        assert md, f"Compilation of {name} produced empty output"
        assert len(md) > 500, f"Compilation of {name} too short ({len(md)} chars)"

    def test_output_contains_all_sections(self, soul_pair):
        name, soul, md = soul_pair
        for heading in REQUIRED_HEADINGS:
            assert heading in md, f"Missing section '{heading}' in {name} soul.md"

    def test_output_contains_name(self, soul_pair):
        name, soul, md = soul_pair
        display_name = soul["metadata"]["name"]
        assert display_name in md, f"Name '{display_name}' not found in compiled output"

    def test_output_starts_with_role_directive(self, soul_pair):
        name, soul, md = soul_pair
        assert "You are **" in md, f"{name} soul.md missing role directive"

    def test_catchphrases_present_in_output(self, soul_pair):
        name, soul, md = soul_pair
        for cp in soul["layers"]["C"]["catchphrases"][:3]:
            assert cp["phrase"] in md, f"Catchphrase '{cp['phrase'][:40]}...' missing from {name} soul.md"


class TestProvenanceIntegrity:
    """Test that provenance data is preserved through compilation."""

    @pytest.fixture(scope="class", params=["linus-torvalds", "warren-buffett"])
    def soul_data(self, request):
        soul_path = SOULS_DIR / request.param / "soul.yaml"
        return request.param, load_soul(soul_path)

    def test_all_worldview_items_have_provenance(self, soul_data):
        name, soul = soul_data
        for item in soul["layers"]["A"]["worldview"]:
            assert item["provenance"]["source_file"], f"Missing source_file in {name} worldview"
            assert item["provenance"]["quote"], f"Missing quote in {name} worldview"

    def test_all_scenarios_have_provenance(self, soul_data):
        name, soul = soul_data
        for s in soul["layers"]["D"]["scenarios"]:
            assert s["provenance"]["source_file"], f"Missing source_file in {name} scenario"
            assert s["provenance"]["quote"], f"Missing quote in {name} scenario"


class TestIdempotency:
    """Test that compilation is deterministic."""

    @pytest.fixture(scope="class", params=["linus-torvalds", "warren-buffett"])
    def soul(self, request):
        soul_path = SOULS_DIR / request.param / "soul.yaml"
        return request.param, load_soul(soul_path)

    def test_compiling_twice_produces_identical_output(self, soul):
        name, soul_data = soul
        md1 = compile_soul_md(soul_data)
        md2 = compile_soul_md(soul_data)
        assert md1 == md2, f"Non-deterministic compilation for {name}"
