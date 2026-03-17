# SoulCraft Web UI — P0 MVP Task Plan (v2)

> **项目路径**: `/Users/huluobo/workSpace/soulcraft-ui/`
> **技术栈**: Next.js (latest) + TypeScript + Tailwind CSS + SQLite (better-sqlite3)
> **工作流**: 每个 Task 完成后 → Codex+Gemini review → 通过后 commit → 下一个 Task → 全部完成后 push + 汇报

---

## Task 1: 项目基础 + 数据层 + 种子数据

**目标**: 安装依赖、创建 SQLite 数据层、Agent CRUD、种子数据

**文件清单**:
- `package.json` — 新增 `better-sqlite3`, `uuid`
- `src/types/agent.ts` — Agent + Message 类型定义
- `src/lib/db.ts` — SQLite 初始化（global 缓存避免 HMR 重建）

```sql
-- agents 表完整 schema
CREATE TABLE IF NOT EXISTS agents (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  avatar_url TEXT,
  company_tag TEXT,
  soul_ref TEXT,
  model TEXT DEFAULT 'gpt-5',
  thinking_level TEXT DEFAULT 'high',
  thinking_enabled INTEGER DEFAULT 1,
  context_length INTEGER DEFAULT 128000,
  connected_apps TEXT DEFAULT '[]',
  status TEXT DEFAULT 'idle' CHECK(status IN ('idle','working','error')),
  current_task TEXT,
  summary TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

-- messages 表完整 schema
CREATE TABLE IF NOT EXISTS messages (
  id TEXT PRIMARY KEY,
  agent_id TEXT NOT NULL,
  direction TEXT NOT NULL CHECK(direction IN ('inbound','outbound')),
  content TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_messages_agent ON messages(agent_id);
```

- `src/lib/agents.ts` — CRUD: getAllAgents, getAgent, createAgent, updateAgent, deleteAgent, getAgentsByCompany
- `src/lib/seed.ts` — 5 个三国主题 Agent 种子数据（诸葛亮/曹操/孙权/张飞/独立顾问），含 connected_apps

**验收标准**:
- `npm run build` 通过
- 种子数据可正确插入和查询（通过 seed 脚本验证）

**关键注意**:
- `better-sqlite3` 是 native 模块，需在 `next.config` 中 `serverExternalPackages` 配置
- DB 实例使用 `globalThis` 缓存避免 HMR 重复创建

---

## Task 2: CRUD API Routes

**目标**: Agent 列表、创建、查询、更新、删除 + 消息发送

**文件清单**:
- `src/app/api/agents/route.ts` — GET（支持 `?group_by=company`）/ POST（JSON schema 校验）
- `src/app/api/agents/[id]/route.ts` — GET / PATCH / DELETE
- `src/app/api/agents/[id]/message/route.ts` — POST 发送消息
- `src/app/api/seed/route.ts` — DEV-only 种子触发端点

**验收标准**:
```bash
# CRUD 完整往返测试
curl -s http://localhost:3000/api/agents | jq '.length'
curl -s -X POST http://localhost:3000/api/agents \
  -H 'Content-Type: application/json' \
  -d '{"name":"Test","model":"gpt-5"}' | jq '.id'
# PATCH/DELETE/GET by id
```
- `npm run build` 通过

---

## Task 3: SSE 实时推送

**目标**: 独立的 SSE 基础设施 + 事件端点

**文件清单**:
- `src/lib/event-bus.ts` — **`globalThis` 缓存的 EventEmitter 单例**（避免 HMR 重建）
- `src/app/api/agents/events/route.ts` — SSE 端点
  - `export const dynamic = 'force-dynamic'`
  - 监听 `request.signal` abort 事件清理 listener（防内存泄漏）
  - 事件类型：`agent:status`, `agent:output`, `agent:created`, `agent:deleted`
- 修改 `agents.ts` CRUD 操作：变更时通过 event-bus 发射事件

**验收标准**:
```bash
# SSE 连接测试
curl -s -N http://localhost:3000/api/agents/events &
# 另一个终端触发状态变更
curl -s -X PATCH http://localhost:3000/api/agents/<id> \
  -H 'Content-Type: application/json' -d '{"status":"working"}'
# SSE 终端应收到 agent:status 事件
```
- `npm run build` 通过

**关键注意**:
- EventEmitter 是进程内的，仅适用于单进程 MVP（文档明确标注）
- SSE 路由必须 force-dynamic
- 客户端断开时通过 AbortSignal 清理

---

## Task 4: 前端组件 + 页面集成

**目标**: Agent 工卡组件 + 公司分区网格 + SSE Hook + 主页面

**文件清单**:
- `src/components/StatusBadge.tsx` — idle(灰绿) / working(蓝+脉冲) / error(红)
- `src/components/AppIcons.tsx` — wechat/feishu/discord/slack/telegram/email
- `src/components/AgentCard.tsx` — 折叠态（身份+状态+摘要）/ 展开态（输出流+消息框+配置）
- `src/components/AgentCardGrid.tsx` — 按 company_tag 分组，响应式 1/2/3 列
- `src/components/DashboardClient.tsx` — Client Component wrapper（持有 SSE 状态）
- `src/hooks/useAgentSSE.ts` — 初始 GET 全量 + SSE 增量更新
- `src/app/layout.tsx` — 根布局（Noto Sans SC 字体）
- `src/app/page.tsx` — Server Component，渲染 DashboardClient
- `src/app/globals.css` — 全局样式 + CSS 变量

**验收标准**:
- `npm run build` 通过
- `npm run dev` 启动后页面正确渲染工卡网格
- 工卡按公司分组、折叠/展开正常
- SSE 实时状态更新可见

---

## Task 5: 视觉打磨 + 最终验证 + Push

**目标**: UI 打磨、截图验证、README、commit + push

**内容**:
- 颜色、间距、hover/focus 效果调整
- working 状态脉冲动画
- 浏览器截图验证各状态工卡
- README.md 编写（项目说明、启动命令、截图）
- `git add -A && git commit` + push to GitHub

**验收标准**:
- 浏览器截图确认 UI 渲染正确（idle/working/error 三种状态）
- `npm run build` 零错误
- Codex + Gemini 最终 review 通过
- 代码已 push 到 GitHub

---

## 流程约束

```
For each Task 1-5:
  1. 编码实现
  2. 本地验证（build + curl/浏览器）
  3. Codex review
  4. Gemini review
  5. 修复反馈（如有）
  6. git commit（不 push）
  7. 进入下一个 Task

All Tasks 完成后：
  8. git push to GitHub
  9. 向用户汇报完整结果
```

## v2 变更记录（基于 Codex+Gemini review）

- ✅ 种子数据前移到 Task 1（原 Task 4）
- ✅ SSE 独立为 Task 3（原合并在 Task 2）
- ✅ Schema 字段完整定义（connected_apps, updated_at, summary, CHECK 约束, 索引）
- ✅ EventEmitter 使用 `globalThis` 缓存
- ✅ SSE 路由 `export const dynamic = 'force-dynamic'`
- ✅ AbortSignal 清理 listener
- ✅ 新增 DashboardClient.tsx（Client Component wrapper）
- ✅ `better-sqlite3` 配置 serverExternalPackages
- ✅ 移除错误的 `git init`（项目已初始化）
- ✅ 修正 Next.js 版本标注为 latest
