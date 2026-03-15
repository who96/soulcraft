# Findings: Phase 1 Audit Results

## Codex Audit (Independent)
- **Item 3 (Schema):** PASS — schema exists, validates, provenance model works but lacks confidence/parser_type
- **Item 4 (Base Souls):** PARTIAL — souls exist but "end-to-end" overstated (hand-authored); 16 source files referenced but missing from repo; compiler drops major chunks
- **Item 5 (Verification):** PARTIAL — structural tests exist but only 1 synthetic holdout; no behavioral eval; no assertion soul.md matches compiler output
- **Item 6 (Compiler+Demo):** PARTIAL — compiler+demo work but not OpenClaw-specific; compiler lossy (drops 6+ sub-sections)

## Gemini Audit (Independent)  
- **Item 3:** PASS with warnings — provenance model thin, no URI/span/location
- **Item 4:** PARTIAL — 80% data loss in compilation; source files missing
- **Item 5:** FAIL — tests are pipeline tests not soul tests; holdout set meaningless for compiler
- **Item 6:** PARTIAL — basic text templater; no advanced prompt engineering

## Key Findings

### Critical Bug: Compiler Lossy
Sections dropped by compiler (verified by Codex script):
```
knowledge_sources     → NOT in soul.md ❌
original_concepts     → NOT in soul.md ❌
rhetoric_style        → NOT in soul.md ❌
humor_style           → NOT in soul.md ❌
emotional_triggers    → NOT in soul.md ❌
argument_structure    → NOT in soul.md ❌
source_file names     → NOT in soul.md ❌
```

### Source Files Missing
Linus: 7 files missing (ted_talk_2016.txt, lkml_*.txt, interview_*.txt, just_for_fun_quotes.txt)
Buffett: 9 files missing (shareholder_letter_*.txt, cnbc_*.txt, annual_meeting_*.txt, etc.)

These are references to public materials used during hand-extraction. Files contain selected quotes, not the full source documents. Decision: mark as `reference_only` in metadata rather than include verbatim transcripts.

### Holdout Set Weakness
Only 1 synthetic soul (test-philosopher). Not enough to prove generalization. Need 2+ more diverse holdout souls.
