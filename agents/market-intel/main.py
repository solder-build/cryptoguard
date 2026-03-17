"""
CryptoGuard - Market Intelligence Agent
=========================================
Gradient AI ADK agent that analyzes market context and social signals.
Checks trading volume patterns, whale movements, sentiment, and team verification.

Setup:
  pip install -r requirements.txt
  gradient agent deploy
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

import httpx
from gradient_ai import entrypoint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("market-intel")

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are CryptoGuard's Market Intelligence Analyst — a street-smart market
veteran who reads between the lines of trading data and social signals.

PERSONALITY:
- Sharp, skeptical, pattern-recognition-focused. You've seen every scam play.
- You talk like a seasoned trader who's been through multiple market cycles.
- You quantify everything — percentages, ratios, time-series comparisons.
- You distrust hype and look for substance behind the noise.

ANALYSIS FRAMEWORK (score each 0-100, higher = riskier):

1. VOLUME & TRADING PATTERN RISK (weight 30%)
   - Volume/market cap ratio (too high = wash trading, too low = dying)
   - Buy/sell imbalance over 24h
   - Volume distribution: organic (spread out) vs artificial (spikes)
   - Large single transactions relative to typical volume
   - Volume trend: growing, stable, or declining

2. WHALE MOVEMENT RISK (weight 25%)
   - Large wallet accumulation or distribution patterns
   - DEX vs CEX flow direction
   - New whale wallets appearing (potential insider)
   - Known scam wallets interacting with token
   - Smart money wallet behavior

3. SOCIAL & SENTIMENT RISK (weight 25%)
   - Social media mention velocity vs organic baseline
   - Bot activity indicators (repetitive phrasing, new accounts)
   - Influencer promotion patterns (paid vs organic)
   - Community engagement quality (substance vs hype)
   - Negative sentiment or scam warnings from security researchers

4. TEAM & PROJECT VERIFICATION (weight 20%)
   - Team publicly identified and verifiable
   - LinkedIn/GitHub presence and history
   - Previous project track record
   - Audit reports from reputable firms
   - Legal entity and jurisdiction transparency

OUTPUT FORMAT:
Return a structured intelligence report with:
- overall_risk_score: 0-100
- risk_level: "LOW" (0-30) | "MEDIUM" (31-60) | "HIGH" (61-80) | "CRITICAL" (81-100)
- category_scores: dict of each category score
- signals: list of specific market signals detected
- recommendation: brief actionable advice

MARKET MANIPULATION PATTERNS:
- Wash trading: same entity buying and selling to inflate volume
- Pump and dump: coordinated buy pressure followed by insider dump
- Spoofing: large orders placed and cancelled to create false demand
- Layering: multiple order levels to create illusion of support/resistance
- Bear raid: coordinated shorting with FUD campaign
- Rug pull timing: liquidity removal after sustained marketing push
- Sybil attack: many wallets controlled by one entity to fake holder count
"""

# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_dexscreener_profile",
            "description": "Fetch token profile and trading data from DexScreener including social links and community info.",
            "parameters": {
                "type": "object",
                "properties": {
                    "token_address": {
                        "type": "string",
                        "description": "The token contract/mint address.",
                    },
                },
                "required": ["token_address"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_trading_history",
            "description": "Fetch recent trading history for a token to analyze volume patterns and whale transactions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "token_address": {
                        "type": "string",
                        "description": "The token contract/mint address.",
                    },
                    "chain": {
                        "type": "string",
                        "description": "Blockchain. Default: solana",
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
            "name": "fetch_coingecko_data",
            "description": "Fetch token data from CoinGecko including market data, community stats, and developer activity.",
            "parameters": {
                "type": "object",
                "properties": {
                    "token_id": {
                        "type": "string",
                        "description": "CoinGecko token ID or contract address.",
                    },
                },
                "required": ["token_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_whale_transactions",
            "description": "Fetch large transactions (whale movements) for a token from on-chain data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "token_address": {
                        "type": "string",
                        "description": "The token contract/mint address.",
                    },
                    "min_value_usd": {
                        "type": "number",
                        "description": "Minimum transaction value in USD to qualify as whale. Default: 10000",
                    },
                },
                "required": ["token_address"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_token_sentiment",
            "description": "Search for token mentions and sentiment across crypto communities and social platforms.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Token name or symbol to search for.",
                    },
                    "token_address": {
                        "type": "string",
                        "description": "Token address for verification.",
                    },
                },
                "required": ["query"],
            },
        },
    },
]

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------
DEXSCREENER_BASE = "https://api.dexscreener.com/latest/dex"
COINGECKO_BASE = "https://api.coingecko.com/api/v3"


