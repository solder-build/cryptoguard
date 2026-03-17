# Smart Contract Vulnerabilities Knowledge Base

## Overview

This knowledge base catalogs real smart contract vulnerability patterns, exploit case studies, and Solana-specific risks. All data is sourced from verified security reports, postmortems, and the OWASP Smart Contract Top 10 (2025). Total losses from smart contract exploits exceeded $3.4 billion in 2025 alone.

---

## Section 1: Common Vulnerability Patterns

### 1.1 Access Control Vulnerabilities

**OWASP SC01:2025 — $953.2M in losses**

Access control flaws occur when smart contracts fail to properly restrict who can call sensitive functions (minting, pausing, upgrading, withdrawing funds).

**Patterns:**
- Missing `onlyOwner` or role-based access modifiers on critical functions
- Default visibility set to `public` when it should be `internal` or `private`
- Hardcoded admin addresses that can be front-run during deployment
- Missing checks on `msg.sender` or `tx.origin` misuse
- Lack of multi-sig requirements for high-value operations

**Detection Signals:**
- Functions that transfer funds or modify state without access restrictions
- Use of `tx.origin` for authentication (vulnerable to phishing attacks)
- Single externally-owned account (EOA) as sole admin without timelock

**Mitigation:**
- Use OpenZeppelin's `AccessControl` or `Ownable` patterns
- Implement multi-sig wallets for admin functions
- Add timelocks to sensitive operations
- Use role-based access control (RBAC) rather than single-owner patterns

<!-- Source: https://owasp.org/www-project-smart-contract-top-10/ -->
<!-- Source: https://scs.owasp.org/sctop10/ -->

### 1.2 Reentrancy Attacks

**OWASP SC03:2025 — $35.7M in losses (22 incidents in 2024)**

Reentrancy occurs when a contract makes an external call before updating its internal state, allowing the called contract to re-enter the calling function and exploit the stale state.

**Types of Reentrancy:**

1. **Single-function reentrancy**: Attacker repeatedly calls the same vulnerable function before state updates.
   ```
   // VULNERABLE: State update after external call
   function withdraw(uint amount) public {
       require(balances[msg.sender] >= amount);
       (bool success, ) = msg.sender.call{value: amount}("");  // External call
       balances[msg.sender] -= amount;  // State update AFTER call — vulnerable
   }
   ```

2. **Cross-function reentrancy**: Exploiting vulnerabilities across multiple functions that share state variables. Function A makes an external call, and the attacker re-enters via Function B which reads the stale state.

3. **Cross-contract reentrancy**: Two contracts failing to update immediately before a cross-contract call, allowing an attacker to exploit state inconsistency between contracts.

4. **Read-only reentrancy**: Re-entering a view function during execution causes inconsistent state values to be returned, affecting dependent calculations in other contracts. This is particularly insidious because view functions are often assumed to be safe.

**Detection Signals:**
- External calls (`.call()`, `.transfer()`, `.send()`) before state modifications
- Lack of reentrancy guards (mutex/lock patterns)
- Functions that interact with untrusted external contracts

**Mitigation:**
- Follow Checks-Effects-Interactions pattern (validate, update state, then interact)
- Use OpenZeppelin's `ReentrancyGuard` modifier
- Avoid `.call()` with arbitrary data when possible

<!-- Source: https://hacken.io/discover/smart-contract-vulnerabilities/ -->
<!-- Source: https://www.nethermind.io/blog/smart-contract-vulnerabilities-and-mitigation-strategies -->

### 1.3 Logic Errors

**OWASP SC02:2025 — $63.8M in losses**

Business logic flaws where the contract behaves differently than intended, even though the code compiles and runs without technical errors.

**Patterns:**
- Incorrect reward calculation formulas
- Off-by-one errors in loop bounds or array indexing
- Wrong order of operations in mathematical expressions
- Missing edge case handling (zero amounts, empty arrays, overflow conditions)
- Incorrect assumptions about token decimals (18 vs 6 vs 8)
- Rounding errors that accumulate over many transactions

**Detection Signals:**
- Complex mathematical operations without formal verification
- Missing unit tests for edge cases
- Functions that handle multiple token types without decimal normalization

### 1.4 Integer Overflow/Underflow

