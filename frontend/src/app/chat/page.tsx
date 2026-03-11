"use client";

import { useState, useRef, useEffect } from "react";
import AuthGuard from "@/components/AuthGuard";
import ChatMessage from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import ThinkingIndicator from "@/components/ThinkingIndicator";
import { sendMessage, type Citation } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  confidence?: string;
  strategy?: string;
}

function ChatContent() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Olá. Sou o **Kardechat**, seu guia pela Doutrina Espírita.\n\n" +
        "Faça qualquer pergunta sobre os ensinamentos de Allan Kardec — " +
        "buscarei a resposta diretamente nas obras indexadas do autor.\n\n" +
        "Para respostas mais extensas, peça *\"explique com mais detalhes\"*.",
      confidence: "high",
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = async (question: string) => {
    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: question,
    };
    setMessages((prev) => [...prev, userMsg]);
    setCurrentQuestion(question);
    setIsLoading(true);

    try {
      const extensivePatterns = [
        "mais detalhes", "mais detalhe", "explique melhor",
        "aprofunde", "mais extenso", "mais completo",
        "detalhe mais", "elabore mais", "cite as fontes",
      ];
      const isExtensive = extensivePatterns.some((p) =>
        question.toLowerCase().includes(p)
      );

      const lastAssistant = [...messages]
        .reverse()
        .find((m) => m.role === "assistant");

      const response = await sendMessage(question, {
        extensive: isExtensive,
        previous_answer: isExtensive ? lastAssistant?.content : undefined,
      });

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer,
        citations: response.citations,
        confidence: response.confidence,
        strategy: response.strategy,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "Desculpe, ocorreu um erro ao consultar os livros. " +
          "Tente novamente em alguns instantes.",
      };
      setMessages((prev) => [...prev, errorMsg]);
      console.error(err);
    } finally {
      setIsLoading(false);
      setCurrentQuestion("");
    }
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100dvh",
        background: "var(--bg-primary)",
        position: "relative",
        zIndex: 1,
      }}
    >
      {/* Header */}
      <header className="chat-header">
        <div
          style={{
            maxWidth: "720px",
            margin: "0 auto",
            display: "flex",
            alignItems: "center",
            gap: "0.875rem",
          }}
        >
          <span className="header-star">✦</span>
          <div>
            <div className="header-title">Kardechat</div>
            <div className="header-subtitle">Doutrina Espírita · Allan Kardec</div>
          </div>
        </div>
      </header>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "2rem 1.5rem",
        }}
      >
        <div style={{ maxWidth: "720px", margin: "0 auto" }}>
          {messages.map((msg) => (
            <ChatMessage
              key={msg.id}
              role={msg.role}
              content={msg.content}
              citations={msg.citations}
              confidence={msg.confidence}
              strategy={msg.strategy}
            />
          ))}

          {isLoading && currentQuestion && (
            <div className="flex justify-start mb-8">
              <ThinkingIndicator question={currentQuestion} />
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <ChatInput onSend={handleSend} disabled={isLoading} />
    </div>
  );
}

export default function ChatPage() {
  return (
    <AuthGuard>
      {() => <ChatContent />}
    </AuthGuard>
  );
}
