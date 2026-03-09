"use client";

import ReactMarkdown from "react-markdown";
import Citations from "./Citations";
import type { Citation } from "@/lib/api";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  confidence?: string;
  isLoading?: boolean;
}

function ConfidenceBadge({ confidence }: { confidence: string }) {
  const config: Record<string, { label: string; color: string }> = {
    high: { label: "Alta confiança", color: "bg-green-100 text-green-800" },
    medium: { label: "Confiança média", color: "bg-yellow-100 text-yellow-800" },
    low: { label: "Busca ampliada", color: "bg-blue-100 text-blue-800" },
  };

  const c = config[confidence] || config.low;

  return (
    <span className={`inline-block text-xs px-2 py-0.5 rounded-full ${c.color} mb-2`}>
      {c.label}
    </span>
  );
}

export default function ChatMessage({
  role,
  content,
  citations,
  confidence,
  isLoading,
}: ChatMessageProps) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[85%] md:max-w-[70%] rounded-2xl px-5 py-3 ${
          isUser
            ? "bg-primary-700 text-white rounded-br-md"
            : "bg-white shadow-md rounded-bl-md"
        }`}
      >
        {!isUser && confidence && <ConfidenceBadge confidence={confidence} />}

        {isLoading ? (
          <div className="typing-cursor text-spirit-600">Consultando os livros</div>
        ) : (
          <div className={`chat-markdown ${isUser ? "" : "text-spirit-800"}`}>
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        )}

        {!isUser && citations && citations.length > 0 && (
          <Citations citations={citations} />
        )}
      </div>
    </div>
  );
}