Previously a top vulnerability before Solidity 0.8.0 introduced automatic overflow checks. Still relevant for:
- Contracts compiled with Solidity <0.8.0
- Code using `unchecked` blocks for gas optimization
- Assembly/Yul code that bypasses Solidity safety checks
- Non-EVM chains where overflow protection is not automatic

**Impact**: Attacker can manipulate balances, mint unlimited tokens, or bypass balance checks.

### 1.5 Flash Loan Attack Vectors

**OWASP SC07:2025 — $33.8M in losses**

Flash loans allow borrowing large sums without collateral within a single transaction. Attackers combine flash loans with other vulnerabilities to amplify exploits.

**Common Attack Flow:**
1. Borrow massive amount via flash loan (e.g., $100M in ETH)
2. Use borrowed funds to manipulate a price oracle (e.g., swap heavily on a low-liquidity pool)
3. Exploit the manipulated price in a DeFi protocol (borrow against inflated collateral, drain lending pools)
4. Repay flash loan with profit
5. Entire attack completes in one transaction block

**Attack Combinations:**
- Flash loan + price oracle manipulation (most common)
- Flash loan + reentrancy
- Flash loan + governance manipulation (acquire enough tokens to pass a malicious proposal)
- Flash loan + liquidation exploitation

**Detection Signals:**
- Protocols that rely on spot prices from a single DEX pool
- Low-liquidity oracle sources vulnerable to manipulation
- Governance systems with no timelock or minimum voting period

**Mitigation:**
- Use time-weighted average price (TWAP) oracles
- Use Chainlink or other decentralized oracle networks
- Implement minimum liquidity requirements for oracle sources
- Add flash loan guards that detect same-block price changes

<!-- Source: https://scs.owasp.org/sctop10/SC07-FlashLoanAttacks/ -->
<!-- Source: https://hacken.io/discover/flash-loan-attacks/ -->

### 1.6 Price Oracle Manipulation

**OWASP SC06:2025 — $8.8M in losses ($52M in 2024)**

Price oracle manipulation was the second most damaging attack vector in 2024, accounting for $52 million in losses across 37 incidents.

**Patterns:**
- Spot price dependency: Using current pool price instead of TWAP
- Single oracle source: Relying on one DEX pool for price data
- Stale price data: Not checking oracle freshness/heartbeat
- Missing circuit breakers: No maximum price deviation checks

**Real-World Impact:**
- Attacker manipulates price on a low-liquidity pool
- DeFi protocol reads the manipulated price as "real"
- Attacker borrows against inflated collateral or triggers unfair liquidations

### 1.7 Front-Running Vulnerabilities

Transactions on public blockchains are visible in the mempool before execution. Attackers (MEV bots) can:

**Types:**
- **Sandwich attacks**: Place a buy order before and a sell order after a victim's trade, profiting from the price impact
- **Transaction ordering attacks**: Reorder transactions to extract value
- **Backrunning**: Execute immediately after a profitable transaction (e.g., after a large swap, arbitrage the resulting price difference)

**Detection Signals:**
- Functions that execute large swaps without slippage protection
- Missing `deadline` parameters in swap functions
- Protocols that don't use commit-reveal schemes for sensitive operations

### 1.8 Honeypot Contract Patterns

Honeypot contracts are designed to look legitimate but prevent users from selling or withdrawing their tokens.

**Common Honeypot Mechanisms:**
- **Hidden transfer restrictions**: `_transfer()` function contains a check that only allows certain addresses to sell
- **Dynamic tax manipulation**: Buy tax starts at 0-5%, then owner changes sell tax to 90-100%
- **Blacklist after buy**: Contract automatically blacklists buyers from selling
- **Max wallet limits on sells**: Buyers can purchase but sells are capped at tiny amounts
- **Time-locked sells**: Contract requires holding for an impossibly long period before selling
- **Proxy redirect**: Contract appears clean but delegates to a malicious implementation contract

**Detection Methods:**
- Simulate a buy-then-sell transaction before investing (GoPlus, Honeypot.is)
- Check for `blacklist()`, `setFee()`, `setMaxTx()` functions in contract
- Look for upgradeable proxy patterns without verified implementation contracts
- Check if trading is restricted to specific addresses

### 1.9 Hidden Mint Functions

