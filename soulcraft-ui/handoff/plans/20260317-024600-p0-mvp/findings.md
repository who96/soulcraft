# Findings

## 调研结论（已完成）

### 参考项目
- Star-Office-UI: Flask+像素风，6 种 Agent 状态，join-key 多人协作
- OpenClaw-bot-review: Next.js+TS+Tailwind，卡片墙，无 DB
- openclaw-mission-control: Next.js+Docker+PostgreSQL，API-first
- openclaw-control-center: Node.js，员工状态（工作中/待命），协作/用量/任务，Apple 风格

### 架构决策（D-SC-001 ~ D-SC-006）
- Next.js 15 + TS + Tailwind
- SQLite (better-sqlite3)
- 工卡默认 + 像素办公室 P1
- P0 聚焦工卡+SSE+消息
- 表单式编排+API
- 独立项目 soulcraft-ui/

### 已完成基础设施
- Next.js 项目已初始化（428 packages, 0 vulnerabilities）
- 项目目录: `/Users/huluobo/workSpace/soulcraft-ui/`
