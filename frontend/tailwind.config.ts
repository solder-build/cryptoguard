import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0a0a0a",
        surface: "#141414",
        "surface-light": "#1a1a1a",
        border: "#262626",
        "text-primary": "#fafafa",
        "text-secondary": "#a3a3a3",
        safe: "#22c55e",
        caution: "#eab308",
        warning: "#f97316",
        danger: "#ef4444",
        accent: {
          teal: "#14b8a6",
          blue: "#3b82f6",
        },
      },
      fontFamily: {
        mono: ["'JetBrains Mono'", "Fira Code", "monospace"],
      },
      animation: {
        "score-fill": "scoreFill 1.5s ease-out forwards",
        "fade-in": "fadeIn 0.5s ease-out forwards",
        "slide-up": "slideUp 0.4s ease-out forwards",
        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
      keyframes: {
        scoreFill: {
          "0%": { strokeDashoffset: "283" },
          "100%": { strokeDashoffset: "var(--score-offset)" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