**Patterns:**
- `mint()` function callable by owner without cap
- Internal mint function hidden behind obfuscated code
- Proxy contracts where implementation can be swapped to add minting
- "Rebasing" mechanisms that inflate supply to specific wallets

**Impact**: Owner can mint unlimited tokens and sell them, diluting all existing holders to zero.

### 1.10 Proxy Upgrade Risks

Upgradeable contracts (ERC-1967, UUPS, Transparent Proxy) allow developers to change contract logic after deployment.

**Risks:**
- Owner can replace a legitimate implementation with a malicious one
- Storage collision between proxy and implementation contracts
- Missing initialization in new implementation contracts
- No timelock on upgrades (instant malicious upgrade possible)

**Mitigation:**
- Timelock on all upgrade operations (minimum 24-48 hours)
- Multi-sig requirement for upgrades
- Transparent upgrade process with community notification
- Formal verification of upgrade compatibility

---

## Section 2: Real Exploit Case Studies

### Case 1: Bybit Hack — February 21, 2025

- **Amount Lost**: $1.46 billion (401,000 ETH)
- **Vulnerability Type**: Supply chain attack on wallet infrastructure (Safe{Wallet})
- **Attack Vector**: North Korean Lazarus Group (TradeTraitor) compromised a macOS workstation belonging to a Safe{Wallet} developer on February 4, 2025. Attackers embedded malicious JavaScript into Safe's UI library via a Docker project that initiated traffic to `getstockprice[.]com`. The rogue script altered what users saw when authorizing transactions, redirecting funds to attacker-controlled wallets.
- **Key Lesson**: Even legitimate wallet providers can be compromised. Supply chain security is critical. Multi-signature doesn't help if the signing interface itself is compromised.
- **Attribution**: FBI attributed to DPRK's Lazarus Group. $2.02 billion stolen by DPRK in 2025 total.

<!-- Source: https://www.sygnia.co/blog/sygnia-investigation-bybit-hack/ -->
<!-- Source: https://techpoint.africa/guide/bybit-hack-2025/ -->

### Case 2: DMM Bitcoin Exchange — 2024

- **Amount Lost**: $300 million
- **Vulnerability Type**: Private key compromise
- **Attack Vector**: Private keys to exchange hot wallets were stolen, allowing direct fund withdrawal.
- **Key Lesson**: Centralized key management is a single point of failure.

<!-- Source: https://deepstrike.io/blog/crypto-hacking-incidents-statistics-2025-losses-trends -->

### Case 3: WazirX — July 2024

- **Amount Lost**: $230 million
- **Vulnerability Type**: Multi-sig wallet compromise
- **Attack Vector**: Attackers compromised the multi-signature wallet infrastructure, bypassing the multi-sig security model.
- **Key Lesson**: Multi-sig implementation details matter. The signing process, not just the number of signers, must be secured.

<!-- Source: https://deepstrike.io/blog/crypto-hacking-incidents-statistics-2025-losses-trends -->

### Case 4: Chris Larsen Wallet — 2024

- **Amount Lost**: $112 million
- **Vulnerability Type**: Private key compromise
- **Attack Vector**: Personal wallet of Ripple co-founder compromised, funds drained directly.
- **Key Lesson**: High-value individuals are prime targets. Hardware wallets and operational security are essential.

<!-- Source: https://deepstrike.io/blog/crypto-hacking-incidents-statistics-2025-losses-trends -->

### Case 5: Radiant Capital — October 2024

- **Amount Lost**: $50 million
- **Vulnerability Type**: Device compromise / supply chain attack
- **Attack Vector**: Similar methodology to the Bybit heist — developer devices were compromised, allowing attackers to manipulate transaction signing. The attack targeted the multi-sig signing process itself.
- **Key Lesson**: Pattern of nation-state actors targeting the signing infrastructure rather than the smart contracts themselves.

<!-- Source: https://protos.com/2025s-biggest-crypto-hacks-from-exchange-breaches-to-defi-exploits/ -->

### Case 6: Wormhole Bridge — February 2022 (Reference Case)

- **Amount Lost**: $320 million (120,000 wETH)
- **Vulnerability Type**: Signature verification bypass
- **Attack Vector**: Attacker exploited a vulnerability in the Wormhole bridge's signature verification, minting 120,000 wETH on Solana without depositing corresponding ETH on Ethereum.
- **Key Lesson**: Cross-chain bridges are high-value targets. Signature verification must be bulletproof. Jump Trading covered the losses.

