"""
CryptoGuard - Token Risk Analyzer Agent
========================================
Gradient AI ADK agent using LangGraph ReAct pattern.
Performs forensic analysis of crypto tokens: liquidity, holder concentration,
contract permissions, and mint/freeze authority.
"""

import json
import logging
import os

import httpx
from gradient_adk import entrypoint
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("token-analyzer")

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are CryptoGuard's Token Risk Analyzer — a methodical forensic analyst
who dissects crypto tokens to expose hidden dangers.

PERSONALITY:
- Cold, precise, evidence-driven. You never speculate without data.
- You present findings like a forensic report: numbered, categorized, severity-rated.
- When data is missing you say so explicitly rather than guessing.

ANALYSIS FRAMEWORK (score each 0-100, higher = riskier):

1. LIQUIDITY RISK (weight 25%)
   - Total liquidity depth vs market cap ratio
   - Liquidity lock status and duration
   - Single-pool dependency
   - LP token holder concentration

2. HOLDER CONCENTRATION RISK (weight 25%)
   - Top-10 holder percentage (>50% = critical)
   - Creator/deployer holdings
   - Wallet clustering (related wallets)
   - Recent large accumulation patterns

3. CONTRACT PERMISSION RISK (weight 25%)
   - Mint authority: is it revoked?
   - Freeze authority: is it revoked?
   - Upgrade authority / proxy patterns
   - Hidden admin functions
   - Transfer fee mechanisms

4. MARKET PATTERN RISK (weight 25%)
   - Age of token (<24h = high risk)
   - Buy/sell ratio imbalance
   - Wash trading indicators
   - Price manipulation patterns

OUTPUT FORMAT:
Return a structured risk assessment with:
- overall_risk_score: 0-100
- risk_level: "LOW" (0-30) | "MEDIUM" (31-60) | "HIGH" (61-80) | "CRITICAL" (81-100)
- category_scores: dict of each category score
- findings: list of specific risk signals found
- recommendation: brief actionable advice

KNOWN SCAM PATTERNS:
- Honeypot: users can buy but not sell
- Rug pull: dev removes all liquidity
- Slow rug: gradual sell pressure from insider wallets
- Mint exploit: unlimited token minting via unrevoked authority
- Freeze trap: authority freezes user tokens after purchase
- Fee manipulation: hidden transfer taxes that drain value
- Fake liquidity: liquidity added and removed in same block
"""

# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------
DEXSCREENER_BASE = "https://api.dexscreener.com/latest/dex"
BIRDEYE_BASE = "https://public-api.birdeye.so"
SOLSCAN_BASE = "https://pro-api.solscan.io/v2.0"


async def _http_get(url: str, headers: dict | None = None, timeout: float = 15.0) -> dict:
    """Safe HTTP GET with error handling."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url, headers=headers or {})
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        logger.warning("HTTP %s for %s", exc.response.status_code, url)
        return {"error": f"HTTP {exc.response.status_code}", "url": url}
    except httpx.RequestError as exc:
        logger.warning("Request error for %s: %s", url, exc)
        return {"error": str(exc), "url": url}


# ---------------------------------------------------------------------------
# LangChain tool definitions
# ---------------------------------------------------------------------------
@tool
async def fetch_dexscreener_token(token_address: str, chain: str = "solana") -> str:
    """Fetch token pair data from DexScreener including price, liquidity, volume, and transaction counts."""
    url = f"{DEXSCREENER_BASE}/tokens/{token_address}"
    data = await _http_get(url)
    if "error" in data:
        return json.dumps(data)

    pairs = data.get("pairs") or []
    if not pairs:
        return json.dumps({"error": "No pairs found for this token", "token_address": token_address})

    # Filter to requested chain if present
    chain_pairs = [p for p in pairs if p.get("chainId") == chain]
    if not chain_pairs:
        chain_pairs = pairs

    # Take the highest-liquidity pair
    primary = max(chain_pairs, key=lambda p: float(p.get("liquidity", {}).get("usd", 0) or 0))

    result = {
        "pair_address": primary.get("pairAddress"),
        "dex": primary.get("dexId"),
        "chain": primary.get("chainId"),
        "base_token": primary.get("baseToken", {}),
        "quote_token": primary.get("quoteToken", {}),
        "price_usd": primary.get("priceUsd"),
        "price_change_24h": primary.get("priceChange", {}).get("h24"),
        "price_change_6h": primary.get("priceChange", {}).get("h6"),
        "price_change_1h": primary.get("priceChange", {}).get("h1"),
        "volume_24h": primary.get("volume", {}).get("h24"),
        "liquidity_usd": primary.get("liquidity", {}).get("usd"),
        "market_cap": primary.get("marketCap"),
        "fdv": primary.get("fdv"),
        "txns_24h": primary.get("txns", {}).get("h24"),
        "pair_created_at": primary.get("pairCreatedAt"),
        "total_pairs_found": len(pairs),
    }
    return json.dumps(result)


