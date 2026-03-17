"use client";

import { useState, useRef, useEffect, FormEvent } from "react";
import { ChatMessage } from "../lib/types";
import { sendChatMessage } from "../lib/api";
import { getAgentIcon, getAgentName } from "../lib/utils";

type AgentOption = "all" | "token" | "contract" | "market";

const agentOptions: { value: AgentOption; label: string; icon: string }[] = [
  { value: "all", label: "All Agents", icon: "\uD83D\uDEE1\uFE0F" },
  { value: "token", label: "Token Analyzer", icon: "\uD83D\uDD0D" },
  { value: "contract", label: "Contract Auditor", icon: "\uD83D\uDEE1\uFE0F" },
  { value: "market", label: "Market Intel", icon: "\uD83D\uDCCA" },
];

function renderMarkdown(text: string) {
  // Very basic markdown: bold, newlines, and bullet lists
  const lines = text.split("\n");
  return lines.map((line, i) => {
    // Bold
    const processed = line.replace(
      /\*\*(.+?)\*\*/g,
      '<strong class="text-text-primary">$1</strong>'
    );

    if (line.trim() === "") return <br key={i} />;
    if (line.startsWith("- ")) {
      return (
        <li
          key={i}
          className="ml-4 list-disc text-text-secondary text-sm"
          dangerouslySetInnerHTML={{ __html: processed.slice(2) }}
        />
      );
    }
    return (
      <p
        key={i}
        className="text-sm text-text-secondary mb-1"
        dangerouslySetInnerHTML={{ __html: processed }}
      />
    );
  });
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [selectedAgent, setSelectedAgent] = useState<AgentOption>("all");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      agent: selectedAgent,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await sendChatMessage(input.trim(), selectedAgent);
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response,
        agent: selectedAgent,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
        agent: selectedAgent,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6 flex flex-col h-[calc(100vh-8rem)]">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-bold text-text-primary">
          Chat with Agents
        </h1>
        <div className="flex gap-1 bg-surface border border-border rounded-lg p-1">
          {agentOptions.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setSelectedAgent(opt.value)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors flex items-center gap-1.5 ${
                selectedAgent === opt.value
                  ? "bg-surface-light text-text-primary"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              <span>{opt.icon}</span>
              <span className="hidden sm:inline">{opt.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.length === 0 && (
          <div className="text-center py-20">
            <div className="text-5xl mb-4">{"\uD83D\uDCAC"}</div>
            <h2 className="text-text-primary text-lg font-semibold mb-2">
              Ask the Security Team
            </h2>
            <p className="text-text-secondary text-sm max-w-md mx-auto mb-6">
              Chat with our specialized AI agents about any crypto project,
              token, or security concern.
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {[
                "Is this token safe to buy?",
                "Analyze the contract at 0x...",
                "What are the red flags for rug pulls?",
                "Review this project's team",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setInput(suggestion)}
                  className="px-3 py-1.5 rounded-lg bg-surface border border-border text-xs text-text-secondary hover:text-text-primary hover:border-border/80 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {msg.role === "assistant" && (
              <div className="w-8 h-8 rounded-lg bg-surface border border-border flex items-center justify-center text-sm flex-shrink-0 mt-1">
                {msg.agent && msg.agent !== "all"
                  ? getAgentIcon(msg.agent as "token" | "contract" | "market")
                  : "\uD83D\uDEE1\uFE0F"}
              </div>
            )}
            <div
              className={`max-w-[80%] rounded-xl px-4 py-3 ${
                msg.role === "user"
                  ? "bg-gradient-to-r from-accent-teal/20 to-accent-blue/20 border border-accent-teal/20"
                  : "bg-surface border border-border"
              }`}
            >
              {msg.role === "assistant" && msg.agent && (
                <p className="text-xs text-text-secondary/60 mb-2 font-medium">
                  {msg.agent === "all"
                    ? "All Agents"
                    : getAgentName(
                        msg.agent as "token" | "contract" | "market"
                      )}
                </p>
              )}
              <div className="chat-content">
                {msg.role === "assistant"
                  ? renderMarkdown(msg.content)
                  : <p className="text-sm text-text-primary">{msg.content}</p>
                }
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-lg bg-surface border border-border flex items-center justify-center text-sm flex-shrink-0 mt-1">
              {selectedAgent !== "all"
                ? getAgentIcon(selectedAgent as "token" | "contract" | "market")
                : "\uD83D\uDEE1\uFE0F"}
            </div>
            <div className="bg-surface border border-border rounded-xl px-4 py-3">
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full bg-accent-teal animate-bounce" style={{ animationDelay: "0ms" }} />
                <div className="w-2 h-2 rounded-full bg-accent-teal animate-bounce" style={{ animationDelay: "150ms" }} />
                <div className="w-2 h-2 rounded-full bg-accent-teal animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex gap-2 pt-4 border-t border-border">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={`Ask ${
            selectedAgent === "all"
              ? "the security team"
              : agentOptions.find((a) => a.value === selectedAgent)?.label
          }...`}
          disabled={loading}
          className="flex-1 h-12 px-4 bg-surface border border-border rounded-xl text-text-primary text-sm placeholder-text-secondary/60 outline-none focus:border-accent-teal/50 transition-colors disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="h-12 px-5 bg-gradient-to-r from-accent-teal to-accent-blue text-white font-semibold rounded-xl transition-all hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed text-sm"
        >
          Send
        </button>
      </form>
    </div>
  );
}
