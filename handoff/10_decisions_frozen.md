# Decisions Frozen

- D-001: Record stable decisions here with scope/version.
- D-002: Schema format — JSON Schema for validation + YAML instances for authoring. (scope: soul IR, v0.1.0, 2026-03-15)
- D-003: Provenance granularity — file-level + verbatim quote field. No line numbers. (scope: soul IR, v0.1.0, 2026-03-15)
- D-004: First base souls — hand-extracted from public sources. Linus (TED/LKML/interviews), Buffett (shareholder letters/interviews). (scope: Phase 1 MVP, 2026-03-15)
- D-005: Verification v0 — schema compliance + soul.md compilation completeness. No LLM role-play eval yet. (scope: Phase 1, 2026-03-15)
- D-006: Team routing — Sequential pipeline as base. Hybrid routing (stages with sequential/iterative/parallel types) added in Phase 4. Existing sequential teams unchanged. (scope: Phase 2→Phase 4, 2026-03-15→2026-03-16)
- D-007: Team context injection — Append `## Team Context` section to generated team-tuned soul.md. Base soul files never modified. (scope: Phase 2 Teams, 2026-03-15)
- D-008: No trust_level in Phase 2 — minimal team schema. Add when real permission system exists. (scope: Phase 2 Teams, 2026-03-15)
- D-009: Hybrid routing — stages array with type=sequential|iterative|parallel. souls[] is metadata authority (team_role + directives); stages[] controls execution order only. Same soul cannot appear in multiple stages. (scope: Phase 4 Teams, 2026-03-16)
- D-010: Iterative stage — cumulative context buffer, hard max_iterations limit (default 3). No early convergence detection in Phase 4. (scope: Phase 4 Teams, 2026-03-16)
- D-011: Parallel stage — deterministic delimiter merge, array-order = merge-order. No conflict resolution in Phase 4. (scope: Phase 4 Teams, 2026-03-16)
