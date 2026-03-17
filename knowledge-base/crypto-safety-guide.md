# Crypto Safety Guide Knowledge Base

## Overview

This guide provides practical, actionable safety advice for retail crypto investors. It covers project verification, scam identification, recovery steps, and trusted resources. All recommendations are based on real scam patterns observed in 2024-2025, during which investors lost over $6 billion to rug pulls in Q1 2025 alone and $494 million to wallet drainer phishing attacks in 2024.

---

## Section 1: Best Practices for Retail Crypto Investors

### 1.1 Wallet Security

**Use Hardware Wallets for Storage:**
- Keep the majority of funds on a hardware wallet (Ledger, Trezor) that stores private keys offline
- Only keep small amounts on hot wallets (MetaMask, Phantom) for active trading
- Never store private keys or seed phrases digitally (no screenshots, no notes apps, no cloud storage)
- Write seed phrases on physical media (metal backup plates are fire/water resistant) and store in a secure location

**Two-Factor Authentication (2FA):**
- Enable 2FA on every exchange and crypto service account
- Use authenticator apps (Google Authenticator, Authy) rather than SMS 2FA (SIM swap attacks can bypass SMS)
- Keep backup codes for 2FA in a separate secure location from your seed phrases

**Transaction Security:**
- Always verify the full receiving address before sending (not just the first/last few characters — clipboard malware can swap addresses)
- Start with a small test transaction before sending large amounts
- Use address book/whitelisting features on exchanges when available
- Review all token approval transactions carefully before signing — revoke unused approvals periodically using Revoke.cash

<!-- Source: https://trustwallet.com/blog/security/crypto-safety-2025-7-easy-ways-to-avoid-hacks-and-scams -->
<!-- Source: https://nftevening.com/how-to-secure-your-cryptocurrency/ -->

### 1.2 Trading Safety

- **Never invest more than you can afford to lose**: Crypto markets are volatile. Meme coins and new tokens carry near-100% loss risk.
- **Set stop-losses**: Use stop-loss orders to limit downside, especially on leveraged positions.
- **Diversify**: Don't put everything into one token, protocol, or blockchain.
- **Avoid leverage as a beginner**: Leveraged trading amplifies losses. Most retail leveraged traders lose money.
- **Don't chase pumps**: If a token has already gone up 10x-100x, the risk/reward ratio heavily favors the downside. The people promoting it likely already bought at much lower prices.
- **Verify before you ape**: 30 seconds of due diligence can save you from a rug pull. Check RugCheck, Token Sniffer, or GoPlus before buying any new token.

### 1.3 Social Engineering Awareness

- **Nobody legitimate will DM you first**: Real project teams, exchange support, and crypto influencers will never DM you asking for funds, seed phrases, or wallet connections.
- **"Double your crypto" is always a scam**: No legitimate entity offers to multiply your holdings by sending them to a wallet.
- **Fake customer support**: Scammers create fake support accounts on Telegram and X/Twitter. Always go through official channels listed on the project's verified website.
- **Deepfake video scams**: AI-generated videos of celebrities and crypto figures promoting tokens are increasingly common. Verify through official social media accounts.
- **Romance scams ("pig butchering")**: Scammers build romantic relationships over weeks/months, then introduce a "crypto investment opportunity." This is the most financially devastating scam type per victim.

<!-- Source: https://sumsub.com/blog/crypto-scams-you-should-be-aware-of/ -->
<!-- Source: https://coinledger.io/learn/how-to-avoid-crypto-scam -->

### 1.4 Operational Security

- **Use unique passwords for every crypto account**: A password manager (1Password, Bitwarden) is essential.
- **Separate email for crypto**: Use a dedicated email address for exchange accounts, not your primary personal email.
- **Be cautious with browser extensions**: Malicious extensions can read clipboard data, modify web pages, or steal wallet data.
- **Keep software updated**: Wallet apps, browser extensions, and operating systems should always be on the latest version.
- **Avoid public WiFi for crypto transactions**: Use a VPN if you must access crypto accounts on public networks.
- **Beware of airdrop claims**: Most unsolicited airdrop tokens in your wallet are phishing attempts. Interacting with them (trying to sell or approve) can drain your wallet. Ignore tokens you didn't expect to receive.

---

## Section 2: How to Verify a Project Before Investing

### Step 1: Check the Team