<!-- Source: https://defi-planet.com/2025/05/the-biggest-hacks-and-exploits-in-defi-history-what-we-can-learn-from-them/ -->

### Case 7: Euler Finance — March 2023 (Reference Case)

- **Amount Lost**: $197 million
- **Vulnerability Type**: Flash loan + donation attack
- **Attack Vector**: Attacker used flash loans to manipulate the protocol's accounting, exploiting a logic error in how the protocol handled token donations to lending pools.
- **Key Lesson**: Complex DeFi interactions create unexpected attack surfaces. $197M was later returned after negotiation.

### Case 8: Mango Markets — October 2022 (Reference Case)

- **Amount Lost**: $114 million
- **Vulnerability Type**: Price oracle manipulation
- **Attack Vector**: Avraham Eisenberg manipulated the price of MNGO token on the Mango Markets DEX by artificially inflating it, then borrowed against the inflated collateral. He was later convicted in April 2024 — the first criminal prosecution for DeFi market manipulation.
- **Key Lesson**: Price oracle manipulation on low-liquidity markets is a persistent threat. This case set legal precedent for DeFi market manipulation being a crime.

<!-- Source: https://www.arnoldporter.com/en/perspectives/blogs/enforcement-edge/2024/10/remaking-the-classics -->

### Case 9: Ronin Bridge (Axie Infinity) — March 2022 (Reference Case)

- **Amount Lost**: $625 million
- **Vulnerability Type**: Validator key compromise
- **Attack Vector**: North Korean Lazarus Group compromised 5 of 9 validator keys for the Ronin bridge through social engineering (fake job interview targeting a senior engineer). This gave them majority control to authorize withdrawals.
- **Key Lesson**: Social engineering remains the most effective attack vector. Validator sets must be diverse and independently secured.

### Case 10: Poly Network — August 2021 (Reference Case)

- **Amount Lost**: $611 million (returned)
- **Vulnerability Type**: Cross-chain message verification flaw
- **Attack Vector**: Attacker exploited a flaw in cross-chain message verification to forge withdrawal transactions. The attacker later returned all funds, claiming it was done to expose the vulnerability.

### Case 11: Inferno Drainer — 2023-2025

- **Amount Lost**: $81 million in 9 months; $494 million total via wallet drainer ecosystem in 2024
- **Vulnerability Type**: Phishing / social engineering (not smart contract vulnerability per se)
- **Attack Vector**: Spoofed Web3 protocols (Seaport, WalletConnect, Coinbase) via malicious scripts on 16,000+ phishing domains impersonating 100+ crypto brands. Users connected wallets thinking they were claiming airdrops but signed malicious approval transactions.
- **Key Lesson**: The biggest threat to users is not smart contract bugs but phishing attacks that trick users into signing malicious transactions. 332,000 wallet addresses victimized in 2024.

<!-- Source: https://www.group-ib.com/blog/inferno-drainer/ -->
<!-- Source: https://moonlock.com/wallet-drainer-crypto-theft-2024 -->

### Case 12: Coinbase Social Engineering — 2025

- **Amount Lost**: Estimated $300 million+ in customer losses
- **Vulnerability Type**: Insider threat / social engineering
- **Attack Vector**: Attackers bribed Coinbase customer support contractors to access internal systems and customer data, then used the information for targeted phishing attacks.
- **Key Lesson**: Insider threats and social engineering bypass all technical security measures.

<!-- Source: https://finance.yahoo.com/news/bybit-coinbase-2025s-biggest-crypto-200102196.html -->

---

## Section 3: Solana-Specific Security Risks

### 3.1 Program Upgrade Authority

Solana programs (smart contracts) can be deployed as upgradeable by default. The upgrade authority is a single keypair that can replace the entire program logic.

**Risks:**
- Owner can change program behavior at any time with no on-chain governance
- A compromised upgrade authority key means complete program takeover
- No built-in timelock mechanism for upgrades
- Users interacting with an upgradeable program are trusting the upgrade authority completely

**Detection:**
- Check if the program's upgrade authority is set to `None` (immutable/frozen)
- If upgrade authority exists, verify it's a multi-sig or governance program, not a single EOA
- Use `solana program show <program_id>` to check upgrade authority status

