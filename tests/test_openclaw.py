"""Tests for OpenClaw packaging — .openclaw/ directory generation."""

import pytest
from pathlib import Path
from compiler.openclaw import package_openclaw, generate_identity_md, generate_agents_md
from compiler.compile import load_soul

from tests.conftest import SOULS_DIR


REQUIRED_FILES = ["soul.md", "identity.md", "agents.md"]


class TestOpenClawPackaging:
    """Test .openclaw/ directory packaging."""

    @pytest.fixture(params=["linus-torvalds", "warren-buffett"])
    def soul_id(self, request):
        return request.param

    @pytest.fixture
    def soul_path(self, soul_id):
        return SOULS_DIR / soul_id / "soul.yaml"

    def test_packaging_creates_directory(self, soul_path, tmp_path):
        result = package_openclaw(soul_path, output_dir=tmp_path)
        assert result.exists()
        assert result.name == ".openclaw"

    def test_packaging_creates_all_required_files(self, soul_path, tmp_path):
        result = package_openclaw(soul_path, output_dir=tmp_path)
        for fname in REQUIRED_FILES:
            assert (result / fname).exists(), f"Missing: {fname}"

    def test_soul_md_is_valid_compilation(self, soul_path, tmp_path):
        result = package_openclaw(soul_path, output_dir=tmp_path)
        soul_md = (result / "soul.md").read_text()
        soul = load_soul(soul_path)
        assert soul["metadata"]["name"] in soul_md
        assert "## Core Identity" in soul_md

    def test_identity_md_has_metadata(self, soul_path, tmp_path):
        result = package_openclaw(soul_path, output_dir=tmp_path)
        identity = (result / "identity.md").read_text()
        soul = load_soul(soul_path)
        name = soul["metadata"]["name"]
        assert name in identity
        assert "Soul ID" in identity
        assert "Version" in identity

    def test_agents_md_has_routing_stub(self, soul_path, tmp_path):
        result = package_openclaw(soul_path, output_dir=tmp_path)
        agents = (result / "agents.md").read_text()
        soul = load_soul(soul_path)
        name = soul["metadata"]["name"]
        assert name in agents
        assert "Role" in agents
        assert "Routing" in agents


class TestIdentityGeneration:
    """Test identity.md content generation."""

    def test_identity_contains_first_sentence(self):
        soul = load_soul(SOULS_DIR / "linus-torvalds" / "soul.yaml")
        identity = generate_identity_md(soul)
        # Should contain actual content from identity description, not just name
        assert "Linus Torvalds" in identity
        assert "engineer" in identity.lower()

    def test_identity_lists_data_sources(self):
        soul = load_soul(SOULS_DIR / "warren-buffett" / "soul.yaml")
        identity = generate_identity_md(soul)
        assert "Data Sources" in identity


class TestAgentsGeneration:
    """Test agents.md content generation."""

    def test_agents_is_base_stub(self):
        soul = load_soul(SOULS_DIR / "linus-torvalds" / "soul.yaml")
        agents = generate_agents_md(soul)
        assert "base soul" in agents.lower()
        assert "team" in agents.lower()


class TestBatchPackaging:
    """Test batch packaging doesn't overwrite."""

    def test_batch_creates_separate_directories(self, tmp_path):
        linus_path = SOULS_DIR / "linus-torvalds" / "soul.yaml"
        buffett_path = SOULS_DIR / "warren-buffett" / "soul.yaml"

        result1 = package_openclaw(linus_path, output_dir=tmp_path)
        result2 = package_openclaw(buffett_path, output_dir=tmp_path)

        # Should be different directories
        assert result1 != result2
        assert result1.exists()
        assert result2.exists()

        # Both should have all required files
        for d in [result1, result2]:
            for fname in REQUIRED_FILES:
                assert (d / fname).exists()

        # Content should be different
        linus_soul = (result1 / "soul.md").read_text()
        buffett_soul = (result2 / "soul.md").read_text()
        assert "Linus" in linus_soul
        assert "Buffett" in buffett_soul
        assert linus_soul != buffett_soul
