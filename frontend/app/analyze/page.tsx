"use client";

import { useEffect, useState, useCallback, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import SearchBar from "../components/SearchBar";
import RiskScoreGauge from "../components/RiskScoreGauge";
import AgentCard from "../components/AgentCard";
import LoadingAnalysis from "../components/LoadingAnalysis";
import { AnalysisResult } from "../lib/types";
import { analyzeToken } from "../lib/api";
import { truncateAddress } from "../lib/utils";

function AnalyzeContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") || "";

  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = useCallback(async (query: string) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await analyzeToken(query);
      setResult(data);
    } catch {
      setError("Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (initialQuery) {
      runAnalysis(initialQuery);
    }
  }, [initialQuery, runAnalysis]);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
      {/* Search */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-text-primary mb-4">
          Analyze Token
        </h1>
        <SearchBar onSubmit={runAnalysis} />
      </div>

      {/* Loading */}
      {loading && <LoadingAnalysis />}

      {/* Error */}
      {error && (
        <div className="bg-danger/10 border border-danger/30 text-danger rounded-xl px-6 py-4 text-sm">
          {error}
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="space-y-8 animate-fade-in">
          {/* Header with score */}
          <div className="bg-surface border border-border rounded-xl p-6 sm:p-8">
            <div className="flex flex-col sm:flex-row items-center gap-8">
              <RiskScoreGauge
                score={result.overallScore}
                riskLevel={result.overallRisk}
              />
              <div className="flex-1 text-center sm:text-left">
                <p className="text-text-secondary text-sm mb-1">
                  Analysis Target
                </p>
                <p className="text-text-primary font-mono text-lg mb-4 break-all">
                  {truncateAddress(result.query, 12)}
                </p>
                <div className="grid grid-cols-3 gap-4">
                  {result.agents.map((agent) => (
                    <div key={agent.agent} className="text-center">
                      <p className="text-text-secondary text-xs mb-1">
                        {agent.name.split(" ").slice(-1)[0]}
                      </p>
                      <p
                        className="font-mono font-bold text-lg"
                        style={{
                          color:
                            agent.score <= 25
                              ? "#22c55e"
                              : agent.score <= 50
                              ? "#eab308"
                              : agent.score <= 75
                              ? "#f97316"
                              : "#ef4444",
                        }}
                      >
                        {agent.score}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Demo mode banner — only when using mock data */}
          {result.isMock && (
            <div className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-accent-teal/5 border border-accent-teal/20 text-xs text-accent-teal">
              <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Demo mode — showing mock analysis data. Connect the backend API for live results.</span>
            </div>
          )}

          {/* NFA Disclaimer — always shown */}
          <div className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-yellow-500/5 border border-yellow-500/20 text-xs text-yellow-500">
            <span className="flex-shrink-0 text-base">&#9888;&#65039;</span>
            <span>
              <strong>Not Financial Advice.</strong> CryptoGuard provides risk analysis for informational purposes only. Always do your own research (DYOR) before making any investment decisions.
            </span>
          </div>

          {/* Agent Analysis Cards */}
          <div>
            <h2 className="text-text-primary font-semibold text-lg mb-4">
              Agent Reports
            </h2>
            <div className="space-y-3">
              {result.agents.map((agent, i) => (
                <AgentCard key={agent.agent} analysis={agent} index={i} />
              ))}
            </div>
          </div>

          {/* Timestamp */}
          <p className="text-text-secondary/50 text-xs text-center">
            Analysis completed at{" "}
            {new Date(result.timestamp).toLocaleString()}
          </p>
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && !error && (
        <div className="text-center py-20">
          <div className="text-5xl mb-4">{"\uD83D\uDEE1\uFE0F"}</div>
          <h2 className="text-text-primary text-xl font-semibold mb-2">
            Ready to Analyze
          </h2>
          <p className="text-text-secondary text-sm max-w-md mx-auto">
            Paste a token address or project name above to get a comprehensive
            risk analysis from our AI security team.
          </p>
        </div>
      )}
    </div>
  );
}

export default function AnalyzePage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
          <div className="h-12 bg-surface rounded-xl animate-pulse" />
        </div>
      }
    >
      <AnalyzeContent />
    </Suspense>
  );
}
