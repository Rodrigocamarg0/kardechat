"use client";

import { useState } from "react";
import type { Citation } from "@/lib/api";

interface CitationsProps {
  citations: Citation[];
}

export default function Citations({ citations }: CitationsProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!citations.length) return null;

  return (
    <div className="mt-3">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-sm text-spirit-600 hover:text-spirit-800 transition-colors"
      >
        <span
          className={`transform transition-transform ${isOpen ? "rotate-90" : ""}`}
        >
          &#9654;
        </span>
        <span>
          {citations.length} {citations.length === 1 ? "citação" : "citações"}{" "}
          encontrada{citations.length === 1 ? "" : "s"}
        </span>
      </button>

      {isOpen && (
        <div className="mt-3 space-y-3 pl-4 border-l-2 border-spirit-200">
          {citations.map((citation, i) => (
            <div
              key={i}
              className="bg-spirit-50 rounded-lg p-4 text-sm"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-spirit-800">
                  {citation.book}
                </span>
                <span className="text-xs text-spirit-500">
                  {citation.reference} &middot; Similaridade:{" "}
                  {(citation.score * 100).toFixed(0)}%
                </span>
              </div>

              {citation.question && (
                <p className="text-spirit-700 mb-1">
                  <strong>P:</strong> {citation.question}
                </p>
              )}
              {citation.answer && (
                <p className="text-spirit-600">
                  <strong>R:</strong> {citation.answer}
                </p>
              )}
              {citation.text && (
                <p className="text-spirit-600 italic">
                  &ldquo;{citation.text}&rdquo;
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