async def _http_get(url: str, headers: dict | None = None, timeout: float = 15.0) -> dict:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url, headers=headers or {})
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        return {"error": f"HTTP {exc.response.status_code}", "url": url}
    except httpx.RequestError as exc:
        return {"error": str(exc), "url": url}


async def fetch_dexscreener_profile(token_address: str) -> dict:
    """Fetch comprehensive token profile from DexScreener."""
    url = f"{DEXSCREENER_BASE}/tokens/{token_address}"
    data = await _http_get(url)
    if "error" in data:
        return data

    pairs = data.get("pairs") or []
    if not pairs:
        return {"error": "No trading pairs found", "token_address": token_address}

    primary = max(pairs, key=lambda p: float(p.get("liquidity", {}).get("usd", 0) or 0))

    # Analyze volume patterns
    vol_24h = float(primary.get("volume", {}).get("h24", 0) or 0)
    vol_6h = float(primary.get("volume", {}).get("h6", 0) or 0)
    vol_1h = float(primary.get("volume", {}).get("h1", 0) or 0)
    liq = float(primary.get("liquidity", {}).get("usd", 0) or 0)
    mcap = float(primary.get("marketCap", 0) or 0)

    txns_24h = primary.get("txns", {}).get("h24", {})
    buys = int(txns_24h.get("buys", 0) or 0)
    sells = int(txns_24h.get("sells", 0) or 0)
    total_txns = buys + sells

    # Volume/MC ratio — healthy is 0.05-0.3, suspicious if >1.0
    vol_mc_ratio = vol_24h / mcap if mcap > 0 else 0
    # Volume/liquidity ratio — healthy is <5, suspicious if >20
    vol_liq_ratio = vol_24h / liq if liq > 0 else 0
    # Buy/sell ratio — healthy is 0.8-1.2
    buy_sell_ratio = buys / sells if sells > 0 else float("inf")

    # Volume distribution — is it front-loaded?
    vol_1h_pct = (vol_1h / vol_24h * 100) if vol_24h > 0 else 0

    return {
        "token_name": primary.get("baseToken", {}).get("name"),
        "token_symbol": primary.get("baseToken", {}).get("symbol"),
        "price_usd": primary.get("priceUsd"),
        "market_cap": mcap,
        "liquidity_usd": liq,
        "volume_24h": vol_24h,
        "volume_6h": vol_6h,
        "volume_1h": vol_1h,
        "buys_24h": buys,
        "sells_24h": sells,
        "total_transactions_24h": total_txns,
        "buy_sell_ratio": round(buy_sell_ratio, 3),
        "volume_mcap_ratio": round(vol_mc_ratio, 4),
        "volume_liquidity_ratio": round(vol_liq_ratio, 4),
        "volume_1h_pct_of_24h": round(vol_1h_pct, 2),
        "price_change_24h": primary.get("priceChange", {}).get("h24"),
        "price_change_6h": primary.get("priceChange", {}).get("h6"),
        "price_change_1h": primary.get("priceChange", {}).get("h1"),
        "pair_created_at": primary.get("pairCreatedAt"),
        "dex": primary.get("dexId"),
        "website": primary.get("info", {}).get("websites", []),
        "socials": primary.get("info", {}).get("socials", []),
        "total_pairs": len(pairs),
    }


