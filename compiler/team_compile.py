"""SoulCraft Team Compiler — compile team.yaml → team-tuned soul.md files.

A team-tuned soul.md = base soul.md + appended Team Context section.
The base soul files are never modified; team output goes to teams/<id>/build/.

Supports two routing strategies:
  - sequential: pipeline in array order (Phase 2)
  - hybrid: stages with sequential/iterative/parallel types (Phase 4)

Usage:
    python -m compiler.team_compile teams/code-review/team.yaml
    python -m compiler.team_compile --all
"""

import argparse
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from compiler.compile import compile_soul_md, load_soul, validate

TEAM_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "team_schema.json"
SOUL_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "soul_schema.json"
SOULS_DIR = Path(__file__).resolve().parent.parent / "souls"
TEAMS_DIR = Path(__file__).resolve().parent.parent / "teams"


def load_team_schema() -> dict:
    with open(TEAM_SCHEMA_PATH) as f:
        return json.load(f)


def load_team(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def validate_team(team: dict, schema: dict) -> list[str]:
    """Structural validation via JSON Schema."""
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(team), key=lambda e: list(e.absolute_path))
    return [f"{'.'.join(str(p) for p in e.absolute_path)}: {e.message}" for e in errors]


def validate_team_refs(team: dict, souls_dir: Path) -> list[str]:
    """Semantic validation: check soul_ref existence and uniqueness."""
    errors = []
    seen_refs = set()
    for i, soul_entry in enumerate(team.get("souls", [])):
        ref = soul_entry.get("soul_ref", "")
        soul_yaml = souls_dir / ref / "soul.yaml"
        if not soul_yaml.exists():
            errors.append(f"souls[{i}].soul_ref: '{ref}' not found at {soul_yaml}")
        if ref in seen_refs:
            errors.append(f"souls[{i}].soul_ref: '{ref}' is duplicated")
        seen_refs.add(ref)
    return errors


def validate_team_stages(team: dict) -> list[str]:
    """Semantic validation for hybrid teams: stages refs must exist in souls."""
    if team.get("routing_strategy") != "hybrid":
        return []
    errors = []
    soul_refs = {s["soul_ref"] for s in team.get("souls", [])}
    seen_in_stages = set()
    for i, stage in enumerate(team.get("stages", [])):
        for j, ref in enumerate(stage.get("souls", [])):
            if ref not in soul_refs:
                errors.append(
                    f"stages[{i}].souls[{j}]: '{ref}' not found in top-level souls"
                )
            if ref in seen_in_stages:
                errors.append(
                    f"stages[{i}].souls[{j}]: '{ref}' appears in multiple stages"
                )
            seen_in_stages.add(ref)
    # Completeness: every soul must appear in some stage
    orphans = soul_refs - seen_in_stages
    for ref in sorted(orphans):
        errors.append(f"soul '{ref}' declared in souls[] but not used in any stage")
    return errors


def compile_team_context(team: dict, soul_idx: int) -> str:
    """Generate the ## Team Context markdown section for a specific soul (sequential)."""
    meta = team["metadata"]
    souls = team["souls"]
    current = souls[soul_idx]
    total = len(souls)
    position = soul_idx + 1  # 1-based

    lines = [
        "",
        "---",
        "",
        "## Team Context",
        "",
        "> Team-tuned persona. Follow these additional directives in team mode.",
        "",
        f"**Team:** {meta['name']} — {meta['description'].strip()}",
        f"**Your Role:** {current['team_role']}",
        f"**Routing:** Sequential — you are #{position} of {total} in the pipeline.",
        "",
        "### Teammates",
    ]

    for j, s in enumerate(souls):
        if j == soul_idx:
            continue
        lines.append(f"- **{s['soul_ref']}** (#{j + 1}): {s['team_role']}")

    lines.extend([
        "",
        "### Your Directives",
        current["directives"].strip(),
        "",
        "### Handoff Protocol",
        "- Read all previous teammates' outputs before responding.",
        "- Your response will be passed to the next teammate (if any).",
        "- Stay in character. Do not reference the team mechanism itself.",
        "",
    ])

    return "\n".join(lines)


