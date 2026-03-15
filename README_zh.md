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
├── souls/                        ← 原子单元：每人一个 soul.md
│   ├── cao-cao/soul.md           ← 曹操 — CEO / 路由 Agent
│   ├── zhuge-liang/soul.md       ← 诸葛亮 — CTO / 架构师
│   ├── elon-musk/soul.md         ← 马斯克 — 第一性原理创新者
│   ├── warren-buffett/soul.md    ← 巴菲特 — 价值投资者
│   └── duan-yongping/soul.md     ← 段永平 — 产品直觉
│
├── teams/                        ← 预编排团队模板 (YAML)
│   ├── three-kingdoms.yaml       ← 三国管理团队
│   ├── dream-company.yaml        ← 人类最强公司
│   └── china-business.yaml       ← 中国商业天团
│
├── l0_adapter/                   ← 数据源转换器 (DLG/MON/MIC/ATT)
└── docs/                         ← 流水线模板与文档
```

**`souls/` 是原子层，`teams/` 只是组合配方。**

用户可以自由组合：让曹操当 CEO 领导马斯克、巴菲特和段永平——或者替换成任何其他灵魂。

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

### OpenClaw / Claude Code

SoulCraft 的输出可直接作为 `soul.md` 使用：

```
.openclaw/
├── soul.md          ← SoulCraft 生成
├── identity.md
└── agents.md
```

### 多 Agent 编排

**E2 冲突解决**层使真实的多 Agent 交互成为可能：

```python
# 每个 Agent 知道自己如何处理分歧
musk_agent.conflict_style   # "第一性原理辩论，物理问题绝不让步"
buffett_agent.conflict_style # "耐心、数据驱动，数字说了算"
caocao_agent.trust_policy   # "先让第二个人也看看，再做决定"
```

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

- [x] 3+1 流水线 v5 (ABCDE 模型)
- [x] L0 适配器（对话、独白、微爆发、转述 四大解析器）
- [ ] 示例灵魂：巴菲特、马斯克、Linus、曹操
- [ ] 团队模板：三国管理团队、人类最强公司
- [ ] `team.yaml` 规范与路由引擎
- [ ] OpenClaw soul.md 自动生成
- [ ] 验证框架（训练集/对照组分割测试人格准确度）
- [ ] Web UI 人格探索界面
- [ ] 多 Agent 辩论模拟（含冲突解决机制）

---

## 🤝 参与贡献

欢迎贡献！重点方向：

1. **新灵魂** — 从历史/现代人物中提取人格，提交 `soul.md`
2. **新 L0 解析器** — 支持更多数据源格式
3. **团队模板** — 为不同场景设计新的团队组合
4. **评估指标** — 更好的人格还原度度量方法
5. **集成插件** — 对接更多 Agent 框架（OpenClaw、CrewAI、AutoGen）

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
