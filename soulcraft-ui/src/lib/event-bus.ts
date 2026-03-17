import "server-only";
import { EventEmitter } from "events";

export interface AgentEvent {
  type: "agent:status" | "agent:output" | "agent:created" | "agent:deleted";
  agentId: string;
  data: unknown;
  timestamp: string;
}

const globalForBus = globalThis as unknown as { __soulcraft_event_bus?: EventEmitter };

if (!globalForBus.__soulcraft_event_bus) {
  globalForBus.__soulcraft_event_bus = new EventEmitter();
  globalForBus.__soulcraft_event_bus.setMaxListeners(100);
}

export const eventBus = globalForBus.__soulcraft_event_bus;

export function emitAgentEvent(event: AgentEvent): void {
  eventBus.emit("agent-event", event);
}
