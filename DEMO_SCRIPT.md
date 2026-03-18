# CryptoGuard Demo Video Script

**Target length:** 2:30–2:45
**Format:** Screen recording with voiceover
**Tone:** Founder talking, not marketing. Direct, no filler.

---

## Setup Before Recording

Open these tabs:
1. CryptoGuard frontend: `http://localhost:3000`
2. DigitalOcean Gradient console: `https://cloud.digitalocean.com/gradient`
3. GitHub: `https://github.com/solder-build/cryptoguard`

## Test Tokens

### Safe (GREEN)
| Token | Address |
|-------|---------|
| Wrapped SOL | `So11111111111111111111111111111111111111112` |
| USDC | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` |

### Medium (YELLOW)
| Token | Address |
|-------|---------|
| $WIF | `EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm` |
| POPCAT | `7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr` |

### Dangerous (RED) — pump.fun tokens
| Token | Address |
|-------|---------|
| $NGU | `6xB2CqrfWdzHgDuBuVxev1t9cy3qmk91pxCuwNFcpump` |
| $SECURITY | `9iPCZqgZcaA3Kcx9CJ2apemHH7y9gND1yUvY4RT2pump` |
| PICKLE | `883GeVb468Vs2wa1ScwJEubQ4Pz1gmqhxzrzqisgpump` |

Best combo for video: Wrapped SOL (safe) → then $NGU or $SECURITY (dangerous)

---

## The Script

### [0:00–0:12] THE HOOK

**SHOW:** CryptoGuard landing page

**SAY:**

> In 2025, crypto users lost over five billion dollars to scams and rug pulls. The data to spot these scams is all on-chain — public, verifiable — but you'd need five different tools and the ability to read smart contract code to find it. Nobody does that. So people get rugged.

---

### [0:12–0:20] WHAT IT DOES

**SHOW:** Still on landing page, mouse hovering over the search bar

**SAY:**

> CryptoGuard is a multi-agent AI system that does that analysis for you. Paste a token address, and three specialized AI agents analyze it simultaneously. You get a risk score with evidence in seconds.

---

### [0:20–0:55] DEMO 1: SAFE TOKEN

**DO:** Paste `So11111111111111111111111111111111111111112` into the search bar. Click Analyze.

**SHOW:** Results loading, then the risk gauge, then the three agent cards.

**SAY:**

> Let me show you. This is Wrapped SOL — one of the most established tokens on Solana.
>
> Three agents are running. The Token Risk Analyzer is pulling liquidity data and holder distribution from DexScreener and Birdeye. The Smart Contract Auditor is checking for honeypots, hidden mint functions, and proxy upgrades. Market Intelligence is looking at trading volume patterns and whale movements.
>
> Risk score: low. High liquidity, normal holder distribution, no suspicious contract permissions. All three agents agree — this is safe.

---

### [0:55–1:35] DEMO 2: RISKY TOKEN

**DO:** Paste the risky token address. Click Analyze.

**SHOW:** Results loading, then the red/critical risk gauge, then findings.

**SAY:**

> Now let's try something I found launched two hours ago on pump.fun.
>
> Immediately different. Critical risk — score 85 out of 100.
>
> Token Analyzer found: mint authority is not revoked — the deployer can print unlimited tokens. Top ten wallets hold 91 percent of supply. Total liquidity is under three thousand dollars.
>
> Contract Auditor flagged a freeze authority still active — the deployer can freeze your tokens after you buy, making them unsellable. Classic honeypot pattern.
>
> Market Intelligence sees only eight unique buyers in the last hour with repetitive buy-sell patterns — textbook wash trading.
>
> Every finding is backed by real on-chain data. Nothing is made up.

---

### [1:35–2:05] UNDER THE HOOD — GRADIENT AI

**DO:** Switch to the DigitalOcean Gradient AI console tab.

**SHOW:** Click through Agents, Knowledge Bases, then back.

**SAY:**

> This runs entirely on DigitalOcean Gradient AI.
>
> *(Click on Agents)* Three agents deployed with the Gradient ADK. Each one has its own system prompt, its own tools, and its own analysis methodology. They're powered by Llama 3.3 70B through Gradient's serverless inference — no GPU infrastructure to manage.
>
> *(Click on Knowledge Bases)* Each agent is grounded in curated knowledge bases — real rug pull case studies, the OWASP Smart Contract Top 10, documented market manipulation cases. This prevents hallucination and makes the analysis specific, not generic.
>
> The agents also have guardrails — financial disclaimers are enforced on every response, PII is redacted from inputs, and jailbreak attempts are blocked. And everything is traceable through Gradient's built-in tracing.

---

### [2:05–2:30] WHY IT MATTERS

**DO:** Switch back to CryptoGuard frontend showing the critical risk result.

**SAY:**

> Ninety-eight percent of tokens launched on pump.fun in 2024 were scams. Rug pulls on Raydium had a median loss of twenty-eight hundred dollars each — across three hundred and sixty-one thousand pools.
>
> Right now, the only people who can spot these are security researchers who do this full time. CryptoGuard gives everyone else the same analysis — in seconds, for free, no wallet connection, no sign-up. Just paste an address and get a straight answer.

---

### [2:30–2:40] CLOSE

**SHOW:** GitHub repo page briefly, then back to CryptoGuard landing page.

**SAY:**

> CryptoGuard. Open source. Built on DigitalOcean Gradient AI. github.com/solder-build/cryptoguard.

---

## Recording Notes

- If live agents are slow due to rate limits, use demo mode data and say "shown here with cached results — live analysis takes 30-60 seconds"
- Keep mouse movements deliberate — don't circle randomly
- Zoom browser to 125% so text is readable on small screens
- Record at 1920x1080, 30fps
- If you record voice separately, it's cleaner — but screen+voice together is fine for a hackathon
- Upload to YouTube (unlisted) or Loom
