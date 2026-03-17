"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";

interface SearchBarProps {
  size?: "large" | "normal";
  placeholder?: string;
  onSubmit?: (query: string) => void;
}

export default function SearchBar({
  size = "normal",
  placeholder = "Paste a token address or ask about any project...",
  onSubmit,
}: SearchBarProps) {
  const [query, setQuery] = useState("");
  const router = useRouter();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    if (onSubmit) {
      onSubmit(query.trim());
    } else {
      router.push(`/analyze?q=${encodeURIComponent(query.trim())}`);
    }
  };

  const isLarge = size === "large";

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div
        className={`relative flex items-center bg-surface border border-border rounded-xl overflow-hidden transition-all focus-within:border-accent-teal/50 focus-within:shadow-lg focus-within:shadow-accent-teal/5 ${
          isLarge ? "h-14 sm:h-16" : "h-12"
        }`}
      >
        <svg
          className={`absolute left-4 text-text-secondary ${
            isLarge ? "w-5 h-5" : "w-4 h-4"
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
          />
        </svg>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className={`w-full h-full bg-transparent text-text-primary placeholder-text-secondary/60 outline-none ${
            isLarge
              ? "pl-12 pr-32 text-base sm:text-lg"
              : "pl-11 pr-28 text-sm"
          }`}
        />
        <button
          type="submit"
          disabled={!query.trim()}
          className={`absolute right-2 bg-gradient-to-r from-accent-teal to-accent-blue text-white font-semibold rounded-lg transition-all hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed ${
            isLarge
              ? "px-5 py-2.5 text-sm sm:px-6 sm:text-base"
              : "px-4 py-2 text-sm"
          }`}
        >
          Analyze
        </button>
      </div>
    </form>
  );
}
