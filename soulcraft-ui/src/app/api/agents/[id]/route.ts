import { NextResponse } from "next/server";
import { getAgent, updateAgent, deleteAgent } from "@/lib/agents";
import { emitAgentEvent } from "@/lib/event-bus";
import type { AgentUpdateInput } from "@/types/agent";

interface RouteParams {
  params: Promise<{ id: string }>;
}

export async function GET(_request: Request, { params }: RouteParams) {
  const { id } = await params;
  const agent = getAgent(id);
  if (!agent) {
    return NextResponse.json({ error: "Agent not found" }, { status: 404 });
  }
  return NextResponse.json(agent);
}

export async function PATCH(request: Request, { params }: RouteParams) {
  try {
    const { id } = await params;
    const body = (await request.json()) as AgentUpdateInput;
    const agent = updateAgent(id, body);

    if (!agent) {
      return NextResponse.json({ error: "Agent not found" }, { status: 404 });
    }

    emitAgentEvent({
      type: "agent:status",
      agentId: agent.id,
      data: agent,
      timestamp: new Date().toISOString(),
    });

    return NextResponse.json(agent);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}

export async function DELETE(_request: Request, { params }: RouteParams) {
  const { id } = await params;
  const deleted = deleteAgent(id);

  if (!deleted) {
    return NextResponse.json({ error: "Agent not found" }, { status: 404 });
  }

  emitAgentEvent({
    type: "agent:deleted",
    agentId: id,
    data: {},
    timestamp: new Date().toISOString(),
  });

  return NextResponse.json({ success: true });
}
