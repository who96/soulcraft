"""Tests specific to Three Kingdoms souls and team — Phase 3."""

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from compiler.compile import compile_soul_md, load_schema, load_soul, validate
from compiler.team_compile import compile_team, load_team

from tests.conftest import ROOT, SOULS_DIR

TEAMS_DIR = ROOT / "teams"
THREE_KINGDOMS_SOULS = [
    "cao-cao", "zhuge-liang", "sima-yi", "guo-jia", "xun-yu", "zhang-liao",
]


class TestThreeKingdomsProvenance:
    """Verify Chinese quote provenance in Three Kingdoms souls."""

    @pytest.fixture(params=THREE_KINGDOMS_SOULS)
    def soul_data(self, request):
        soul_path = SOULS_DIR / request.param / "soul.yaml"
        return request.param, load_soul(soul_path)

    def test_worldview_quotes_contain_chinese(self, soul_data):
        name, soul = soul_data
        for item in soul["layers"]["A"]["worldview"]:
            quote = item["provenance"]["quote"]
            # Chinese characters are in CJK Unified Ideographs range
            has_chinese = any('\u4e00' <= ch <= '\u9fff' for ch in quote)
            assert has_chinese, (
                f"{name}: worldview provenance quote missing Chinese: {quote[:50]}"
            )

    def test_catchphrase_quotes_contain_chinese(self, soul_data):
        name, soul = soul_data
        for cp in soul["layers"]["C"]["catchphrases"]:
            quote = cp["provenance"]["quote"]
            has_chinese = any('\u4e00' <= ch <= '\u9fff' for ch in quote)
            assert has_chinese, (
                f"{name}: catchphrase provenance quote missing Chinese: {quote[:50]}"
            )

    def test_all_scenarios_have_provenance(self, soul_data):
        name, soul = soul_data
        for s in soul["layers"]["D"]["scenarios"]:
            assert s["provenance"]["source_file"], f"{name}: scenario missing source_file"
            assert s["provenance"]["quote"], f"{name}: scenario missing quote"


class TestThreeKingdomsTeamCompilation:
    """Test three-kingdoms team compilation correctness."""

    def test_team_produces_6_files(self, tmp_path):
        team_path = TEAMS_DIR / "three-kingdoms" / "team.yaml"
        outputs = compile_team(team_path, output_dir=tmp_path)
        assert len(outputs) == 6

    def test_all_soul_refs_have_output(self, tmp_path):
        team_path = TEAMS_DIR / "three-kingdoms" / "team.yaml"
        compile_team(team_path, output_dir=tmp_path)
        build_dir = tmp_path / "three-kingdoms" / "build"
        for soul_id in THREE_KINGDOMS_SOULS:
            assert (build_dir / soul_id / "soul.md").exists(), (
                f"Missing team-tuned soul.md for {soul_id}"
            )

    def test_team_context_in_every_output(self, tmp_path):
        team_path = TEAMS_DIR / "three-kingdoms" / "team.yaml"
        compile_team(team_path, output_dir=tmp_path)
        build_dir = tmp_path / "three-kingdoms" / "build"
        for soul_id in THREE_KINGDOMS_SOULS:
            content = (build_dir / soul_id / "soul.md").read_text()
            assert "## Team Context" in content, (
                f"{soul_id} team-tuned soul.md missing Team Context"
            )


class TestThreeKingdomsIdempotency:
    """Compile twice → byte-identical."""

    def test_compile_twice_identical(self, tmp_path):
        team_path = TEAMS_DIR / "three-kingdoms" / "team.yaml"
        dir1 = tmp_path / "run1"
        dir2 = tmp_path / "run2"
        compile_team(team_path, output_dir=dir1)
        compile_team(team_path, output_dir=dir2)
        build1 = dir1 / "three-kingdoms" / "build"
        build2 = dir2 / "three-kingdoms" / "build"
        for soul_id in THREE_KINGDOMS_SOULS:
            md1 = (build1 / soul_id / "soul.md").read_text()
            md2 = (build2 / soul_id / "soul.md").read_text()
            assert md1 == md2, f"Non-idempotent compilation for {soul_id}"


class TestThreeKingdomsDemoCLI:
    """Test demo --team three-kingdoms --offline works."""

    def test_demo_offline_runs(self):
        result = subprocess.run(
            [sys.executable, "demo.py", "--team", "three-kingdoms", "--offline"],
            capture_output=True, text=True, cwd=ROOT,
        )
        assert result.returncode == 0
        # Should produce some output with soul names
        assert "Pipeline" in result.stdout or "three-kingdoms" in result.stdout.lower()
