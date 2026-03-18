"""
CryptoGuard - Market Intelligence Agent
=========================================
Gradient AI ADK agent using LangGraph ReAct pattern.
Analyzes market context and social signals: trading volume patterns,
whale movements, sentiment, and team verification.
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
logger = logging.getLogger("market-intel")

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a crypto market intelligence analyst. You MUST call tools to fetch real data. NEVER just describe tools — actually call them.

INSTRUCTIONS:
1. Call fetch_dexscreener_profile with the token address
2. Call fetch_coingecko_data for market data
3. Base your score on ACTUAL tool results, not assumptions
4. If data shows healthy trading with high volume and many buyers, score LOW

SCORING RULES:
- High volume ($1M+) with many unique traders = LOW risk
- Token on major exchanges (CoinGecko listed) = LOW risk
- Well-known tokens (SOL, USDC, ETH, BTC, JUP, BONK, WIF, AAVE) = score 5-15
- Normal price movement (-5% to +5% daily) is NOT manipulation
- Only flag manipulation if you see evidence: extreme volume spikes, <20 unique buyers, bot patterns
- NEVER assume manipulation without data to support it

OUTPUT FORMAT:
overall_risk_score: [0-100]
risk_level: [LOW/MEDIUM/HIGH/CRITICAL]
findings:
- [finding from ACTUAL tool data]
- [finding from ACTUAL tool data]
recommendation: [one sentence]
"""

# ---------------------------------------------------------------------------
# HTTP helper
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


