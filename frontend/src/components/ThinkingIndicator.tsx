"use client";

import { useState, useEffect } from "react";

interface ThinkingIndicatorProps {
  question: string;
}

type Phase = "interpreting" | "searching" | "composing";

export default function ThinkingIndicator({ question }: ThinkingIndicatorProps) {
  const [phase, setPhase] = useState<Phase>("interpreting");
  const [dots, setDots] = useState(".");

  useEffect(() => {
    const t1 = setTimeout(() => setPhase("searching"), 900);
    const t2 = setTimeout(() => setPhase("composing"), 2800);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setDots(d => d.length >= 3 ? "." : d + ".");
    }, 420);
    return () => clearInterval(interval);
  }, []);

  const querySnippet =
    question.length > 52 ? question.slice(0, 52) + "…" : question;

  return (
    <div className="thinking-panel msg-appear">
      {/* Step 1 */}
      <div className={`thinking-step ${phase === "interpreting" ? "active" : "done"}`}>
        <span className="step-dot" />
        {phase === "interpreting"
          ? `Interpretando a questão${dots}`
          : "Questão interpretada"}
      </div>

      {/* Tool Call Card */}
      {(phase === "searching" || phase === "composing") && (
        <div className="tool-call-block">
          <div className="tool-call-header">
            <span>⟨/⟩</span>
            <span>search_knowledge</span>
          </div>
          <div className="tool-call-row">
            <span className="tool-key">query</span>
            <span className="tool-sep">:</span>
            <span className="tool-val">&ldquo;{querySnippet}&rdquo;</span>
          </div>
          <div className="tool-call-row">
            <span className="tool-key">limit</span>
            <span className="tool-sep">:</span>
            <span className="tool-val">5</span>
          </div>
          {phase === "searching" && <div className="tool-shimmer" />}
        </div>
      )}

      {/* Step 2 */}
      {phase === "searching" && (
        <div className="thinking-step active">
          <span className="step-dot" />
          {`Pesquisando nas obras${dots}`}
        </div>
      )}

      {/* Step 3 */}
      {phase === "composing" && (
        <>
          <div className="thinking-step done">
            <span className="step-dot" />
            Fontes localizadas
          </div>
          <div className="thinking-step active">
            <span className="step-dot" />
            {`Compondo a resposta${dots}`}
          </div>
        </>
      )}
    </div>
  );
}
