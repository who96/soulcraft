import { eventBus } from "@/lib/event-bus";
import type { AgentEvent } from "@/lib/event-bus";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    start(controller) {
      const onEvent = (event: AgentEvent) => {
        const data = `event: ${event.type}\ndata: ${JSON.stringify(event)}\n\n`;
        controller.enqueue(encoder.encode(data));
      };

      eventBus.on("agent-event", onEvent);

      // Clean up on client disconnect
      request.signal.addEventListener("abort", () => {
        eventBus.off("agent-event", onEvent);
        controller.close();
      });

      // Send initial heartbeat
      controller.enqueue(encoder.encode(": heartbeat\n\n"));
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