**Mitigation:**
- Freeze programs after deployment when possible (`solana program set-upgrade-authority --final`)
- Use multi-sig (Squads Protocol) as upgrade authority
- Implement governance-controlled upgrades with timelock

<!-- Source: https://www.helius.dev/blog/a-hitchhikers-guide-to-solana-program-security -->

### 3.2 PDA (Program Derived Address) Misuse

PDAs are deterministic addresses derived from seeds and a program ID. They serve as program-controlled accounts without private keys.

**Vulnerability Patterns:**

1. **PDA Collision**: An attacker crafts a PDA that collides with an existing one by manipulating seed inputs, potentially hijacking program-controlled accounts.

2. **Missing Bump Seed Validation**: PDAs are found using `find_program_address` which returns a canonical bump. If a program doesn't verify the bump, an attacker could use a different bump to create a different valid PDA.

3. **Insufficient Seed Uniqueness**: If PDA seeds aren't unique enough, different logical entities could map to the same PDA, causing state corruption.

4. **PDA Spoofing**: Attacker creates an account at a PDA-like address using a different program, then passes it to a program that doesn't verify the PDA's owning program.

**Mitigation:**
- Always verify PDA derivation on-chain using `Pubkey::find_program_address()` or Anchor's `seeds` constraint
- Include user-specific data in PDA seeds to prevent collisions
- Validate the bump seed matches the canonical bump
- Check account ownership matches expected program

<!-- Source: https://cantina.xyz/blog/securing-solana-a-developers-guide -->

### 3.3 Cross-Program Invocation (CPI) Vulnerabilities

CPIs allow Solana programs to call other programs. This creates several attack surfaces.

**Vulnerability Patterns:**

1. **Arbitrary CPI**: Program invokes another program without verifying the target program ID. If the callee is determined by user input, an attacker can point it to a malicious program.

2. **Signer Account Forwarding**: When a user signs a transaction, that signer privilege is retained for the entire transaction and forwarded through CPIs. A malicious program called via CPI inherits the user's signer authority.

3. **Missing Program ID Checks**: Not verifying that the invoked program is the expected one (e.g., calling what should be the SPL Token program but could be a malicious substitute).

4. **CPI Re-entrancy**: A called program can call back into the calling program before the first invocation completes, similar to EVM reentrancy but within Solana's account model.

5. **Account Deserialization After CPI**: In Anchor, deserialized accounts are NOT automatically updated after a CPI. If a CPI modifies an account's data, the calling program still sees stale data unless it manually re-reads the account.

**Mitigation:**
- Always hardcode or validate the program ID for CPI targets
- Use Anchor's `Program<'info, T>` type to enforce program ID checks
- Re-read account data after CPIs that modify shared state
- Be cautious about forwarding signer authority to untrusted programs

<!-- Source: https://blog.asymmetric.re/invocation-security-navigating-vulnerabilities-in-solana-cpis/ -->
<!-- Source: https://www.helius.dev/blog/a-hitchhikers-guide-to-solana-program-security -->

### 3.4 Account Validation Issues

Solana's account model requires programs to manually validate all accounts passed in an instruction.

**Vulnerability Patterns:**

1. **Missing Owner Check**: Not verifying that an account is owned by the expected program. An attacker can pass a fake account with fabricated data.

2. **Missing Signer Check**: Not verifying that a required account has actually signed the transaction.

3. **Missing Account Type Check**: Not distinguishing between different account types (e.g., treating a user account as a vault account).

4. **Account Data Matching**: Not verifying that account data matches expected values (e.g., a token account's mint matches the expected mint).

5. **Duplicate Accounts**: Not checking that the same account isn't passed twice for different parameters, which can cause double-counting.

**Mitigation (Anchor Framework):**
- Use Anchor's account constraints: `#[account(has_one = authority)]`, `#[account(constraint = ...)]`
- Use typed accounts: `Account<'info, TokenAccount>` instead of raw `AccountInfo`
- Add explicit checks: `#[account(owner = program_id)]`
- Use `#[account(signer)]` for accounts that must sign

### 3.5 Solana-Specific Attack Patterns

**Closable Account Re-initialization:**
- If a program closes an account (zeroes data, transfers lamports), another transaction in the same slot could re-initialize it before the account is garbage collected.
- Mitigation: Write a "closed" discriminator to the account data, check for it on initialization.

