import type { Message } from "src/pages/chat";

export async function askQuestionStream(question: string, history: Message[], shell_history: string): Promise<
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
            shell_history
        }),
    });
  return response.body?.getReader();
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
