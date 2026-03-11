"use client";

import ReactMarkdown from "react-markdown";
import Citations from "./Citations";
import type { Citation } from "@/lib/api";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  confidence?: string;
  strategy?: string;
  isLoading?: boolean;
}

const CONFIDENCE_CONFIG: Record<string, { label: string; cls: string }> = {
  high:   { label: "alta correspondência", cls: "high" },
  medium: { label: "correspondência média", cls: "medium" },
  low:    { label: "busca ampliada",        cls: "low" },
};

export default function ChatMessage({
  role,
  content,
  citations,
  confidence,
  strategy,
  isLoading,
}: ChatMessageProps) {
  const isUser = role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end mb-6 msg-appear">
        <div className="user-bubble">{content}</div>
      </div>
    );
  }

  const confConfig = confidence
    ? CONFIDENCE_CONFIG[confidence] ?? CONFIDENCE_CONFIG.low
    : null;

  return (
    <div className="flex justify-start mb-8 msg-appear">
      <div style={{ maxWidth: "82%", minWidth: 0 }}>
        {/* Confidence tag */}
        {confConfig && !isLoading && (
          <div className={`confidence-tag ${confConfig.cls}`}>
            <span>◈</span>
            <span>{confConfig.label}</span>
          </div>
        )}

        {/* Content */}
        <div className="chat-markdown">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>

        {/* Citations */}
        {citations && citations.length > 0 && (
          <Citations citations={citations} strategy={strategy} />
        )}
      </div>
    </div>
  );
}
