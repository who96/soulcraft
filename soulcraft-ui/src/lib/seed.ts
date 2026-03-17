import "server-only";
import { createAgent } from "./agents";
import { getDb } from "./db";
import type { AgentCreateInput } from "@/types/agent";

const SEED_AGENTS: AgentCreateInput[] = [
  {
    name: "诸葛亮",
    company_tag: "蜀汉集团",
    model: "gpt-5",
    thinking_level: "high",
    thinking_enabled: true,
    context_length: 128000,
    connected_apps: ["feishu", "discord"],
    status: "working",
    current_task: "正在分析北伐战略方案...",
    summary: "Strategic Advisor | 运筹帷幄之中，决胜千里之外",
  },
  {
    name: "曹操",
    company_tag: "魏国集团",
    model: "claude-4",
    thinking_level: "medium",
    thinking_enabled: true,
    context_length: 200000,
    connected_apps: ["wechat", "slack", "email"],
    status: "idle",
    current_task: null,
    summary: "Supreme Commander | 宁教我负天下人",
  },
  {
    name: "孙权",
    company_tag: "东吴集团",
    model: "gpt-5",
    thinking_level: "high",
    thinking_enabled: true,
    context_length: 128000,
    connected_apps: ["feishu", "telegram"],
    status: "idle",
    current_task: null,
    summary: "Coalition Leader | 生子当如孙仲谋",
  },
  {
    name: "张飞",
    company_tag: "蜀汉集团",
    model: "gpt-4.1",
    thinking_level: "low",
    thinking_enabled: false,
    context_length: 32000,
    connected_apps: ["discord"],
    status: "error",
    current_task: "任务执行失败：连接超时",
    summary: "Vanguard General | 燕人张翼德在此！",
  },
  {
    name: "司马懿",
    company_tag: null,
    model: "gemini-3",
    thinking_level: "high",
    thinking_enabled: true,
    context_length: 100000,
    connected_apps: ["wechat", "email"],
    status: "idle",
    current_task: null,
    summary: "Independent Consultant | 静观其变，后发制人",
  },
];

export function seedAgents(): { created: number; skipped: boolean } {
  const db = getDb();
  const count = (db.prepare("SELECT COUNT(*) as count FROM agents").get() as { count: number }).count;

  if (count > 0) {
    return { created: 0, skipped: true };
  }

  const insertAll = db.transaction(() => {
    for (const agent of SEED_AGENTS) {
      createAgent(agent);
    }
  });

  insertAll();
  return { created: SEED_AGENTS.length, skipped: false };
}
