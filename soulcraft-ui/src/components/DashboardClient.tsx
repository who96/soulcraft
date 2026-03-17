"use client";

import { useAgentSSE } from "@/hooks/useAgentSSE";
import { AgentCardGrid } from "@/components/AgentCardGrid";

export function DashboardClient() {
  const { agents, loading, connected } = useAgentSSE();

  return (
    <div>
      {/* Header bar */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">SoulCraft</h1>
          <p className="text-sm text-white/40 mt-1">Agent 管理控制台</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-xs text-white/40">
            <span className={`w-2 h-2 rounded-full ${connected ? "bg-emerald-400" : "bg-red-400"}`} />
            <span>{connected ? "实时连接" : "断开"}</span>
          </div>
          <div className="text-xs text-white/30 bg-white/5 px-3 py-1.5 rounded-lg">
            {agents.length} 个 Agent
          </div>
        </div>
      </div>

      {/* Main content */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin w-8 h-8 border-2 border-white/20 border-t-white/60 rounded-full" />
        </div>
      ) : (
        <AgentCardGrid agents={agents} />
      )}
    </div>
  );
}
