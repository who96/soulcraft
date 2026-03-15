# 🔮 SoulCraft

**[English](README.md)** | **[中文](README_zh.md)**

**Craft AI souls from humanity's greatest minds.**

SoulCraft is a data-driven persona extraction pipeline that transforms real human data (interviews, speeches, letters, social media) into structured AI personality definitions compatible with multi-agent systems like [OpenClaw](https://github.com/openclaw), [Claude Code](https://docs.anthropic.com/en/docs/agents), and [Codex](https://openai.com/codex).

> *"We don't write personas. We extract them from reality."*

---

## 🌟 Vision

Imagine a world where the greatest minds in human history can collaborate:

- **Cao Cao (曹操)** routes and reviews all decisions as your CEO
- **Warren Buffett** reviews your investment thesis
- **Elon Musk** challenges your product with first-principles thinking
- **Linus Torvalds** reviews your code architecture
- **Zhuge Liang (诸葛亮)** architects your system design

SoulCraft makes this possible — not through shallow role-play prompts, but through **deep, evidence-based persona extraction** from real human data. Each soul is an atomic, reusable unit. Mix and match freely across teams.

---

## 🏗️ Architecture

```
L0 Adapter          L1 Extraction       L1.5 Aggregation    L2 Profile          +1 System Prompt
───────────         ─────────────       ────────────────    ──────────          ────────────────
Heterogeneous  ──→  Structured     ──→  Knowledge      ──→  Persona        ──→  soul.md /
Data Sources        Extraction          Bible               Profile             System Prompt
(interviews,        (per-file)          (unified)           (ABCDE layers)      (deployable)
letters, tweets)
```

### The ABCDE Persona Model

| Layer | Name | What it captures |
|-------|------|-----------------|
| **A** | Soul | Core identity, worldview, beliefs |
| **B** | Cognition | Knowledge systems, theories, intellectual sources |
| **C** | Expression | Speech patterns, catchphrases, rhetorical style |
| **D** | Behavior | Situational responses, teaching style, preferences |
| **E** | Meta | Blind spots (explicit + inferred), conflict resolution patterns |

---

## 📦 Components

### L0 Adapter — Data Source Converter

Converts heterogeneous data into a unified transcript format. **Zero LLM dependency** — pure structural conversion.

```bash
# Interview subtitles → dialogue format
python -m l0_adapter --type DLG \
  --input podcast_interview.srt \
  --output transcripts/ \
  --target-speaker "Elon Musk"

# Shareholder letters → monologue format
python -m l0_adapter --type MON \
  --input "buffett_letters/*.pdf" \
  --output transcripts/ \
  --target-speaker "Warren Buffett"

# Tweets → grouped micro-burst format
python -m l0_adapter --type MIC \
  --input tweets.json \
  --output transcripts/ \
  --target-speaker "Elon Musk" \
  --group-by thread
```

**Source types by communication mode:**

| Type | Mode | Sources |
|------|------|---------|
| `DLG` | Dialogue | Interviews, podcasts, email threads |
| `MON` | Monologue | Letters, speeches, blog posts |
| `MIC` | Micro-burst | Tweets, social media posts |
| `ATT` | Attributed | Biographies, news articles |

### 3+1 Pipeline — Persona Extraction Engine

A 4-stage pipeline driven by a master prompt template:

1. **L1 Knowledge Extraction** — Per-file structured extraction with source tracing
2. **L1.5 Aggregation** — Knowledge graph + persona data consolidation
3. **L2 Persona Profile** — ABCDE five-layer persona decomposition
4. **+1 System Prompt** — Compile into deployable `soul.md` / System Prompt

---

## 📂 Project Structure

```
soulcraft/
├── souls/                              ← Atomic units
│   ├── cao-cao/
│   │   ├── soul.md                     ← Base soul: pure personality
│   │   └── teams/three-kingdoms/
│   │       └── soul.md                 ← Team-tuned: personality + orchestration directives
│   ├── zhuge-liang/
│   │   ├── soul.md
│   │   └── teams/three-kingdoms/soul.md
│   ├── warren-buffett/soul.md
│   └── elon-musk/soul.md
│
├── teams/                              ← Team manifest files
│   ├── three-kingdoms.yaml             ← References team-tuned souls
│   └── dream-company.yaml
│
├── l0_adapter/                         ← Data source converter (DLG/MON/MIC/ATT)
└── docs/                               ← Pipeline templates & documentation
```

---

## 🧬 Dual-Layer Soul Model

Like open-source LLMs, SoulCraft provides two modes:

| Mode | Analogy | What it contains |
|------|---------|------------------|
| **Base Soul** | `Qwen-base` | Pure personality. No orchestration. Use as-is or fine-tune yourself. |
| **Team-Tuned Soul** | `Qwen-instruct` | Personality + orchestration directives (who reports to whom, conflict rules, trust levels). |

**Orchestration is embedded in the persona file, not in a separate routing engine.** The host framework (OpenClaw, CrewAI, AutoGen) handles execution.

A team-tuned soul adds:
- Chain of command (who is the superior, who are subordinates)
- Request routing rules (what to handle, what to delegate)
- Conflict arbitration strategy
- Trust level and review policies

---

## 🏯 Team Templates

### Three Kingdoms Management Team

| Role | Soul | Why |
|------|------|-----|
| **CEO / Router** | Cao Cao (曹操) | Cross-validates outputs, trust-level based delegation, fast course-correction |
| **COO** | Xun Yu (荀彧) | Resource allocation, operational planning |
| **CSO** | Guo Jia (郭嘉) | Risk assessment, competitive strategy |
| **CTO** | Zhuge Liang (诸葛亮) | System architecture, technical decisions |
| **VP Engineering** | Zhang Liao (张辽) | Execution, implementation, delivery |
| **Red Team** | Sima Yi (司马懿) | Adversarial review, find weaknesses |

Built-in conflict dynamics: CTO vs Red Team (healthy adversarial tension), CSO (aggressive) vs COO (conservative) strategic balance, CEO as final arbiter.

---

## 🔌 Integration

SoulCraft is a **compiler**, not a runtime. It produces soul artifacts; host frameworks execute them.

```bash
# Export to different frameworks
soulcraft export warren-buffett --target openclaw   # → .openclaw/soul.md
soulcraft export warren-buffett --target crewai      # → Agent(role, backstory, ...)
soulcraft export warren-buffett --target autogen      # → AssistantAgent config
```

### OpenClaw

```
.openclaw/
├── soul.md          ← Generated by SoulCraft
├── identity.md
└── agents.md
```

### Canonical Soul IR

Under the hood, SoulCraft maintains a `soul.json` (or `.yaml`) as the source of truth. `soul.md` is a human-readable compilation target. The IR includes ABCDE layers, provenance (source quotes, confidence scores, parser type), and version metadata.

---

## 🚀 Quick Start

```bash
git clone https://github.com/who96/soulcraft.git
cd soulcraft

# Convert interview subtitles to unified format
python -m l0_adapter --type DLG \
  --input examples/sample_interview.srt \
  --output examples/transcripts/ \
  --target-speaker "Example Person"

# Then use the 3+1 pipeline prompt template to extract persona
# (See docs/pipeline_prompt_template.md)
```

---

## 📖 Documentation

- [L0 Adapter Usage](l0_adapter/README.md)
- [3+1 Pipeline Prompt Template](docs/pipeline_prompt_template.md)
- [ABCDE Persona Model](docs/persona_model.md)
- [Integration with OpenClaw](docs/openclaw_integration.md)
- [Team Templates Roadmap](docs/roadmap_team_templates.md)

---

## 🗺️ Roadmap

### Phase 1: Core Loop (MVP)

- [x] 3+1 Pipeline v5 with ABCDE model
- [x] L0 Adapter (Dialogue, Monologue, Micro-burst, Attributed parsers)
- [x] Canonical soul schema (JSON/YAML IR with provenance)
- [x] Example base souls: Linus, Buffett (end-to-end)
- [x] Verification v0 (holdout set + automated eval script)
- [x] OpenClaw soul.md compiler + runnable demo

### Phase 2: Teams & Ecosystem

- [ ] More base souls: Cao Cao, Munger, Zhuge Liang
- [ ] Three Kingdoms team-tuned souls
- [ ] CrewAI / AutoGen exporters
- [ ] Contributor submission template

### Phase 3: Advanced

- [ ] Web UI for soul browsing + evidence chain
- [ ] More team templates (Dream Company, China Business)
- [ ] Multi-agent interaction playground

---

## 🤝 Contributing

We welcome contributions! Key areas:

1. **New base souls** — Extract personas and submit `soul.md` with evidence
2. **New L0 parsers** — Support more data source formats
3. **Team-tuned variants** — Create orchestration-aware soul variants
4. **Evaluation metrics** — Better ways to measure persona fidelity
5. **Framework exporters** — Connect with more agent frameworks (OpenClaw, CrewAI, AutoGen)

---

## 📜 License

MIT License

---

## 🙏 Acknowledgements

- [Character-LLM](https://github.com/choosewhatulike/character-llm) — Experience Reconstruction inspiration
- [Microsoft TinyTroupe](https://github.com/microsoft/TinyTroupe) — Multi-agent persona simulation
- [OpenClaw](https://github.com/openclaw) — `soul.md` ecosystem

---

*"Bad programmers worry about the code. Good programmers worry about data structures and their relationships." — Linus Torvalds*

*SoulCraft worries about the soul.*
