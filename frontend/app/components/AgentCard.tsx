"use client";

import { useState } from "react";
import { AgentAnalysis } from "../lib/types";
import { getRiskColor, getAgentIcon } from "../lib/utils";

interface AgentCardProps {
  analysis: AgentAnalysis;
  index: number;
}

export default function AgentCard({ analysis, index }: AgentCardProps) {
  const [expanded, setExpanded] = useState(false);
  const color = getRiskColor(analysis.riskLevel);

  return (
    <div
      className="bg-surface border border-border rounded-xl overflow-hidden animate-slide-up"
      style={{ animationDelay: `${index * 150}ms`, animationFillMode: "both" }}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-6 py-5 flex items-center gap-4 hover:bg-surface-light transition-colors text-left"
      >
        <div className="text-3xl flex-shrink-0">{getAgentIcon(analysis.agent)}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-1">
            <h3 className="text-text-primary font-semibold text-lg">
              {analysis.name}
            </h3>
            <span
              className="text-xs font-mono font-bold px-2 py-0.5 rounded"
              style={{
                color,
                backgroundColor: `${color}15`,
              }}
            >
              {analysis.score}/100
            </span>
          </div>
          <p className="text-text-secondary text-sm line-clamp-2">
            {analysis.summary}
          </p>
        </div>
        <svg
          className={`w-5 h-5 text-text-secondary transition-transform flex-shrink-0 ${
            expanded ? "rotate-180" : ""
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {expanded && (
        <div className="px-6 pb-6 border-t border-border">
          {/* Key Findings */}
          <div className="mt-4">
            <h4 className="text-text-primary font-medium mb-3 text-sm uppercase tracking-wider">
              Key Findings
            </h4>
            <ul className="space-y-2">
              {analysis.findings.map((finding, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <span
                    className="mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: color }}
                  />
                  <span className="text-text-secondary">{finding}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Detailed Analysis */}
          <div className="mt-5">
            <h4 className="text-text-primary font-medium mb-2 text-sm uppercase tracking-wider">
              Detailed Analysis
            </h4>
            <p className="text-text-secondary text-sm leading-relaxed">
              {analysis.details}
            </p>
          </div>

          {/* Score Bar */}
          <div className="mt-5">
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-text-secondary">Risk Score</span>
              <span style={{ color }} className="font-mono font-bold">
                {analysis.score}/100
              </span>
            </div>
            <div className="h-2 bg-border rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-1000 ease-out"
                style={{
                  width: `${analysis.score}%`,
                  backgroundColor: color,
                  boxShadow: `0 0 10px ${color}60`,
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
