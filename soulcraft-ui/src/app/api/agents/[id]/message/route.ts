import { NextResponse } from "next/server";
import { getAgent, createMessage } from "@/lib/agents";
import { emitAgentEvent } from "@/lib/event-bus";

interface RouteParams {
  params: Promise<{ id: string }>;
}

export async function POST(request: Request, { params }: RouteParams) {
  try {
    const { id } = await params;
    const agent = getAgent(id);

    if (!agent) {
      return NextResponse.json({ error: "Agent not found" }, { status: 404 });
    }

    const body = (await request.json()) as { content?: string };

    if (!body.content || typeof body.content !== "string") {
      return NextResponse.json({ error: "content is required" }, { status: 400 });
    }

    const message = createMessage(id, "inbound", body.content);

    emitAgentEvent({
      type: "agent:output",
      agentId: id,
      data: { message },
      timestamp: new Date().toISOString(),
    });

    return NextResponse.json(message, { status: 201 });
  } catch (err) {
    const msg = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
