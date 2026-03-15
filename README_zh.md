# 🔮 铸魂 SoulCraft

**[English](README.md)** | **[中文](README_zh.md)**

**从人类最伟大的头脑中，锻造 AI 灵魂。**

SoulCraft 是一套数据驱动的人格提取流水线，将真实人类数据（访谈、演讲、信件、社交媒体）转化为结构化的 AI 人格定义，可直接用于 [OpenClaw](https://github.com/openclaw)、[Claude Code](https://docs.anthropic.com/en/docs/agents)、[Codex](https://openai.com/codex) 等多智能体编排系统。

> *"我们不编写人设，我们从现实中提取。"*

---

## 🌟 愿景：人类群星闪耀

想象一个世界，人类历史上最伟大的头脑可以协同工作：

- **曹操** 作为你的 CEO，路由并交叉验证所有决策
- **沃伦·巴菲特** 审核你的投资方案
- **埃隆·马斯克** 用第一性原理挑战你的产品
- **Linus Torvalds** 审查你的代码架构
- **诸葛亮** 设计你的系统架构

SoulCraft 让这一切成为可能——不是通过浅层的角色扮演提示词，而是通过**深度、有据可查的人格提取**。每个灵魂都是原子级、可复用的单元，可以自由组合。

---

## 🏗️ 架构

```
L0 适配器          L1 知识提取         L1.5 聚合          L2 画像            +1 系统提示词
───────────       ─────────────      ────────────       ──────────        ────────────────
异构数据源   ──→   结构化提取    ──→   知识图谱       ──→  人格画像     ──→   soul.md /
(访谈、信件、      (逐文件)           (统一整合)          (ABCDE 五层)       系统提示词
推文)
```

### ABCDE 人格模型

| 层 | 名称 | 提取内容 |
|----|------|---------|
| **A** | 灵魂 | 核心身份、世界观、信念 |
| **B** | 认知 | 知识体系、理论框架、思想来源 |
| **C** | 表达 | 语言风格、口头禅、修辞特征 |
| **D** | 行为 | 情景反应、教学风格、偏好 |
| **E** | 元认知 | 盲区（显式 + 推断）、冲突解决模式 |

---

## 📦 核心组件

### L0 适配器 — 数据源转换器

将异构数据转换为统一的转写本格式。**零 LLM 依赖** — 纯结构化转换。

```bash
# 访谈字幕 → 对话格式
python -m l0_adapter --type DLG \
  --input podcast_interview.srt \
  --output transcripts/ \
  --target-speaker "Elon Musk"

# 股东信 → 独白格式
python -m l0_adapter --type MON \
  --input "buffett_letters/*.pdf" \
  --output transcripts/ \
  --target-speaker "Warren Buffett"

# 推文 → 按线程分组的微爆发格式
python -m l0_adapter --type MIC \
  --input tweets.json \
  --output transcripts/ \
  --target-speaker "Elon Musk" \
  --group-by thread
```

**按沟通模式分类的数据源：**

| 类型 | 模式 | 来源 |
|------|------|------|
| `DLG` | 对话 | 访谈、播客、邮件讨论 |
| `MON` | 独白 | 信件、演讲、博客文章 |
| `MIC` | 微爆发 | 推文、社交媒体帖子 |
| `ATT` | 转述 | 传记、新闻报道 |

### 3+1 流水线 — 人格提取引擎

由主提示词模板驱动的 4 阶段流水线：

1. **L1 知识提取** — 逐文件结构化提取，附来源溯源
2. **L1.5 聚合** — 知识图谱 + 人格数据整合
3. **L2 人格画像** — ABCDE 五层人格分解
4. **+1 系统提示词** — 编译为可部署的 `soul.md` / 系统提示词

---

## 📂 项目结构

```
soulcraft/
├── souls/                              ← 原子单元
│   ├── cao-cao/
│   │   ├── soul.md                     ← 基座版：纯人格
│   │   └── teams/three-kingdoms/
│   │       └── soul.md                 ← 团队版：人格 + 编排指令
│   ├── zhuge-liang/
│   │   ├── soul.md
│   │   └── teams/three-kingdoms/soul.md
│   ├── warren-buffett/soul.md
│   └── elon-musk/soul.md
│
├── teams/                              ← 团队清单文件
│   ├── three-kingdoms.yaml             ← 引用各成员的团队版 soul
│   └── dream-company.yaml
│
├── l0_adapter/                         ← 数据源转换器 (DLG/MON/MIC/ATT)
└── docs/                               ← 流水线模板与文档
```

---

## 🧬 双层灵魂模型

就像开源大模型同时提供 base 和 instruct 版本一样，SoulCraft 提供两种模式：

| 模式 | 类比 | 包含内容 |
|------|------|----------|
| **基座灵魂** | `Qwen-base` | 纯人格。无编排指令。用户可自行微调。|
| **团队微调灵魂** | `Qwen-instruct` | 人格 + 编排指令（上下级、冲突规则、信任等级）。开箱即用。|

**编排逻辑写在人设文件里，不是独立的路由引擎。** 宿主框架（OpenClaw / CrewAI / AutoGen）负责执行。

团队微调版额外包含：
- 指挥链（谁是上级、谁是下属）
- 请求路由规则（什么自己处理、什么转交）
- 冲突仲裁策略
- 信任等级与审查策略

---

## 🏯 团队模板

### 三国管理团队

| 角色 | 灵魂 | 原因 |
|------|------|------|
| **CEO / 路由器** | 曹操 | 交叉验证输出、基于信任等级的委派、快速纠偏 |
| **COO** | 荀彧 | 资源分配、运营规划 |
| **CSO** | 郭嘉 | 风险评估、竞争策略 |
| **CTO** | 诸葛亮 | 系统架构、技术决策 |
| **VP 工程** | 张辽 | 执行实施、攻坚交付 |
| **红队** | 司马懿 | 对抗性审查、找弱点 |

内置冲突动态：CTO vs 红队（良性对抗张力）、CSO（激进）vs COO（保守）的战略平衡、CEO 做最终仲裁。

### 为什么选曹操当 CEO？

"多疑"不是缺点，是必备特质：
- **交叉验证**：同时问荀彧和郭嘉，对比两人意见 → 并行调度 + diff 结果
- **信任分级**：对新人严格审查，对核心圈放权 → `untrusted` → `on-failure` → `never`
- **越权过滤**：杀杨修 = 拒绝 Agent 越权猜测意图 → 过滤幻觉
- **快速止损**：发现错误立刻调整 → retry + fallback

---

## 🔌 集成

SoulCraft 是**编译器**，不是运行时。它生产灵魂产物，宿主框架负责执行。

```bash
# 导出到不同框架
soulcraft export warren-buffett --target openclaw   # → .openclaw/soul.md
soulcraft export warren-buffett --target crewai      # → Agent(role, backstory, ...)
soulcraft export warren-buffett --target autogen      # → AssistantAgent 配置
```

### OpenClaw

```
.openclaw/
├── soul.md          ← SoulCraft 生成
├── identity.md
└── agents.md
```

### 规范灵魂 IR

SoulCraft 在底层维护 `soul.json`（或 `.yaml`）作为数据源。`soul.md` 是人类可读的编译目标。IR 包含 ABCDE 五层数据、来源溯源（原文引用、置信度、解析器类型）和版本元数据。

---

## 🚀 快速开始

```bash
git clone https://github.com/who96/soulcraft.git
cd soulcraft

# 将访谈字幕转换为统一格式
python -m l0_adapter --type DLG \
  --input examples/sample_interview.srt \
  --output examples/transcripts/ \
  --target-speaker "示例人物"

# 然后使用 3+1 流水线提示词模板进行人格提取
# (详见 docs/pipeline_prompt_template.md)
```

---

## 📖 文档

- [L0 适配器使用说明](l0_adapter/README.md)
- [3+1 流水线提示词模板](docs/pipeline_prompt_template.md)
- [ABCDE 人格模型](docs/persona_model.md)
- [OpenClaw 集成指南](docs/openclaw_integration.md)
- [团队模板路线图](docs/roadmap_team_templates.md)

---

## 🗺️ 路线图

### Phase 1：核心闭环（MVP）

- [x] 3+1 流水线 v5（ABCDE 模型）
- [x] L0 适配器（对话、独白、微爆发、转述 四大解析器）
- [ ] 规范灵魂 Schema（JSON/YAML IR，含来源溯源）
- [ ] 示例基座灵魂：Linus、巴菲特（端到端跑通）
- [ ] 验证框架 v0（留出测试集 + 自动评估脚本）
- [ ] OpenClaw soul.md 编译器 + 可运行 demo

### Phase 2：团队与生态

- [ ] 更多基座灵魂：曹操、芒格、诸葛亮
- [ ] 三国管理团队微调版灵魂
- [ ] CrewAI / AutoGen 导出器
- [ ] 贡献者提交模板

### Phase 3：进阶功能

- [ ] Web UI（灵魂浏览 + 证据链查看）
- [ ] 更多团队模板（人类最强公司、中国商业天团）
- [ ] 多 Agent 交互实验场

---

## 🤝 参与贡献

欢迎贡献！重点方向：

1. **新基座灵魂** — 从历史/现代人物中提取人格，附证据提交 `soul.md`
2. **新 L0 解析器** — 支持更多数据源格式
3. **团队微调版** — 为团队场景创建含编排指令的灵魂变体
4. **评估指标** — 更好的人格还原度度量方法
5. **框架导出器** — 对接更多 Agent 框架（OpenClaw、CrewAI、AutoGen）

---

## 📜 许可证

MIT 许可证

---

## 🙏 致谢

- [Character-LLM](https://github.com/choosewhatulike/character-llm) — 经验重建方法启发
- [Microsoft TinyTroupe](https://github.com/microsoft/TinyTroupe) — 多 Agent 人格模拟
- [OpenClaw](https://github.com/openclaw) — `soul.md` 生态

---

*"差劲的程序员担心代码，优秀的程序员担心数据结构和它们之间的关系。" — Linus Torvalds*

*SoulCraft 担心的是灵魂。*