def compile_hybrid_team_context(
    team: dict, soul_ref: str, stage: dict, stage_idx: int, total_stages: int,
) -> str:
    """Generate ## Team Context for a soul in a hybrid team."""
    meta = team["metadata"]
    souls_map = {s["soul_ref"]: s for s in team["souls"]}
    current = souls_map[soul_ref]
    stage_type = stage["type"]
    stage_name = stage["name"]
    stage_souls = stage["souls"]

    type_labels = {
        "sequential": "Sequential",
        "iterative": "Iterative Core Engine",
        "parallel": "Parallel Review Daemon",
    }
    type_label = type_labels[stage_type]

    lines = [
        "",
        "---",
        "",
        "## Team Context",
        "",
        "> Team-tuned persona. Follow these additional directives in team mode.",
        "",
        f"**Team:** {meta['name']} — {meta['description'].strip()}",
        f"**Your Role:** {current['team_role']}",
        f"**Stage:** {stage_name} ({type_label}) — stage {stage_idx + 1} of {total_stages}",
    ]

    if stage_type == "iterative":
        max_iter = stage.get("max_iterations", 3)
        lines.append(f"**Iterations:** Up to {max_iter} rounds of iterative refinement.")
        lines.append("")
        lines.append(
            "> You are in the core iterative engine. Collaborate intensively "
            "with your stage teammates to refine the output through multiple rounds."
        )
    elif stage_type == "parallel":
        lines.append("")
        lines.append(
            "> You are a parallel review daemon. Produce your analysis independently. "
            "Your output will be merged with other parallel reviewers for the next stage."
        )

    lines.append("")
    lines.append("### Stage Teammates")
    for ref in stage_souls:
        if ref == soul_ref:
            continue
        s = souls_map[ref]
        lines.append(f"- **{ref}**: {s['team_role']}")

    lines.append("")
    lines.append("### All Team Members")
    for s in team["souls"]:
        if s["soul_ref"] == soul_ref:
            continue
        lines.append(f"- **{s['soul_ref']}**: {s['team_role']}")

    lines.extend([
        "",
        "### Your Directives",
        current["directives"].strip(),
        "",
        "### Handoff Protocol",
        "- Read all previous outputs before responding.",
        "- Your response will be passed to the next stage (if any).",
        "- Stay in character. Do not reference the team mechanism itself.",
        "",
    ])

    return "\n".join(lines)


def _validate_and_load(team_path: Path, souls_dir: Path):
    """Shared validation for both sequential and hybrid teams."""
    schema = load_team_schema()
    team = load_team(team_path)

    errors = validate_team(team, schema)
    if errors:
        print(f"  ❌ Schema validation failed ({len(errors)} errors):")
        for err in errors:
            print(f"    - {err}")
        raise SystemExit(1)

    ref_errors = validate_team_refs(team, souls_dir)
    if ref_errors:
        print(f"  ❌ Reference validation failed ({len(ref_errors)} errors):")
        for err in ref_errors:
            print(f"    - {err}")
        raise SystemExit(1)

    stage_errors = validate_team_stages(team)
    if stage_errors:
        print(f"  ❌ Stage validation failed ({len(stage_errors)} errors):")
        for err in stage_errors:
            print(f"    - {err}")
        raise SystemExit(1)

    with open(SOUL_SCHEMA_PATH) as f:
        soul_schema = json.load(f)

    return team, soul_schema


