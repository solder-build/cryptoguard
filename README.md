# CryptoGuard

> Multi-agent crypto threat intelligence that tells you if a token will steal your money — before you buy it.

[![Built for DigitalOcean Gradient AI Hackathon 2026](https://img.shields.io/badge/DigitalOcean-Gradient%20AI%20Hackathon%202026-0080FF?style=for-the-badge&logo=digitalocean)](https://digitalocean.devpost.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## The Problem

In 2025, retail crypto users lost over **$5.6 billion** to scams, rug pulls, and fraudulent tokens. Most victims had no way to verify what they were buying. The information exists — on-chain data, contract source code, holder distributions — but it's scattered across dozens of tools, written in a language most people don't speak.

There's no reason a normal person should need to read Solidity bytecode to avoid getting robbed.

## What CryptoGuard Does

You paste a token address. Three specialized AI agents analyze it simultaneously and return a risk score with evidence.

That's it. No account required, no wallet connection, no premium tier. Just a straight answer: is this token likely to steal your money?

```
                     +-----------------------+
                     |     User Query        |
                     | "Is 0xABC... safe?"   |
                     +-----------+-----------+
                                 |
                     +-----------v-----------+
                     |    Gradient AI        |
                     |    Router Agent       |
                     |  (multi-agent routing)|
                     +-----------+-----------+
                        |        |        |
            +-----------+   +----+----+   +-----------+
            |               |         |               |
  +---------v---------+  +--v------+  +---------v---------+
  |  Token Risk       |  | Smart   |  |  Market           |
  |  Analyzer         |  |Contract |  |  Intelligence     |
  |                   |  |Auditor  |  |                   |
  | - Liquidity       |  |         |  | - Social signals  |
  | - Holders         |  |- Vulns  |  | - Volume patterns |
  | - Permissions     |  |- Honey  |  | - Whale moves     |
  | - Market patterns |  |  pots   |  | - Sentiment       |
  +---------+---------+  +----+----+  +---------+---------+
            |                 |                   |
            +--------+--------+--------+----------+
                     |                 |
          +----------v----------+     |
          |  Knowledge Bases    |     |
          |  (scam patterns,    |     |
          |   exploit history)  |     |
          +---------------------+     |
                                      |
                     +----------------v---------+
                     |        Guardrails        |
                     | - Financial disclaimers  |
                     | - PII protection         |
                     | - No investment advice   |
                     +----------------+---------+
                                      |
                     +----------------v---------+
                     |     Risk Assessment      |
                     |  Score: 82/100 CRITICAL  |
                     |  "Do not buy this token" |
                     +---------------------------+
```

## Screenshots

> Screenshots will be added before submission.

<!-- TODO: Add screenshots of:
  1. Dashboard overview with risk score visualization
  2. Token analysis in progress (multi-agent)
  3. Detailed findings breakdown
  4. Chat interface with agent responses
-->

## Tech Stack

| Layer | Technology |
|-------|------------|
| **AI Agents** | DigitalOcean Gradient AI ADK (Python 3.11) |
| **Agent Routing** | Gradient AI multi-agent routing |
| **Knowledge** | Gradient AI Knowledge Bases (scam patterns, exploit DB) |
| **Safety** | Gradient AI Guardrails (disclaimers, PII) |
| **Backend** | FastAPI (Python) — orchestrator for agent calls |
| **Frontend** | Next.js 14, React 18, Tailwind CSS, TypeScript |
| **Data Sources** | DexScreener, Birdeye, Solscan APIs |
| **Infra** | DigitalOcean App Platform + Gradient AI serverless |

## How It Uses DigitalOcean Gradient AI

CryptoGuard uses every major feature of the Gradient AI platform:

### Agents (Gradient ADK)
Three specialized agents built with the Gradient ADK, each with its own system prompt, tool definitions, and domain expertise:
- **Token Risk Analyzer** — calls DexScreener, Birdeye, and Solscan APIs via tool calling to pull liquidity, holder, and authority data. Scores risk across 4 categories (liquidity, holder concentration, contract permissions, market patterns) on a 0-100 scale.
- **Smart Contract Auditor** — analyzes contract source code for honeypot patterns, reentrancy vulnerabilities, hidden admin functions, and fee manipulation.
- **Market Intelligence** — evaluates social signals, volume anomalies, whale wallet movements, and sentiment patterns.

### Multi-Agent Routing
A router agent examines the user's query and dispatches it to one or more specialist agents. A query like "Is this token safe?" hits all three. A query like "Can the dev mint more tokens?" routes only to the Token Risk Analyzer.

### Knowledge Bases
Agents are grounded with curated knowledge bases containing:
- Historical rug pull patterns and post-mortem analyses
- Known scam contract signatures and bytecode patterns
- Common social engineering tactics used in crypto fraud
- Regulatory guidance on token classification

### Guardrails
Every response passes through guardrails that enforce:
- **Financial disclaimers** — CryptoGuard does not provide investment advice
- **PII protection** — no wallet addresses are stored or logged
- **Scope boundaries** — agents refuse to execute trades or interact with wallets

### Serverless Inference
Agents run on Gradient AI's serverless infrastructure. No GPU provisioning, no idle costs. Each agent scales independently based on query volume.

### Tool Calling
Agents use OpenAI-compatible function calling to query external APIs (DexScreener, Birdeye, Solscan) in real time. Tool definitions and handlers are co-located with each agent.

### Agent Evaluations
We use Gradient AI's evaluation framework to test agent accuracy against known scam tokens and verified safe tokens. Evaluation datasets include labeled examples from documented rug pulls.

### Tracing
All agent interactions are traced end-to-end through Gradient AI's tracing system, enabling debugging of multi-agent conversations and measuring latency per agent.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- DigitalOcean account with Gradient AI access
- (Optional) Birdeye API key, Solscan Pro API key

### 1. Clone the repo

```bash
git clone https://github.com/rsulisthio/cryptoguard.git
cd cryptoguard
```

### 2. Deploy agents to Gradient AI

```bash
cd agents/token-analyzer
pip install -r requirements.txt
gradient agent deploy
```

Repeat for `agents/contract-auditor` and `agents/market-intelligence` once they're built.

### 3. Set environment variables

```bash
cp .env.example .env
```

Edit `.env`:
```
GRADIENT_API_KEY=your_gradient_api_key
GRADIENT_TOKEN_ANALYZER_URL=https://your-agent.gradient.ai/api/v1/chat/completions
GRADIENT_CONTRACT_AUDITOR_URL=https://your-agent.gradient.ai/api/v1/chat/completions
GRADIENT_MARKET_INTEL_URL=https://your-agent.gradient.ai/api/v1/chat/completions
BIRDEYE_API_KEY=optional_birdeye_key
SOLSCAN_API_KEY=optional_solscan_key
```

### 4. Run the backend

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 5. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/analyze` | Submit a token address for full multi-agent analysis |
| `POST` | `/api/analyze/token` | Token Risk Analyzer only |
| `POST` | `/api/analyze/contract` | Smart Contract Auditor only |
| `POST` | `/api/analyze/market` | Market Intelligence only |
| `POST` | `/api/chat` | Chat with agents (conversational interface) |
| `GET`  | `/api/health` | Health check |

### Example Request

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"token_address": "So11111111111111111111111111111111111111112", "chain": "solana"}'
```

### Example Response

```json
{
  "query": "So11111111111111111111111111111111111111112",
  "overallScore": 12,
  "overallRisk": "SAFE",
  "timestamp": "2026-03-18T10:30:00Z",
  "agents": [
    {
      "agent": "token",
      "name": "Token Risk Analyzer",
      "score": 8,
      "riskLevel": "SAFE",
      "summary": "Wrapped SOL — native asset, no mint/freeze authority concerns.",
      "findings": ["Liquidity: $2.1B across 1,247 pairs", "No single holder >5%"],
      "details": "..."
    },
    {
      "agent": "contract",
      "name": "Smart Contract Auditor",
      "score": 5,
      "riskLevel": "SAFE",
      "summary": "Native wrapped token program — no custom contract logic.",
      "findings": [],
      "details": "..."
    },
    {
      "agent": "market",
      "name": "Market Intelligence",
      "score": 15,
      "riskLevel": "SAFE",
      "summary": "Established asset with consistent volume and organic trading.",
      "findings": ["24h volume: $1.8B", "No wash trading indicators"],
      "details": "..."
    }
  ]
}
```

## Project Structure

```
cryptoguard/
├── agents/
│   ├── token-analyzer/          # Gradient ADK agent
│   │   ├── .gradient/
│   │   │   └── agent.yml        # Agent config
│   │   ├── main.py              # Agent entrypoint + tools
│   │   └── requirements.txt
│   ├── contract-auditor/        # Smart contract analysis agent
│   │   ├── .gradient/
│   │   │   └── agent.yml
│   │   └── main.py
│   └── market-intelligence/     # Market signals agent
│       ├── .gradient/
│       │   └── agent.yml
│       └── main.py
├── api/                         # FastAPI orchestrator
│   ├── main.py
│   └── requirements.txt
├── frontend/                    # Next.js dashboard
│   ├── app/
│   │   └── lib/
│   │       └── types.ts         # TypeScript interfaces
│   ├── package.json
│   ├── tailwind.config.ts
│   └── next.config.js
├── knowledge-bases/             # Gradient AI knowledge base data
│   ├── scam-patterns.jsonl
│   └── exploit-history.jsonl
├── guardrails/                  # Guardrail configurations
│   └── financial-disclaimer.yml
├── evals/                       # Agent evaluation datasets
│   └── known-scams.jsonl
├── README.md
├── SUBMISSION.md
├── SETUP.md
├── LICENSE
└── .env.example
```

## Team

**Richard Sulisthio** — Solo builder
- Ex-Tokopedia (Indonesia's largest marketplace)
- Tsinghua University CS
- Building [Solder](https://solder.ai) — AI agent infrastructure on Solana
- Built Cortex prediction agents, multi-chain DeFi tooling
- [GitHub](https://github.com/rsulisthio) | [X/Twitter](https://x.com/ricksulisthio)

## License

MIT. See [LICENSE](LICENSE).

---

*Built for the [DigitalOcean Gradient AI Hackathon 2026](https://digitalocean.devpost.com/). CryptoGuard does not provide investment advice. All risk scores are informational and should not be the sole basis for any financial decision.*
