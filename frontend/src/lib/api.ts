const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Citation {
  book: string;
  reference: string;
  question?: string;
  answer?: string;
  text?: string;
  score: number;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  strategy: string;
  confidence: string;
  top_score: number;
}

export async function sendMessage(
  question: string,
  token: string,
  options?: { extensive?: boolean; previous_answer?: string }
): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      question,
      extensive: options?.extensive || false,
      previous_answer: options?.previous_answer || null,
    }),
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error(`Erro na API: ${res.status} – ${error}`);
  }

  return res.json();
}