**Missing Rent Exemption Checks:**
- Accounts below the rent-exempt threshold are garbage collected. An attacker could create an account with just enough lamports to pass initial checks, then let it get garbage collected, causing program errors.

**Instruction Ordering Attacks:**
- Unlike EVM where each transaction is atomic, Solana transactions can contain multiple instructions. An attacker can craft a transaction where instruction ordering creates unexpected state.

<!-- Source: https://github.com/slowmist/solana-smart-contract-security-best-practices -->
<!-- Source: https://dedaub.com/blog/ethereum-developers-on-solana-common-mistakes/ -->

---

## Section 4: OWASP Smart Contract Top 10 (2025) Summary

| Rank | Vulnerability | Financial Impact | Key Risk |
|------|--------------|-----------------|----------|
| SC01 | Access Control | $953.2M | Unauthorized function calls |
| SC02 | Logic Errors | $63.8M | Incorrect business logic |
| SC03 | Reentrancy | $35.7M | State manipulation via callbacks |
| SC04 | Lack of Input Validation | $14.6M | Unvalidated parameters |
| SC05 | Oracle Manipulation | $8.8M | Price feed manipulation |
| SC06 | Unchecked External Calls | $550.7K | Silent failure of external calls |
| SC07 | Flash Loan Attacks | $33.8M | Uncollateralized loan exploits |
| SC08 | Integer Overflow/Underflow | — | Arithmetic boundary errors |
| SC09 | Insecure Randomness | — | Predictable random values |
| SC10 | Denial of Service | — | Contract becomes unusable |

<!-- Source: https://scs.owasp.org/sctop10/ -->
<!-- Source: https://www.resonance.security/blog-posts/owasp-sc-top-10-2025-breakdown-the-most-critical-smart-contract-risks-of-2025 -->

---

## Section 5: 2024-2025 Exploit Statistics

- **Total stolen in 2025**: $3.4 billion (Chainalysis estimate: $2.7 billion confirmed)
- **Largest single incident**: Bybit — $1.46 billion (February 2025)
- **DPRK (North Korea) total**: $2.02 billion stolen in 2025 ($681M more than 2024)
- **Top attack vectors in 2024**: Private key theft ($449M across 31 incidents), Price oracle manipulation ($52M across 37 incidents), Reentrancy ($47M across 22 incidents)
- **Input validation failures**: Account for 34.6% of direct contract exploitation cases
- **Q2 2025 breakdown by value**: Phishing ~49.3%, Code vulnerabilities ~29.4%, Other vectors ~21.3%
- **DEX exploit losses in 2025**: $3.1 billion in six months

<!-- Source: https://threesigma.xyz/blog/exploit/2024-defi-exploits-top-vulnerabilities -->
<!-- Source: https://deepstrike.io/blog/crypto-hacking-incidents-statistics-2025-losses-trends -->
<!-- Source: https://www.theblock.co/post/382477/crypto-hack-2025-chainalysis -->

---

## Section 6: Security Analysis Checklist for Agents

When analyzing a smart contract, CryptoGuard agents should check:

**EVM (Ethereum/BSC/Polygon/etc.):**
1. Is the contract source code verified on the block explorer?
2. Has the contract been audited by a reputable firm? (CertiK, Trail of Bits, OpenZeppelin, Halborn, Quantstamp)
3. Is the contract upgradeable? If so, who controls upgrades and is there a timelock?
4. Does the owner have excessive permissions (mint, pause, blacklist, fee manipulation)?
5. Are there reentrancy guards on functions that make external calls?
6. Does the contract use secure oracle sources (Chainlink, TWAP)?
7. Are there flash loan protections?
8. Is the contract a fork of a known protocol? If so, what was changed?

**Solana:**
1. Is the program upgrade authority renounced or controlled by multi-sig?
2. Is mint authority renounced?
3. Is freeze authority disabled?
4. Are all accounts properly validated (owner, signer, type checks)?
5. Are PDA seeds unique and bump seeds validated?
6. Are CPI targets verified (program ID checks)?
7. Are accounts re-read after CPIs that modify shared state?
8. Has the program been audited by a Solana-specialized firm? (Neodyme, OtterSec, Sec3, Halborn)
