# Token Risk Patterns Knowledge Base

## Overview

This knowledge base provides real-world token risk patterns, rug pull indicators, and case studies sourced from documented incidents in 2024-2025. All data is sourced from verified reports and on-chain analysis.

---

## Section 1: Rug Pull Indicators

### 1.1 Liquidity Red Flags

- **No liquidity lock**: Developers can drain the liquidity pool at any time. Legitimate projects lock liquidity for 6-12 months minimum using time-lock contracts (e.g., Team.Finance, Unicrypt).
- **Short liquidity lock duration**: Locks under 30 days are suspicious. Some projects lock partial liquidity, which still allows partial rug pulls.
- **Low liquidity relative to market cap**: A token with a $10M market cap but only $50K in liquidity is extremely vulnerable to price manipulation.
- **Single-sided liquidity removal**: When developers remove one side of a trading pair (typically the base asset like SOL, ETH, or USDC), leaving holders with worthless tokens.

<!-- Source: https://tradesanta.com/blog/how-to-avoid-crypto-rug-pulls-in-2025 -->
<!-- Source: https://cryptocatguru.com/rug-pull-checks/ -->

### 1.2 Token Holder Concentration

- **Top 10 wallets holding >50% of supply**: Extreme concentration risk. Insiders can dump and crash the price at will.
- **Team allocation without vesting**: If team tokens are fully unlocked at launch, the team can sell immediately. Legitimate projects use vesting schedules (12-24 month linear vesting is standard).
- **Wallet clustering**: Multiple wallets controlled by the same entity, disguising concentration. On-chain analysis tools (Arkham, Nansen) can identify wallet clusters.
- **Threshold**: A healthy distribution has no single non-exchange wallet holding more than 5% of circulating supply.

<!-- Source: https://www.tokenmetrics.com/blog/how-do-i-know-if-a-coin-is-a-rug-pull-guide-2025 -->

### 1.3 Smart Contract Authority Risks

- **Mint authority not renounced**: The deployer can create unlimited new tokens, diluting existing holders to zero. On Solana, check with `spl-token display <mint_address>` — if Mint Authority is not "Disabled," this is a critical red flag.
- **Freeze authority enabled**: The deployer can freeze any holder's tokens, preventing them from selling. This is a hallmark of honeypot scams.
- **Upgrade authority retained**: The contract owner can change the contract logic at any time, potentially adding malicious functions post-launch.
- **Hidden owner functions**: Functions like `setFee()`, `blacklist()`, `pause()`, or `setMaxTx()` that give the owner disproportionate control.
- **Proxy contracts without timelocks**: Upgradeable contracts that can be changed instantly without governance delay.

<!-- Source: https://www.dextools.io/tutorials/how-to-spot-a-rug-pull-2026-checklist -->
<!-- Source: https://coincodex.com/article/68333/rug-pull-crypto/ -->

### 1.4 Social and Marketing Red Flags

- **Anonymous team**: While pseudonymous teams exist in crypto, total anonymity with no track record is a major risk factor.
- **No verifiable social media presence**: Fake followers, purchased engagement, recently created accounts.
- **Celebrity/influencer endorsements as primary marketing**: Paid promoters who have no stake in the project's long-term success.
- **Aggressive FOMO tactics**: "Get in now or miss out forever," countdown timers, artificial scarcity claims.
- **Unrealistic APY promises**: Double-digit daily returns, guaranteed profits, "100x guaranteed" — these are mathematically unsustainable and indicate Ponzi mechanics.
- **No whitepaper or technical documentation**: Legitimate projects explain their technology, tokenomics, and roadmap in detail.
- **Copied whitepaper**: Plagiarized content from other projects, detectable via plagiarism checkers.

<!-- Source: https://chaotikkplanet.com/how-to-avoid-crypto-rug-pulls/ -->

### 1.5 Honeypot Indicators

- **Buy-only contracts**: Users can buy but the contract prevents selling. Before buying, use GoPlus Security API or Honeypot.is to simulate whether selling is possible.
- **Hidden fee escalation**: Contract starts with 0% sell tax, then owner changes it to 99%.
- **Max transaction limits on sells only**: Buyers can purchase freely but sells are capped at tiny amounts.
- **Blacklist functions**: Owner can blacklist any wallet address from selling.

