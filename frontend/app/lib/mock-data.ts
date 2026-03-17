import { AnalysisResult, ChatMessage, RecentAnalysis } from "./types";

export const MOCK_ANALYSES: Record<string, AnalysisResult> = {
  safe: {
    query: "So11111111111111111111111111111111111111112",
    overallScore: 12,
    overallRisk: "SAFE",
    timestamp: new Date().toISOString(),
    agents: [
      {
        agent: "token",
        name: "Token Risk Analyzer",
        score: 8,
        riskLevel: "SAFE",
        summary:
          "This token demonstrates strong fundamental characteristics consistent with a well-established, legitimate cryptocurrency project.",
        findings: [
          "Market cap exceeds $30B with deep liquidity across 50+ exchanges",
          "Token distribution is well-diversified — top 10 holders control <15%",
          "Consistent trading volume averaging $2.1B daily over 90 days",
          "No unusual mint authority or freeze authority detected",
          "Token has been active for 4+ years with stable growth trajectory",
        ],
        details:
          "The token exhibits all hallmarks of a mature, established cryptocurrency. Supply mechanics are transparent with a clear inflation schedule. Liquidity depth analysis shows healthy order books across major trading pairs. No signs of wash trading or artificial volume inflation detected in our analysis of on-chain transaction patterns.",
      },
      {
        agent: "contract",
        name: "Smart Contract Auditor",
        score: 10,
        riskLevel: "SAFE",
        summary:
          "The program has undergone multiple professional audits and demonstrates best-in-class security practices.",
        findings: [
          "Audited by Kudelski Security, Neodyme, and OtterSec",
          "Open-source codebase with active community review",
          "No known vulnerabilities in current deployed version",
          "Upgrade authority is governed by multisig with timelock",
          "Program follows Solana security best practices",
        ],
        details:
          "The on-chain program is the native SOL token wrapper, one of the most scrutinized programs in the Solana ecosystem. The code is open-source, has been formally verified, and undergoes continuous security review by the Solana Foundation and independent auditors. No privilege escalation vectors or reentrancy risks identified.",
      },
      {
        agent: "market",
        name: "Market Intelligence",
        score: 18,
        riskLevel: "SAFE",
        summary:
          "Strong market presence with legitimate community engagement and institutional adoption signals.",
        findings: [
          "Listed on all major exchanges including Coinbase, Binance, Kraken",
          "Active developer ecosystem with 2,500+ monthly active developers",
          "Institutional custody support from Fireblocks, BitGo, Anchorage",
          "Positive sentiment ratio of 78% across social platforms",
          "No coordinated shill campaigns or bot activity detected",
        ],
        details:
          "Market intelligence analysis reveals a healthy, organically grown ecosystem. Social media sentiment is predominantly positive with substantive technical discussions rather than hype-driven content. The project has strong institutional backing and regulatory engagement. No evidence of coordinated pump schemes, fake partnerships, or misleading marketing detected.",
      },
    ],
  },

  caution: {
    query: "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    overallScore: 42,
    overallRisk: "CAUTION",
    timestamp: new Date().toISOString(),
    agents: [
      {
        agent: "token",
        name: "Token Risk Analyzer",
        score: 38,
        riskLevel: "CAUTION",
        summary:
          "This token shows mixed signals — some legitimate characteristics but several risk factors that warrant caution.",
        findings: [
          "Market cap of $4.2M with moderate but inconsistent liquidity",
          "Top 5 wallets hold 34% of total supply — moderate concentration",
          "Token launched 3 months ago — limited track record",
          "Liquidity pool has $890K locked but only for 6 months",
          "Some large wallet movements detected in last 48 hours",
        ],
        details:
          "The token has basic legitimacy indicators but the concentrated holder distribution is concerning. The short lock period on liquidity means the risk profile could change dramatically in a few months. Recent large transfers between top wallets suggest potential coordinated positioning. The project needs more time to establish trust through consistent behavior.",
      },
      {
        agent: "contract",
        name: "Smart Contract Auditor",
        score: 45,
        riskLevel: "CAUTION",
        summary:
          "Contract is functional but lacks professional audit and has some concerning permission structures.",
        findings: [
          "No professional audit found — self-deployed contract",
          "Mint authority is held by a single wallet (not multisig)",
          "Token metadata is mutable — can be changed at any time",
          "No freeze authority (positive sign)",
          "Contract code is not verified/open-source",
        ],
        details:
          "The contract follows a standard SPL token pattern but the single-wallet mint authority is a risk vector. If compromised, unlimited tokens could be minted. The mutable metadata means the token name, symbol, or image could be changed without notice — a common tactic in rug pull setups. Recommending the team pursue a professional audit and transition to multisig governance.",
      },
      {
        agent: "market",
        name: "Market Intelligence",
        score: 44,
        riskLevel: "CAUTION",
        summary:
          "Growing community but some social signals suggest inorganic growth patterns.",
        findings: [
          "Twitter following grew 400% in 2 weeks — potentially inorganic",
          "Telegram group has high member count but low engagement ratio",
          "Project website is professional but domain registered 2 months ago",
          "Team is semi-doxxed — LinkedIn profiles exist but limited history",
          "Some paid promotion detected on crypto influencer channels",
        ],
        details:
          "The community growth pattern shows characteristics of both organic and paid acquisition. While the project does appear to have real users and holders, the aggressive social media growth and influencer marketing campaign suggest the team is prioritizing hype over substance. The semi-anonymous team adds uncertainty but is not uncommon in crypto. Proceed with caution and size positions conservatively.",
      },
    ],
  },

  danger: {
    query: "ScamToken111111111111111111111111111111111",
    overallScore: 89,
    overallRisk: "DANGER",
    timestamp: new Date().toISOString(),
    agents: [
      {
        agent: "token",
        name: "Token Risk Analyzer",
        score: 92,
        riskLevel: "DANGER",
        summary:
          "Critical risk indicators detected. This token exhibits multiple characteristics of a fraudulent project.",
        findings: [
          "Single wallet holds 78% of total supply",
          "Liquidity pool has only $12K — extremely thin",
          "No liquidity lock detected — can be pulled at any time",
          "Token created 4 days ago with no prior history",
          "Buy/sell tax asymmetry detected: 2% buy, 45% sell (honeypot pattern)",
        ],
        details:
          "This token has nearly every red flag in our detection system. The extreme supply concentration means one wallet can crash the price at will. The lack of liquidity lock means the deployer can remove all liquidity at any time, leaving holders with worthless tokens. The asymmetric tax structure is a classic honeypot — users can buy but selling is heavily penalized or impossible. This has all the characteristics of a planned rug pull.",
      },
      {
        agent: "contract",
        name: "Smart Contract Auditor",
        score: 88,
        riskLevel: "DANGER",
        summary:
          "Contract contains multiple malicious functions and hidden owner privileges.",
        findings: [
          "Hidden mint function can create unlimited tokens",
          "Owner can blacklist wallets from selling",
          "Transfer function contains hidden fee that routes to deployer",
          "Contract is a fork of a known scam template (97% code similarity)",
          "Proxy pattern detected — contract logic can be changed post-deploy",
        ],
        details:
          "The contract is a near-identical copy of a known scam contract template that has been used in 40+ rug pulls over the past 6 months. The hidden mint function is obfuscated but allows the owner to inflate supply without limit. The blacklist function prevents targeted wallets from selling — a common trap used after initial buyers are locked in. The proxy pattern means even the current analysis could become outdated if the owner swaps the implementation contract. DO NOT INTERACT with this contract.",
      },
      {
        agent: "market",
        name: "Market Intelligence",
        score: 86,
        riskLevel: "DANGER",
        summary:
          "Coordinated shill campaign detected with multiple fraud indicators.",
        findings: [
          "90% of Twitter mentions come from bot accounts (created <30 days ago)",
          "Fake partnership announcements with major protocols (denied by those protocols)",
          "Deployer wallet linked to 3 previous rug pulls totaling $2.1M stolen",
          "Website cloned from a legitimate project with minor modifications",
          "Fake audit certificate — the listed audit firm confirms no engagement",
        ],
        details:
          "Our social intelligence analysis reveals a highly coordinated fraud operation. The deployer wallet has direct on-chain links to three previous scam tokens that collectively defrauded users of over $2.1 million. The Twitter campaign uses a network of bot accounts to create artificial hype. The claimed audit from 'CertiK' is fabricated — we confirmed directly with CertiK that no audit was performed. The project website is a pixel-perfect clone of a legitimate DeFi protocol. This is a sophisticated scam operation and users should avoid any interaction.",
      },
    ],
  },
};

