"use client";

import { useState, useRef, useEffect } from "react";
import type { Agent } from "@/types/agent";
import { StatusBadge } from "./StatusBadge";
import { AppIcons } from "./AppIcons";

function getAvatarColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  const h = ((hash % 360) + 360) % 360;
  return `hsl(${h}, 65%, 45%)`;
}

interface AgentCardProps {
  agent: Agent;
  onSendMessage?: (agentId: string, content: string) => void;
}

export function AgentCard({ agent, onSendMessage }: AgentCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (expanded && inputRef.current) {
      inputRef.current.focus();
    }
  }, [expanded]);

  const firstChar = agent.name.charAt(0);
  const avatarBg = getAvatarColor(agent.name);

  const handleSend = async () => {
    if (!message.trim() || sending) return;
    setSending(true);
    try {
      if (onSendMessage) {
        onSendMessage(agent.id, message.trim());
        setMessage("");
      } else {
        const res = await fetch(`/api/agents/${agent.id}/message`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content: message.trim() }),
        });
        if (res.ok) {
          setMessage("");
        }
      }
    } finally {
      setSending(false);
    }
  };

  return (
    <div
      className={`rounded-xl border transition-all duration-200 cursor-pointer
        ${expanded
          ? "border-white/20 bg-white/[0.06] shadow-lg"
          : "border-white/10 bg-white/[0.03] hover:border-white/15 hover:bg-white/[0.05]"
        }`}
      onClick={() => !expanded && setExpanded(true)}
    >
      {/* Collapsed header — always visible */}
      <div className="p-4">
        <div className="flex items-start gap-3">
          {/* Avatar */}
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-lg shrink-0"
            style={{ backgroundColor: avatarBg }}
          >
            {firstChar}
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2">
              <h3 className="text-sm font-semibold text-white truncate">{agent.name}</h3>
              <StatusBadge status={agent.status} />
            </div>
            {agent.summary && (
              <p className="text-xs text-white/50 mt-0.5 truncate">{agent.summary}</p>
            )}
          </div>
        </div>

        {/* Meta line */}
        <div className="mt-3 flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 text-xs text-white/40">
            {agent.company_tag && (
              <span className="px-1.5 py-0.5 rounded bg-white/10 text-white/60">{agent.company_tag}</span>
            )}
            <span>{agent.model}</span>
            <span>·</span>
            <span>🧠{agent.thinking_level}</span>
            <span>·</span>
            <span>{(agent.context_length / 1000).toFixed(0)}K</span>
          </div>
          <AppIcons apps={agent.connected_apps} />
        </div>
      </div>

      {/* Expanded section */}
      {expanded && (
        <div className="border-t border-white/10" onClick={(e) => e.stopPropagation()}>
          {/* Current task / live output */}
          {agent.current_task && (
            <div className="px-4 py-3 border-b border-white/5">
              <div className="flex items-center gap-2 text-xs text-white/50 mb-1">
                <span className={agent.status === "working" ? "animate-spin" : ""}>🔄</span>
                <span>当前任务</span>
              </div>
              <p className="text-xs text-white/70 font-mono leading-relaxed">
                {agent.current_task}
              </p>
            </div>
          )}

          {/* Message input */}
          <div className="px-4 py-3 border-b border-white/5">
            <div className="flex items-center gap-2">
              <input
                ref={inputRef}
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                placeholder="发送消息给此 Agent..."
                className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-white/30 focus:outline-none focus:border-white/25"
                disabled={sending}
              />
              <button
                onClick={handleSend}
                disabled={!message.trim() || sending}
                className="px-3 py-2 rounded-lg bg-blue-500/20 text-blue-400 text-sm font-medium hover:bg-blue-500/30 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                ▶
              </button>
            </div>
          </div>

          {/* Config section */}
          <div className="px-4 py-3 flex items-center justify-between text-xs text-white/40">
            <div className="flex items-center gap-3">
              <span>模型: {agent.model}</span>
              <span>思考: {agent.thinking_level}</span>
              <span>{agent.thinking_enabled ? "✅开启" : "⛔关闭"}</span>
            </div>
            <button
              onClick={() => setExpanded(false)}
              className="text-white/30 hover:text-white/60 transition-colors"
            >
              收起 ▲
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