async def fetch_trading_history(token_address: str, chain: str = "solana") -> dict:
    """Fetch recent trades to detect patterns."""
    # Use DexScreener pairs endpoint for trade data
    url = f"{DEXSCREENER_BASE}/tokens/{token_address}"
    data = await _http_get(url)
    if "error" in data:
        return data

    pairs = data.get("pairs") or []
    if not pairs:
        return {"error": "No pairs found", "token_address": token_address}

    chain_pairs = [p for p in pairs if p.get("chainId") == chain]
    if not chain_pairs:
        chain_pairs = pairs

    # Aggregate across all pairs on the requested chain
    total_vol_24h = sum(float(p.get("volume", {}).get("h24", 0) or 0) for p in chain_pairs)
    total_buys = sum(int(p.get("txns", {}).get("h24", {}).get("buys", 0) or 0) for p in chain_pairs)
    total_sells = sum(int(p.get("txns", {}).get("h24", {}).get("sells", 0) or 0) for p in chain_pairs)

    # Check for volume anomalies across time windows
    primary = max(chain_pairs, key=lambda p: float(p.get("volume", {}).get("h24", 0) or 0))
    vol_5m = float(primary.get("volume", {}).get("m5", 0) or 0)
    vol_1h = float(primary.get("volume", {}).get("h1", 0) or 0)
    vol_6h = float(primary.get("volume", {}).get("h6", 0) or 0)
    vol_24h = float(primary.get("volume", {}).get("h24", 0) or 0)

    # Volume acceleration — rapid increase is suspicious
    vol_acceleration = (vol_1h * 24) / vol_24h if vol_24h > 0 else 0

    return {
        "chain": chain,
        "total_pairs": len(chain_pairs),
        "aggregate_volume_24h": total_vol_24h,
        "aggregate_buys_24h": total_buys,
        "aggregate_sells_24h": total_sells,
        "volume_5m": vol_5m,
        "volume_1h": vol_1h,
        "volume_6h": vol_6h,
        "volume_24h": vol_24h,
        "volume_acceleration": round(vol_acceleration, 3),
        "volume_acceleration_note": (
            "NORMAL" if 0.5 < vol_acceleration < 2.0
            else "HIGH — possible coordinated activity" if vol_acceleration > 2.0
            else "LOW — declining interest"
        ),
    }


async def fetch_coingecko_data(token_id: str) -> dict:
    """Fetch data from CoinGecko free API."""
    # Try as an ID first, then as contract address
    url = f"{COINGECKO_BASE}/coins/{token_id}"
    data = await _http_get(url)
    if "error" in data:
        # Try searching by contract address on Solana
        url = f"{COINGECKO_BASE}/coins/solana/contract/{token_id}"
        data = await _http_get(url)

    if "error" in data:
        return {
            "note": "Token not found on CoinGecko. This could mean it's too new or too small "
                    "to be listed, which itself is a risk signal for newer tokens.",
            "token_id": token_id,
        }

    market_data = data.get("market_data", {})
    community = data.get("community_data", {})
    developer = data.get("developer_data", {})

    return {
        "name": data.get("name"),
        "symbol": data.get("symbol"),
        "market_cap_rank": data.get("market_cap_rank"),
        "coingecko_score": data.get("coingecko_score"),
        "liquidity_score": data.get("liquidity_score"),
        "community_score": data.get("community_score"),
        "developer_score": data.get("developer_score"),
        "current_price_usd": market_data.get("current_price", {}).get("usd"),
        "market_cap_usd": market_data.get("market_cap", {}).get("usd"),
        "total_volume_usd": market_data.get("total_volume", {}).get("usd"),
        "price_change_24h_pct": market_data.get("price_change_percentage_24h"),
        "price_change_7d_pct": market_data.get("price_change_percentage_7d"),
        "price_change_30d_pct": market_data.get("price_change_percentage_30d"),
        "ath_change_pct": market_data.get("ath_change_percentage", {}).get("usd"),
        "twitter_followers": community.get("twitter_followers"),
        "telegram_members": community.get("telegram_channel_user_count"),
        "reddit_subscribers": community.get("reddit_subscribers"),
        "github_forks": developer.get("forks"),
        "github_stars": developer.get("stars"),
        "github_commits_4w": developer.get("commit_count_4_weeks"),
        "genesis_date": data.get("genesis_date"),
        "categories": data.get("categories", []),
        "platforms": data.get("platforms", {}),
    }


