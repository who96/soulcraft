"use client";

import type { AgentStatus } from "@/types/agent";

const STATUS_CONFIG: Record<AgentStatus, { label: string; color: string; pulse: boolean }> = {
  idle: { label: "待命", color: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30", pulse: false },
  working: { label: "工作中", color: "bg-blue-500/20 text-blue-400 border-blue-500/30", pulse: true },
  error: { label: "异常", color: "bg-red-500/20 text-red-400 border-red-500/30", pulse: false },
};

export function StatusBadge({ status }: { status: AgentStatus }) {
  const config = STATUS_CONFIG[status];

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium border ${config.color}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${config.pulse ? "animate-pulse" : ""} ${
        status === "idle" ? "bg-emerald-400" : status === "working" ? "bg-blue-400" : "bg-red-400"
      }`} />
      {config.label}
    </span>
  );
}