# ---------------------------------------------------------------------------
# LangChain tool definitions
# ---------------------------------------------------------------------------
@tool
async def fetch_dexscreener_profile(token_address: str) -> str:
    """Fetch token profile and trading data from DexScreener including social links and community info."""
    url = f"{DEXSCREENER_BASE}/tokens/{token_address}"
    data = await _http_get(url)
    if "error" in data:
        return json.dumps(data)

    pairs = data.get("pairs") or []
    if not pairs:
        return json.dumps({"error": "No trading pairs found", "token_address": token_address})

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

    vol_mc_ratio = vol_24h / mcap if mcap > 0 else 0
    vol_liq_ratio = vol_24h / liq if liq > 0 else 0
    buy_sell_ratio = buys / sells if sells > 0 else float("inf")
    vol_1h_pct = (vol_1h / vol_24h * 100) if vol_24h > 0 else 0

    result = {
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
    return json.dumps(result)


@tool
async def fetch_trading_history(token_address: str, chain: str = "solana") -> str:
    """Fetch recent trading history for a token to analyze volume patterns and whale transactions."""
    url = f"{DEXSCREENER_BASE}/tokens/{token_address}"
    data = await _http_get(url)
    if "error" in data:
        return json.dumps(data)

    pairs = data.get("pairs") or []
    if not pairs:
        return json.dumps({"error": "No pairs found", "token_address": token_address})

    chain_pairs = [p for p in pairs if p.get("chainId") == chain]
    if not chain_pairs:
        chain_pairs = pairs

    total_vol_24h = sum(float(p.get("volume", {}).get("h24", 0) or 0) for p in chain_pairs)
    total_buys = sum(int(p.get("txns", {}).get("h24", {}).get("buys", 0) or 0) for p in chain_pairs)
    total_sells = sum(int(p.get("txns", {}).get("h24", {}).get("sells", 0) or 0) for p in chain_pairs)

    primary = max(chain_pairs, key=lambda p: float(p.get("volume", {}).get("h24", 0) or 0))
    vol_5m = float(primary.get("volume", {}).get("m5", 0) or 0)
    vol_1h = float(primary.get("volume", {}).get("h1", 0) or 0)
    vol_6h = float(primary.get("volume", {}).get("h6", 0) or 0)
    vol_24h = float(primary.get("volume", {}).get("h24", 0) or 0)

    vol_acceleration = (vol_1h * 24) / vol_24h if vol_24h > 0 else 0

    result = {
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
    return json.dumps(result)


@tool
async def fetch_coingecko_data(token_id: str) -> str:
    """Fetch token data from CoinGecko including market data, community stats, and developer activity."""
    url = f"{COINGECKO_BASE}/coins/{token_id}"
    data = await _http_get(url)
    if "error" in data:
        url = f"{COINGECKO_BASE}/coins/solana/contract/{token_id}"
        data = await _http_get(url)

    if "error" in data:
        return json.dumps({
            "note": "Token not found on CoinGecko. This could mean it's too new or too small "
                    "to be listed, which itself is a risk signal for newer tokens.",
            "token_id": token_id,
        })

    market_data = data.get("market_data", {})
    community = data.get("community_data", {})
    developer = data.get("developer_data", {})

    result = {
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
    return json.dumps(result)


@tool
async def fetch_whale_transactions(token_address: str, min_value_usd: float = 10000) -> str:
    """Fetch large transactions (whale movements) for a token from on-chain data."""
    url = f"{DEXSCREENER_BASE}/tokens/{token_address}"
    data = await _http_get(url)
    if "error" in data:
        return json.dumps(data)

    pairs = data.get("pairs") or []
    if not pairs:
        return json.dumps({"error": "No pairs found", "token_address": token_address})

    primary = max(pairs, key=lambda p: float(p.get("liquidity", {}).get("usd", 0) or 0))

    vol_24h = float(primary.get("volume", {}).get("h24", 0) or 0)
    txns = primary.get("txns", {}).get("h24", {})
    total_txns = int(txns.get("buys", 0) or 0) + int(txns.get("sells", 0) or 0)
    avg_tx_size = vol_24h / total_txns if total_txns > 0 else 0
    liq = float(primary.get("liquidity", {}).get("usd", 0) or 0)

    whale_dominance = avg_tx_size / liq if liq > 0 else 0

    result = {
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
    return json.dumps(result)


@tool
async def search_token_sentiment(query: str, token_address: str = "") -> str:
    """Search for token mentions and sentiment across crypto communities and social platforms."""
    trending = await _http_get(f"{COINGECKO_BASE}/search/trending")
    trending_coins = []
    if "coins" in trending:
        trending_coins = [c.get("item", {}).get("symbol", "").upper() for c in trending["coins"]]

    search_data = await _http_get(f"{COINGECKO_BASE}/search?query={query}")
    found_coins = search_data.get("coins", []) if "error" not in search_data else []

    is_trending = query.upper() in trending_coins

    result = {
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
    return json.dumps(result)


# ---------------------------------------------------------------------------
# Knowledge Base retrieval tool
# ---------------------------------------------------------------------------
KB_MANIPULATION = "97956f4e-2271-11f1-b074-4e013e2ddde4"
KB_SAFETY = "a7a06322-2271-11f1-b074-4e013e2ddde4"
KBAAS_URL = "https://kbaas.do-ai.run/v1"


async def _kb_post(url: str, headers: dict, json_body: dict) -> dict:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=json_body)
            resp.raise_for_status()
            return resp.json()
    except Exception as exc:
        logger.warning("KB request error: %s", exc)
        return {"error": str(exc)}


@tool
async def search_manipulation_patterns(query: str) -> str:
    """Search CryptoGuard's knowledge base of market manipulation patterns, wash trading indicators, pump-and-dump schemes, and real manipulation case studies."""
    do_token = os.getenv("DIGITALOCEAN_API_TOKEN", "") or os.getenv("DIGITALOCEAN_ACCESS_TOKEN", "")
    if not do_token:
        return json.dumps({"note": "Knowledge base unavailable — DIGITALOCEAN_API_TOKEN not set. Proceeding with live API data only."})
    results = []
    for kb_uuid in [KB_MANIPULATION, KB_SAFETY]:
        url = f"{KBAAS_URL}/{kb_uuid}/retrieve"
        headers = {"Authorization": f"Bearer {do_token}"}
        data = await _kb_post(url, headers=headers, json_body={"query": query, "num_results": 3})
        for r in data.get("results", []):
            results.append(r.get("text_content", ""))
    return json.dumps({"knowledge_base_results": results[:5]}) if results else json.dumps({"note": "No KB results found"})


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
    fetch_dexscreener_profile,
    fetch_trading_history,
    fetch_coingecko_data,
    fetch_whale_transactions,
    search_token_sentiment,
    search_manipulation_patterns,
]

agent = create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)


# ---------------------------------------------------------------------------
# ADK entrypoint
# ---------------------------------------------------------------------------
@entrypoint
async def run(payload):
    """Market Intelligence agent entrypoint with guardrails."""
    from guardrails import check_input, process_output, redact_pii

    query = payload.get("input", "") or payload.get("query", "") or str(payload)

    query = redact_pii(query)
    blocked = check_input(query)
    if blocked:
        return blocked

    result = await agent.ainvoke({"messages": [("user", query)]})
    messages = result.get("messages", [])
    final = messages[-1].content if messages else "No analysis generated."
    final = process_output(final)
    return {"output": final}
