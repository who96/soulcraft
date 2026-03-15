# Task Plan: Phase 1 MVP Completion — Fix Gaps from Codex/Gemini Audit

## Goal
Fix all gaps identified by Codex and Gemini in Phase 1 Steps 3-6: lossy compiler, weak holdout set, missing OpenClaw packaging. Every sub-task gets independent Codex+Gemini review before commit+push.

## Current Phase
Phase 1

## Phases

### Phase 1: Fix Lossy Compiler
The compiler drops `knowledge_sources`, `original_concepts`, `rhetoric_style`, `humor_style`, `emotional_triggers`, `argument_structure`, and all provenance references from the compiled soul.md output. Fix this.
- [ ] Add Knowledge Sources section to compiler output
- [ ] Add Original Concepts section to compiler output
- [ ] Add Rhetoric & Humor Style section to compiler output
- [ ] Add Emotional Triggers section to compiler output
- [ ] Add Argument Structure section to compiler output
- [ ] Add Provenance References appendix (source files + key quotes)
- [ ] Update REQUIRED_HEADINGS in test_compiler.py
- [ ] Run pytest — all tests pass
- [ ] Codex review ✅
- [ ] Gemini review ✅
- [ ] Commit: "fix(compiler): emit all ABCDE layers in soul.md"
- **Status:** pending

### Phase 2: Strengthen Holdout Test Set
Currently only 1 synthetic soul. Add 2+ more with different profiles to prove generalization.
- [ ] Create holdout soul: Marcus Aurelius (stoic philosopher, real-ish data)
- [ ] Create holdout soul: Ada Lovelace (mathematician/programmer)
- [ ] Verify all holdout souls pass schema + compilation
- [ ] Run pytest — all tests still pass
- [ ] Codex review ✅
- [ ] Gemini review ✅
- [ ] Commit: "test: add holdout souls for verification generalization"
- **Status:** pending

### Phase 3: Add OpenClaw Packaging Flow
Add `.openclaw/` directory packaging so soul.md can be deployed directly into an OpenClaw project.
- [ ] Create `compiler/openclaw.py` — package soul.md + identity.md + agents.md
- [ ] Add `--target openclaw` flag to compiler CLI
- [ ] Add test for OpenClaw packaging output
- [ ] Test with `python -m compiler.compile --all --target openclaw`
- [ ] Codex review ✅
- [ ] Gemini review ✅
- [ ] Commit: "feat(compiler): add OpenClaw .openclaw/ packaging"
- **Status:** pending

### Phase 4: Final Push
- [ ] Run full pytest suite
- [ ] git add + commit + push all Phase 1 work
- **Status:** pending

## Key Questions
1. Should provenance quotes appear in the soul.md body or in a separate appendix? → Appendix (keeps prompt token-efficient but auditable)
2. Should OpenClaw packaging create a full `.openclaw/` dir or just adapt soul.md naming? → Full directory

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Provenance in appendix | Keeps system prompt focused; LLM doesn't need to read every source file name |
| Keep holdout souls synthetic | Real public figure data would need same provenance rigor as base souls |
| OpenClaw = directory packaging | Matches the `.openclaw/` convention described in README |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|       | 1       |            |

## Notes
- Update phase status as you progress: pending → in_progress → complete
- Re-read this plan before major decisions
- Log ALL errors
- Each phase gets Codex + Gemini review before commit
