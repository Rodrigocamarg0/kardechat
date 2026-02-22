"use client";

import { useState, useRef, useEffect } from "react";
import type { Session } from "@supabase/supabase-js";
import AuthGuard from "@/components/AuthGuard";
import ChatMessage from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import { sendMessage, type Citation } from "@/lib/api";
import { supabase } from "@/lib/supabase";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  confidence?: string;
}

function ChatContent({ session }: { session: Session }) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Olá! Sou o **Kardechat**, seu guia pela Doutrina Espírita. " +
        "Faça qualquer pergunta sobre os ensinamentos de Allan Kardec e " +
        "buscarei a resposta nos livros do Pentateuco Espírita.\n\n" +
        "Você pode pedir respostas mais detalhadas a qualquer momento.",
      confidence: "high",
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
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
    setIsLoading(true);

    try {
      const token = session.access_token;

      // Detecta se o usuário quer resposta extensiva
      const extensivePatterns = [
        "mais detalhes",
        "mais detalhe",
        "explique melhor",
        "aprofunde",
        "mais extenso",
        "mais completo",
        "detalhe mais",
        "elabore mais",
        "cite as fontes",
      ];
      const isExtensive = extensivePatterns.some((p) =>
        question.toLowerCase().includes(p)
      );

      // Pega última resposta do assistente para contexto extensivo
      const lastAssistant = [...messages]
        .reverse()
        .find((m) => m.role === "assistant");

      const response = await sendMessage(question, token, {
        extensive: isExtensive,
        previous_answer: isExtensive ? lastAssistant?.content : undefined,
      });

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer,
        citations: response.citations,
        confidence: response.confidence,
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
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
  };

  return (
    <div className="flex flex-col h-screen bg-spirit-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur border-b border-spirit-200 px-4 py-3">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">&#9770;</span>
            <h1 className="text-xl font-bold text-spirit-900">Kardechat</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-spirit-500 hidden sm:inline">
              {session.user.email}
            </span>
            <button
              onClick={handleLogout}
              className="text-sm text-spirit-500 hover:text-spirit-700 transition-colors"
            >
              Sair
            </button>
          </div>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto">
          {messages.map((msg) => (
            <ChatMessage
              key={msg.id}
              role={msg.role}
              content={msg.content}
              citations={msg.citations}
              confidence={msg.confidence}
            />
          ))}

          {isLoading && (
            <ChatMessage role="assistant" content="" isLoading />
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
      {(session) => <ChatContent session={session} />}
    </AuthGuard>
  );
}
