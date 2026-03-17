"use client";

import Link from "next/link";
import SearchBar from "./components/SearchBar";
import { MOCK_RECENT_ANALYSES } from "./lib/mock-data";
import { getRiskColor } from "./lib/utils";

const agents = [
  {
    icon: "\uD83D\uDD0D",
    name: "Token Risk Analyzer",
    description: "Forensic analysis of token fundamentals, supply distribution, liquidity depth, and holder behavior patterns.",
    color: "from-teal-500/20 to-cyan-500/20",
  },
  {
    icon: "\uD83D\uDEE1\uFE0F",
    name: "Smart Contract Auditor",
    description: "Security assessment of contract code, permission structures, upgrade patterns, and known vulnerability matching.",
    color: "from-blue-500/20 to-indigo-500/20",
  },
  {
    icon: "\uD83D\uDCCA",
    name: "Market Intelligence",
    description: "Social signal analysis, community health metrics, team credibility checks, and market context evaluation.",
    color: "from-purple-500/20 to-pink-500/20",
  },
];

export default function HomePage() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6">
      {/* Hero */}
      <section className="pt-20 pb-16 sm:pt-28 sm:pb-20 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface border border-border text-xs text-text-secondary mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-safe animate-pulse" />
          Multi-Agent Threat Intelligence
        </div>
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-text-primary mb-4 leading-tight">
          <span className="bg-gradient-to-r from-accent-teal to-accent-blue bg-clip-text text-transparent">
            CryptoGuard
          </span>
        </h1>
        <p className="text-xl sm:text-2xl text-text-secondary mb-2">
          Your AI Crypto Security Team
        </p>
        <p className="text-text-secondary/70 max-w-xl mx-auto mb-10 text-sm sm:text-base">
          Three specialized AI agents work together to analyze tokens,
          audit contracts, and evaluate market signals — protecting you from
          scams and rug pulls.
        </p>

        <div className="max-w-2xl mx-auto">
          <SearchBar size="large" />
          <div className="mt-3 flex flex-wrap items-center justify-center gap-2 text-xs text-text-secondary/50">
            <span>Try:</span>
            <Link
              href="/analyze?q=So11111111111111111111111111111111111111112"
              className="hover:text-accent-teal transition-colors font-mono"
            >
              SOL token
            </Link>
            <span>|</span>
            <Link
              href="/analyze?q=ScamToken111111111111111111111111111111111"
              className="hover:text-danger transition-colors font-mono"
            >
              Scam token
            </Link>
            <span>|</span>
            <Link
              href="/analyze?q=7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
              className="hover:text-caution transition-colors font-mono"
            >
              Risky token
            </Link>
          </div>
        </div>
      </section>

      {/* Agent Cards */}
      <section className="pb-16 sm:pb-20">
        <h2 className="text-center text-text-secondary text-sm font-medium uppercase tracking-wider mb-8">
          Your Security Team
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {agents.map((agent, i) => (
            <div
              key={i}
              className="bg-surface border border-border rounded-xl p-6 hover:border-border/80 transition-all group"
            >
              <div
                className={`w-12 h-12 rounded-lg bg-gradient-to-br ${agent.color} flex items-center justify-center text-2xl mb-4`}
              >
                {agent.icon}
              </div>
              <h3 className="text-text-primary font-semibold mb-2">
                {agent.name}
              </h3>
              <p className="text-text-secondary text-sm leading-relaxed">
                {agent.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Recent Analyses */}
      <section className="pb-20">
        <h2 className="text-center text-text-secondary text-sm font-medium uppercase tracking-wider mb-8">
          Recent Analyses
        </h2>
        <div className="bg-surface border border-border rounded-xl overflow-hidden">
          <div className="grid grid-cols-[1fr_auto_auto_auto] gap-4 px-6 py-3 border-b border-border text-xs text-text-secondary uppercase tracking-wider">
            <span>Target</span>
            <span>Score</span>
            <span>Risk</span>
            <span>Time</span>
          </div>
          {MOCK_RECENT_ANALYSES.map((analysis, i) => {
            const color = getRiskColor(analysis.riskLevel);
            return (
              <Link
                key={i}
                href={`/analyze?q=${encodeURIComponent(analysis.query)}`}
                className="grid grid-cols-[1fr_auto_auto_auto] gap-4 px-6 py-3.5 items-center hover:bg-surface-light transition-colors border-b border-border last:border-b-0"
              >
                <span className="font-mono text-sm text-text-primary truncate">
                  {analysis.query}
                </span>
                <span
                  className="font-mono text-sm font-bold text-right w-10"
                  style={{ color }}
                >
                  {analysis.score}
                </span>
                <span
                  className="text-xs font-semibold px-2 py-0.5 rounded w-20 text-center"
                  style={{
                    color,
                    backgroundColor: `${color}15`,
                  }}
                >
                  {analysis.riskLevel}
                </span>
                <span className="text-xs text-text-secondary w-20 text-right">
                  {analysis.timestamp}
                </span>
              </Link>
            );
          })}
        </div>
      </section>
    </div>
  );
}
