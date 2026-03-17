import "server-only";
import { v4 as uuidv4 } from "uuid";
import { getDb } from "./db";
import type { Agent, AgentCreateInput, AgentUpdateInput, ConnectedApp, Message } from "@/types/agent";

interface AgentRow {
  id: string;
  name: string;
  avatar_url: string | null;
  company_tag: string | null;
  soul_ref: string | null;
  model: string;
  thinking_level: string;
  thinking_enabled: number;
  context_length: number;
  connected_apps: string;
  status: string;
  current_task: string | null;
  summary: string | null;
  created_at: string;
  updated_at: string;
}

function parseConnectedApps(raw: string): ConnectedApp[] {
  try {
    const arr = JSON.parse(raw);
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}

function rowToAgent(row: AgentRow): Agent {
  return {
    ...row,
    thinking_enabled: Boolean(row.thinking_enabled),
    connected_apps: parseConnectedApps(row.connected_apps),
    status: row.status as Agent["status"],
  };
}

export function getAllAgents(): Agent[] {
  const db = getDb();
  const rows = db.prepare("SELECT * FROM agents ORDER BY company_tag, name").all() as AgentRow[];
  return rows.map(rowToAgent);
}

export function getAgent(id: string): Agent | null {
  const db = getDb();
  const row = db.prepare("SELECT * FROM agents WHERE id = ?").get(id) as AgentRow | undefined;
  return row ? rowToAgent(row) : null;
}

export function createAgent(input: AgentCreateInput): Agent {
  const db = getDb();
  const id = uuidv4();

  db.prepare(`
    INSERT INTO agents (id, name, avatar_url, company_tag, soul_ref, model,
      thinking_level, thinking_enabled, context_length, connected_apps,
      status, current_task, summary)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    id,
    input.name,
    input.avatar_url ?? null,
    input.company_tag ?? null,
    input.soul_ref ?? null,
    input.model ?? "gpt-5",
    input.thinking_level ?? "high",
    input.thinking_enabled === true ? 1 : 0,
    input.context_length ?? 128000,
    JSON.stringify(input.connected_apps ?? []),
    input.status ?? "idle",
    input.current_task ?? null,
    input.summary ?? null,
  );

  return getAgent(id)!;
}

export function updateAgent(id: string, input: AgentUpdateInput): Agent | null {
  const db = getDb();
  const existing = getAgent(id);
  if (!existing) return null;

  const fields: string[] = [];
  const values: unknown[] = [];

  if (input.name !== undefined) { fields.push("name = ?"); values.push(input.name); }
  if (input.avatar_url !== undefined) { fields.push("avatar_url = ?"); values.push(input.avatar_url); }
  if (input.company_tag !== undefined) { fields.push("company_tag = ?"); values.push(input.company_tag); }
  if (input.soul_ref !== undefined) { fields.push("soul_ref = ?"); values.push(input.soul_ref); }
  if (input.model !== undefined) { fields.push("model = ?"); values.push(input.model); }
  if (input.thinking_level !== undefined) { fields.push("thinking_level = ?"); values.push(input.thinking_level); }
  if (input.thinking_enabled !== undefined) { fields.push("thinking_enabled = ?"); values.push(input.thinking_enabled === true ? 1 : 0); }
  if (input.context_length !== undefined) { fields.push("context_length = ?"); values.push(input.context_length); }
  if (input.connected_apps !== undefined) { fields.push("connected_apps = ?"); values.push(JSON.stringify(input.connected_apps)); }
  if (input.status !== undefined) { fields.push("status = ?"); values.push(input.status); }
  if (input.current_task !== undefined) { fields.push("current_task = ?"); values.push(input.current_task); }
  if (input.summary !== undefined) { fields.push("summary = ?"); values.push(input.summary); }

  if (fields.length === 0) return existing;

  fields.push("updated_at = datetime('now')");
  values.push(id);

  db.prepare(`UPDATE agents SET ${fields.join(", ")} WHERE id = ?`).run(...values);
  return getAgent(id);
}

export function deleteAgent(id: string): boolean {
  const db = getDb();
  const result = db.prepare("DELETE FROM agents WHERE id = ?").run(id);
  return result.changes > 0;
}

export function getAgentsByCompany(): Map<string, Agent[]> {
  const agents = getAllAgents();
  const groups = new Map<string, Agent[]>();

  for (const agent of agents) {
    const key = agent.company_tag ?? "独立顾问";
    const list = groups.get(key) ?? [];
    list.push(agent);
    groups.set(key, list);
  }

  return groups;
}

export function createMessage(agentId: string, direction: "inbound" | "outbound", content: string): Message {
  const db = getDb();
  const id = uuidv4();

  db.prepare(`
    INSERT INTO messages (id, agent_id, direction, content)
    VALUES (?, ?, ?, ?)
  `).run(id, agentId, direction, content);

  return db.prepare("SELECT * FROM messages WHERE id = ?").get(id) as Message;
}

export function getMessages(agentId: string, limit = 50): Message[] {
  const db = getDb();
  return db.prepare(
    "SELECT * FROM messages WHERE agent_id = ? ORDER BY created_at DESC LIMIT ?"
  ).all(agentId, limit) as Message[];
}
