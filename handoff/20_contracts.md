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

## Gate (Phase 1 MVP) — ✅ PASSED

- ≥2 base souls (Linus, Buffett) extracted end-to-end
- All tests passing: `pytest tests/ -v` → 0 failures
- Both soul.md files compiled successfully

---

## Team IR Schema Contract (v0.1.0)

- **Format**: JSON Schema at `schemas/team_schema.json`, instances in YAML at `teams/<id>/team.yaml`
- **Required top-level keys**: `metadata`, `routing_strategy`, `souls`
- **Routing**: `sequential` only (array order = execution order, no `order` field)
- **Souls**: array of `{ soul_ref, team_role, directives }`, minItems 2
- **ID**: URL-safe slug, matches directory name under `teams/`

## Team Compiler Contract

- **Input**: `team.yaml` conforming to team schema + base `soul.yaml` files in `souls/`
- **Output**: team-tuned `soul.md` files at `teams/<team-id>/build/<soul-id>/soul.md`
- **Structure**: base soul.md + appended `## Team Context` section
- **Validation**: structural (JSON Schema) + semantic (soul_ref existence, no duplicates)
- **Idempotency**: compiling the same team.yaml twice produces byte-identical output
- **No base pollution**: base `souls/` directory is never modified

## Demo Contract

- **Single soul**: `python demo.py --soul <id>` — loads `souls/<id>/soul.md`
- **Team mode**: `python demo.py --team <id>` — loads `teams/<id>/build/*/soul.md`
- **Mutual exclusion**: `--soul` and `--team` cannot be used together
- **Handoff format V1**: prior soul output wrapped in `===SOULCRAFT_HANDOFF_V1 soul=<id>===...===END_HANDOFF===`
- **Offline**: `--offline` prints prompts without API call

## Gate (Phase 2 Teams) — ✅ PASSED

- Team schema defined and validates
- ≥1 team (code-review: Linus + Buffett) compiled and tested
- All tests passing: `pytest tests/ -v` → 0 failures (53 Phase 1 + 32 Phase 2)
- Demo `--team code-review --offline` works end-to-end
