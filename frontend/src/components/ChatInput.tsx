"use client";

import { useState, useRef, useEffect } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 150) + "px";
    }
  }, [message]);

  const handleSubmit = () => {
    const trimmed = message.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setMessage("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-spirit-200 bg-white/80 backdrop-blur px-4 py-3">
      <div className="max-w-3xl mx-auto flex gap-3 items-end">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Faça sua pergunta sobre a Doutrina Espírita..."
          disabled={disabled}
          rows={1}
          className="flex-1 resize-none rounded-xl border border-spirit-300 px-4 py-3 text-spirit-800 placeholder-spirit-400 focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-transparent disabled:opacity-50 bg-white"
        />
        <button
          onClick={handleSubmit}
          disabled={disabled || !message.trim()}
          className="bg-primary-700 hover:bg-primary-800 disabled:bg-spirit-300 text-white rounded-xl px-5 py-3 transition-colors font-medium"
        >
          Enviar
        </button>
      </div>
      <p className="text-center text-xs text-spirit-400 mt-2 max-w-3xl mx-auto">
        Respostas baseadas nos livros de Allan Kardec. Para respostas mais
        detalhadas, peça &ldquo;explique com mais detalhes&rdquo;.
      </p>
    </div>
  );
}
