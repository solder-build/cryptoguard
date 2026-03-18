import { AnalysisResult, AgentAnalysis, RiskLevel } from "./types";
import { getMockAnalysis, getMockChatResponse } from "./mock-data";

// Use NEXT_PUBLIC_API_URL if set, otherwise use relative paths (Next.js rewrites proxy to backend)
const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

// 3 minute timeout — agents can take 30-120s on free tier
const FETCH_TIMEOUT = 180_000;

async function apiFetch<T>(
  path: string,
  options: RequestInit
): Promise<{ data: T | null; error: string | null; isMock: boolean }> {

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT);

  try {
    const res = await fetch(`${API_URL}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    clearTimeout(timer);

    if (!res.ok) {
      throw new Error(`API error: ${res.status}`);
    }

    const data = await res.json();
    return { data, error: null, isMock: false };
  } catch {
    clearTimeout(timer);
    return { data: null, error: "Backend unavailable", isMock: true };
  }
}

function scoreToRiskLevel(score: number): RiskLevel {
  if (score <= 25) return "SAFE";
  if (score <= 50) return "CAUTION";
  if (score <= 75) return "WARNING";
  return "DANGER";
}

function mapApiResponse(raw: Record<string, unknown>): AnalysisResult {
  const unified = (raw.unified_risk_score || {}) as Record<string, unknown>;
  const overallScore = (unified.overall_score as number) ?? 50;
  const agentResponses = (raw.agent_responses || []) as Record<string, unknown>[];

  const agentMap: Record<string, "token" | "contract" | "market"> = {
    "token-analyzer": "token",
    "contract-auditor": "contract",
    "market-intel": "market",
  };

  const agents: AgentAnalysis[] = agentResponses.map((ar) => {
    const agentId = ar.agent as string;
    const response = (ar.response as string) || "";
    const agentScore = (ar.risk_score as number) ?? overallScore;
    const error = ar.error as string | undefined;

    // Extract findings and summary from response
    let findings: string[] = [];
    let summary = "";
    let details = response || error || "";

    if (response) {
      // Try parsing JSON from response (agent may return JSON block)
      const jsonMatch = response.match(/\{[\s\S]*"findings"[\s\S]*\}/);
      if (jsonMatch) {
        try {
          const parsed = JSON.parse(jsonMatch[0]);
          if (Array.isArray(parsed.findings)) {
            findings = parsed.findings.map((f: string) => f.replace(/^[\s\-\*]+/, "").trim());
          }
          summary = parsed.recommendation || parsed.summary || "";
          // Clean details: remove raw JSON, keep readable text
          details = response.replace(jsonMatch[0], "").replace(/```json\s*/g, "").replace(/```\s*/g, "").trim();
          if (!details) details = parsed.recommendation || "";
        } catch {
          // JSON parse failed, fall through to line parsing
        }
      }

      // Fallback: extract bullet points
      if (findings.length === 0) {
        const lines = response.split("\n").filter((l: string) => l.trim().startsWith("-") || l.trim().startsWith("*"));
        findings = lines.slice(0, 5).map((l: string) => l.replace(/^[\s\-\*]+/, "").trim()).filter(Boolean);
      }

      // Fallback summary
      if (!summary) {
        const recMatch = response.match(/recommendation[:\s]+(.*?)(?:\n|$)/i);
        summary = recMatch ? recMatch[1].trim() : response.replace(/```[\s\S]*?```/g, "").slice(0, 200);
      }

      // Clean up details — remove disclaimer duplication
      details = details.replace(/---[\s\S]*Disclaimer[\s\S]*$/i, "").trim();
    }

    if (error) {
      findings.push(`Agent error: ${error.slice(0, 100)}`);
    }

    return {
      agent: agentMap[agentId] || "token",
      name: (ar.agent_name as string) || agentId,
      score: agentScore,
      riskLevel: scoreToRiskLevel(agentScore),
      summary: summary || error || "Analysis completed",
      findings: findings.length > 0 ? findings : ["No specific findings reported"],
      details,
    };
  });

  // If no agents responded, add placeholders
  if (agents.length === 0) {
    agents.push({
      agent: "token",
      name: "Token Risk Analyzer",
      score: overallScore,
      riskLevel: scoreToRiskLevel(overallScore),
      summary: "Analysis completed",
      findings: ["See details below"],
      details: "",
    });
  }

  return {
    query: raw.query as string || "",
    overallScore,
    overallRisk: scoreToRiskLevel(overallScore),
    timestamp: (raw.timestamp as string) || new Date().toISOString(),
    agents,
    isMock: false,
  };
}

export async function analyzeToken(
  query: string,
  type: "token" | "project" | "general" = "token"
): Promise<AnalysisResult> {
  const { data, isMock } = await apiFetch<Record<string, unknown>>("/api/analyze", {
    method: "POST",
    body: JSON.stringify({ query, chain: "solana" }),
  });

  if (isMock || !data) {
    await new Promise((r) => setTimeout(r, 2500));
    const mock = getMockAnalysis(query);
    mock.isMock = true;
    return mock;
  }

  return mapApiResponse(data);
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
