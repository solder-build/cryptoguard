"use client";

import { useEffect, useState } from "react";

const agents = [
  { icon: "\uD83D\uDD0D", name: "Token Risk Analyzer", action: "Scanning liquidity, holders, permissions..." },
  { icon: "\uD83D\uDEE1\uFE0F", name: "Smart Contract Auditor", action: "Checking for honeypots, hidden functions..." },
  { icon: "\uD83D\uDCCA", name: "Market Intelligence", action: "Analyzing volume, whales, sentiment..." },
];

export default function LoadingAnalysis() {
  const [activeAgent, setActiveAgent] = useState(0);
  const [elapsed, setElapsed] = useState(0);

  // Advance to next agent every 8s (realistic for actual agent response times)
  // Caps at the last agent — no looping
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveAgent((prev) => Math.min(prev + 1, agents.length - 1));
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  // Elapsed timer
  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center gap-8 py-16">
      {/* Scanning animation */}
      <div className="relative">
        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-accent-teal/20 to-accent-blue/20 flex items-center justify-center">
          <div className="w-14 h-14 rounded-full bg-gradient-to-br from-accent-teal/30 to-accent-blue/30 flex items-center justify-center">
            <svg
              className="w-8 h-8 text-accent-teal animate-pulse"
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
        {/* Orbiting dot */}
        <div className="absolute inset-0 animate-spin" style={{ animationDuration: "3s" }}>
          <div className="w-2.5 h-2.5 bg-accent-teal rounded-full absolute -top-1 left-1/2 -translate-x-1/2 shadow-lg shadow-accent-teal/50" />
        </div>
      </div>

      <div className="text-center">
        <h3 className="text-text-primary text-xl font-semibold mb-1">
          Analyzing Target
        </h3>
        <p className="text-text-secondary text-sm">
          {elapsed}s elapsed
        </p>
      </div>

      {/* Ping-pong bar */}
      <div className="w-full max-w-sm">
        <div className="h-1 bg-surface rounded-full overflow-hidden relative">
          <div
            className="absolute h-full w-1/3 bg-gradient-to-r from-transparent via-accent-teal to-transparent rounded-full"
            style={{
              animation: "pingpong 1.5s ease-in-out infinite alternate",
            }}
          />
        </div>
        <style jsx>{`
          @keyframes pingpong {
            0% { left: 0%; }
            100% { left: 67%; }
          }
        `}</style>
      </div>

      {/* Agent steps */}
      <div className="w-full max-w-sm space-y-2">
        {agents.map((agent, i) => {
          const isDone = i < activeAgent;
          const isActive = i === activeAgent;
          const isPending = i > activeAgent;

          return (
            <div
              key={i}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg border transition-all duration-500 ${
                isActive
                  ? "border-accent-teal/40 bg-accent-teal/5"
                  : isDone
                  ? "border-safe/20 bg-safe/5 opacity-80"
                  : "border-border/50 bg-surface/50 opacity-40"
              }`}
            >
              <span className={`text-lg ${isPending ? "grayscale opacity-50" : ""}`}>
                {agent.icon}
              </span>
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium ${isDone ? "text-safe" : isActive ? "text-text-primary" : "text-text-secondary"}`}>
                  {agent.name}
                </p>
                <p className="text-text-secondary text-xs truncate">
                  {isDone ? "Done" : isActive ? agent.action : "Queued"}
                </p>
              </div>
              {isDone && (
                <svg className="w-4 h-4 text-safe flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              )}
              {isActive && (
                <div className="flex gap-1 flex-shrink-0">
                  <div className="w-1.5 h-1.5 bg-accent-teal rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <div className="w-1.5 h-1.5 bg-accent-teal rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <div className="w-1.5 h-1.5 bg-accent-teal rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
