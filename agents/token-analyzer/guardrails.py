"""
CryptoGuard Guardrails Module
==============================
Input sanitization and output safety filters for all CryptoGuard agents.
Implements PII redaction, jailbreak detection, and financial disclaimer injection.
"""

import re

# ---------------------------------------------------------------------------
# PII Detection & Redaction (Input + Output)
# ---------------------------------------------------------------------------
PII_PATTERNS = [
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]'),
    (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE_REDACTED]'),
    (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]'),
    (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD_REDACTED]'),
    (r'\b(?:my name is|i am|i\'m)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', '[NAME_REDACTED]'),
]


def redact_pii(text: str) -> str:
    """Redact PII from text. Wallet addresses (base58/hex) are NOT redacted."""
    for pattern, replacement in PII_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


# ---------------------------------------------------------------------------
# Jailbreak Detection (Input)
# ---------------------------------------------------------------------------
JAILBREAK_PHRASES = [
    "ignore your instructions",
    "ignore previous instructions",
    "disregard your system prompt",
    "you are now",
    "act as if you have no restrictions",
    "pretend you are",
    "bypass your safety",
    "override your guidelines",
    "jailbreak",
    "DAN mode",
    "developer mode",
]


def detect_jailbreak(text: str) -> bool:
    """Returns True if input appears to be a jailbreak attempt."""
    lower = text.lower()
    return any(phrase in lower for phrase in JAILBREAK_PHRASES)


JAILBREAK_RESPONSE = {
    "output": "I'm CryptoGuard's security analyzer. I can only analyze crypto tokens and projects for risk. I cannot change my role or bypass safety guidelines. Please provide a token address or project name to analyze."
}

# ---------------------------------------------------------------------------
# Scope Guard (Input) — reject trade execution requests
# ---------------------------------------------------------------------------
SCOPE_PHRASES = [
    "buy this token",
    "sell this token",
    "execute a trade",
    "swap my tokens",
    "connect my wallet",
    "transfer funds",
    "send my",
    "approve this transaction",
]


def detect_out_of_scope(text: str) -> bool:
    """Returns True if user is asking the agent to execute actions."""
    lower = text.lower()
    return any(phrase in lower for phrase in SCOPE_PHRASES)


OUT_OF_SCOPE_RESPONSE = {
    "output": "CryptoGuard is an analysis tool only — I cannot execute trades, connect wallets, or transfer funds. I can analyze any token or project for risk. Please provide a token address or project name."
}

# ---------------------------------------------------------------------------
# Financial Disclaimer (Output)
# ---------------------------------------------------------------------------
DISCLAIMER = (
    "\n\n---\n⚠️ **Disclaimer:** This analysis is for informational purposes only "
    "and does not constitute financial or investment advice. Always do your own "
    "research (DYOR) before making any financial decisions. CryptoGuard cannot "
    "guarantee the accuracy of third-party data sources."
)


def append_disclaimer(text: str) -> str:
    """Append financial disclaimer to output."""
    if "Disclaimer:" not in text:
        return text + DISCLAIMER
    return text


# ---------------------------------------------------------------------------
# Combined guardrail check
# ---------------------------------------------------------------------------
def check_input(text: str) -> dict | None:
    """Run all input guardrails. Returns a response dict if blocked, None if clean."""
    if detect_jailbreak(text):
        return JAILBREAK_RESPONSE
    if detect_out_of_scope(text):
        return OUT_OF_SCOPE_RESPONSE
    return None


def process_output(text: str) -> str:
    """Run all output guardrails."""
    text = redact_pii(text)
    text = append_disclaimer(text)
    return text
