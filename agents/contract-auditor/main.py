"""
CryptoGuard - Smart Contract Auditor Agent
============================================
Gradient AI ADK agent that audits smart contract code for vulnerabilities.
Checks for honeypot patterns, hidden mints, proxy upgradability, and ownership issues.

Setup:
  pip install -r requirements.txt
  gradient agent deploy
"""

import json
import logging
import re
from typing import Any

import httpx
from gradient_ai import entrypoint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("contract-auditor")

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are CryptoGuard's Smart Contract Auditor — a security researcher who
analyzes smart contract code with the precision of a penetration tester.

PERSONALITY:
- Direct, technical, no-nonsense. You speak in security terminology.
- You classify findings by severity: CRITICAL, HIGH, MEDIUM, LOW, INFO.
- You cite specific code patterns and line references when possible.
- You never say "looks safe" without evidence — absence of proof is not proof of absence.

AUDIT FRAMEWORK (score each 0-100, higher = riskier):

1. HONEYPOT ANALYSIS (weight 30%)
   - Can holders sell freely? Check for transfer restrictions.
   - Are there max transaction limits that prevent selling?
   - Hidden fees that make selling unprofitable?
   - Blacklist mechanisms that can block specific addresses?
   - Cooldown periods that prevent rapid sells?

2. HIDDEN FUNCTION ANALYSIS (weight 25%)
   - Unrestricted mint functions (can supply be inflated?)
   - Hidden fee modification functions
   - Pause/unpause mechanisms controlled by single address
   - Self-destruct or delegatecall patterns
   - Obfuscated function names or dead code paths

3. PROXY & UPGRADABILITY RISK (weight 25%)
   - Is the contract upgradable via proxy?
   - Who controls the upgrade mechanism?
   - Has implementation been verified on-chain?
   - Timelock on upgrades?
   - Storage collision risks in proxy patterns

4. OWNERSHIP & ACCESS CONTROL (weight 20%)
   - Is ownership renounced?
   - Multi-sig vs single-key admin
   - Role-based access control implementation
   - Emergency functions accessible by owner
   - Contract can receive and drain ETH/SOL

OUTPUT FORMAT:
Return a structured audit with:
- overall_risk_score: 0-100
- risk_level: "LOW" (0-30) | "MEDIUM" (31-60) | "HIGH" (61-80) | "CRITICAL" (81-100)
- category_scores: dict of each category score
- vulnerabilities: list of {severity, title, description, code_reference}
- recommendation: brief actionable advice

