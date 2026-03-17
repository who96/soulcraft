"use client";

import type { Agent } from "@/types/agent";
import { AgentCard } from "./AgentCard";

interface AgentCardGridProps {
  agents: Agent[];
}

function groupByCompany(agents: Agent[]): [string, Agent[]][] {
  const groups = new Map<string, Agent[]>();

  for (const agent of agents) {
    const key = agent.company_tag ?? "独立顾问";
    const list = groups.get(key) ?? [];
    list.push(agent);
    groups.set(key, list);
  }

  // Sort: named companies first alphabetically, then "独立顾问" last
  const entries = Array.from(groups.entries());
  entries.sort(([a], [b]) => {
    if (a === "独立顾问") return 1;
    if (b === "独立顾问") return -1;
    return a.localeCompare(b, "zh-CN");
  });

  return entries;
}

export function AgentCardGrid({ agents }: AgentCardGridProps) {
  const groups = groupByCompany(agents);

  if (agents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-white/30">
        <span className="text-4xl mb-4">🏢</span>
        <p className="text-lg">暂无 Agent</p>
        <p className="text-sm mt-1">使用 API 创建或触发种子数据</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {groups.map(([company, companyAgents]) => (
        <section key={company}>
          <div className="flex items-center gap-3 mb-4">
            <h2 className="text-sm font-semibold text-white/70 uppercase tracking-wider">
              {company}
            </h2>
            <span className="text-xs text-white/30 bg-white/5 px-2 py-0.5 rounded-full">
              {companyAgents.length}
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {companyAgents.map((agent) => (
              <AgentCard key={agent.id} agent={agent} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
