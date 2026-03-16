"""Phase 4 Dream Company Tests — hybrid routing, 7 new souls, team assembly."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
TEAM_SCHEMA_PATH = ROOT / "schemas" / "team_schema.json"
SOUL_SCHEMA_PATH = ROOT / "schemas" / "soul_schema.json"
DREAM_COMPANY_TEAM = ROOT / "teams" / "dream-company" / "team.yaml"

# All 7 new souls + Cagan (backup component)
NEW_SOULS = [
    "jeff-bezos", "steve-jobs", "marty-cagan", "edward-tufte",
    "john-carmack", "nassim-taleb", "charlie-munger",
]


@pytest.fixture(scope="module")
def team_schema():
    with open(TEAM_SCHEMA_PATH) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def soul_schema():
    with open(SOUL_SCHEMA_PATH) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def dream_company_team():
    with open(DREAM_COMPANY_TEAM) as f:
        return yaml.safe_load(f)


# ============================================================
# 1. Schema — Hybrid Routing Validation
# ============================================================

class TestHybridSchema:
    def test_hybrid_validates(self, team_schema, dream_company_team):
        v = Draft202012Validator(team_schema)
        errors = sorted(v.iter_errors(dream_company_team), key=str)
        assert not errors, f"Validation errors: {errors}"

    def test_sequential_still_validates(self, team_schema):
        """Backward compat: sequential teams without stages still validate."""
        with open(ROOT / "teams" / "code-review" / "team.yaml") as f:
            team = yaml.safe_load(f)
        v = Draft202012Validator(team_schema)
        errors = list(v.iter_errors(team))
        assert not errors

    def test_sequential_with_stages_rejected(self, team_schema):
        bad = {
            "metadata": {"name": "X", "id": "x", "version": "0.1.0", "description": "x"},
            "routing_strategy": "sequential",
            "souls": [
                {"soul_ref": "a", "team_role": "R", "directives": "D"},
                {"soul_ref": "b", "team_role": "R", "directives": "D"},
            ],
            "stages": [{"name": "test", "type": "sequential", "souls": ["a"]}],
        }
        v = Draft202012Validator(team_schema)
        errors = list(v.iter_errors(bad))
        assert len(errors) > 0, "sequential+stages should be rejected"

    def test_hybrid_without_stages_rejected(self, team_schema):
        bad = {
            "metadata": {"name": "X", "id": "x", "version": "0.1.0", "description": "x"},
            "routing_strategy": "hybrid",
            "souls": [
                {"soul_ref": "a", "team_role": "R", "directives": "D"},
                {"soul_ref": "b", "team_role": "R", "directives": "D"},
            ],
        }
        v = Draft202012Validator(team_schema)
        errors = list(v.iter_errors(bad))
        assert len(errors) > 0, "hybrid without stages should be rejected"

    def test_unknown_routing_rejected(self, team_schema):
        bad = {
            "metadata": {"name": "X", "id": "x", "version": "0.1.0", "description": "x"},
            "routing_strategy": "parallel",
            "souls": [
                {"soul_ref": "a", "team_role": "R", "directives": "D"},
                {"soul_ref": "b", "team_role": "R", "directives": "D"},
            ],
        }
        v = Draft202012Validator(team_schema)
        errors = list(v.iter_errors(bad))
        assert any("parallel" in str(e) for e in errors)

    def test_unknown_stage_type_rejected(self, team_schema):
        bad = {
            "metadata": {"name": "X", "id": "x", "version": "0.1.0", "description": "x"},
            "routing_strategy": "hybrid",
            "souls": [
                {"soul_ref": "a", "team_role": "R", "directives": "D"},
                {"soul_ref": "b", "team_role": "R", "directives": "D"},
            ],
            "stages": [{"name": "bad", "type": "dag", "souls": ["a", "b"]}],
        }
        v = Draft202012Validator(team_schema)
        errors = list(v.iter_errors(bad))
        assert any("dag" in str(e) for e in errors)


# ============================================================
# 2. Soul Validation — All New Souls
# ============================================================

class TestNewSouls:
    @pytest.mark.parametrize("soul_id", NEW_SOULS)
    def test_soul_exists(self, soul_id):
        soul_path = ROOT / "souls" / soul_id / "soul.yaml"
        assert soul_path.exists(), f"Soul {soul_id} not found"

    @pytest.mark.parametrize("soul_id", NEW_SOULS)
    def test_soul_validates(self, soul_id, soul_schema):
        from compiler.compile import load_soul, validate
        soul = load_soul(ROOT / "souls" / soul_id / "soul.yaml")
        errors = validate(soul, soul_schema)
        assert not errors, f"{soul_id}: {errors}"

    @pytest.mark.parametrize("soul_id", NEW_SOULS)
    def test_soul_compiles(self, soul_id):
        from compiler.compile import load_soul, compile_soul_md
        soul = load_soul(ROOT / "souls" / soul_id / "soul.yaml")
        md = compile_soul_md(soul)
        assert len(md) > 1000, f"{soul_id} soul.md is too short ({len(md)} chars)"

    @pytest.mark.parametrize("soul_id", NEW_SOULS)
    def test_soul_has_abcde(self, soul_id):
        with open(ROOT / "souls" / soul_id / "soul.yaml") as f:
            soul = yaml.safe_load(f)
        layers = soul["layers"]
        assert "A" in layers, f"{soul_id} missing layer A"
        assert "B" in layers, f"{soul_id} missing layer B"
        assert "C" in layers, f"{soul_id} missing layer C"
        assert "D" in layers, f"{soul_id} missing layer D"
        assert "E" in layers, f"{soul_id} missing layer E"


# ============================================================
# 3. Hybrid Team Compilation
# ============================================================

class TestDreamCompanyCompilation:
    def test_compile_produces_7_files(self, tmp_path):
        from compiler.team_compile import compile_team
        outputs = compile_team(DREAM_COMPANY_TEAM, output_dir=tmp_path)
        assert len(outputs) == 7

    def test_output_in_stage_scoped_dirs(self, tmp_path):
        from compiler.team_compile import compile_team
        compile_team(DREAM_COMPANY_TEAM, output_dir=tmp_path)
        build_dir = tmp_path / "dream-company" / "build"
        expected_dirs = [
            "00-core-engine",
            "01-implementation",
            "02-review-daemons",
            "03-final-arbiter",
        ]
        for d in expected_dirs:
            assert (build_dir / d).is_dir(), f"Missing stage dir: {d}"

    def test_all_soul_refs_have_output(self, tmp_path):
        from compiler.team_compile import compile_team
        compile_team(DREAM_COMPANY_TEAM, output_dir=tmp_path)
        build_dir = tmp_path / "dream-company" / "build"
        expected = {
            "00-core-engine/steve-jobs",
            "00-core-engine/linus-torvalds",
            "00-core-engine/edward-tufte",
            "01-implementation/john-carmack",
            "02-review-daemons/warren-buffett",
            "02-review-daemons/nassim-taleb",
            "03-final-arbiter/jeff-bezos",
        }
        for rel in expected:
            soul_md = build_dir / rel / "soul.md"
            assert soul_md.exists(), f"Missing: {rel}/soul.md"
            assert len(soul_md.read_text()) > 1000

    def test_team_context_in_every_output(self, tmp_path):
        from compiler.team_compile import compile_team
        outputs = compile_team(DREAM_COMPANY_TEAM, output_dir=tmp_path)
        for out in outputs:
            content = out.read_text()
            assert "## Team Context" in content


class TestHybridTeamContext:
    @pytest.fixture
    def compiled_outputs(self, tmp_path):
        from compiler.team_compile import compile_team
        return compile_team(DREAM_COMPANY_TEAM, output_dir=tmp_path)

    @pytest.fixture
    def build_dir(self, tmp_path, compiled_outputs):
        return tmp_path / "dream-company" / "build"

    def test_iterative_soul_has_engine_label(self, build_dir):
        md = (build_dir / "00-core-engine" / "steve-jobs" / "soul.md").read_text()
        assert "Iterative Core Engine" in md
        assert "core iterative engine" in md.lower()

    def test_parallel_soul_has_daemon_label(self, build_dir):
        md = (build_dir / "02-review-daemons" / "nassim-taleb" / "soul.md").read_text()
        assert "Parallel Review Daemon" in md
        assert "parallel review daemon" in md.lower()

    def test_sequential_soul_has_sequential_label(self, build_dir):
        md = (build_dir / "01-implementation" / "john-carmack" / "soul.md").read_text()
        assert "Sequential" in md

    def test_iterative_has_max_iterations(self, build_dir):
        md = (build_dir / "00-core-engine" / "linus-torvalds" / "soul.md").read_text()
        assert "Up to 3 rounds" in md

    def test_team_name_present(self, build_dir):
        md = (build_dir / "03-final-arbiter" / "jeff-bezos" / "soul.md").read_text()
        assert "The Pragmatist's Workshop" in md


class TestDreamCompanyIdempotency:
    def test_compile_twice_identical(self, tmp_path):
        from compiler.team_compile import compile_team
        dir1 = tmp_path / "run1"
        dir2 = tmp_path / "run2"
        out1 = compile_team(DREAM_COMPANY_TEAM, output_dir=dir1)
        out2 = compile_team(DREAM_COMPANY_TEAM, output_dir=dir2)
        assert len(out1) == len(out2)
        for p1, p2 in zip(out1, out2):
            assert p1.read_text() == p2.read_text()


# ============================================================
# 4. Stage Validation
# ============================================================

class TestStageValidation:
    def test_stage_ref_not_in_souls_rejected(self):
        from compiler.team_compile import validate_team_stages
        team = {
            "routing_strategy": "hybrid",
            "souls": [
                {"soul_ref": "a", "team_role": "R", "directives": "D"},
            ],
            "stages": [
                {"name": "x", "type": "sequential", "souls": ["a", "ghost"]},
            ],
        }
        errors = validate_team_stages(team)
        assert any("ghost" in e for e in errors)

    def test_duplicate_soul_across_stages_rejected(self):
        from compiler.team_compile import validate_team_stages
        team = {
            "routing_strategy": "hybrid",
            "souls": [
                {"soul_ref": "a", "team_role": "R", "directives": "D"},
                {"soul_ref": "b", "team_role": "R", "directives": "D"},
            ],
            "stages": [
                {"name": "x", "type": "sequential", "souls": ["a"]},
                {"name": "y", "type": "sequential", "souls": ["a"]},
            ],
        }
        errors = validate_team_stages(team)
        assert any("multiple stages" in e for e in errors)

    def test_sequential_team_skips_stage_validation(self):
        from compiler.team_compile import validate_team_stages
        team = {"routing_strategy": "sequential", "souls": []}
        errors = validate_team_stages(team)
        assert errors == []

    def test_orphan_soul_not_in_any_stage(self):
        """Soul declared in souls[] but not used in any stage."""
        from compiler.team_compile import validate_team_stages
        team = {
            "routing_strategy": "hybrid",
            "souls": [
                {"soul_ref": "used", "team_role": "R", "directives": "D"},
                {"soul_ref": "orphan", "team_role": "R", "directives": "D"},
            ],
            "stages": [
                {"name": "s", "type": "sequential", "souls": ["used"]},
            ],
        }
        errors = validate_team_stages(team)
        assert any("orphan" in e for e in errors)


# ============================================================
# 5. Backward Compatibility Regression
# ============================================================

class TestBackwardCompatRegression:
    def test_code_review_unchanged(self, tmp_path):
        """code-review sequential team compiles same as before."""
        from compiler.team_compile import compile_team
        code_review = ROOT / "teams" / "code-review" / "team.yaml"
        outputs = compile_team(code_review, output_dir=tmp_path)
        assert len(outputs) == 2
        for out in outputs:
            content = out.read_text()
            assert "## Team Context" in content
            assert "Sequential" in content

    def test_three_kingdoms_unchanged(self, tmp_path):
        """three-kingdoms sequential team compiles same as before."""
        from compiler.team_compile import compile_team
        tk = ROOT / "teams" / "three-kingdoms" / "team.yaml"
        outputs = compile_team(tk, output_dir=tmp_path)
        assert len(outputs) == 6
        for out in outputs:
            content = out.read_text()
            assert "## Team Context" in content


# ============================================================
# 6. CLI
# ============================================================

class TestDreamCompanyCLI:
    def test_compile_cli(self):
        r = subprocess.run(
            [sys.executable, "-m", "compiler.team_compile",
             str(DREAM_COMPANY_TEAM)],
            capture_output=True, text=True, cwd=ROOT,
        )
        assert r.returncode == 0
        assert "dream-company" in r.stdout

    def test_demo_offline_cli(self):
        r = subprocess.run(
            [sys.executable, "demo.py",
             "--team", "dream-company", "--offline"],
            capture_output=True, text=True, cwd=ROOT,
        )
        assert r.returncode == 0
        assert "Hybrid Team Demo" in r.stdout
        assert "core-engine" in r.stdout
        assert "review-daemons" in r.stdout

    def test_openclaw_team_cli(self, tmp_path):
        r = subprocess.run(
            [sys.executable, "-m", "compiler.openclaw",
             "--team", str(DREAM_COMPANY_TEAM),
             "--output-dir", str(tmp_path)],
            capture_output=True, text=True, cwd=ROOT,
        )
        assert r.returncode == 0
        openclaw_dir = tmp_path / "dream-company" / ".openclaw"
        assert openclaw_dir.exists()
        assert (openclaw_dir / "agents.md").exists()

        agents_md = (openclaw_dir / "agents.md").read_text()
        assert "hybrid" in agents_md.lower()
        assert "Stages" in agents_md

        # All 7 souls have subdirs
        for ref in ["steve-jobs", "linus-torvalds", "edward-tufte",
                     "john-carmack", "warren-buffett", "nassim-taleb", "jeff-bezos"]:
            soul_dir = openclaw_dir / ref
            assert soul_dir.exists(), f"Missing OpenClaw subdir: {ref}"
            assert (soul_dir / "soul.md").exists()
            assert (soul_dir / "identity.md").exists()


# ============================================================
# 7. Parallel Merge Format
# ============================================================

class TestParallelMerge:
    def test_build_parallel_merge(self):
        from demo import build_parallel_merge
        outputs = [("soul-a", "output a"), ("soul-b", "output b")]
        merged = build_parallel_merge(outputs)
        assert "===SOULCRAFT_PARALLEL_V1 soul=soul-a===" in merged
        assert "===END_PARALLEL===" in merged
        # Order must be deterministic
        a_pos = merged.index("soul-a")
        b_pos = merged.index("soul-b")
        assert a_pos < b_pos
