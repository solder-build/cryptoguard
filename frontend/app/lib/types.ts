export type RiskLevel = "SAFE" | "CAUTION" | "WARNING" | "DANGER";

export type AgentType = "token" | "contract" | "market";

export interface AgentAnalysis {
  agent: AgentType;
  name: string;
  score: number;
  riskLevel: RiskLevel;
  summary: string;
  findings: string[];
  details: string;
}

export interface AnalysisResult {
  query: string;
  overallScore: number;
  overallRisk: RiskLevel;
  timestamp: string;
  agents: AgentAnalysis[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  agent?: AgentType | "all";
  timestamp: string;
}

export interface RecentAnalysis {
  query: string;
  score: number;
  riskLevel: RiskLevel;
  timestamp: string;
}
