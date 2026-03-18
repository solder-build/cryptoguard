# CryptoGuard — Devpost Submission

## Inspiration

I've watched friends lose real money to crypto scams. Not edge cases — normal people who saw a token trending on Twitter, checked a few things, thought it looked legitimate, and bought in. Then the liquidity disappeared, or the dev minted a billion tokens and dumped, or the contract silently blocked sells.

The information to avoid these scams exists. It's on-chain, it's public, it's verifiable. But it's spread across five different block explorers, requires reading Solidity, and you need to know what "mint authority revoked" means. That's not reasonable to expect from someone who just wants to buy a token.

I built CryptoGuard because this should be a one-step process: paste an address, get a straight answer.

## What It Does

CryptoGuard is a multi-agent AI system that analyzes crypto tokens for scam signals and risk factors. You give it a token address, and three specialized agents run simultaneously:

1. **Token Risk Analyzer** — pulls liquidity data, holder distribution, mint/freeze authority status, and market patterns from DexScreener, Birdeye, and Solscan. Scores risk across four weighted categories.

2. **Smart Contract Auditor** — examines contract code for honeypot patterns, reentrancy vulnerabilities, hidden admin functions, proxy upgrade risks, and fee manipulation.

3. **Market Intelligence** — evaluates social sentiment, volume anomalies, whale wallet movements, and wash trading indicators.

Each agent produces a 0-100 risk score with specific findings. A router agent coordinates them, and the combined result gives you a clear verdict: SAFE, CAUTION, WARNING, or DANGER, with evidence for every claim.

There's no guessing, no vibes-based analysis. Every finding links to verifiable on-chain data.

## How We Built It

CryptoGuard is built entirely on DigitalOcean's Gradient AI platform.

**Agents**: Each of the three specialist agents is built with the Gradient ADK (Python). They have distinct system prompts that define their analysis methodology, and they use tool calling (OpenAI function-calling format) to query external blockchain data APIs in real time. For example, the Token Risk Analyzer defines five tools — `fetch_dexscreener_token`, `fetch_birdeye_token_security`, `fetch_birdeye_token_overview`, `fetch_solscan_token_holders`, and `fetch_solscan_token_meta` — and the Gradient AI runtime orchestrates calling them.

**Multi-Agent Routing**: A router agent examines incoming queries and dispatches to the right specialist(s). A broad query like "Is this token safe?" activates all three agents. A targeted question like "Does the contract have a honeypot?" goes only to the Smart Contract Auditor. This keeps responses fast and relevant.

**Knowledge Bases**: Agents are grounded with Gradient AI Knowledge Bases containing curated datasets of historical rug pull analyses, known scam contract patterns, and exploit post-mortems. This prevents hallucination and ensures risk assessments reference real precedents.

**Guardrails**: Every response passes through Gradient AI Guardrails that enforce financial disclaimers, prevent PII leakage, and keep agents within their scope (no investment advice, no trade execution).

**Evaluation & Tracing**: We built evaluation datasets of known scam tokens (documented rug pulls with public post-mortems) and verified safe tokens (major assets like SOL, ETH, USDC) to validate agent accuracy. Gradient AI tracing gives us end-to-end visibility into multi-agent conversations.

**Frontend**: A Next.js dashboard with a dark-themed UI shows risk scores as visual gauges, findings as expandable cards, and supports a conversational chat interface where you can ask follow-up questions to specific agents.

**Backend**: A FastAPI orchestrator sits between the frontend and Gradient AI agent endpoints, handling request routing, response aggregation, and caching.

## Challenges We Ran Into

**Agent coordination timing**: Getting three agents to run in parallel and merging their results into a coherent risk score required careful orchestration. We had to handle cases where one agent returns quickly (DexScreener data is fast) while another is still processing (contract analysis takes longer).

**Knowledge base curation**: Garbage in, garbage out. Scraping "scam databases" gave us mostly noise. We ended up manually curating post-mortem analyses from documented exploits — fewer entries, but much higher signal quality.

**Guardrail balance**: Too strict and the agents refuse to give useful answers ("I cannot assess financial risk"). Too loose and they start sounding like they're giving investment advice. Finding the right boundary took iteration.

**Tool calling reliability**: External APIs (Birdeye, Solscan) have rate limits and occasional downtime. We had to make agents graceful when tools return errors — they acknowledge missing data rather than hallucinating numbers.

## Accomplishments We're Proud Of

- **Multi-agent architecture that actually improves accuracy**: Each agent is a genuine specialist. The Token Risk Analyzer is better at liquidity analysis than a general-purpose agent because its system prompt is tight and its tools are purpose-built. The whole is meaningfully greater than the sum.

- **Real tool calling against live blockchain data**: This isn't a demo with mocked data. The agents query real APIs and analyze real tokens in real time.

- **Honest uncertainty**: When data is missing or an API is down, agents say so explicitly. They don't fill gaps with confident-sounding guesses. That's harder to build than it sounds.

- **Clean Gradient AI integration**: We used the full platform — ADK agents, knowledge bases, guardrails, multi-agent routing, serverless inference, tool calling, evaluations, and tracing. It's not a wrapper around a single LLM call.

## What We Learned

**Gradient AI ADK is genuinely well-designed for multi-agent systems.** The separation between agent logic (system prompts, tools) and infrastructure (deployment, scaling, routing) let us focus on the crypto-specific parts instead of building plumbing.

**Knowledge bases change agent behavior more than prompt engineering.** Grounding agents with real scam data made their responses dramatically more specific and useful compared to relying solely on the model's training data.

**Guardrails are a product feature, not a safety checkbox.** The financial disclaimers aren't just compliance — they set user expectations correctly. Users trust the tool more when it's honest about its limitations.

**Agent evaluations are essential, not optional.** We caught multiple failure modes (agents being too aggressive with risk scores, false positives on legitimate tokens) only because we had a labeled evaluation set.

## What's Next

- **Real-time monitoring**: Watch-list feature that continuously monitors tokens you hold and alerts you to risk changes (new large holder, liquidity removal, authority changes).
- **Multi-chain expansion**: Currently focused on Solana. Ethereum, Base, and BSC support next — the Token Risk Analyzer tools already support these chains via DexScreener.
- **Mobile app**: Push notifications for risk alerts. Nobody wants to keep a browser tab open.
- **Community-sourced intelligence**: Let users flag tokens they've been scammed by, building a crowd-verified knowledge base.
- **Browser extension**: One-click risk check directly from DEX interfaces (Jupiter, Uniswap, PancakeSwap).
- **Deeper contract analysis**: Bytecode decompilation for unverified contracts, using Gradient AI's serverless inference for heavier compute.

## Built With

DigitalOcean Gradient AI, Python, FastAPI, Next.js, React, TypeScript, Tailwind CSS, LangGraph, LangChain, DexScreener API, Birdeye API, Solscan API
