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

---

## OpenClaw Team Packaging Contract

- **Input**: `team.yaml` conforming to team schema
- **Output**: `.openclaw/` directory with `agents.md` + per-soul subdirs (`soul.md` + `identity.md`)
- **`agents.md`**: team routing info with pipeline order, roles, and team metadata
- **Per-soul dirs**: team-tuned `soul.md` (from team compiler) + `identity.md` (from base soul)
- **CLI**: `python -m compiler.openclaw --team teams/<id>/team.yaml`
- **Additive**: existing `package_openclaw()` is never modified
- **Hermetic output**: when `output_dir` is provided, all intermediates go there, not repo

## Gate (Phase 3 Three Kingdoms) — ✅ PASSED

- 6 Three Kingdoms base souls extracted: cao-cao, zhuge-liang, sima-yi, guo-jia, xun-yu, zhang-liao
- All 6 pass schema validation and compile to soul.md
- three-kingdoms management team: 6-soul sequential pipeline (COO→CSO→CTO→VP Eng→Red Team→CEO)
- OpenClaw team packaging implemented with TDD (13 new tests, 1 regression, 1 hermetic)
- All tests passing: `pytest tests/ -v` → 169 passed
- Demo `--team three-kingdoms --offline` works end-to-end