<!-- Source: https://www.dextools.io/tutorials/how-to-spot-a-rug-pull-2026-checklist -->

---

## Section 2: Real Rug Pull Case Studies

### Case 1: Mantra (OM Token) — 2025

- **Date**: Early 2025
- **Amount Lost**: $5.52 billion in market value destroyed
- **What Happened**: 17 wallets moved 43.6 million OM tokens ($227 million) to exchanges in a short timeframe, triggering a 94% price crash from $6.35 to $0.37.
- **Red Flags Present**: Extreme holder concentration, large coordinated exchange deposits, rapid price decline.
- **Classification**: Largest rug pull of 2025. Marketed as a "real-world asset DeFi platform."

<!-- Source: https://coinedition.com/crypto-2025-rug-pulls-fast-crashes-what-the-crypto-community-must-learn-and-how-to-spot-rugs/ -->

### Case 2: LIBRA Token (Argentina Cryptogate) — February 2025

- **Date**: February 14, 2025
- **Amount Lost**: ~$4 billion in market cap wiped; $251 million direct investor losses
- **What Happened**: Argentina President Javier Milei promoted the $LIBRA token on social media. Price surged from $0.000001 to $5.20 in 40 minutes. Founders held 70% of total supply and sold at the peak, crashing the price by 95%.
- **Red Flags Present**: 70% insider supply, political figure endorsement, no utility, no liquidity lock, token created minutes before promotion.
- **Aftermath**: Federal investigation launched against Milei. Evidence of a $5 million payment scheme linking Milei to the promotion. Dubbed "Cryptogate" by media.

<!-- Source: https://en.wikipedia.org/wiki/$Libra_cryptocurrency_scandal -->
<!-- Source: https://nftevening.com/argentina-president-libra-collapse/ -->

### Case 3: $TRUMP Memecoin — January 2025

- **Date**: January 17, 2025
- **Amount Lost**: $2 billion in investor losses; 813,000+ wallets affected
- **What Happened**: Launched 3 days before presidential inauguration. 800 million of 1 billion tokens retained by Trump-owned companies (80% insider holding). Price peaked at $75, fell 86% by end of 2025.
- **Red Flags Present**: 80% insider supply, no utility, political figure token, no vesting schedule.
- **Additional Concerns**: Trump Organization and partners earned $100 million in trading fees. Leaked information about a "dinner with the president" promotion allowed insiders to front-run.

<!-- Source: https://fortune.com/2025/02/11/trump-memecoin-traders-2-billion-dollar-loss-family-100-million-fees/ -->
<!-- Source: https://en.wikipedia.org/wiki/$Trump -->

### Case 4: $MELANIA Memecoin — January 2025

- **Date**: January 19, 2025
- **Amount Lost**: 99% price decline from launch to November 2025
- **What Happened**: Launched one day before inauguration. Partially handled by Hayden Davis (later implicated in LIBRA scandal). Team repeatedly drained liquidity pools ("soft rug pull"), selling over $4 million from liquidity.
- **Red Flags Present**: Insider involvement (same team as LIBRA), ongoing liquidity extraction, no utility.

<!-- Source: https://www.coinspeaker.com/heres-how-melania-trumps-meme-coin-has-been-executing-soft-rug-pulls/ -->

### Case 5: Hawk Tuah ($HAWK) — December 2024

- **Date**: December 4, 2024
- **Amount Lost**: Market cap crashed from $490 million to near zero (93%+ decline within minutes)
- **What Happened**: Influencer Hailey Welch ("Hawk Tuah girl") launched $HAWK token. 97% of supply was initially held by 10 wallets. Only 3% was available for public sale. 285 presale investors, 30% of whom immediately dumped.
- **Red Flags Present**: 97% insider concentration, tokenomics changed before launch (20% early investor allocation reduced to 17% but lock removed), influencer-driven hype.
- **Aftermath**: Potential DOJ investigation and civil lawsuits.

