"""Tests for SoulCraft Team Schema, Compiler, and Sequential Handoff."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from compiler.compile import compile_soul_md, load_soul
from compiler.team_compile import (
    compile_team,
    compile_team_context,
    load_team,
    load_team_schema,
    validate_team,
    validate_team_refs,
)
from tests.conftest import ROOT, SOULS_DIR

TEAM_SCHEMA_PATH = ROOT / "schemas" / "team_schema.json"
TEAMS_DIR = ROOT / "teams"
CODE_REVIEW_TEAM = TEAMS_DIR / "code-review" / "team.yaml"


@pytest.fixture(scope="session")
def team_schema():
    with open(TEAM_SCHEMA_PATH) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def code_review_team():
    return load_team(CODE_REVIEW_TEAM)


# ── T4.1: Schema Structural Validation ───


class TestTeamSchema:
    """Test team_schema.json and structural validation."""

    def test_schema_is_valid_json(self):
        with open(TEAM_SCHEMA_PATH) as f:
            schema = json.load(f)
        assert schema["title"] == "SoulCraft Team Schema"

    def test_code_review_team_validates(self, team_schema):
        team = load_team(CODE_REVIEW_TEAM)
        errors = validate_team(team, team_schema)
        assert errors == [], f"Validation errors: {errors}"

    def test_missing_metadata_fails(self, team_schema):
        bad = {"routing_strategy": "sequential", "souls": []}
        errors = validate_team(bad, team_schema)
        assert len(errors) > 0

    def test_missing_souls_fails(self, team_schema):
        bad = {
            "metadata": {"name": "X", "id": "x", "version": "0.1.0", "description": "x"},
            "routing_strategy": "sequential",
        }
        errors = validate_team(bad, team_schema)
        assert len(errors) > 0

    def test_souls_min_items_enforced(self, team_schema):
        bad = {
            "metadata": {"name": "X", "id": "x", "version": "0.1.0", "description": "x"},
            "routing_strategy": "sequential",
            "souls": [
                {"soul_ref": "linus-torvalds", "team_role": "R", "directives": "D"},
            ],
        }
        errors = validate_team(bad, team_schema)
        assert any("too short" in e for e in errors)

    def test_invalid_routing_strategy_fails(self, team_schema):
        bad = {
            "metadata": {"name": "X", "id": "x", "version": "0.1.0", "description": "x"},
            "routing_strategy": "parallel",
            "souls": [
                {"soul_ref": "a", "team_role": "R", "directives": "D"},
                {"soul_ref": "b", "team_role": "R", "directives": "D"},
            ],
        }
        errors = validate_team(bad, team_schema)
        assert any("sequential" in e for e in errors)

    def test_invalid_id_pattern_fails(self, team_schema):
        bad = {
            "metadata": {"name": "X", "id": "Bad_Id", "version": "0.1.0", "description": "x"},
            "routing_strategy": "sequential",
            "souls": [
                {"soul_ref": "a", "team_role": "R", "directives": "D"},
                {"soul_ref": "b", "team_role": "R", "directives": "D"},
            ],
        }
        errors = validate_team(bad, team_schema)
        assert len(errors) > 0


# ── T4.2: Semantic Validation ───


class TestTeamSemanticValidation:
    """Test semantic validation (soul_ref existence, duplicates)."""

    def test_nonexistent_soul_ref_fails(self):
        team = {
            "metadata": {"name": "X", "id": "x", "version": "0.1.0", "description": "x"},
            "routing_strategy": "sequential",
            "souls": [
                {"soul_ref": "nonexistent-soul", "team_role": "R", "directives": "D"},
                {"soul_ref": "also-missing", "team_role": "R", "directives": "D"},
            ],
        }
        errors = validate_team_refs(team, SOULS_DIR)
        assert len(errors) == 2
        assert "nonexistent-soul" in errors[0]

    def test_duplicate_soul_ref_fails(self):
        team = {
            "metadata": {"name": "X", "id": "x", "version": "0.1.0", "description": "x"},
            "routing_strategy": "sequential",
            "souls": [
                {"soul_ref": "linus-torvalds", "team_role": "R1", "directives": "D"},
                {"soul_ref": "linus-torvalds", "team_role": "R2", "directives": "D"},
            ],
        }
        errors = validate_team_refs(team, SOULS_DIR)
        assert any("duplicated" in e for e in errors)

    def test_valid_refs_pass(self):
        team = load_team(CODE_REVIEW_TEAM)
        errors = validate_team_refs(team, SOULS_DIR)
        assert errors == []


# ── T4.3: Team Compilation ───


class TestTeamCompilation:
    """Test team compilation produces correct output."""

    def test_compile_produces_correct_number_of_files(self, tmp_path):
        outputs = compile_team(CODE_REVIEW_TEAM, output_dir=tmp_path)
        assert len(outputs) == 2

    def test_output_files_exist(self, tmp_path):
        outputs = compile_team(CODE_REVIEW_TEAM, output_dir=tmp_path)
        for p in outputs:
            assert p.exists()
            assert p.name == "soul.md"

    def test_output_in_correct_directory_structure(self, tmp_path):
        outputs = compile_team(CODE_REVIEW_TEAM, output_dir=tmp_path)
        # Should be at tmp_path/code-review/build/<soul-id>/soul.md
        for p in outputs:
            assert "build" in str(p)
            assert p.parent.name in ("linus-torvalds", "warren-buffett")


# ── T4.4: Team Context Content ───


class TestTeamContext:
    """Test that Team Context section contains all required elements."""

    @pytest.fixture
    def team_tuned_linus(self, tmp_path):
        outputs = compile_team(CODE_REVIEW_TEAM, output_dir=tmp_path)
        return outputs[0].read_text()  # Linus is first

    @pytest.fixture
    def team_tuned_buffett(self, tmp_path):
        outputs = compile_team(CODE_REVIEW_TEAM, output_dir=tmp_path)
        return outputs[1].read_text()  # Buffett is second

    def test_contains_team_context_heading(self, team_tuned_linus):
        assert "## Team Context" in team_tuned_linus

    def test_contains_team_name(self, team_tuned_linus):
        assert "Code Review Team" in team_tuned_linus

    def test_contains_role(self, team_tuned_linus):
        assert "Technical Reviewer" in team_tuned_linus

    def test_contains_routing_info(self, team_tuned_linus):
        assert "#1 of 2" in team_tuned_linus

    def test_contains_teammates(self, team_tuned_linus):
        assert "warren-buffett" in team_tuned_linus

    def test_contains_directives(self, team_tuned_linus):
        assert "code quality" in team_tuned_linus.lower()

    def test_contains_handoff_protocol(self, team_tuned_linus):
        assert "Handoff Protocol" in team_tuned_linus

    def test_base_soul_content_preserved(self, team_tuned_linus):
        """The team-tuned version still has all base soul sections."""
        assert "## Core Identity" in team_tuned_linus
        assert "## Core Beliefs" in team_tuned_linus
        assert "You are **Linus Torvalds**" in team_tuned_linus

    def test_buffett_is_second_in_pipeline(self, team_tuned_buffett):
        assert "#2 of 2" in team_tuned_buffett
        assert "linus-torvalds" in team_tuned_buffett


# ── T4.5: Idempotency ───


class TestTeamIdempotency:
    """Test that compiling the same team twice produces identical output."""

    def test_compile_twice_identical(self, tmp_path):
        dir1 = tmp_path / "run1"
        dir2 = tmp_path / "run2"
        out1 = compile_team(CODE_REVIEW_TEAM, output_dir=dir1)
        out2 = compile_team(CODE_REVIEW_TEAM, output_dir=dir2)
        for p1, p2 in zip(out1, out2):
            assert p1.read_text() == p2.read_text()


# ── T4.6: No Base Pollution ───


class TestTeamNoBasePollution:
    """Ensure team compilation does NOT modify base soul files."""

    def test_base_soul_md_unchanged(self, tmp_path):
        # Record state before
        linus_base = SOULS_DIR / "linus-torvalds" / "soul.md"
        buffett_base = SOULS_DIR / "warren-buffett" / "soul.md"

        linus_before = linus_base.read_text() if linus_base.exists() else None
        buffett_before = buffett_base.read_text() if buffett_base.exists() else None

        # Compile team
        compile_team(CODE_REVIEW_TEAM, output_dir=tmp_path)

        # Verify unchanged
        linus_after = linus_base.read_text() if linus_base.exists() else None
        buffett_after = buffett_base.read_text() if buffett_base.exists() else None

        assert linus_before == linus_after, "Base Linus soul.md was modified!"
        assert buffett_before == buffett_after, "Base Buffett soul.md was modified!"

    def test_no_team_context_in_base_soul(self, tmp_path):
        compile_team(CODE_REVIEW_TEAM, output_dir=tmp_path)
        # Base soul.yaml should never contain Team Context
        for soul_dir in SOULS_DIR.iterdir():
            soul_yaml = soul_dir / "soul.yaml"
            if soul_yaml.exists():
                content = soul_yaml.read_text()
                assert "Team Context" not in content


# ── T4.7: Sequential Handoff ───


class TestSequentialHandoff:
    """Test the handoff data format for sequential routing."""

    def test_second_soul_prompt_includes_first_output(self, tmp_path):
        """Simulate sequential handoff: verify the prompt structure."""
        outputs = compile_team(CODE_REVIEW_TEAM, output_dir=tmp_path)

        # Read both team-tuned soul.md files
        linus_system = outputs[0].read_text()
        buffett_system = outputs[1].read_text()

        # Simulate first soul output
        first_soul_output = "This code is garbage. Fix the data structures."
        user_query = "Review this code: for i in range(10): pass"

        # Build the handoff prompt (as demo.py would)
        handoff_prompt = (
            f"===SOULCRAFT_HANDOFF_V1 soul=linus-torvalds===\n"
            f"{first_soul_output}\n"
            f"===END_HANDOFF===\n\n"
            f"{user_query}"
        )

        # Verify structure
        assert "SOULCRAFT_HANDOFF_V1 soul=linus-torvalds" in handoff_prompt
        assert first_soul_output in handoff_prompt
        assert user_query in handoff_prompt

        # Verify both system prompts have team context
        assert "## Team Context" in linus_system
        assert "## Team Context" in buffett_system

        # Verify Buffett knows about Linus
        assert "linus-torvalds" in buffett_system
        assert "#2 of 2" in buffett_system


# ── T4.8: CLI Smoke Tests ───


class TestTeamCLI:
    """Smoke test for team compiler CLI."""

    def test_compile_cli(self):
        result = subprocess.run(
            [sys.executable, "-m", "compiler.team_compile",
             "teams/code-review/team.yaml"],
            capture_output=True, text=True, cwd=ROOT,
        )
        assert result.returncode == 0
        assert "Team-tuned" in result.stdout

    def test_demo_team_offline_cli(self):
        result = subprocess.run(
            [sys.executable, "demo.py", "--team", "code-review", "--offline"],
            capture_output=True, text=True, cwd=ROOT,
        )
        assert result.returncode == 0
        assert "Pipeline" in result.stdout
        assert "linus-torvalds" in result.stdout
        assert "warren-buffett" in result.stdout

    def test_demo_soul_team_mutual_exclusion(self):
        result = subprocess.run(
            [sys.executable, "demo.py", "--soul", "linus-torvalds",
             "--team", "code-review"],
            capture_output=True, text=True, cwd=ROOT,
        )
        assert result.returncode != 0


# ── T4.9: Handoff Prompt Format ───


class TestHandoffPromptFormat:
    """Test the build_handoff_prompt utility from demo.py."""

    def test_no_prior_outputs_returns_query(self):
        sys.path.insert(0, str(ROOT))
        from demo import build_handoff_prompt

        result = build_handoff_prompt("Review code", [])
        assert result == "Review code"

    def test_with_prior_outputs(self):
        sys.path.insert(0, str(ROOT))
        from demo import build_handoff_prompt

        prior = [("linus-torvalds", "Bad code.")]
        result = build_handoff_prompt("Review code", prior)
        assert "===SOULCRAFT_HANDOFF_V1 soul=linus-torvalds===" in result
        assert "Bad code." in result
        assert "===END_HANDOFF===" in result
        assert "Review code" in result

