import type { LLMResponse, Message } from "src/pages/chat";

export async function askQuestionStream(question: string, history: Message[]): Promise<
  ReadableStreamDefaultReader | undefined
> {
  const headers = new Headers({ "Cache-Control": "no-cache" });
    headers.set("Content-Type", "application/json");
    const response = await fetch("/api/chat_rq_stream", {
        method: "POST",
        headers,
        body: JSON.stringify({
            query: question,
            history,
            shell_history: '',
        }),
    });
  return response.body?.getReader();
}

export async function askQuestion(question: string): Promise<LLMResponse> {
  const url = new URL("/api/chat_rq", window.location.origin);

  url.searchParams.set("query", question);

  const response = await fetch(url.toString(), {
    method: "GET",
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  const text = await response.text();

  const trimmed = text.trim();
  if (trimmed.startsWith("<table")) {
    return {
      answer: trimmed,
      format: "Table",
    } as LLMResponse;
  } else if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
    try {
      const json = JSON.parse(trimmed);
      if (Array.isArray(json)) {
        return {
          answer: json,
          format: "Json",
        } as LLMResponse;
      } else if (typeof json === "object") {
        return { answer: json, format: "Json" } as LLMResponse;
      }
    } catch (e) {}
  }
  return { answer: trimmed, format: "Text" } as LLMResponse;
}

export interface AuthResponse {
  code: string;
  name: string;
  email: string;
}

export async function login({
  email,
  password,
}: {
  email: string;
  password: string;
}): Promise<AuthResponse> {
  const response = await fetch(`/api/authenticate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(`Login failed: ${message}`);
  }
  return await response.json();
}
