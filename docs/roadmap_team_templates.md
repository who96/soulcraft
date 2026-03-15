# SoulCraft Roadmap: Team Templates

## 概念：预制 Agent Team 模板

SoulCraft 不仅提取单个人格，还可以组装**预制团队模板**——一组互相配合（甚至对抗）的 Agent 组成的编排单元。

---

## Team #1: 三国管理团队 🏯

### 阵容

| Agent | 人物 | 角色 | 调度触发 |
|-------|------|------|---------|
| **Router / CEO** | 曹操 | 请求路由 + 交叉验证 | 所有请求入口 |
| **COO** | 荀彧 | 运营调度、资源分配 | 排期、流程、资源问题 |
| **CSO** | 郭嘉 | 战略分析、风险预判 | 竞争分析、方向决策 |
| **CTO** | 诸葛亮 | 技术架构、系统设计 | 技术选型、架构设计 |
| **VP Eng** | 张辽 | 执行实施、攻坚 | 写代码、实现功能 |
| **Red Team** | 司马懿 | 对抗审计、找漏洞 | 安全审计、压力测试 |

### 为什么选曹操当 Router

"多疑"不是 bug，是 feature：
- **交叉验证**：同时问荀彧和郭嘉，对比结果 → 并行调度 + diff
- **信任分级**：对新人严格审查，对核心圈放权 → approval policy (untrusted → on-failure → never)
- **越权过滤**：杀杨修 = 拒绝 Agent 越权猜测意图 → 过滤幻觉
- **快速止损**：发现错误立刻调整 → retry + fallback

### 团队动态（内置冲突机制）

- 诸葛亮 vs 司马懿 → CTO vs Red Team 良性对抗
- 郭嘉（激进）vs 荀彧（保守）→ 战略平衡
- 曹操最终仲裁 → Router 做最终决策

### 数据源

《三国志》+ 《三国演义》→ L0 ATT parser → 3+1 Pipeline → 每人一个 soul.md

### 实现路径

1. L0: 用 ATT parser 从三国文本提取各角色直接引语
2. L1-L2: 跑 3+1 Pipeline 生成每个人的 persona
3. +1: 生成 soul.md
4. 编排: 写 `team.yaml` 定义路由规则和角色触发条件

---

## Team #2: 人类最强公司 🌟 (Future)

| Agent | 人物 | 角色 |
|-------|------|------|
| CEO / Router | 曹操 或 李世民 | 编排 + 验证 |
| 创业顾问 | Elon Musk | 第一性原理、颠覆式创新 |
| 投资顾问 | Warren Buffett | 价值投资、长期主义 |
| 技术专家 | Linus Torvalds | 代码架构、工程品味 |
| 产品经理 | Steve Jobs | 用户体验、产品直觉 |
| 战略顾问 | Charlie Munger | 多元思维模型 |

---

## 待验证

- [ ] 竞品调研：有没有类似的"历史人物多 Agent 团队"开源项目？
- [ ] 编排格式：team.yaml 还是直接兼容 OpenClaw 的 agents.md？
- [ ] 冲突仲裁机制：当 Agent 意见分歧时，Router 如何决策？
