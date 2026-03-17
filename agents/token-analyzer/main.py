"""
CryptoGuard - Token Risk Analyzer Agent
========================================
Gradient AI ADK agent that performs forensic analysis of crypto tokens.
Checks liquidity, holder concentration, contract permissions, and mint/freeze authority.

Setup:
  pip install -r requirements.txt
  gradient agent deploy

Endpoint is OpenAI-compatible: POST /api/v1/chat/completions
"""

import json
import logging
from typing import Any

import httpx
from gradient_ai import entrypoint

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
# Tool definitions (OpenAI function-calling format)
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_dexscreener_token",
            "description": "Fetch token pair data from DexScreener including price, liquidity, volume, and transaction counts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "token_address": {
                        "type": "string",
                        "description": "The token contract/mint address to look up.",
                    },
                    "chain": {
                        "type": "string",
                        "description": "Blockchain to search on. Default: solana",
                        "enum": ["solana", "ethereum", "bsc", "base", "arbitrum"],
                    },
                },
                "required": ["token_address"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_birdeye_token_security",
            "description": "Fetch token security data from Birdeye including holder distribution, top holders, and mint/freeze authority status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "token_address": {
                        "type": "string",
                        "description": "The token mint address.",
                    },
                },
                "required": ["token_address"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_birdeye_token_overview",
            "description": "Fetch token overview from Birdeye including market cap, supply info, and basic metadata.",
            "parameters": {
                "type": "object",
                "properties": {
                    "token_address": {
                        "type": "string",
                        "description": "The token mint address.",
                    },
                },
                "required": ["token_address"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_solscan_token_holders",
            "description": "Fetch top token holders from Solscan to analyze holder concentration.",
            "parameters": {
                "type": "object",
                "properties": {
                    "token_address": {
                        "type": "string",
                        "description": "The token mint address on Solana.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top holders to return. Default 20.",
                    },
                },
                "required": ["token_address"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_solscan_token_meta",
            "description": "Fetch token metadata and authority info from Solscan including mint authority, freeze authority, and supply.",
            "parameters": {
                "type": "object",
                "properties": {
                    "token_address": {
                        "type": "string",
                        "description": "The token mint address on Solana.",
                    },
                },
                "required": ["token_address"],
            },
        },
    },
]

# ---------------------------------------------------------------------------
# Tool implementations
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


async def fetch_dexscreener_token(token_address: str, chain: str = "solana") -> dict:
    """Fetch pair data from DexScreener public API (no key needed)."""
    url = f"{DEXSCREENER_BASE}/tokens/{token_address}"
    data = await _http_get(url)
    if "error" in data:
        return data

    pairs = data.get("pairs") or []
    if not pairs:
        return {"error": "No pairs found for this token", "token_address": token_address}

    # Filter to requested chain if present
    chain_pairs = [p for p in pairs if p.get("chainId") == chain]
    if not chain_pairs:
        chain_pairs = pairs

    # Take the highest-liquidity pair
    primary = max(chain_pairs, key=lambda p: float(p.get("liquidity", {}).get("usd", 0) or 0))

    return {
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


async def fetch_birdeye_token_security(token_address: str) -> dict:
    """Fetch token security info from Birdeye public API."""
    url = f"{BIRDEYE_BASE}/defi/token_security?address={token_address}"
    headers = {"X-API-KEY": "", "x-chain": "solana"}
    data = await _http_get(url, headers=headers)
    if "error" in data:
        # Birdeye may require API key; return partial info
        return {
            "note": "Birdeye API key not configured — security data unavailable. "
                    "Configure BIRDEYE_API_KEY in environment for full analysis.",
            "token_address": token_address,
        }
    return data.get("data", data)


async def fetch_birdeye_token_overview(token_address: str) -> dict:
    """Fetch token overview from Birdeye."""
    url = f"{BIRDEYE_BASE}/defi/token_overview?address={token_address}"
    headers = {"X-API-KEY": "", "x-chain": "solana"}
    data = await _http_get(url, headers=headers)
    if "error" in data:
        return {
            "note": "Birdeye API key not configured — overview data unavailable.",
            "token_address": token_address,
        }
    return data.get("data", data)


async def fetch_solscan_token_holders(token_address: str, limit: int = 20) -> dict:
    """Fetch top holders from Solscan."""
    url = f"{SOLSCAN_BASE}/token/holders?address={token_address}&page=1&page_size={limit}"
    headers = {"token": ""}  # Solscan pro API key
    data = await _http_get(url, headers=headers)
    if "error" in data:
        return {
            "note": "Solscan API key not configured — holder data unavailable.",
            "token_address": token_address,
        }
    return data.get("data", data)


async def fetch_solscan_token_meta(token_address: str) -> dict:
    """Fetch token metadata from Solscan including authorities."""
    url = f"{SOLSCAN_BASE}/token/meta?address={token_address}"
    headers = {"token": ""}
    data = await _http_get(url, headers=headers)
    if "error" in data:
        return {
            "note": "Solscan API key not configured — metadata unavailable.",
            "token_address": token_address,
        }
    return data.get("data", data)


# Map tool names to implementations
TOOL_HANDLERS: dict[str, Any] = {
    "fetch_dexscreener_token": fetch_dexscreener_token,
    "fetch_birdeye_token_security": fetch_birdeye_token_security,
    "fetch_birdeye_token_overview": fetch_birdeye_token_overview,
    "fetch_solscan_token_holders": fetch_solscan_token_holders,
    "fetch_solscan_token_meta": fetch_solscan_token_meta,
}


# ---------------------------------------------------------------------------
# ADK entrypoint
# ---------------------------------------------------------------------------
@entrypoint
async def main(request):
    """
    Token Risk Analyzer agent entrypoint.

    The Gradient AI runtime calls this function with the incoming request.
    We return the system prompt, tools, and handle tool call results.
    """
    messages = request.get("messages", [])
    last_message = messages[-1] if messages else {}

    # If the last message contains tool call results, execute the tool
    if last_message.get("role") == "tool":
        tool_name = last_message.get("name", "")
        handler = TOOL_HANDLERS.get(tool_name)
        if handler:
            try:
                args = json.loads(last_message.get("content", "{}"))
                result = await handler(**args)
                return {"content": json.dumps(result, indent=2)}
            except Exception as exc:
                logger.error("Tool %s failed: %s", tool_name, exc)
                return {"content": json.dumps({"error": str(exc)})}

    # Standard request — return agent configuration
    return {
        "system": SYSTEM_PROMPT,
        "tools": TOOLS,
        "messages": messages,
    }