async def fetch_whale_transactions(token_address: str, min_value_usd: float = 10000) -> dict:
    """Fetch large transactions. Uses DexScreener data as a proxy."""
    # DexScreener doesn't provide individual tx data, so we analyze
    # volume concentration as a whale indicator
    url = f"{DEXSCREENER_BASE}/tokens/{token_address}"
    data = await _http_get(url)
    if "error" in data:
        return data

    pairs = data.get("pairs") or []
    if not pairs:
        return {"error": "No pairs found", "token_address": token_address}

    primary = max(pairs, key=lambda p: float(p.get("liquidity", {}).get("usd", 0) or 0))

    vol_24h = float(primary.get("volume", {}).get("h24", 0) or 0)
    txns = primary.get("txns", {}).get("h24", {})
    total_txns = int(txns.get("buys", 0) or 0) + int(txns.get("sells", 0) or 0)
    avg_tx_size = vol_24h / total_txns if total_txns > 0 else 0
    liq = float(primary.get("liquidity", {}).get("usd", 0) or 0)

    # High avg tx size relative to liquidity = whale dominated
    whale_dominance = avg_tx_size / liq if liq > 0 else 0

    return {
        "volume_24h": vol_24h,
        "total_transactions_24h": total_txns,
        "avg_transaction_size_usd": round(avg_tx_size, 2),
        "liquidity_usd": liq,
        "whale_dominance_ratio": round(whale_dominance, 6),
        "whale_dominance_assessment": (
            "LOW — retail-dominated trading" if whale_dominance < 0.01
            else "MODERATE — some large players" if whale_dominance < 0.05
            else "HIGH — whale-dominated, high manipulation risk"
        ),
        "min_value_threshold": min_value_usd,
        "estimated_whale_txns": (
            int(vol_24h / min_value_usd) if avg_tx_size > min_value_usd else 0
        ),
        "note": "Individual transaction data requires dedicated on-chain indexer. "
                "This analysis is based on aggregate volume patterns.",
    }


async def search_token_sentiment(query: str, token_address: str = "") -> dict:
    """Search for token sentiment using CoinGecko trending and search."""
    # Check if token is trending on CoinGecko
    trending = await _http_get(f"{COINGECKO_BASE}/search/trending")
    trending_coins = []
    if "coins" in trending:
        trending_coins = [c.get("item", {}).get("symbol", "").upper() for c in trending["coins"]]

    # Search CoinGecko
    search_data = await _http_get(f"{COINGECKO_BASE}/search?query={query}")
    found_coins = search_data.get("coins", []) if "error" not in search_data else []

    is_trending = query.upper() in trending_coins

    return {
        "query": query,
        "is_trending_on_coingecko": is_trending,
        "coingecko_search_results": len(found_coins),
        "top_matches": [
            {
                "name": c.get("name"),
                "symbol": c.get("symbol"),
                "market_cap_rank": c.get("market_cap_rank"),
            }
            for c in found_coins[:5]
        ],
        "trending_coins_now": trending_coins[:10],
        "sentiment_note": (
            "Token is currently trending — verify whether this is organic or manufactured hype."
            if is_trending
            else "Token is not trending on major aggregators."
        ),
        "analysis_limitations": (
            "Full social sentiment analysis requires Twitter/Reddit API access. "
            "This provides CoinGecko aggregated data only."
        ),
    }


TOOL_HANDLERS: dict[str, Any] = {
    "fetch_dexscreener_profile": fetch_dexscreener_profile,
    "fetch_trading_history": fetch_trading_history,
    "fetch_coingecko_data": fetch_coingecko_data,
    "fetch_whale_transactions": fetch_whale_transactions,
    "search_token_sentiment": search_token_sentiment,
}


# ---------------------------------------------------------------------------
# ADK entrypoint
# ---------------------------------------------------------------------------
@entrypoint
async def main(request):
    """Market Intelligence agent entrypoint."""
    messages = request.get("messages", [])
    last_message = messages[-1] if messages else {}

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

    return {
        "system": SYSTEM_PROMPT,
        "tools": TOOLS,
        "messages": messages,
    }
