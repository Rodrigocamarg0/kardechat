"use client";

import { useState } from "react";
import type { Citation } from "@/lib/api";

interface CitationsProps {
  citations: Citation[];
  strategy?: string;
}

const BOOK_COLORS: Record<string, { dot: string; fill: string }> = {
  "O Livro dos Espíritos":             { dot: "#c9a84c", fill: "#c9a84c" },
  "O Livro dos Médiuns":               { dot: "#4a9c9c", fill: "#4a9c9c" },
  "O Evangelho Segundo o Espiritismo": { dot: "#c97a4c", fill: "#c97a4c" },
  "A Gênese":                          { dot: "#5c7cfa", fill: "#5c7cfa" },
};

function getBookColor(book: string) {
  if (book.toLowerCase().includes("espírit") || book.toLowerCase().includes("espirito"))
    return BOOK_COLORS["O Livro dos Espíritos"];
  if (book.toLowerCase().includes("médium") || book.toLowerCase().includes("medium"))
    return BOOK_COLORS["O Livro dos Médiuns"];
  if (book.toLowerCase().includes("evangelho"))
    return BOOK_COLORS["O Evangelho Segundo o Espiritismo"];
  if (book.toLowerCase().includes("gênese") || book.toLowerCase().includes("genesis"))
    return BOOK_COLORS["A Gênese"];
  return { dot: "#7a6d5a", fill: "#967a64" };
}

const STRATEGY_LABELS: Record<string, string> = {
  q_to_q:      "Q→Q match",
  book_search: "busca textual",
  hybrid:      "busca híbrida",
  expanded:    "busca ampliada",
};

function SourceCard({
  citation,
  index,
  forceOpen,
}: {
  citation: Citation;
  index: number;
  forceOpen: boolean;
}) {
  const [localOpen, setLocalOpen] = useState(false);
  const open = forceOpen || localOpen;
  const colors = getBookColor(citation.book);
  const pct = Math.round(citation.score * 100);

  return (
    <div className="source-card">
      <button
        className="source-card-trigger"
        onClick={() => setLocalOpen(!localOpen)}
        aria-expanded={open}
        style={{ animationDelay: `${index * 60}ms` }}
      >
        <div className="source-book-info">
          <span className="book-dot" style={{ background: colors.dot }} />
          <span className="book-name">{citation.book}</span>
        </div>
        <div className="source-meta">
          {citation.reference && (
            <span className="reference-tag">{citation.reference}</span>
          )}
          <div className="resonance">
            <div className="resonance-bar">
              <div
                className="resonance-fill"
                style={{ width: `${pct}%`, background: colors.fill }}
              />
            </div>
            <span className="resonance-pct">{pct}%</span>
          </div>
          <span className={`chevron ${open ? "open" : ""}`}>▶</span>
        </div>
      </button>

      {open && (
        <div className="source-card-body">
          {citation.question && (
            <div className="source-question">
              <span className="source-q-label">P</span>
              <span>{citation.question}</span>
            </div>
          )}
          {citation.answer && (
            <div className="source-answer">
              <span className="source-a-label">R</span>
              <span>{citation.answer}</span>
            </div>
          )}
          {citation.text && !citation.question && (
            <p className="source-text">{citation.text}</p>
          )}
        </div>
      )}
    </div>
  );
}

export default function Citations({ citations, strategy }: CitationsProps) {
  const [expanded, setExpanded] = useState(false);

  if (!citations.length) return null;

  const strategyLabel = strategy ? (STRATEGY_LABELS[strategy] ?? strategy) : null;

  return (
    <div className="sources-section">
      <div className="sources-header">
        <span className="sources-label">Fontes Consultadas</span>
        <span className="sources-count">{citations.length}</span>
        {strategyLabel && (
          <span
            className="sources-count"
            style={{
              color: "var(--emerald)",
              borderColor: "rgba(74,153,102,0.3)",
            }}
          >
            {strategyLabel}
          </span>
        )}
        <button
          onClick={() => setExpanded(!expanded)}
          style={{
            marginLeft: "auto",
            fontFamily: "var(--font-mono)",
            fontSize: "0.65rem",
            color: "var(--text-muted)",
            background: "none",
            border: "none",
            cursor: "pointer",
            textDecoration: "underline",
            textUnderlineOffset: "3px",
          }}
        >
          {expanded ? "recolher" : "expandir todas"}
        </button>
      </div>

      <div>
        {citations.map((citation, i) => (
          <SourceCard
            key={i}
            citation={citation}
            index={i}
            forceOpen={expanded}
          />
        ))}
      </div>
    </div>
  );
}
