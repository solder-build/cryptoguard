"use client";

import { useEffect, useState } from "react";
import { RiskLevel } from "../lib/types";
import { getRiskColor } from "../lib/utils";

interface RiskScoreGaugeProps {
  score: number;
  riskLevel: RiskLevel;
  size?: number;
  strokeWidth?: number;
  animated?: boolean;
}

export default function RiskScoreGauge({
  score,
  riskLevel,
  size = 180,
  strokeWidth = 10,
  animated = true,
}: RiskScoreGaugeProps) {
  const [displayScore, setDisplayScore] = useState(animated ? 0 : score);
  const [fillProgress, setFillProgress] = useState(animated ? 0 : score);

  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (fillProgress / 100) * circumference;
  const color = getRiskColor(riskLevel);

  useEffect(() => {
    if (!animated) return;

    const duration = 1500;
    const startTime = performance.now();

    function animate(currentTime: number) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);

      setDisplayScore(Math.round(eased * score));
      setFillProgress(eased * score);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    }

    requestAnimationFrame(animate);
  }, [score, animated]);

  const riskLabel = {
    SAFE: "SAFE",
    CAUTION: "CAUTION",
    WARNING: "WARNING",
    DANGER: "DANGER",
  };

  const riskIcon = {
    SAFE: "\u2705",
    CAUTION: "\u26A0\uFE0F",
    WARNING: "\u26A0\uFE0F",
    DANGER: "\uD83D\uDEAB",
  };

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative" style={{ width: size, height: size }}>
        <svg
          width={size}
          height={size}
          className="-rotate-90"
          viewBox={`0 0 ${size} ${size}`}
        >
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#262626"
            strokeWidth={strokeWidth}
          />
          {/* Score arc */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{
              filter: `drop-shadow(0 0 8px ${color}40)`,
              transition: animated ? "none" : "stroke-dashoffset 1.5s ease-out",
            }}
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="text-4xl font-bold font-mono"
            style={{ color }}
          >
            {displayScore}
          </span>
          <span className="text-xs text-text-secondary mt-1">/ 100 RISK</span>
        </div>
      </div>
      <div
        className="px-4 py-1.5 rounded-full border text-sm font-semibold tracking-wider"
        style={{
          color,
          borderColor: `${color}50`,
          backgroundColor: `${color}15`,
        }}
      >
        {riskIcon[riskLevel]} {riskLabel[riskLevel]}
      </div>
    </div>
  );
}