- Are team members publicly identified with real names and verifiable backgrounds?
- Do they have LinkedIn profiles with credible work history?
- Have they built successful projects before?
- Can you find independent references (conference talks, interviews, code contributions)?
- **Red Flag**: Completely anonymous team with no track record. (Note: Pseudonymous teams with proven track records, like Bitcoin's Satoshi, are different from anonymous teams with zero history.)

### Step 2: Read the Documentation

- Does a whitepaper or technical documentation exist?
- Is it original (not copy-pasted from another project)?
- Does it explain the technology in detail, or is it just marketing fluff?
- Are tokenomics clearly defined with vesting schedules?
- **Red Flag**: No whitepaper, or a whitepaper that's just buzzwords without substance.

### Step 3: Verify the Smart Contract

- Is the contract source code verified on a block explorer (Etherscan, Solscan)?
- Has it been audited by a reputable firm? (CertiK, Trail of Bits, OpenZeppelin, Halborn, OtterSec)
- Is the audit report publicly available and recent?
- Check the contract on RugCheck (Solana) or Token Sniffer (EVM chains):
  - Mint authority renounced?
  - Freeze authority disabled?
  - Liquidity locked? For how long?
  - Hidden owner functions?
- **Red Flag**: Unverified source code, no audit, mint authority active.

### Step 4: Analyze Token Distribution

- Use Bubblemaps or block explorers to check holder distribution
- What percentage does the team hold? (Healthy: <15% with vesting. Unhealthy: >30% unlocked.)
- What percentage do the top 10 wallets hold? (Healthy: <30%. Dangerous: >50%.)
- Are team tokens locked with a vesting schedule?
- Is liquidity locked? Verify on-chain, not just the project's claims.
- **Red Flag**: Top 10 wallets hold >50% of supply. No vesting.

### Step 5: Evaluate Liquidity

- What is the liquidity-to-market-cap ratio? (Healthy: >10%. Dangerous: <2%.)
- Is liquidity locked? On which platform? For how long?
- Can you actually sell the token? Simulate a sell on a DEX before buying.
- **Red Flag**: Locked liquidity <30 days, or no lock at all.

### Step 6: Check Social Presence

- Does the project have an active community (Discord, Telegram, X/Twitter)?
- Are followers/members real or purchased? (Check engagement ratios.)
- Is the GitHub active with recent commits from multiple developers?
- Are there independent discussions about the project (not just paid promotions)?
- **Red Flag**: Fake followers, paid influencer promotions only, no GitHub activity.

### Step 7: Look for Independent Validation

- Is the token listed on CoinGecko or CoinMarketCap?
- Are there reviews from independent crypto analysts?
- Has the project been covered by reputable crypto media?
- Is there a working product, or just a roadmap?
- **Red Flag**: No independent coverage, no working product, only hype.

---

## Section 3: Red Flag Checklist (10-Point)

Rate each factor. If 3 or more red flags are present, the risk is very high. If 5 or more, avoid the project entirely.

| # | Red Flag | What to Check |
|---|----------|---------------|
| 1 | **Anonymous team, no track record** | LinkedIn, GitHub, conference history. Not pseudonymous-with-reputation — truly unknown. |
| 2 | **Unverified or unaudited contract** | Block explorer verification status. Presence of audit report from reputable firm. |
| 3 | **Mint authority not renounced** | RugCheck, SolSniffer, Token Sniffer. Can the deployer create unlimited new tokens? |
| 4 | **Liquidity not locked or <30 day lock** | Check lock contract on-chain (not just team's claims). Verify on Team.Finance/Unicrypt. |
| 5 | **Top 10 wallets hold >50% of supply** | Bubblemaps, block explorer, DEXTools holder analysis. |
| 6 | **Unrealistic return promises** | "100x guaranteed," double-digit daily APY, "risk-free" claims. No legitimate investment is risk-free. |
| 7 | **No working product** | Is there a live dApp? A working MVP? Or just a website with a roadmap? |
| 8 | **Paid influencer hype as primary marketing** | Influencers promoting without disclosing payment. No organic community growth. |
| 9 | **Honeypot indicators** | Cannot simulate a sell transaction. Hidden sell restrictions. Use GoPlus or Honeypot.is to test. |
| 10 | **Recently created token with no history** | Token deployed <7 days ago, website domain registered <30 days ago, social accounts <30 days old. |

### Quick Decision Framework

```
0-2 red flags: Proceed with caution, normal due diligence
3-4 red flags: HIGH RISK — invest only what you're prepared to lose 100%
5-7 red flags: VERY HIGH RISK — strong indicators of scam
8-10 red flags: ALMOST CERTAINLY A SCAM — do not invest
```

---

## Section 4: What to Do If You've Been Scammed

### Immediate Steps (First 24 Hours)

1. **Stop all further transactions**: Do not send more funds. Do not interact with the scammer's contract or wallet.

2. **Revoke token approvals**: Use Revoke.cash to revoke any approvals you granted to the scammer's contract. This prevents further draining.

3. **Move remaining funds**: Transfer any remaining funds from the compromised wallet to a new, secure wallet. Consider the compromised wallet permanently unsafe.

4. **Document everything**:
   - Screenshots of all communications with the scammer
   - Transaction hashes (IDs) of all transactions
   - Wallet addresses involved (yours and the scammer's)
   - Website URLs, social media profiles, contract addresses
   - Timeline of events
   - Amount lost in both crypto and USD value at time of loss

5. **Do NOT pay anyone who claims they can "recover" your funds**: Recovery scams are extremely common. They target known scam victims, promising to retrieve stolen funds for an upfront fee, then disappear with that fee too.

### Reporting

6. **Report to law enforcement**:
   - **United States**: File with FBI's Internet Crime Complaint Center (IC3) at ic3.gov
   - **United States**: Report to the FTC at reportfraud.ftc.gov
   - **United States**: Report to the SEC if securities fraud is suspected at sec.gov/tcr
   - **United Kingdom**: Report to Action Fraud at actionfraud.police.uk
   - **Europe**: Report to local cyber crime units (varies by country)
   - **Global**: File a report with local police — even if they can't act immediately, it creates a record

7. **Report to the platform**:
   - If the scam occurred on a centralized exchange, contact their fraud/compliance team immediately
   - If on a DEX, report the contract address to the chain's scam databases
   - Report phishing sites to Google Safe Browsing and PhishTank

8. **Report to blockchain analytics firms**:
   - Report the scammer's wallet to Chainalysis, Elliptic, or TRM Labs through their public reporting forms
   - These firms work with law enforcement and can flag/trace stolen funds

### Recovery Possibilities (Realistic Assessment)

**When recovery is possible:**
- Funds were sent to a centralized exchange (exchange can freeze the account — time-sensitive)
- Large-scale rug pull with identifiable team (law enforcement and class action lawsuits)
- Bug bounty/whitehat situations where the exploiter returns funds (has happened: Euler Finance returned $197M)

**When recovery is unlikely:**
- Funds sent to a mixer (Tornado Cash, etc.)
- Small individual losses (<$10K) — law enforcement prioritizes larger cases
- Fully anonymous scammer with no traceable identity
- Funds bridged across multiple chains and mixed

**Tax Implications:**
- In many jurisdictions (US, UK, etc.), scam losses may be tax-deductible as theft losses
- Consult a crypto-aware tax professional
- Document the loss thoroughly for tax purposes

<!-- Source: https://trustwallet.com/blog/security/crypto-safety-2025-7-easy-ways-to-avoid-hacks-and-scams -->
<!-- Source: https://coinledger.io/learn/how-to-avoid-crypto-scam -->

---

## Section 5: Common Scam Types (2024-2025)

### 5.1 Rug Pulls
- **How it works**: Developers create a token, build hype, attract investors, then drain liquidity and disappear.
- **2024-2025 scale**: 98.6% of tokens on Pump.fun were rug pulls. Q1 2025 saw $6 billion in rug pull losses.
- **How to avoid**: Use the 10-point checklist above. Check liquidity locks, holder distribution, and contract authority.

### 5.2 Phishing / Wallet Drainers
- **How it works**: Fake websites mimicking legitimate dApps trick users into connecting wallets and signing malicious approval transactions.
- **2024 scale**: $494 million stolen from 332,000 wallets. Inferno Drainer operated 16,000+ phishing domains impersonating 100+ crypto brands.
- **How to avoid**: Always verify URLs manually. Bookmark legitimate dApp URLs. Never click links from DMs or emails. Use hardware wallets that show transaction details on the device screen.

### 5.3 Pig Butchering (Romance Scams)
- **How it works**: Scammer builds a fake romantic relationship over weeks/months, then convinces victim to "invest" in a fake crypto platform. Victim sees fake profits on the platform, invests more, then platform disappears.
- **Scale**: FBI reported $3.96 billion in losses from investment fraud (primarily pig butchering) in 2023.
- **How to avoid**: Be suspicious of unsolicited romantic contacts who bring up crypto investment. Never invest through platforms recommended by someone you haven't met in person.

### 5.4 Fake Exchange/Wallet Apps
- **How it works**: Malicious apps mimicking real exchanges or wallets steal login credentials and private keys.
- **How to avoid**: Only download apps from official app stores. Verify the developer name matches the official company. Check download counts (real Coinbase app has millions of downloads; fakes have hundreds).

### 5.5 Airdrop Scams
- **How it works**: Unsolicited tokens appear in your wallet. Interacting with them (trying to sell or approve) triggers a malicious smart contract that drains your wallet.
- **How to avoid**: Ignore tokens you didn't expect. Never try to sell unknown tokens. Don't interact with contracts for tokens you didn't request.

### 5.6 Impersonation Scams
- **How it works**: Scammers create accounts mimicking exchange support staff, project founders, or crypto influencers. They contact victims offering "help" or "opportunities."
- **2025 trend**: AI deepfake videos of Elon Musk, Vitalik Buterin, and other figures used to promote scam tokens.
- **How to avoid**: Verify through official channels. No legitimate support team will DM you first. No real person is giving away free crypto.

---

## Section 6: Trusted Resources for Research

### Token Analysis Tools

| Tool | What It Does | URL |
|------|-------------|-----|
| RugCheck | Solana token risk analysis — checks mint/freeze authority, liquidity, holders | rugcheck.xyz |
| Token Sniffer | Multi-chain scam detection — identifies contract red flags | tokensniffer.com |
| GoPlus Security | Honeypot detection, malicious contract identification | gopluslabs.io |
| DEXTools | Real-time trading data, liquidity analysis, holder distribution | dextools.io |
| DexScreener | Real-time price charts, trading pairs, liquidity metrics | dexscreener.com |
| Bubblemaps | Visual token holder concentration analysis | bubblemaps.io |
| Honeypot.is | Simulates buy/sell to detect honeypot contracts | honeypot.is |

### On-Chain Analysis

| Tool | What It Does | URL |
|------|-------------|-----|
| Etherscan | Ethereum block explorer — verify contracts, check transactions | etherscan.io |
| Solscan | Solana block explorer — verify programs, check accounts | solscan.io |
| Arkham Intelligence | Wallet clustering, entity identification, fund tracing | arkhamintelligence.com |
| Nansen | Portfolio tracking, wallet labeling, smart money tracking | nansen.ai |
| Revoke.cash | Review and revoke token approvals you've granted | revoke.cash |

### Security Information

| Resource | What It Provides | URL |
|----------|-----------------|-----|
| Rekt News | DeFi exploit postmortems and analysis | rekt.news |
| DeFi Llama Hacks | Comprehensive database of DeFi hacks and amounts | defillama.com/hacks |
| Chainalysis Blog | Market manipulation research, crime reports | chainalysis.com/blog |
| SlowMist | Security alerts, hack analysis, vulnerability reports | slowmist.com |
| OWASP Smart Contract Top 10 | Industry standard vulnerability classification | scs.owasp.org/sctop10 |

### Reporting Scams

| Agency/Platform | How to Report | URL |
|----------------|---------------|-----|
| FBI IC3 | File internet crime complaint (US) | ic3.gov |
| FTC | Report fraud (US) | reportfraud.ftc.gov |
| SEC | Report securities fraud (US) | sec.gov/tcr |
| Action Fraud | Report cyber crime (UK) | actionfraud.police.uk |
| Google Safe Browsing | Report phishing websites | safebrowsing.google.com/safebrowsing/report_phish |
| PhishTank | Community phishing database | phishtank.org |

### News and Analysis

| Source | Focus | URL |
|--------|-------|-----|
| The Block | Crypto news and data | theblock.co |
| DL News | DeFi investigative reporting | dlnews.com |
| CoinDesk | Crypto industry news | coindesk.com |
| Protos | Crypto investigations | protos.com |
| Decrypt | Crypto news and education | decrypt.co |

---

## Section 7: Quick Reference — Emergency Actions

### "I Think I'm Being Scammed Right Now"

1. STOP all transactions immediately
2. Do NOT send any more funds
3. Do NOT share your seed phrase with anyone (not even "support")
4. Disconnect your wallet from any suspicious site
5. Revoke approvals at revoke.cash
6. Move funds to a new wallet if your current wallet may be compromised

### "I Just Bought a Token and I'm Not Sure If It's Safe"

1. Check the token on RugCheck (Solana) or Token Sniffer (EVM)
2. Try to simulate a sell transaction (can you actually sell?)
3. Check holder distribution (are top wallets holding >50%?)
4. Check if liquidity is locked and for how long
5. If multiple red flags are present, consider selling immediately even at a loss

### "Someone Is Asking for My Seed Phrase"

- **This is ALWAYS a scam. No exceptions.**
- No legitimate exchange, wallet provider, support team, or project will ever ask for your seed phrase
- Your seed phrase gives complete control of all funds in your wallet
- If you've already shared it, immediately create a new wallet and move all funds