def _compile_sequential(team: dict, team_path: Path, souls_dir: Path,
                        soul_schema: dict, output_dir: Path | None) -> list[Path]:
    """Compile a sequential team — original Phase 2 logic, UNTOUCHED."""
    team_id = team["metadata"]["id"]
    if output_dir:
        build_dir = output_dir / team_id / "build"
    else:
        build_dir = team_path.parent / "build"

    output_paths = []
    for i, soul_entry in enumerate(team["souls"]):
        ref = soul_entry["soul_ref"]
        soul_path = souls_dir / ref / "soul.yaml"
        soul = load_soul(soul_path)

        soul_errors = validate(soul, soul_schema)
        if soul_errors:
            print(f"  ❌ Soul '{ref}' validation failed:")
            for err in soul_errors:
                print(f"    - {err}")
            raise SystemExit(1)

        base_md = compile_soul_md(soul)
        team_context = compile_team_context(team, i)
        team_tuned_md = base_md + team_context

        soul_build_dir = build_dir / ref
        soul_build_dir.mkdir(parents=True, exist_ok=True)
        out_path = soul_build_dir / "soul.md"
        out_path.write_text(team_tuned_md)
        output_paths.append(out_path)

    return output_paths


def _compile_hybrid(team: dict, team_path: Path, souls_dir: Path,
                    soul_schema: dict, output_dir: Path | None) -> list[Path]:
    """Compile a hybrid team — stage-scoped output directories."""
    team_id = team["metadata"]["id"]
    if output_dir:
        build_dir = output_dir / team_id / "build"
    else:
        build_dir = team_path.parent / "build"

    stages = team["stages"]
    total_stages = len(stages)
    output_paths = []

    for stage_idx, stage in enumerate(stages):
        stage_name = stage["name"]
        stage_dir_name = f"{stage_idx:02d}-{stage_name}"

        for ref in stage["souls"]:
            soul_path = souls_dir / ref / "soul.yaml"
            soul = load_soul(soul_path)

            soul_errors = validate(soul, soul_schema)
            if soul_errors:
                print(f"  ❌ Soul '{ref}' validation failed:")
                for err in soul_errors:
                    print(f"    - {err}")
                raise SystemExit(1)

            base_md = compile_soul_md(soul)
            team_context = compile_hybrid_team_context(
                team, ref, stage, stage_idx, total_stages,
            )
            team_tuned_md = base_md + team_context

            soul_build_dir = build_dir / stage_dir_name / ref
            soul_build_dir.mkdir(parents=True, exist_ok=True)
            out_path = soul_build_dir / "soul.md"
            out_path.write_text(team_tuned_md)
            output_paths.append(out_path)

    return output_paths


def compile_team(team_path: Path, souls_dir: Path | None = None,
                 output_dir: Path | None = None) -> list[Path]:
    """Compile a team.yaml into team-tuned soul.md files.

    Dispatches to sequential or hybrid compilation based on routing_strategy.
    Returns list of output soul.md paths.
    """
    souls_dir = souls_dir or SOULS_DIR
    team, soul_schema = _validate_and_load(team_path, souls_dir)

    routing = team["routing_strategy"]
    if routing == "sequential":
        return _compile_sequential(team, team_path, souls_dir, soul_schema, output_dir)
    elif routing == "hybrid":
        return _compile_hybrid(team, team_path, souls_dir, soul_schema, output_dir)
    else:
        print(f"  ❌ Unknown routing_strategy: '{routing}'")
        raise SystemExit(1)


def find_all_teams() -> list[Path]:
    return sorted(TEAMS_DIR.glob("*/team.yaml"))


def main():
    parser = argparse.ArgumentParser(
        description="Compile team.yaml → team-tuned soul.md files"
    )
    parser.add_argument("team_files", nargs="*", help="Path(s) to team.yaml")
    parser.add_argument("--all", action="store_true", help="Compile all teams")
    parser.add_argument("--output-dir", type=Path, help="Output base directory")
    args = parser.parse_args()

    if args.all:
        team_files = find_all_teams()
    else:
        team_files = [Path(f) for f in args.team_files]

    if not team_files:
        print("No team files specified. Use --all or provide paths.", file=sys.stderr)
        sys.exit(1)

    for team_path in team_files:
        print(f"Compiling team: {team_path}")
        outputs = compile_team(team_path, output_dir=args.output_dir)
        for out in outputs:
            print(f"  📝 Team-tuned → {out}")


if __name__ == "__main__":
    main()