<!-- Source: https://www.halborn.com/blog/post/explained-the-hawk-tuah-rug-pull-december-2024 -->
<!-- Source: https://www.ccn.com/education/crypto/hawk-tuah-rug-pull-explained/ -->

### Case 6: Froggy Coin — 2024

- **Date**: 2024
- **Amount Lost**: 99.95% price drop
- **What Happened**: Liquidity was drained from the pool by the deployer, leaving holders unable to sell.
- **Red Flags Present**: Unlocked liquidity, anonymous team, no audit.

<!-- Source: https://openexo.com/l/771cc129 -->

### Case 7: DIO Token — 2024

- **Date**: 2024
- **Amount Lost**: 98.8% price drop
- **What Happened**: Alleged pump-and-dump manipulation. Token was promoted heavily, then insiders sold coordinated.
- **Red Flags Present**: Coordinated insider selling, artificial hype campaign.

<!-- Source: https://openexo.com/l/771cc129 -->

### Case 8: Sharpei (Solana Meme Coin) — 2024

- **Date**: 2024
- **Amount Lost**: 96.3% price drop
- **What Happened**: Project falsely claimed an alliance with a major entity. Once debunked, price collapsed.
- **Red Flags Present**: False partnership claims, no verification of stated alliances.

<!-- Source: https://openexo.com/l/771cc129 -->

### Case 9: Pump.fun Ecosystem — 2024-2025

- **Date**: January 2024 - March 2025
- **Amount Lost**: ~$500 million in Solana-based rug pulls in 2024 alone
- **What Happened**: 98.6% of tokens launched on Pump.fun collapsed into worthless pump-and-dump schemes. Over 7 million tokens deployed, only 97,000 maintained liquidity above $1,000.
- **Red Flags Present**: One-click token deployment with no barriers, no audits, anonymous deployers, instant liquidity removal capability.
- **Legal Action**: Class action lawsuit filed against Pump.fun, Solana Foundation, Solana Labs, and Jito Labs. 5,000+ private messages between engineers allegedly discussing manipulation of coin launches.

<!-- Source: https://www.soliduslabs.com/reports/solana-rug-pulls-pump-dumps-crypto-compliance -->
<!-- Source: https://thedefiant.io/news/defi/alarming-99-of-memecoin-launches-on-pumpfun-are-pump-and-dumps-or-rug-pulls-report -->

### Case 10: Raydium DEX Ecosystem — 2024

- **Date**: 2024
- **Amount Lost**: Median rug pull worth $2,800 each across 361,000 pools
- **What Happened**: 93% of liquidity pools on Raydium exhibited soft rug pull characteristics.
- **Red Flags Present**: Low liquidity, rapid creation/abandonment cycle, concentrated holders.

<!-- Source: https://www.soliduslabs.com/reports/solana-rug-pulls-pump-dumps-crypto-compliance -->

---

## Section 3: Token Health Metrics

### 3.1 Healthy Liquidity Depth

- **Minimum viable liquidity**: At least 10-20% of market cap should be in liquidity pools for safe trading.
- **Liquidity-to-market-cap ratio**: Healthy tokens maintain >15% ratio. Below 5% is a warning sign. Below 1% is extremely dangerous.
- **Locked liquidity duration**: 6+ months is acceptable. 12+ months is ideal. Lifetime locks indicate strongest commitment.
- **Liquidity lock verification**: Check on-chain via DexScreener, DEXTools, or directly on the lock contract (Team.Finance, Unicrypt, PinkLock).

### 3.2 Normal vs. Suspicious Trading Volume Patterns

**Normal Patterns:**
- Volume correlates with price movement and news events
- Gradual volume increases during uptrends
- Volume decreases during consolidation periods
- Buy/sell ratio roughly balanced over time (40-60% range)
- Organic spread of transaction sizes (mix of small and large trades)

**Suspicious Patterns:**
- Volume spikes with no corresponding news or catalyst
- Perfectly round-number transactions repeating at regular intervals (wash trading signal)
- Volume concentrated in very few wallets (detectable via on-chain analysis)
- Volume 10x-100x above average with no fundamental reason
- All transactions nearly identical in size and timing
- Volume entirely during off-peak hours with no geographic explanation

### 3.3 Healthy Holder Distribution

