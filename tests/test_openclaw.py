"""Tests for OpenClaw packaging — .openclaw/ directory generation."""

import pytest
from pathlib import Path
from compiler.openclaw import (
    package_openclaw,
    package_team_openclaw,
    generate_identity_md,
    generate_agents_md,
    generate_team_agents_md,
)
from compiler.compile import load_soul
from compiler.team_compile import load_team

from tests.conftest import ROOT, SOULS_DIR

TEAMS_DIR = ROOT / "teams"
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


# ── Team OpenClaw Packaging ──────────────────────────────────────────


class TestTeamOpenClawPackaging:
    """Test .openclaw/ team package generation.

    Expected structure:
        .openclaw/
        ├── agents.md              ← Team routing (souls, roles, order)
        ├── <soul-id>/
        │   ├── soul.md            ← Team-tuned soul.md
        │   └── identity.md        ← Per-soul identity card
        └── ...
    """

    TEAM_YAML = TEAMS_DIR / "three-kingdoms" / "team.yaml"

    @pytest.fixture
    def team_pkg(self, tmp_path):
        return package_team_openclaw(self.TEAM_YAML, output_dir=tmp_path)

    def test_creates_openclaw_directory(self, team_pkg):
        assert team_pkg.exists()
        assert team_pkg.name == ".openclaw"

    def test_has_agents_md(self, team_pkg):
        assert (team_pkg / "agents.md").exists()

    def test_agents_md_lists_all_souls(self, team_pkg):
        agents = (team_pkg / "agents.md").read_text()
        team = load_team(self.TEAM_YAML)
        for soul_entry in team["souls"]:
            assert soul_entry["soul_ref"] in agents

    def test_agents_md_has_sequential_routing(self, team_pkg):
        agents = (team_pkg / "agents.md").read_text()
        assert "sequential" in agents.lower()

    def test_agents_md_has_team_name(self, team_pkg):
        agents = (team_pkg / "agents.md").read_text()
        assert "Three Kingdoms" in agents

    def test_has_subdirectory_per_soul(self, team_pkg):
        team = load_team(self.TEAM_YAML)
        for soul_entry in team["souls"]:
            soul_dir = team_pkg / soul_entry["soul_ref"]
            assert soul_dir.is_dir(), f"Missing subdir: {soul_entry['soul_ref']}"

    def test_each_soul_has_soul_md(self, team_pkg):
        team = load_team(self.TEAM_YAML)
        for soul_entry in team["souls"]:
            soul_md = team_pkg / soul_entry["soul_ref"] / "soul.md"
            assert soul_md.exists(), f"Missing soul.md for {soul_entry['soul_ref']}"

    def test_each_soul_has_identity_md(self, team_pkg):
        team = load_team(self.TEAM_YAML)
        for soul_entry in team["souls"]:
            identity = team_pkg / soul_entry["soul_ref"] / "identity.md"
            assert identity.exists(), f"Missing identity.md for {soul_entry['soul_ref']}"

    def test_soul_md_is_team_tuned(self, team_pkg):
        """Team-tuned soul.md should contain Team Context section."""
        soul_md = (team_pkg / "cao-cao" / "soul.md").read_text()
        assert "## Team Context" in soul_md

    def test_soul_md_contains_base_personality(self, team_pkg):
        """Team-tuned soul.md should still contain base personality."""
        soul_md = (team_pkg / "cao-cao" / "soul.md").read_text()
        assert "## Core Identity" in soul_md


class TestTeamAgentsMdGeneration:
    """Test generate_team_agents_md content."""

    def test_contains_pipeline_order(self):
        team = load_team(TEAMS_DIR / "three-kingdoms" / "team.yaml")
        agents = generate_team_agents_md(team)
        # Should list souls in pipeline order with numbers
        assert "#1" in agents or "1." in agents

    def test_contains_roles(self):
        team = load_team(TEAMS_DIR / "three-kingdoms" / "team.yaml")
        agents = generate_team_agents_md(team)
        for soul_entry in team["souls"]:
            assert soul_entry["team_role"] in agents


class TestExistingPackagingRegression:
    """Verify existing package_openclaw still works after team feature."""

    def test_base_packaging_still_works(self, tmp_path):
        linus_path = SOULS_DIR / "linus-torvalds" / "soul.yaml"
        result = package_openclaw(linus_path, output_dir=tmp_path)
        assert result.exists()
        for fname in REQUIRED_FILES:
            assert (result / fname).exists()
        soul_md = (result / "soul.md").read_text()
        assert "Linus Torvalds" in soul_md
        assert "## Core Identity" in soul_md

    def test_team_packaging_output_dir_is_hermetic(self, tmp_path):
        """When output_dir is set, build files go to tmp, not repo."""
        team_yaml = TEAMS_DIR / "three-kingdoms" / "team.yaml"
        result = package_team_openclaw(team_yaml, output_dir=tmp_path)
        # Build files should be under tmp_path, not under repo teams/ dir
        expected_build = tmp_path / "three-kingdoms" / "build"
        assert expected_build.exists(), "Build dir should be in output_dir"
        assert result.exists()
        assert (result / "agents.md").exists()
