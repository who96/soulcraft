"use client";

import type { ConnectedApp } from "@/types/agent";

const APP_CONFIG: Record<ConnectedApp, { icon: string; label: string }> = {
  wechat: { icon: "💬", label: "微信" },
  feishu: { icon: "🐦", label: "飞书" },
  discord: { icon: "🎮", label: "Discord" },
  slack: { icon: "💼", label: "Slack" },
  telegram: { icon: "✈️", label: "Telegram" },
  email: { icon: "📧", label: "Email" },
};

export function AppIcons({ apps }: { apps: ConnectedApp[] }) {
  if (apps.length === 0) return null;

  return (
    <div className="flex items-center gap-1">
      {apps.map((app) => {
        const config = APP_CONFIG[app];
        if (!config) return null;
        return (
          <span
            key={app}
            title={config.label}
            className="text-sm cursor-default hover:scale-110 transition-transform"
          >
            {config.icon}
          </span>
        );
      })}
    </div>
  );
}
