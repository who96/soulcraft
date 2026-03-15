"""SoulCraft Compiler — compile soul.yaml → soul.md (OpenClaw format).

Usage:
    python -m compiler.compile souls/linus-torvalds/soul.yaml
    python -m compiler.compile --all
"""

import argparse
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, ValidationError

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "soul_schema.json"
SOULS_DIR = Path(__file__).resolve().parent.parent / "souls"


def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def load_soul(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def validate(soul: dict, schema: dict) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(soul), key=lambda e: list(e.absolute_path))
    return [f"{'.'.join(str(p) for p in e.absolute_path)}: {e.message}" for e in errors]


def compile_identity(layer_a: dict) -> str:
    return layer_a["identity"]["description"].strip()


def compile_beliefs(layer_a: dict) -> str:
    lines = []
    for i, item in enumerate(layer_a["worldview"], 1):
        lines.append(f"{i}. {item['content'].strip()}")
    return "\n".join(lines)


def compile_values(layer_a: dict) -> str:
    affirm = [v for v in layer_a["values"] if v["stance"] == "affirm"]
    reject = [v for v in layer_a["values"] if v["stance"] == "reject"]
    lines = []
    if affirm:
        lines.append("**Affirm:**")
        for v in affirm:
            lines.append(f"- {v['content'].strip()}")
    if reject:
        lines.append("\n**Reject:**")
        for v in reject:
            lines.append(f"- {v['content'].strip()}")
    return "\n".join(lines)


def compile_catchphrases(layer_c: dict) -> str:
    lines = []
    for cp in layer_c["catchphrases"]:
        lines.append(f"- **\"{cp['phrase']}\"** — {cp['context']}")
    return "\n".join(lines)


def compile_scenarios(layer_d: dict) -> str:
    lines = []
    for s in layer_d["scenarios"]:
        lines.append(f"- **{s['trigger']}** → {s['response'].strip()}")
    return "\n".join(lines)


def compile_blind_spots(layer_e: dict) -> str:
    lines = []
    bs = layer_e["blind_spots"]
    for item in bs.get("explicit", []):
        lines.append(f"- {item['content'].strip()}")
    for item in bs.get("inferred", []):
        lines.append(f"- _{item['content'].strip()}_ (inferred, confidence: {item['confidence']})")
    return "\n".join(lines)


def compile_conflict_style(layer_e: dict) -> str:
    cs = layer_e["conflict_style"]
    lines = [
        f"**Default strategy:** {cs['default_strategy']['content'].strip()}",
        "",
        "**Tactics:**",
    ]
    for t in cs.get("tactics", []):
        lines.append(f"- {t['content'].strip()}")
    if "escalation_path" in cs:
        lines.append(f"\n**Escalation path:** {cs['escalation_path']['content'].strip()}")
    if "concession_conditions" in cs:
        lines.append(f"\n**Concession conditions:** {cs['concession_conditions']['content'].strip()}")
    lines.append("\n**Non-negotiable:**")
    for nn in cs.get("non_negotiable", []):
        lines.append(f"- {nn['content'].strip()}")
    if "recovery_mode" in cs:
        lines.append(f"\n**Recovery mode:** {cs['recovery_mode']['content'].strip()}")
    return "\n".join(lines)


def compile_frameworks(layer_b: dict) -> str:
    lines = []
    for fw in layer_b["frameworks"]:
        lines.append(f"### {fw['name']}\n{fw['description'].strip()}\n")
    return "\n".join(lines)


def compile_knowledge_sources(layer_b: dict) -> str:
    sources = layer_b.get("knowledge_sources", [])
    if not sources:
        return ""
    lines = []
    for ks in sources:
        attitude = ks.get("attitude", "").strip()
        lines.append(f"- **{ks['name']}** ({ks['type']}): {attitude}")
    return "\n".join(lines)


def compile_original_concepts(layer_b: dict) -> str:
    concepts = layer_b.get("original_concepts", [])
    if not concepts:
        return ""
    lines = []
    for oc in concepts:
        lines.append(f"### {oc['name']}\n{oc['description'].strip()}\n")
    return "\n".join(lines)


def compile_expression_style(layer_c: dict) -> str:
    parts = []
    if "rhetoric_style" in layer_c:
        parts.append(f"**Rhetoric:** {layer_c['rhetoric_style']['content'].strip()}")
    if "humor_style" in layer_c:
        parts.append(f"**Humor:** {layer_c['humor_style']['content'].strip()}")
    if "argument_structure" in layer_c:
        parts.append(f"**Argument structure:** {layer_c['argument_structure']['content'].strip()}")
    return "\n\n".join(parts)


def compile_emotional_triggers(layer_c: dict) -> str:
    triggers = layer_c.get("emotional_triggers", [])
    if not triggers:
        return ""
    lines = []
    for et in triggers:
        response = et.get("response", "").strip()
        lines.append(f"- **{et['trigger']}** → {response}")
    return "\n".join(lines)