export const MOCK_RECENT_ANALYSES: RecentAnalysis[] = [
  {
    query: "So11111...1112",
    score: 12,
    riskLevel: "SAFE",
    timestamp: "2 hours ago",
  },
  {
    query: "7xKXtg2...gAsU",
    score: 42,
    riskLevel: "CAUTION",
    timestamp: "5 hours ago",
  },
  {
    query: "EPjFWdd5...M9zJ",
    score: 8,
    riskLevel: "SAFE",
    timestamp: "1 day ago",
  },
  {
    query: "DezXAZ8z...aBDc",
    score: 61,
    riskLevel: "WARNING",
    timestamp: "1 day ago",
  },
  {
    query: "ScamTok1...1111",
    score: 89,
    riskLevel: "DANGER",
    timestamp: "2 days ago",
  },
];

export const MOCK_CHAT_RESPONSES: Record<string, string> = {
  token:
    "Based on my analysis of the token fundamentals, I can see the following:\n\n**Supply Distribution**: The token has a total supply of 1 billion with 78% currently in circulation. The top 10 holders control approximately 23% of the supply, which is within acceptable ranges for a mid-cap token.\n\n**Liquidity Analysis**: There's $4.2M in liquidity across 3 DEX pools. The largest pool on Raydium has $2.8M. Liquidity has been locked for 12 months via a verified timelock contract.\n\n**Risk Assessment**: Moderate risk. The fundamentals are acceptable but the token is relatively new (launched 2 months ago) and hasn't been tested through a major market downturn. I'd rate it 35/100 on the risk scale.",
  contract:
    "I've completed my security assessment of the contract:\n\n**Code Quality**: The contract follows standard SPL token patterns. No custom transfer logic or hidden functions detected.\n\n**Permissions**: Mint authority is held by a 3/5 multisig wallet. Freeze authority has been revoked. Metadata is immutable.\n\n**Vulnerability Scan**: No known vulnerability patterns detected. The contract does not use proxy patterns and cannot be upgraded.\n\n**Audit Status**: The contract has been audited by OtterSec (report available). No critical or high-severity findings.\n\n**Security Score**: 15/100 risk — this is a well-secured contract with appropriate governance controls.",
  market:
    "Here's my market intelligence report:\n\n**Social Sentiment**: Overall positive with a 72% positive ratio across Twitter, Discord, and Telegram. Engagement appears organic — no significant bot activity detected.\n\n**Community Health**: Discord has 15K members with 2.1K daily active users (14% DAU ratio — healthy). Telegram group shows consistent discussion patterns.\n\n**Team Credibility**: Fully doxxed team with verifiable backgrounds. Lead developer previously worked at Phantom wallet. CEO has 8 years in fintech.\n\n**Market Context**: The token is in the DePIN sector which has been trending. Volume has increased 340% in the last 30 days, largely driven by a legitimate catalyst (mainnet launch).\n\n**Rating**: Low risk from a market intelligence perspective. The community and team check out.",
  all: "**Multi-Agent Analysis Summary**\n\nI've coordinated with all three agents to provide a comprehensive assessment:\n\n**Token Risk Analyzer** reports moderate fundamentals with acceptable supply distribution and locked liquidity. Risk: 35/100.\n\n**Smart Contract Auditor** found no vulnerabilities, proper governance controls, and a clean audit from OtterSec. Risk: 15/100.\n\n**Market Intelligence** confirms organic community growth, a doxxed team with credible backgrounds, and positive market positioning. Risk: 22/100.\n\n**Overall Assessment**: This project scores 24/100 on our risk scale — **SAFE**. The fundamentals, security, and market signals all align positively. The main risk factor is the project's relative youth (2 months). We recommend monitoring holder concentration trends and liquidity depth over the coming months.",
};

export function getMockAnalysis(query: string): AnalysisResult {
  const q = query.toLowerCase().trim();

  if (
    q.includes("so1111") ||
    q.includes("sol") ||
    q.includes("solana") ||
    q.includes("safe")
  ) {
    return { ...MOCK_ANALYSES.safe, query };
  }
  if (
    q.includes("scam") ||
    q.includes("rug") ||
    q.includes("honeypot") ||
    q.includes("danger")
  ) {
    return { ...MOCK_ANALYSES.danger, query };
  }
  // Default to caution for unknown tokens
  return { ...MOCK_ANALYSES.caution, query };
}

export function getMockChatResponse(
  agent: string,
  _message: string
): string {
  return MOCK_CHAT_RESPONSES[agent] || MOCK_CHAT_RESPONSES.all;
}
