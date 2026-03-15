# SoulCraft: Team Templates Architecture

## Core Concept: Base Soul vs Team-Tuned Soul

Like open-source LLMs (Qwen-base vs Qwen-instruct), SoulCraft provides two modes:

```
souls/cao-cao/
├── soul.md                         ← Base: pure personality, no orchestration
└── teams/three-kingdoms/
    └── soul.md                     ← Team-tuned: personality + orchestration directives
```

**Orchestration is embedded in the persona file.** No separate routing engine. The host framework (OpenClaw/CrewAI) handles execution.

### What team-tuned soul adds

A team-tuned soul.md extends the base soul with:

1. **Chain of command**: Who is superior, who are subordinates
2. **Request routing**: What to handle, what to delegate (with trigger conditions)
3. **Conflict arbitration**: How to resolve disagreements
4. **Trust levels**: Review policies for each team member
5. **Handoff protocol**: How to transfer work between agents

---

## Team #1: Three Kingdoms Management Team 🏯

### Roster

| Role | Character | Team-Tuned Additions |
|------|-----------|---------------------|
| **CEO / Router** | 曹操 (Cao Cao) | Cross-validates all outputs; delegates by domain; final arbiter |
| **COO** | 荀彧 (Xun Yu) | Owns resource allocation; reports to CEO; conservative strategy balance |
| **CSO** | 郭嘉 (Guo Jia) | Owns risk/competition; reports to CEO; aggressive strategy balance |
| **CTO** | 诸葛亮 (Zhuge Liang) | Owns architecture; reports to CEO; adversarial tension with Red Team |
| **VP Eng** | 张辽 (Zhang Liao) | Owns execution; reports to CTO; implements decisions |
| **Red Team** | 司马懿 (Sima Yi) | Audits all outputs; reports to CEO; adversarial tension with CTO |

### Why Cao Cao as CEO

"Suspicion" is a feature, not a bug:
- **Cross-validation**: Asks both Xun Yu and Guo Jia, diffs results → parallel dispatch
- **Trust levels**: Strict review for new agents, autonomy for trusted core → approval policy
- **Hallucination filter**: Kills Yang Xiu = refuses agent overreach → filter unauthorized behavior
- **Fast correction**: Adjusts immediately when errors found → retry + fallback

### Built-in Conflict Dynamics

- CTO (诸葛亮) vs Red Team (司马懿) → healthy adversarial review
- CSO (郭嘉, aggressive) vs COO (荀彧, conservative) → strategic balance
- CEO (曹操) → final arbiter when consensus fails

---

## Team #2: Humanity's Dream Company 🌟 (Phase 2+)

| Role | Character |
|------|-----------|
| CEO / Router | 曹操 or 李世民 |
| Innovation | Elon Musk |
| Investment | Warren Buffett |
| Technology | Linus Torvalds |
| Product | Steve Jobs |
| Strategy | Charlie Munger |

---

## Data Sources for Three Kingdoms

| Character | Primary Source | Parser |
|-----------|--------------|--------|
| 曹操 | 《三国演义》direct quotes, 《短歌行》etc. | ATT + MON |
| 诸葛亮 | 《出师表》, 《三国演义》dialogues | ATT + MON |
| 郭嘉 | 《三国演义》attributed quotes | ATT |
| 荀彧 | 《三国演义》attributed quotes | ATT |
| 张辽 | 《三国演义》battle narratives | ATT |
| 司马懿 | 《三国演义》attributed quotes | ATT |

---

## Implementation Path

```
Phase 1 (MVP): ✅ Build base souls for modern figures (Linus, Buffett)
Phase 2 (Teams): ✅ Team infrastructure
  2a. ✅ Team schema (team_schema.json) — sequential routing
  2b. ✅ Team compiler (team_compile.py) — team.yaml → team-tuned soul.md
  2c. ✅ First team: Code Review (Linus + Buffett) — end-to-end demo
  2d. ✅ demo.py --team — sequential pipeline with handoff protocol
Phase 3 (More Teams & Integration):
  3a. Extract base souls for Three Kingdoms characters from 《三国演义》
  3b. Create team-tuned variants with orchestration directives
  3c. Write three-kingdoms.yaml team manifest
  3d. OpenClaw team-aware packaging
Phase 4: More teams (Dream Company, China Business All-Stars), Web UI
```