KNOWN VULNERABILITY PATTERNS:
- Reentrancy: external calls before state updates
- Integer overflow/underflow (pre-Solidity 0.8)
- Unchecked return values on transfers
- Front-running susceptible functions
- Flash loan attack vectors
- Oracle manipulation
- Access control bypass via tx.origin
- Delegatecall to untrusted contracts
- Storage collision in upgradable proxies
- Signature replay attacks
"""

# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_contract_source",
            "description": "Fetch verified contract source code from a block explorer (Etherscan, Solscan, BSCScan).",
            "parameters": {
                "type": "object",
                "properties": {
                    "contract_address": {
                        "type": "string",
                        "description": "The contract/program address.",
                    },
                    "chain": {
                        "type": "string",
                        "description": "Blockchain. Default: solana",
                        "enum": ["solana", "ethereum", "bsc", "base", "arbitrum"],
                    },
                },
                "required": ["contract_address"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_contract_abi",
            "description": "Fetch the contract ABI to analyze function signatures and access modifiers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contract_address": {
                        "type": "string",
                        "description": "The contract address (EVM chains only).",
                    },
                    "chain": {
                        "type": "string",
                        "description": "Blockchain. Default: ethereum",
                        "enum": ["ethereum", "bsc", "base", "arbitrum"],
                    },
                },
                "required": ["contract_address"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_honeypot",
            "description": "Check if a token contract is a honeypot using the Honeypot.is API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "token_address": {
                        "type": "string",
                        "description": "The token contract address.",
                    },
                    "chain": {
                        "type": "string",
                        "description": "Chain ID. Default: 1 (Ethereum)",
                        "enum": ["1", "56", "8453", "42161"],
                    },
                },
                "required": ["token_address"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_gopluslabs_security",
            "description": "Fetch token security audit data from GoPlus Labs API including honeypot check, owner analysis, and trading restrictions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "token_address": {
                        "type": "string",
                        "description": "The token contract address.",
                    },
                    "chain_id": {
                        "type": "string",
                        "description": "Chain ID: 1=ETH, 56=BSC, 137=Polygon, 42161=Arbitrum. Default: 1",
                    },
                },
                "required": ["token_address"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_bytecode_patterns",
            "description": "Analyze raw contract bytecode for known malicious patterns like selfdestruct, delegatecall to external addresses, or hidden proxy patterns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contract_address": {
                        "type": "string",
                        "description": "The contract address.",
                    },
                    "chain": {
                        "type": "string",
                        "description": "Blockchain. Default: ethereum",
                        "enum": ["ethereum", "bsc", "base", "arbitrum"],
                    },
                },
                "required": ["contract_address"],
            },
        },
    },
]

# ---------------------------------------------------------------------------
# Tool implementations
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


async def fetch_contract_source(contract_address: str, chain: str = "solana") -> dict:
    """Fetch verified source code from block explorers."""
    if chain == "solana":
        # Solana programs — check if verified on Solscan
        url = f"https://pro-api.solscan.io/v2.0/account/{contract_address}"
        data = await _http_get(url, headers={"token": ""})
        if "error" in data:
            return {
                "note": "Solscan API key not configured. For Solana programs, "
                        "provide the source code directly or check anchor-verified status.",
                "contract_address": contract_address,
                "suggestion": "Try searching for the program IDL on-chain or check "
                              "https://solscan.io/account/" + contract_address,
            }
        return data.get("data", data)

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
        return {
            "contract_name": result.get("ContractName"),
            "compiler_version": result.get("CompilerVersion"),
            "optimization_used": result.get("OptimizationUsed"),
            "is_proxy": result.get("Proxy") == "1",
            "implementation": result.get("Implementation"),
            "source_code_length": len(source),
            "source_code": source[:10000] if source else "Not verified",
            "license": result.get("LicenseType"),
        }
    return {"error": "Source code not verified or not found", "contract_address": contract_address}


async def fetch_contract_abi(contract_address: str, chain: str = "ethereum") -> dict:
    """Fetch contract ABI from block explorer."""
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
            # Extract key function signatures for analysis
            functions = []
            for item in abi:
                if item.get("type") == "function":
                    functions.append({
                        "name": item.get("name"),
                        "inputs": [i.get("type") for i in item.get("inputs", [])],
                        "outputs": [o.get("type") for o in item.get("outputs", [])],
                        "state_mutability": item.get("stateMutability"),
                    })
            return {
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
            }
        except json.JSONDecodeError:
            return {"error": "Invalid ABI format", "contract_address": contract_address}
    return {"error": "ABI not available", "contract_address": contract_address}


async def check_honeypot(token_address: str, chain: str = "1") -> dict:
    """Check honeypot status via Honeypot.is API."""
    url = f"{HONEYPOT_BASE}/IsHoneypot?address={token_address}&chainID={chain}"
    data = await _http_get(url)
    if "error" in data:
        return data

    honeypot_result = data.get("honeypotResult", {})
    simulation = data.get("simulationResult", {})
    return {
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


async def fetch_gopluslabs_security(token_address: str, chain_id: str = "1") -> dict:
    """Fetch security data from GoPlus Labs (free, no API key)."""
    url = f"{GOPLUS_BASE}/token_security/{chain_id}?contract_addresses={token_address}"
    data = await _http_get(url)
    if "error" in data:
        return data

    result = data.get("result", {})
    token_data = result.get(token_address.lower(), {})
    if not token_data:
        return {"error": "Token not found in GoPlus database", "token_address": token_address}

    return {
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
    }


async def analyze_bytecode_patterns(contract_address: str, chain: str = "ethereum") -> dict:
    """Analyze bytecode for known malicious opcodes."""
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
        return {"error": "No bytecode found (EOA or empty)", "contract_address": contract_address}

    # Analyze opcodes
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

    return {
        "bytecode_length": len(bytecode),
        "is_contract": len(bytecode) > 2,
        "findings": findings,
        "finding_count": len(findings),
    }


TOOL_HANDLERS: dict[str, Any] = {
    "fetch_contract_source": fetch_contract_source,
    "fetch_contract_abi": fetch_contract_abi,
    "check_honeypot": check_honeypot,
    "fetch_gopluslabs_security": fetch_gopluslabs_security,
    "analyze_bytecode_patterns": analyze_bytecode_patterns,
}


# ---------------------------------------------------------------------------
# ADK entrypoint
# ---------------------------------------------------------------------------
@entrypoint
async def main(request):
    """Smart Contract Auditor agent entrypoint."""
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
