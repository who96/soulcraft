import { NextResponse } from "next/server";
import { getAllAgents, createAgent } from "@/lib/agents";
import { emitAgentEvent } from "@/lib/event-bus";
import type { AgentCreateInput } from "@/types/agent";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const groupBy = searchParams.get("group_by");

  const agents = getAllAgents();

  if (groupBy === "company") {
    const groups: Record<string, typeof agents> = {};
    for (const agent of agents) {
      const key = agent.company_tag ?? "独立顾问";
      (groups[key] ??= []).push(agent);
    }
    return NextResponse.json(groups);
  }

  return NextResponse.json(agents);
}

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as AgentCreateInput;

    if (!body.name || typeof body.name !== "string") {
      return NextResponse.json({ error: "name is required" }, { status: 400 });
    }

    const agent = createAgent(body);

    emitAgentEvent({
      type: "agent:created",
      agentId: agent.id,
      data: agent,
      timestamp: new Date().toISOString(),
    });

    return NextResponse.json(agent, { status: 201 });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
