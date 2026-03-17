# CryptoGuard Setup Guide

Step-by-step instructions to get CryptoGuard running locally and deployed on DigitalOcean Gradient AI.

**Time estimate**: 30-45 minutes for full setup.

**Prerequisites**:
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ and npm 9+ installed
- [ ] Git installed
- [ ] A DigitalOcean account ([sign up](https://cloud.digitalocean.com/registrations/new))

---

## Step 1: Create a DigitalOcean Account

If you don't have one already:

1. Go to [cloud.digitalocean.com](https://cloud.digitalocean.com/registrations/new)
2. Create an account (GitHub SSO works)
3. Add a payment method (required for Gradient AI access)

## Step 2: Set Up Gradient AI

1. Navigate to the [Gradient AI console](https://cloud.digitalocean.com/gradient) in your DigitalOcean dashboard.
2. Enable Gradient AI for your account if prompted.
3. Generate an API key:
   - Go to **API** > **Tokens/Keys**
   - Click **Generate New Token**
   - Name it `cryptoguard` and copy the key immediately (you won't see it again)

Save this key — you'll need it in Step 6.

## Step 3: Clone the Repository

```bash
git clone https://github.com/rsulisthio/cryptoguard.git
cd cryptoguard
```

## Step 4: Deploy Agents via ADK

Each agent is a self-contained Gradient ADK project in the `agents/` directory. Deploy them one at a time.

### Install the Gradient CLI

```bash
pip install gradient-ai-cli
gradient auth login
```

Enter your DigitalOcean API key when prompted.

### Deploy the Token Risk Analyzer

```bash
cd agents/token-analyzer
pip install -r requirements.txt
gradient agent deploy
```

On success, the CLI prints the agent's endpoint URL. It looks like:

```
Agent deployed successfully.
Endpoint: https://cryptoguard-token-analyzer-xxxxx.gradient.ai/api/v1/chat/completions
```

Copy this URL.

### Deploy the Smart Contract Auditor

```bash
cd agents/contract-auditor
pip install -r requirements.txt
gradient agent deploy
```

Copy the endpoint URL.

### Deploy the Market Intelligence Agent

```bash
cd agents/market-intelligence
pip install -r requirements.txt
gradient agent deploy
```

Copy the endpoint URL.

> **Note**: Each deployment takes 1-3 minutes. The agents run on Gradient AI's serverless infrastructure — no GPU or VM provisioning needed.

## Step 5: Configure Knowledge Bases

Knowledge bases ground the agents in real scam data so they don't rely solely on training data.

### Create the knowledge bases in the Gradient console

1. Go to **Gradient AI** > **Knowledge Bases** in the DigitalOcean dashboard.

2. Create a knowledge base named `cryptoguard-scam-patterns`:
   - Click **Create Knowledge Base**
   - Name: `cryptoguard-scam-patterns`
   - Upload `knowledge-bases/scam-patterns.jsonl`
   - Wait for indexing to complete

3. Create a knowledge base named `cryptoguard-exploit-history`:
   - Click **Create Knowledge Base**
   - Name: `cryptoguard-exploit-history`
   - Upload `knowledge-bases/exploit-history.jsonl`
   - Wait for indexing to complete

### Attach knowledge bases to agents

1. Go to **Gradient AI** > **Agents**
2. Select each agent and add the relevant knowledge bases:
   - Token Risk Analyzer: attach `cryptoguard-scam-patterns`
   - Smart Contract Auditor: attach both `cryptoguard-scam-patterns` and `cryptoguard-exploit-history`
   - Market Intelligence: attach `cryptoguard-scam-patterns`

## Step 6: Set Up Guardrails

1. Go to **Gradient AI** > **Guardrails** in the dashboard.

2. Create a guardrail named `cryptoguard-financial`:
   - **Type**: Output guardrail
   - **Rule**: Append financial disclaimer to every response
   - **Disclaimer text**: "This analysis is for informational purposes only and does not constitute investment advice. Always do your own research before making financial decisions."

3. Create a guardrail named `cryptoguard-pii`:
   - **Type**: Input + Output guardrail
   - **Rule**: Block and redact personally identifiable information (names, emails, phone numbers)
   - Wallet addresses are NOT considered PII (they're public by design)

4. Create a guardrail named `cryptoguard-scope`:
   - **Type**: Input guardrail
   - **Rule**: Reject queries that ask the agent to execute trades, transfer funds, or connect to wallets

5. Attach all three guardrails to each agent in the agent settings.

## Step 7: Configure Multi-Agent Routing

1. Go to **Gradient AI** > **Routing** in the dashboard.

2. Create a router named `cryptoguard-router`:
   - Add all three agents as routing targets
   - Configure routing rules:

| Query Pattern | Routes To |
|---------------|-----------|
| General safety check ("Is this safe?", "Analyze this token") | All three agents |
| Liquidity/holders/authority questions | Token Risk Analyzer |
| Contract/code/vulnerability questions | Smart Contract Auditor |
| Social/volume/whale/sentiment questions | Market Intelligence |

3. Copy the router endpoint URL — this is the single entry point the backend will call.

## Step 8: Configure Environment Variables

```bash
cd /path/to/cryptoguard
cp .env.example .env
```

Edit `.env` with the values from previous steps:

```bash
# Gradient AI
GRADIENT_API_KEY=your_api_key_from_step_2
GRADIENT_ROUTER_URL=https://your-router-endpoint.gradient.ai/api/v1/chat/completions
GRADIENT_TOKEN_ANALYZER_URL=https://your-token-analyzer.gradient.ai/api/v1/chat/completions
GRADIENT_CONTRACT_AUDITOR_URL=https://your-contract-auditor.gradient.ai/api/v1/chat/completions
GRADIENT_MARKET_INTEL_URL=https://your-market-intel.gradient.ai/api/v1/chat/completions

# External APIs (optional — agents degrade gracefully without these)
BIRDEYE_API_KEY=your_birdeye_key
SOLSCAN_API_KEY=your_solscan_pro_key

# App config
API_PORT=8000
FRONTEND_URL=http://localhost:3000
```

> **DexScreener requires no API key** — it's a free public API. Birdeye and Solscan keys are optional; agents will note when data is unavailable due to missing keys.

## Step 9: Run the Backend

```bash
cd api
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Verify it's running:

```bash
curl http://localhost:8000/api/health
```

Expected output:

```json
{"status": "ok", "agents": {"token_analyzer": "connected", "contract_auditor": "connected", "market_intelligence": "connected"}}
```

## Step 10: Run the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Step 11: Test Everything

### Quick smoke test

1. Open the dashboard at `http://localhost:3000`
2. Paste a known safe token address: `So11111111111111111111111111111111111111112` (Wrapped SOL)
3. You should see a low risk score (under 20) from all three agents
4. Check that the financial disclaimer appears at the bottom of the response

### Test with a higher-risk token

1. Find a recently launched, low-liquidity token on [DexScreener](https://dexscreener.com/solana)
2. Paste its address into CryptoGuard
3. Expect a higher risk score with specific findings about liquidity, holder concentration, and contract permissions

### Test agent routing

1. Use the chat interface
2. Ask: "Does this token have a honeypot in the contract?" — should route to Smart Contract Auditor
3. Ask: "What's the whale activity on this token?" — should route to Market Intelligence
4. Ask: "Is this token safe to buy?" — should trigger all three agents

### Verify guardrails

1. Try sending PII in a query: "My name is John Smith and my email is john@example.com, is token X safe?" — PII should be redacted
2. Try asking: "Buy this token for me" — should be rejected by the scope guardrail
3. Confirm every response includes the financial disclaimer

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `gradient: command not found` | Run `pip install gradient-ai-cli` and ensure pip's bin directory is in your PATH |
| Agent deployment fails | Check your API key is valid: `gradient auth whoami` |
| Backend can't reach agents | Verify the agent URLs in `.env` match the deployed endpoints |
| Birdeye/Solscan data missing | These require API keys. The agents will work without them but report reduced data coverage |
| Frontend shows blank page | Check the backend is running on port 8000. Check browser console for CORS errors |
| Risk scores seem wrong | Run the evaluation suite: `cd evals && python run_evals.py` to check agent accuracy against known tokens |

## Production Deployment (Optional)

To deploy the full stack on DigitalOcean:

1. **Agents** are already deployed on Gradient AI (Step 4).
2. **Backend**: Deploy the FastAPI app to [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform/):
   ```bash
   doctl apps create --spec api/app-spec.yml
   ```
3. **Frontend**: Deploy the Next.js app to App Platform:
   ```bash
   doctl apps create --spec frontend/app-spec.yml
   ```

Set the same environment variables in the App Platform dashboard under **Settings** > **App-Level Environment Variables**.
