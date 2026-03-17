import { AnalysisResult, ChatMessage } from "./types";
import { getMockAnalysis, getMockChatResponse } from "./mock-data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

async function apiFetch<T>(
  path: string,
  options: RequestInit
): Promise<{ data: T | null; error: string | null; isMock: boolean }> {
  if (!API_URL) {
    return { data: null, error: "No API URL configured", isMock: true };
  }

  try {
    const res = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!res.ok) {
      throw new Error(`API error: ${res.status}`);
    }

    const data = await res.json();
    return { data, error: null, isMock: false };
  } catch {
    return { data: null, error: "Backend unavailable", isMock: true };
  }
}

export async function analyzeToken(
  query: string,
  type: "token" | "project" | "general" = "token"
): Promise<AnalysisResult> {
  const { data, isMock } = await apiFetch<AnalysisResult>("/api/analyze", {
    method: "POST",
    body: JSON.stringify({ query, type }),
  });

  if (isMock || !data) {
    // Simulate network delay for realistic demo
    await new Promise((r) => setTimeout(r, 2500));
    return getMockAnalysis(query);
  }

  return data;
}

export async function sendChatMessage(
  message: string,
  agent: "token" | "contract" | "market" | "all" = "all"
): Promise<string> {
  const { data, isMock } = await apiFetch<{ response: string }>(
    "/api/chat",
    {
      method: "POST",
      body: JSON.stringify({ message, agent }),
    }
  );

  if (isMock || !data) {
    await new Promise((r) => setTimeout(r, 1800));
    return getMockChatResponse(agent, message);
  }

  return data.response;
}

export async function checkHealth(): Promise<boolean> {
  const { error } = await apiFetch<{ status: string }>("/api/health", {
    method: "GET",
  });
  return !error;
}
