# Contracts

## Soul IR Schema Contract (v0.1.0)

- **Format**: JSON Schema at `schemas/soul_schema.json`, instances in YAML at `souls/<id>/soul.yaml`
- **Required top-level keys**: `metadata`, `layers`
- **Layers**: A (Soul), B (Cognition), C (Expression), D (Behavior), E (Meta) — all required
- **Provenance model**: `{ source_file: string, quote: string }` — file-level + verbatim quote, no line numbers
- **Version**: semver (`x.y.z`) in `metadata.version`
- **ID**: URL-safe slug (`^[a-z0-9][a-z0-9-]*$`) in `metadata.id`, matches directory name

## Compiler Contract

- **Input**: `soul.yaml` conforming to soul schema
- **Output**: `soul.md` in OpenClaw-compatible format with role directive
- **Validation**: schema validation runs before compilation; invalid YAML → exit code 1, no output
- **Required sections in soul.md**: Core Identity, Core Beliefs, Values, Knowledge Frameworks, Catchphrases, Response Rules, Blind Spots, Conflict Style, Basic Info
- **Idempotency**: compiling the same YAML twice produces byte-identical output

## Gate (Phase 1 MVP)

- ≥2 base souls (Linus, Buffett) extracted end-to-end
- All tests passing: `pytest tests/ -v` → 0 failures
- Both soul.md files compiled successfully
