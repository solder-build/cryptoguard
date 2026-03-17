import { RiskLevel, AgentType } from "./types";

export function getRiskColor(level: RiskLevel): string {
  switch (level) {
    case "SAFE":
      return "#22c55e";
    case "CAUTION":
      return "#eab308";
    case "WARNING":
      return "#f97316";
    case "DANGER":
      return "#ef4444";
  }
}

export function getRiskBgClass(level: RiskLevel): string {
  switch (level) {
    case "SAFE":
      return "bg-safe/10 text-safe border-safe/30";
    case "CAUTION":
      return "bg-caution/10 text-caution border-caution/30";
    case "WARNING":
      return "bg-warning/10 text-warning border-warning/30";
    case "DANGER":
      return "bg-danger/10 text-danger border-danger/30";
  }
}

export function getScoreRiskLevel(score: number): RiskLevel {
  if (score <= 25) return "SAFE";
  if (score <= 50) return "CAUTION";
  if (score <= 75) return "WARNING";
  return "DANGER";
}

export function getAgentIcon(agent: AgentType): string {
  switch (agent) {
    case "token":
      return "\uD83D\uDD0D";
    case "contract":
      return "\uD83D\uDEE1\uFE0F";
    case "market":
      return "\uD83D\uDCCA";
  }
}

export function getAgentName(agent: AgentType): string {
  switch (agent) {
    case "token":
      return "Token Risk Analyzer";
    case "contract":
      return "Smart Contract Auditor";
    case "market":
      return "Market Intelligence";
  }
}

export function truncateAddress(address: string, chars = 6): string {
  if (address.length <= chars * 2 + 3) return address;
  return `${address.slice(0, chars)}...${address.slice(-chars)}`;
}
