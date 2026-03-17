export type AgentStatus = "idle" | "working" | "error";

export type ConnectedApp =
  | "wechat"
  | "feishu"
  | "discord"
  | "slack"
  | "telegram"
  | "email";

export interface Agent {
  id: string;
  name: string;
  avatar_url: string | null;
  company_tag: string | null;
  soul_ref: string | null;
  model: string;
  thinking_level: string;
  thinking_enabled: boolean;
  context_length: number;
  connected_apps: ConnectedApp[];
  status: AgentStatus;
  current_task: string | null;
  summary: string | null;
  created_at: string;
  updated_at: string;
}

export interface AgentCreateInput {
  name: string;
  avatar_url?: string | null;
  company_tag?: string | null;
  soul_ref?: string | null;
  model?: string;
  thinking_level?: string;
  thinking_enabled?: boolean;
  context_length?: number;
  connected_apps?: ConnectedApp[];
  status?: AgentStatus;
  current_task?: string | null;
  summary?: string | null;
}

export interface AgentUpdateInput {
  name?: string;
  avatar_url?: string | null;
  company_tag?: string | null;
  soul_ref?: string | null;
  model?: string;
  thinking_level?: string;
  thinking_enabled?: boolean;
  context_length?: number;
  connected_apps?: ConnectedApp[];
  status?: AgentStatus;
  current_task?: string | null;
  summary?: string | null;
}

export interface Message {
  id: string;
  agent_id: string;
  direction: "inbound" | "outbound";
  content: string;
  created_at: string;
}