def compile_provenance_appendix(soul: dict) -> str:
    """Collect all unique source files and key quotes for auditability."""
    sources = set()
    quotes = []
    _walk_provenance(soul, sources, quotes)
    if not sources:
        return ""
    lines = ["### Source Files"]
    for src in sorted(sources):
        lines.append(f"- `{src}`")
    # Include up to 5 key quotes for grounding
    if quotes:
        lines.append("\n### Key Quotes")
        seen = set()
        for q in quotes:
            if q not in seen and len(seen) < 8:
                lines.append(f'- "{q}"')
                seen.add(q)
    return "\n".join(lines)


def _walk_provenance(obj, sources: set, quotes: list):
    """Recursively extract provenance data from any nested dict/list."""
    if isinstance(obj, dict):
        if "provenance" in obj:
            prov = obj["provenance"]
            if isinstance(prov, dict):
                if "source_file" in prov:
                    sources.add(prov["source_file"])
                if "quote" in prov:
                    quotes.append(prov["quote"])
        for v in obj.values():
            _walk_provenance(v, sources, quotes)
    elif isinstance(obj, list):
        for item in obj:
            _walk_provenance(item, sources, quotes)


def compile_soul_md(soul: dict) -> str:
    meta = soul["metadata"]
    a = soul["layers"]["A"]
    b = soul["layers"]["B"]
    c = soul["layers"]["C"]
    d = soul["layers"]["D"]
    e = soul["layers"]["E"]

    name = meta["name"]

    sections = [
        f"# {name}\n",
        f"> SoulCraft v{meta['version']} | extraction: {meta.get('extraction_method', 'unknown')}\n",
        f"You are **{name}**. From this moment, all your responses must be in "
        f"{name}'s identity, tone, knowledge system, and expression habits. "
        f"Do not respond as an assistant. Do not explain that you are playing a role. "
        f"Do not break character.\n",
        "---\n",
        f"## Core Identity\n\n{compile_identity(a)}\n",
        f"## Core Beliefs\n\n{compile_beliefs(a)}\n",
        f"## Values\n\n{compile_values(a)}\n",
        f"## Knowledge Frameworks\n\n{compile_frameworks(b)}\n",
    ]

    # Layer B: Knowledge Sources + Original Concepts
    ks_text = compile_knowledge_sources(b)
    if ks_text:
        sections.append(f"## Key Influences\n\n{ks_text}\n")
    oc_text = compile_original_concepts(b)
    if oc_text:
        sections.append(f"## Original Ideas\n\n{oc_text}\n")

    # Layer C: Catchphrases + Expression Style + Emotional Triggers
    sections.append(f"## Catchphrases & Expression Habits\n\n{compile_catchphrases(c)}\n")
    es_text = compile_expression_style(c)
    if es_text:
        sections.append(f"## Expression Style\n\n{es_text}\n")
    et_text = compile_emotional_triggers(c)
    if et_text:
        sections.append(f"## Emotional Triggers\n\n{et_text}\n")

    # Layer D + E
    sections.extend([
        f"## Response Rules\n\n{compile_scenarios(d)}\n",
        f"## Blind Spots\n\n{compile_blind_spots(e)}\n",
        f"## Conflict Style\n\n{compile_conflict_style(e)}\n",
    ])

    # Provenance appendix
    prov_text = compile_provenance_appendix(soul)
    if prov_text:
        sections.append(f"---\n\n## Provenance\n\n{prov_text}\n")

    sections.append(
        f"---\n\n## Basic Info\n\n- **Name:** {name}\n- **Soul ID:** {meta['id']}\n- **Version:** {meta['version']}\n"
    )

    return "\n".join(sections)


def find_all_souls() -> list[Path]:
    return sorted(SOULS_DIR.glob("*/soul.yaml"))


def main():
    parser = argparse.ArgumentParser(description="Compile soul.yaml → soul.md")
    parser.add_argument("soul_files", nargs="*", help="Path(s) to soul.yaml file(s)")
    parser.add_argument("--all", action="store_true", help="Compile all souls in souls/")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, don't compile")
    parser.add_argument("--output-dir", type=Path, help="Output directory (default: same as input)")
    args = parser.parse_args()

    schema = load_schema()

    if args.all:
        soul_files = find_all_souls()
    else:
        soul_files = [Path(f) for f in args.soul_files]

    if not soul_files:
        print("No soul files specified. Use --all or provide paths.", file=sys.stderr)
        sys.exit(1)

    exit_code = 0
    for soul_path in soul_files:
        print(f"Processing: {soul_path}")
        soul = load_soul(soul_path)

        errors = validate(soul, schema)
        if errors:
            print(f"  ❌ Validation failed ({len(errors)} errors):")
            for err in errors:
                print(f"    - {err}")
            exit_code = 1
            continue

        print("  ✅ Schema validation passed")

        if args.validate_only:
            continue

        md_content = compile_soul_md(soul)
        output_dir = args.output_dir or soul_path.parent
        output_path = output_dir / "soul.md"
        output_path.write_text(md_content)
        print(f"  📝 Compiled → {output_path}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
