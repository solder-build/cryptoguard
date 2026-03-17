"use client";

import { useEffect, useState } from "react";

const agents = [
  { icon: "\uD83D\uDD0D", name: "Token Risk Analyzer", action: "Scanning token fundamentals..." },
  { icon: "\uD83D\uDEE1\uFE0F", name: "Smart Contract Auditor", action: "Auditing contract security..." },
  { icon: "\uD83D\uDCCA", name: "Market Intelligence", action: "Gathering market signals..." },
];

export default function LoadingAnalysis() {
  const [activeAgent, setActiveAgent] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveAgent((prev) => (prev + 1) % agents.length);
    }, 800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center gap-8 py-16">
      {/* Pulsing shield */}
      <div className="relative">
        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-accent-teal/20 to-accent-blue/20 flex items-center justify-center animate-pulse">
          <div className="w-14 h-14 rounded-full bg-gradient-to-br from-accent-teal/30 to-accent-blue/30 flex items-center justify-center">
            <svg
              className="w-8 h-8 text-accent-teal"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"
              />
            </svg>
          </div>
        </div>
      </div>

      <div className="text-center">
        <h3 className="text-text-primary text-xl font-semibold mb-2">
          Agents Analyzing...
        </h3>
        <p className="text-text-secondary text-sm">
          Our AI security team is reviewing this target
        </p>
      </div>

      {/* Agent progress */}
      <div className="w-full max-w-sm space-y-3">
        {agents.map((agent, i) => (
          <div
            key={i}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg border transition-all duration-300 ${
              i === activeAgent
                ? "border-accent-teal/40 bg-accent-teal/5"
                : i < activeAgent
                ? "border-safe/30 bg-safe/5"
                : "border-border bg-surface"
            }`}
          >
            <span className="text-xl">{agent.icon}</span>
            <div className="flex-1">
              <p className="text-text-primary text-sm font-medium">
                {agent.name}
              </p>
              <p className="text-text-secondary text-xs">
                {i < activeAgent
                  ? "Complete"
                  : i === activeAgent
                  ? agent.action
                  : "Waiting..."}
              </p>
            </div>
            {i < activeAgent && (
              <svg
                className="w-4 h-4 text-safe"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={3}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M5 13l4 4L19 7"
                />
              </svg>
            )}
            {i === activeAgent && (
              <div className="w-4 h-4 border-2 border-accent-teal border-t-transparent rounded-full animate-spin" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