@tool
async def fetch_birdeye_token_security(token_address: str) -> str:
    """Fetch token security data from Birdeye including holder distribution, top holders, and mint/freeze authority status."""
    url = f"{BIRDEYE_BASE}/defi/token_security?address={token_address}"
    headers = {"X-API-KEY": "", "x-chain": "solana"}
    data = await _http_get(url, headers=headers)
    if "error" in data:
        return json.dumps({
            "note": "Birdeye API key not configured — security data unavailable. "
                    "Configure BIRDEYE_API_KEY in environment for full analysis.",
            "token_address": token_address,
        })
    return json.dumps(data.get("data", data))


@tool
async def fetch_birdeye_token_overview(token_address: str) -> str:
    """Fetch token overview from Birdeye including market cap, supply info, and basic metadata."""
    url = f"{BIRDEYE_BASE}/defi/token_overview?address={token_address}"
    headers = {"X-API-KEY": "", "x-chain": "solana"}
    data = await _http_get(url, headers=headers)
    if "error" in data:
        return json.dumps({
            "note": "Birdeye API key not configured — overview data unavailable.",
            "token_address": token_address,
        })
    return json.dumps(data.get("data", data))


@tool
async def fetch_solscan_token_holders(token_address: str, limit: int = 20) -> str:
    """Fetch top token holders from Solscan to analyze holder concentration."""
    url = f"{SOLSCAN_BASE}/token/holders?address={token_address}&page=1&page_size={limit}"
    headers = {"token": ""}  # Solscan pro API key
    data = await _http_get(url, headers=headers)
    if "error" in data:
        return json.dumps({
            "note": "Solscan API key not configured — holder data unavailable.",
            "token_address": token_address,
        })
    return json.dumps(data.get("data", data))


@tool
async def fetch_solscan_token_meta(token_address: str) -> str:
    """Fetch token metadata and authority info from Solscan including mint authority, freeze authority, and supply."""
    url = f"{SOLSCAN_BASE}/token/meta?address={token_address}"
    headers = {"token": ""}
    data = await _http_get(url, headers=headers)
    if "error" in data:
        return json.dumps({
            "note": "Solscan API key not configured — metadata unavailable.",
            "token_address": token_address,
        })
    return json.dumps(data.get("data", data))


# ---------------------------------------------------------------------------
# Knowledge Base retrieval tool
# ---------------------------------------------------------------------------
KB_TOKEN_RISKS = "67c9668a-2271-11f1-b074-4e013e2ddde4"
KB_SAFETY = "a7a06322-2271-11f1-b074-4e013e2ddde4"
KBAAS_URL = "https://kbaas.do-ai.run/v1"


@tool
async def search_scam_patterns(query: str) -> str:
    """Search CryptoGuard's knowledge base of known rug pull patterns, scam indicators, and real exploit case studies. Use this to compare a token's characteristics against known scam patterns."""
    do_token = os.getenv("DIGITALOCEAN_API_TOKEN", "") or os.getenv("DIGITALOCEAN_ACCESS_TOKEN", "")
    if not do_token:
        return json.dumps({"note": "Knowledge base unavailable — DIGITALOCEAN_API_TOKEN not set. Proceeding with live API data only."})
    results = []
    for kb_uuid in [KB_TOKEN_RISKS, KB_SAFETY]:
        url = f"{KBAAS_URL}/{kb_uuid}/retrieve"
        headers = {"Authorization": f"Bearer {do_token}"}
        data = await _http_get_post(url, headers=headers, json_body={"query": query, "num_results": 3})
        for r in data.get("results", []):
            results.append(r.get("text_content", ""))
    return json.dumps({"knowledge_base_results": results[:5]}) if results else json.dumps({"note": "No KB results found"})


async def _http_get_post(url: str, headers: dict | None = None, json_body: dict | None = None, timeout: float = 15.0) -> dict:
    """HTTP POST with error handling."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, headers=headers or {}, json=json_body or {})
            resp.raise_for_status()
            return resp.json()
    except Exception as exc:
        logger.warning("KB request error: %s", exc)
        return {"error": str(exc)}


# ---------------------------------------------------------------------------
# LangGraph ReAct agent
# ---------------------------------------------------------------------------
llm = ChatOpenAI(
    model=os.getenv("GRADIENT_MODEL", "llama3.3-70b-instruct"),
    base_url="https://inference.do-ai.run/v1",
    api_key=os.getenv("GRADIENT_MODEL_ACCESS_KEY", ""),
    temperature=0,
    max_retries=5,
)

tools = [
    fetch_dexscreener_token,
    fetch_birdeye_token_security,
    fetch_birdeye_token_overview,
    fetch_solscan_token_holders,
    fetch_solscan_token_meta,
    search_scam_patterns,
]

agent = create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)


# ---------------------------------------------------------------------------
# ADK entrypoint
# ---------------------------------------------------------------------------
@entrypoint
async def run(payload):
    """Token Risk Analyzer agent entrypoint with guardrails."""
    from guardrails import check_input, process_output, redact_pii

    query = payload.get("input", "") or payload.get("query", "") or str(payload)

    # Input guardrails
    query = redact_pii(query)
    blocked = check_input(query)
    if blocked:
        return blocked

    # Run agent
    result = await agent.ainvoke({"messages": [("user", query)]})
    messages = result.get("messages", [])
    final = messages[-1].content if messages else "No analysis generated."

    # Output guardrails
    final = process_output(final)
    return {"output": final}
