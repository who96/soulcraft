"""SoulCraft Team Compiler — compile team.yaml → team-tuned soul.md files.

A team-tuned soul.md = base soul.md + appended Team Context section.
The base soul files are never modified; team output goes to teams/<id>/build/.

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

from compiler.compile import compile_soul_md, load_soul, validate as validate_soul

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


def compile_team_context(team: dict, soul_idx: int) -> str:
    """Generate the ## Team Context markdown section for a specific soul."""
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


def compile_team(team_path: Path, souls_dir: Path | None = None,
                 output_dir: Path | None = None) -> list[Path]:
    """Compile a team.yaml into team-tuned soul.md files.

    Returns list of output soul.md paths.
    """
    souls_dir = souls_dir or SOULS_DIR
    schema = load_team_schema()
    team = load_team(team_path)

    # Structural validation
    errors = validate_team(team, schema)
    if errors:
        print(f"  ❌ Schema validation failed ({len(errors)} errors):")
        for err in errors:
            print(f"    - {err}")
        raise SystemExit(1)

    # Semantic validation
    ref_errors = validate_team_refs(team, souls_dir)
    if ref_errors:
        print(f"  ❌ Reference validation failed ({len(ref_errors)} errors):")
        for err in ref_errors:
            print(f"    - {err}")
        raise SystemExit(1)

    # Load soul schema for soul validation
    with open(SOUL_SCHEMA_PATH) as f:
        soul_schema = json.load(f)

    # Determine output directory
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

        # Validate soul
        soul_errors = validate_soul(soul, soul_schema)
        if soul_errors:
            print(f"  ❌ Soul '{ref}' validation failed:")
            for err in soul_errors:
                print(f"    - {err}")
            raise SystemExit(1)

        # Compile base soul.md
        base_md = compile_soul_md(soul)

        # Append team context
        team_context = compile_team_context(team, i)
        team_tuned_md = base_md + team_context

        # Write output
        soul_build_dir = build_dir / ref
        soul_build_dir.mkdir(parents=True, exist_ok=True)
        out_path = soul_build_dir / "soul.md"
        out_path.write_text(team_tuned_md)
        output_paths.append(out_path)

    return output_paths


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
