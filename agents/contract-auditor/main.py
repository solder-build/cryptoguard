"""
CryptoGuard - Smart Contract Auditor Agent
============================================
Gradient AI ADK agent using LangGraph ReAct pattern.
Audits smart contract code for vulnerabilities: honeypot patterns,
hidden mints, proxy upgradability, and ownership issues.
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
logger = logging.getLogger("contract-auditor")

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a smart contract security auditor. You MUST call your tools to fetch real data before answering. NEVER describe what tools you would call — actually call them.

INSTRUCTIONS:
1. ALWAYS call check_honeypot first with the token address
2. THEN call fetch_gopluslabs_security for security analysis
3. THEN call search_vulnerability_patterns with a relevant query
4. Analyze the data you receive
5. Return a risk score and findings

OUTPUT FORMAT (use this exact structure):
overall_risk_score: [0-100]
risk_level: [LOW/MEDIUM/HIGH/CRITICAL]
findings:
- [finding 1]
- [finding 2]
- [finding 3]
recommendation: [one sentence]

Score guide: 0-30 LOW, 31-60 MEDIUM, 61-80 HIGH, 81-100 CRITICAL
Red flags: honeypot detected, hidden mint, proxy upgradeable, owner not renounced, blacklist function
"""

# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------
ETHERSCAN_BASE = "https://api.etherscan.io/api"
HONEYPOT_BASE = "https://api.honeypot.is/v2"
GOPLUS_BASE = "https://api.gopluslabs.com/api/v1"


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
async def fetch_contract_source(contract_address: str, chain: str = "solana") -> str:
    """Fetch verified contract source code from a block explorer (Etherscan, Solscan, BSCScan)."""
    if chain == "solana":
        url = f"https://pro-api.solscan.io/v2.0/account/{contract_address}"
        data = await _http_get(url, headers={"token": ""})
        if "error" in data:
            return json.dumps({
                "note": "Solscan API key not configured. For Solana programs, "
                        "provide the source code directly or check anchor-verified status.",
                "contract_address": contract_address,
                "suggestion": "Try searching for the program IDL on-chain or check "
                              "https://solscan.io/account/" + contract_address,
            })
        return json.dumps(data.get("data", data))

    # EVM chains
    explorer_urls = {
        "ethereum": ETHERSCAN_BASE,
        "bsc": "https://api.bscscan.com/api",
        "base": "https://api.basescan.org/api",
        "arbitrum": "https://api.arbiscan.io/api",
    }
    base = explorer_urls.get(chain, ETHERSCAN_BASE)
    url = f"{base}?module=contract&action=getsourcecode&address={contract_address}"
    data = await _http_get(url)

    if data.get("status") == "1" and data.get("result"):
        result = data["result"][0]
        source = result.get("SourceCode", "")
        return json.dumps({
            "contract_name": result.get("ContractName"),
            "compiler_version": result.get("CompilerVersion"),
            "optimization_used": result.get("OptimizationUsed"),
            "is_proxy": result.get("Proxy") == "1",
            "implementation": result.get("Implementation"),
            "source_code_length": len(source),
            "source_code": source[:10000] if source else "Not verified",
            "license": result.get("LicenseType"),
        })
    return json.dumps({"error": "Source code not verified or not found", "contract_address": contract_address})


@tool
async def fetch_contract_abi(contract_address: str, chain: str = "ethereum") -> str:
    """Fetch the contract ABI to analyze function signatures and access modifiers."""
    explorer_urls = {
        "ethereum": ETHERSCAN_BASE,
        "bsc": "https://api.bscscan.com/api",
        "base": "https://api.basescan.org/api",
        "arbitrum": "https://api.arbiscan.io/api",
    }
    base = explorer_urls.get(chain, ETHERSCAN_BASE)
    url = f"{base}?module=contract&action=getabi&address={contract_address}"
    data = await _http_get(url)

    if data.get("status") == "1":
        try:
            abi = json.loads(data["result"])
            functions = []
            for item in abi:
                if item.get("type") == "function":
                    functions.append({
                        "name": item.get("name"),
                        "inputs": [i.get("type") for i in item.get("inputs", [])],
                        "outputs": [o.get("type") for o in item.get("outputs", [])],
                        "state_mutability": item.get("stateMutability"),
                    })
            return json.dumps({
                "total_functions": len(functions),
                "functions": functions,
                "has_owner_functions": any("owner" in f["name"].lower() for f in functions),
                "has_pause_functions": any("pause" in f["name"].lower() for f in functions),
                "has_mint_functions": any("mint" in f["name"].lower() for f in functions),
                "has_blacklist_functions": any(
                    kw in f["name"].lower()
                    for f in functions
                    for kw in ["blacklist", "blocklist", "ban", "restrict"]
                ),
            })
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid ABI format", "contract_address": contract_address})
    return json.dumps({"error": "ABI not available", "contract_address": contract_address})


@tool
async def check_honeypot(token_address: str, chain: str = "1") -> str:
    """Check if a token contract is a honeypot using the Honeypot.is API."""
    url = f"{HONEYPOT_BASE}/IsHoneypot?address={token_address}&chainID={chain}"
    data = await _http_get(url)
    if "error" in data:
        return json.dumps(data)

    honeypot_result = data.get("honeypotResult", {})
    simulation = data.get("simulationResult", {})
    result = {
        "is_honeypot": honeypot_result.get("isHoneypot", None),
        "honeypot_reason": honeypot_result.get("honeypotReason"),
        "buy_tax": simulation.get("buyTax"),
        "sell_tax": simulation.get("sellTax"),
        "transfer_tax": simulation.get("transferTax"),
        "buy_gas": simulation.get("buyGas"),
        "sell_gas": simulation.get("sellGas"),
        "max_buy": data.get("holderAnalysis", {}).get("maxBuy"),
        "max_sell": data.get("holderAnalysis", {}).get("maxSell"),
    }
    return json.dumps(result)


