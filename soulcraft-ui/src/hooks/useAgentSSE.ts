"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import type { Agent } from "@/types/agent";
import type { AgentEvent } from "@/lib/event-bus";

export function useAgentSSE() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Initial fetch
  useEffect(() => {
    fetch("/api/agents")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data: unknown) => {
        if (Array.isArray(data)) {
          setAgents(data as Agent[]);
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  // SSE connection
  useEffect(() => {
    const es = new EventSource("/api/agents/events");
    eventSourceRef.current = es;

    es.onopen = () => setConnected(true);
    es.onerror = () => setConnected(false);

    const handleEvent = (e: MessageEvent) => {
      try {
        const event: AgentEvent = JSON.parse(e.data);

        setAgents((prev) => {
          switch (event.type) {
            case "agent:created":
              return [...prev, event.data as Agent];
            case "agent:status":
              return prev.map((a) =>
                a.id === event.agentId ? (event.data as Agent) : a
              );
            case "agent:deleted":
              return prev.filter((a) => a.id !== event.agentId);
            case "agent:output":
              // Trigger re-render for the target agent (message received)
              return prev.map((a) =>
                a.id === event.agentId ? { ...a } : a
              );
            default:
              return prev;
          }
        });
      } catch {
        // Ignore parse errors
      }
    };

    es.addEventListener("agent:created", handleEvent);
    es.addEventListener("agent:status", handleEvent);
    es.addEventListener("agent:deleted", handleEvent);
    es.addEventListener("agent:output", handleEvent);

    return () => {
      es.close();
      eventSourceRef.current = null;
    };
  }, []);

  const refreshAgents = useCallback(async () => {
    const res = await fetch("/api/agents");
    if (!res.ok) return;
    const data: unknown = await res.json();
    if (Array.isArray(data)) {
      setAgents(data as Agent[]);
    }
  }, []);

  return { agents, loading, connected, refreshAgents };
}