**Healthy Distribution Curve:**
- Top holder (non-exchange): <5% of circulating supply
- Top 10 holders (non-exchange): <25% of circulating supply
- Top 50 holders (non-exchange): <40% of circulating supply
- Thousands of unique holders with a natural Pareto distribution
- Growing holder count over time (not declining)

**Unhealthy Distribution:**
- Single wallet holding >20% of supply (unless a known exchange or locked contract)
- Top 10 wallets holding >50% of supply
- Declining unique holder count (people are leaving)
- Cluster of wallets all funded from the same source
- Wallets that received tokens through direct transfers (not market purchases)

### 3.4 Token Creation Pattern Analysis

**Normal Token Launch:**
- Deployed contract is verified and source code is publicly readable
- Liquidity added and locked in the same transaction or shortly after
- Team tokens vested over 12-24 months
- Marketing begins before or at launch, not after price peaks
- Gradual organic price discovery

**Suspicious Token Launch:**
- Token created and liquidity added within seconds (sniper-friendly)
- Large buys from insider wallets within the first block
- Contract deployed but not verified (source code hidden)
- Liquidity added without any lock
- Social media promotion begins only after insider wallets have bought
- Multiple tokens deployed from the same wallet in short succession (serial scammer)

---

## Section 4: Risk Scoring Framework

### Composite Risk Score (0-100)

CryptoGuard agents should evaluate tokens against these weighted criteria:

| Factor | Weight | High Risk Threshold |
|--------|--------|-------------------|
| Liquidity lock status | 15% | No lock or <30 days |
| Holder concentration | 15% | Top 10 wallets >50% |
| Mint authority | 12% | Not renounced |
| Freeze authority | 10% | Enabled |
| Contract verification | 10% | Unverified source code |
| Audit status | 8% | No audit |
| Team identity | 8% | Fully anonymous, no track record |
| Social media authenticity | 7% | Fake followers, no real community |
| Tokenomics transparency | 8% | No vesting, hidden allocations |
| Trading pattern health | 7% | Wash trading signals detected |

**Risk Levels:**
- 0-25: Low Risk (multiple positive indicators, established project)
- 26-50: Moderate Risk (some concerns but no critical red flags)
- 51-75: High Risk (multiple red flags present, proceed with extreme caution)
- 76-100: Critical Risk (strong rug pull indicators, avoid)

---

## Section 5: 2024-2025 Statistics

- **2024**: 58 documented rug pull cases, $106 million to $3.4 billion lost (varying by reporting methodology)
- **Q1 2025**: ~$6 billion wiped by crypto rug pulls, up 6,500% from $90 million in Q1 2024
- **Average rug pull timeline**: 12 days from launch to pull (down from 21 days in 2023)
- **58% of rug pulls** occurred on decentralized exchanges (Uniswap, PancakeSwap, Raydium)
- **Solana ecosystem**: 98.6% of tokens on Pump.fun were rug pulls or pump-and-dumps
- **Wallet drainer attacks**: $494 million stolen from 332,000 wallet addresses in 2024 (67% increase year-over-year)

<!-- Source: https://coinlaw.io/rug-pulls-amp-ponzi-schemes-in-crypto-statistics/ -->
<!-- Source: https://moonlock.com/wallet-drainer-crypto-theft-2024 -->

---

## Section 6: Verification Tools Reference

Agents should recommend these tools for users conducting their own due diligence:

| Tool | Purpose | URL |
|------|---------|-----|
| RugCheck | Solana token risk analysis | rugcheck.xyz |
| Token Sniffer | Multi-chain scam detection | tokensniffer.com |
| GoPlus Security | Honeypot detection, contract analysis | gopluslabs.io |
| DEXTools | Liquidity analysis, holder distribution | dextools.io |
| DexScreener | Real-time trading data, liquidity metrics | dexscreener.com |
| Bubblemaps | Visual holder concentration analysis | bubblemaps.io |
| Arkham Intelligence | Wallet clustering, entity identification | arkhamintelligence.com |
| Honeypot.is | Simulate buy/sell to detect honeypots | honeypot.is |
| SolSniffer | Solana-specific token auditing | solsniffer.com |