@tool
async def fetch_gopluslabs_security(token_address: str, chain_id: str = "1") -> str:
    """Fetch token security audit data from GoPlus Labs API including honeypot check, owner analysis, and trading restrictions."""
    url = f"{GOPLUS_BASE}/token_security/{chain_id}?contract_addresses={token_address}"
    data = await _http_get(url)
    if "error" in data:
        return json.dumps(data)

    result = data.get("result", {})
    token_data = result.get(token_address.lower(), {})
    if not token_data:
        return json.dumps({"error": "Token not found in GoPlus database", "token_address": token_address})

    return json.dumps({
        "is_open_source": token_data.get("is_open_source"),
        "is_proxy": token_data.get("is_proxy"),
        "is_mintable": token_data.get("is_mintable"),
        "can_take_back_ownership": token_data.get("can_take_back_ownership"),
        "owner_change_balance": token_data.get("owner_change_balance"),
        "hidden_owner": token_data.get("hidden_owner"),
        "selfdestruct": token_data.get("selfdestruct"),
        "external_call": token_data.get("external_call"),
        "buy_tax": token_data.get("buy_tax"),
        "sell_tax": token_data.get("sell_tax"),
        "is_honeypot": token_data.get("is_honeypot"),
        "transfer_pausable": token_data.get("transfer_pausable"),
        "is_blacklisted": token_data.get("is_blacklisted"),
        "is_whitelisted": token_data.get("is_whitelisted"),
        "trading_cooldown": token_data.get("trading_cooldown"),
        "personal_slippage_modifiable": token_data.get("personal_slippage_modifiable"),
        "holder_count": token_data.get("holder_count"),
        "total_supply": token_data.get("total_supply"),
        "owner_address": token_data.get("owner_address"),
        "creator_address": token_data.get("creator_address"),
    })


@tool
async def analyze_bytecode_patterns(contract_address: str, chain: str = "ethereum") -> str:
    """Analyze raw contract bytecode for known malicious patterns like selfdestruct, delegatecall to external addresses, or hidden proxy patterns."""
    explorer_urls = {
        "ethereum": ETHERSCAN_BASE,
        "bsc": "https://api.bscscan.com/api",
        "base": "https://api.basescan.org/api",
        "arbitrum": "https://api.arbiscan.io/api",
    }
    base = explorer_urls.get(chain, ETHERSCAN_BASE)
    url = f"{base}?module=proxy&action=eth_getCode&address={contract_address}&tag=latest"
    data = await _http_get(url)

    bytecode = data.get("result", "")
    if not bytecode or bytecode == "0x":
        return json.dumps({"error": "No bytecode found (EOA or empty)", "contract_address": contract_address})

    findings = []

    # SELFDESTRUCT (0xff)
    if "ff" in bytecode.lower():
        findings.append({
            "severity": "HIGH",
            "pattern": "SELFDESTRUCT",
            "description": "Contract contains SELFDESTRUCT opcode — can be permanently destroyed.",
        })

    # DELEGATECALL (0xf4)
    if "f4" in bytecode.lower():
        findings.append({
            "severity": "MEDIUM",
            "pattern": "DELEGATECALL",
            "description": "Contract uses DELEGATECALL — common in proxies but can be exploited.",
        })

    # CREATE2 (0xf5) — metamorphic contract indicator
    if "f5" in bytecode.lower():
        findings.append({
            "severity": "MEDIUM",
            "pattern": "CREATE2",
            "description": "Contract uses CREATE2 — could be a metamorphic contract that replaces itself.",
        })

    result = {
        "bytecode_length": len(bytecode),
        "is_contract": len(bytecode) > 2,
        "findings": findings,
        "finding_count": len(findings),
    }
    return json.dumps(result)


# ---------------------------------------------------------------------------
# Knowledge Base retrieval tool
# ---------------------------------------------------------------------------
KB_CONTRACT_VULNS = "87e4aa23-2271-11f1-b074-4e013e2ddde4"
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
async def search_vulnerability_patterns(query: str) -> str:
    """Search CryptoGuard's knowledge base of smart contract vulnerabilities, exploit case studies, and honeypot patterns. Use this to check if a contract's behavior matches known exploit patterns."""
    do_token = os.getenv("DIGITALOCEAN_API_TOKEN", "") or os.getenv("DIGITALOCEAN_ACCESS_TOKEN", "")
    if not do_token:
        return json.dumps({"note": "Knowledge base unavailable — DIGITALOCEAN_API_TOKEN not set. Proceeding with live API data only."})
    results = []
    for kb_uuid in [KB_CONTRACT_VULNS, KB_SAFETY]:
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
    fetch_contract_source,
    fetch_contract_abi,
    check_honeypot,
    fetch_gopluslabs_security,
    analyze_bytecode_patterns,
    search_vulnerability_patterns,
]

agent = create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)


# ---------------------------------------------------------------------------
# ADK entrypoint
# ---------------------------------------------------------------------------
@entrypoint
async def run(payload):
    """Smart Contract Auditor agent entrypoint with guardrails."""
    from guardrails import check_input, process_output, redact_pii

    query = payload.get("input", "") or payload.get("query", "") or str(payload)

    query = redact_pii(query)
    blocked = check_input(query)
    if blocked:
        return blocked

    result = await agent.ainvoke({"messages": [("user", query)]})
    messages = result.get("messages", [])
    final = messages[-1].content if messages else "No audit generated."
    final = process_output(final)
    return {"output": final}
