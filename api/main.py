"""
CryptoGuard - API Orchestrator
================================
FastAPI server that routes queries to Gradient AI agent endpoints,
aggregates multi-agent responses, and produces unified risk scores.

Setup:
  cd api/
  pip install -r requirements.txt
  cp ../.env.example .env  # fill in your keys
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload

Endpoints:
  POST /api/analyze  — Full analysis (calls all 3 agents in parallel)
  POST /api/chat     — Chat with a specific agent
  GET  /api/health   — Health check
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cryptoguard-api")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
AGENT_CONFIG = {
    "token-analyzer": {
        "endpoint": os.getenv("TOKEN_ANALYZER_ENDPOINT", ""),
        "key": os.getenv("TOKEN_ANALYZER_KEY", ""),
        "name": "Token Risk Analyzer",
        "description": "Analyzes token liquidity, holder concentration, and contract permissions",
    },
    "contract-auditor": {
        "endpoint": os.getenv("CONTRACT_AUDITOR_ENDPOINT", ""),
        "key": os.getenv("CONTRACT_AUDITOR_KEY", ""),
        "name": "Smart Contract Auditor",
        "description": "Audits smart contract code for vulnerabilities and malicious patterns",
    },
    "market-intel": {
        "endpoint": os.getenv("MARKET_INTEL_ENDPOINT", ""),
        "key": os.getenv("MARKET_INTEL_KEY", ""),
        "name": "Market Intelligence",
        "description": "Analyzes trading patterns, whale movements, and social signals",
    },
}

GRADIENT_MODEL_ACCESS_KEY = os.getenv("GRADIENT_MODEL_ACCESS_KEY", "")

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="CryptoGuard API",
    description="Multi-agent crypto threat intelligence platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request/Response models
# ---------------------------------------------------------------------------
class AgentName(str, Enum):
    TOKEN_ANALYZER = "token-analyzer"
    CONTRACT_AUDITOR = "contract-auditor"
    MARKET_INTEL = "market-intel"


class AnalyzeRequest(BaseModel):
    """Request body for full multi-agent analysis."""
    query: str = Field(..., description="Token address, project name, or analysis question")
    chain: str = Field(default="solana", description="Blockchain to analyze on")
    agents: list[AgentName] | None = Field(
        default=None,
        description="Specific agents to use. Default: all three.",
    )


class ChatRequest(BaseModel):
    """Request body for single-agent chat."""
    agent: AgentName = Field(..., description="Which agent to chat with")
    messages: list[dict] = Field(..., description="Chat messages in OpenAI format")
    stream: bool = Field(default=False, description="Whether to stream the response")


class RiskScore(BaseModel):
    """Unified risk score output."""
    overall_score: int = Field(..., ge=0, le=100)
    risk_level: str
    category_scores: dict[str, int]
    confidence: float = Field(..., ge=0.0, le=1.0)


class AgentResponse(BaseModel):
    """Response from a single agent."""
    agent: str
    agent_name: str
    response: str
    risk_score: int | None = None
    latency_ms: int
    error: str | None = None


class AnalyzeResponse(BaseModel):
    """Full analysis response aggregating all agents."""
    query: str
    chain: str
    unified_risk_score: RiskScore
    agent_responses: list[AgentResponse]
    timestamp: str
    total_latency_ms: int


# ---------------------------------------------------------------------------
# Agent communication
# ---------------------------------------------------------------------------
async def call_agent(
    agent_id: str,
    messages: list[dict],
    timeout: float = 120.0,
) -> dict:
    """
    Call a Gradient AI ADK agent endpoint (POST /run with {"input": "..."}).
    Returns the full response dict or an error dict.
    """
    config = AGENT_CONFIG.get(agent_id)
    if not config:
        return {"error": f"Unknown agent: {agent_id}"}

    endpoint = config["endpoint"]
    api_key = config["key"]

    if not endpoint:
        return {
            "error": f"Agent {agent_id} endpoint not configured. "
                     f"Set {agent_id.upper().replace('-', '_')}_ENDPOINT in .env",
        }

    # ADK agents use /run endpoint with {"input": "..."} format
    url = endpoint.rstrip("/")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    # Extract the last user message as the input
    user_msg = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_msg = msg.get("content", "")
            break
    payload = {"input": user_msg}

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            # ADK returns {"output": "..."} format
            content = data.get("output", "") or data.get("content", "") or json.dumps(data)
            return {"content": content, "raw": data}
    except httpx.HTTPStatusError as exc:
        logger.error("Agent %s returned HTTP %s", agent_id, exc.response.status_code)
        return {"error": f"HTTP {exc.response.status_code}: {exc.response.text[:500]}"}
    except httpx.RequestError as exc:
        logger.error("Agent %s request failed: %s", agent_id, exc)
        return {"error": f"Connection error: {str(exc)}"}


async def call_agent_streaming(
    agent_id: str,
    messages: list[dict],
    timeout: float = 120.0,
):
    """
    Call a Gradient AI ADK agent. ADK agents don't natively stream via /run,
    so we call synchronously and yield the result as a single SSE event.
    """
    result = await call_agent(agent_id, messages, timeout)
    content = result.get("content", result.get("error", "No response"))
    yield f"data: {json.dumps({'content': content})}\n\n"
    yield "data: [DONE]\n\n"


# ---------------------------------------------------------------------------
# Risk score calculation
# ---------------------------------------------------------------------------
def extract_risk_score(agent_response: str) -> int | None:
    """
    Extract a numeric risk score from agent response text.
    Agents are prompted to include overall_risk_score in their output.
    """
    # Try JSON parsing first
    try:
        # Look for JSON block in the response
        for start_char, end_char in [("{", "}"), ("```json", "```")]:
            start = agent_response.find(start_char)
            if start >= 0:
                if start_char == "```json":
                    start += 7
                    end = agent_response.find(end_char, start)
                else:
                    # Find matching closing brace
                    depth = 0
                    end = start
                    for i, c in enumerate(agent_response[start:], start):
                        if c == "{":
                            depth += 1
                        elif c == "}":
                            depth -= 1
                            if depth == 0:
                                end = i + 1
                                break
                if end > start:
                    candidate = agent_response[start:end]
                    parsed = json.loads(candidate)
                    if "overall_risk_score" in parsed:
                        score = int(parsed["overall_risk_score"])
                        return max(0, min(100, score))
    except (json.JSONDecodeError, ValueError, TypeError):
        pass

    # Fallback: regex for "risk_score": N or "overall_risk_score": N
    import re
    patterns = [
        r'"overall_risk_score"\s*:\s*(\d+)',
        r'"risk_score"\s*:\s*(\d+)',
        r"overall_risk_score\s*:\s*(\d+)",
        r"risk score[:\s]+(\d+)",
        r"(\d+)\s*/\s*100",
    ]
    for pattern in patterns:
        match = re.search(pattern, agent_response, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            if 0 <= score <= 100:
                return score

    return None


def calculate_unified_risk_score(
    agent_scores: dict[str, int | None],
) -> RiskScore:
    """
    Calculate a deterministic unified risk score from individual agent scores.

    Weights:
      - token-analyzer: 35% (fundamental token safety)
      - contract-auditor: 35% (code-level security)
      - market-intel: 30% (market behavior signals)

    Confidence is based on how many agents successfully returned scores.
    """
    weights = {
        "token-analyzer": 0.35,
        "contract-auditor": 0.35,
        "market-intel": 0.30,
    }

    valid_scores = {k: v for k, v in agent_scores.items() if v is not None}
    total_agents = len(agent_scores)
    responding_agents = len(valid_scores)

    if responding_agents == 0:
        return RiskScore(
            overall_score=50,
            risk_level="UNKNOWN",
            category_scores={},
            confidence=0.0,
        )

    # Normalize weights for responding agents only
    total_weight = sum(weights.get(k, 0.33) for k in valid_scores)
    weighted_sum = sum(
        score * (weights.get(agent, 0.33) / total_weight)
        for agent, score in valid_scores.items()
    )

    overall = int(round(weighted_sum))
    overall = max(0, min(100, overall))

    # Confidence: based on number of agents that responded
    confidence = round(responding_agents / total_agents, 2) if total_agents > 0 else 0.0

    # Risk level classification
    if overall <= 30:
        risk_level = "LOW"
    elif overall <= 60:
        risk_level = "MEDIUM"
    elif overall <= 80:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    return RiskScore(
        overall_score=overall,
        risk_level=risk_level,
        category_scores={k: v for k, v in valid_scores.items()},
        confidence=confidence,
    )


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health")
async def health_check():
    """Health check endpoint. Returns agent configuration status."""
    agent_status = {}
    for agent_id, config in AGENT_CONFIG.items():
        agent_status[agent_id] = {
            "name": config["name"],
            "configured": bool(config["endpoint"]),
            "endpoint_set": bool(config["endpoint"]),
            "key_set": bool(config["key"]),
        }
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agents": agent_status,
        "gradient_key_set": bool(GRADIENT_MODEL_ACCESS_KEY),
    }


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    """
    Run a full multi-agent analysis on a token/project.

    Calls all requested agents in parallel, extracts individual risk scores,
    and produces a unified weighted risk score.
    """
    start_time = time.monotonic()

    # Determine which agents to call
    agent_ids = [a.value for a in req.agents] if req.agents else list(AGENT_CONFIG.keys())

    # Build the analysis prompt
    user_message = (
        f"Analyze the following for risk and threats.\n"
        f"Query: {req.query}\n"
        f"Chain: {req.chain}\n\n"
        f"Use your tools to fetch real data, then produce your risk assessment "
        f"with an overall_risk_score (0-100) and detailed findings.\n"
        f"Return your assessment as a JSON object with keys: "
        f"overall_risk_score, risk_level, category_scores, findings, recommendation."
    )

    messages = [{"role": "user", "content": user_message}]

    # Call agents sequentially to avoid rate limits on free tier
    # Switch to asyncio.gather for parallel calls if on a paid tier
    results = {}
    for agent_id in agent_ids:
        try:
            results[agent_id] = await call_agent(agent_id, messages)
        except Exception as exc:
            results[agent_id] = {"error": str(exc)}

    # Build agent responses and extract scores
    agent_responses = []
    agent_scores = {}

    for agent_id in agent_ids:
        result = results.get(agent_id, {})
        config = AGENT_CONFIG[agent_id]
        elapsed = int((time.monotonic() - start_time) * 1000)

        if "error" in result:
            agent_responses.append(AgentResponse(
                agent=agent_id,
                agent_name=config["name"],
                response="",
                risk_score=None,
                latency_ms=elapsed,
                error=result["error"],
            ))
            agent_scores[agent_id] = None
        else:
            content = result.get("content", "")
            score = extract_risk_score(content)
            agent_responses.append(AgentResponse(
                agent=agent_id,
                agent_name=config["name"],
                response=content,
                risk_score=score,
                latency_ms=elapsed,
            ))
            agent_scores[agent_id] = score

    # Calculate unified risk score
    unified = calculate_unified_risk_score(agent_scores)
    total_elapsed = int((time.monotonic() - start_time) * 1000)

    return AnalyzeResponse(
        query=req.query,
        chain=req.chain,
        unified_risk_score=unified,
        agent_responses=agent_responses,
        timestamp=datetime.now(timezone.utc).isoformat(),
        total_latency_ms=total_elapsed,
    )


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """
    Chat with a specific agent. Supports streaming.
    """
    agent_id = req.agent.value

    if req.stream:
        return StreamingResponse(
            call_agent_streaming(agent_id, req.messages),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    start_time = time.monotonic()
    result = await call_agent(agent_id, req.messages)
    elapsed = int((time.monotonic() - start_time) * 1000)

    if "error" in result:
        raise HTTPException(
            status_code=502,
            detail={
                "error": result["error"],
                "agent": agent_id,
                "latency_ms": elapsed,
            },
        )

    return {
        "agent": agent_id,
        "agent_name": AGENT_CONFIG[agent_id]["name"],
        "response": result.get("content", ""),
        "latency_ms": elapsed,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return {
        "error": "Internal server error",
        "detail": str(exc) if os.getenv("DEBUG") else "An unexpected error occurred",
    }


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup():
    logger.info("CryptoGuard API starting")
    unconfigured = [
        aid for aid, cfg in AGENT_CONFIG.items() if not cfg["endpoint"]
    ]
    if unconfigured:
        logger.warning(
            "Agents without endpoints configured: %s. "
            "Set environment variables in .env file.",
            ", ".join(unconfigured),
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
