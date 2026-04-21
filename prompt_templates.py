"""
Investment AI Prompt Templates

Pre-filled prompts for deep investment analysis, auto-populated with stock data.
Based on the Investment AI Prompt Toolkit.
"""


def build_prompt_context(ticker, name, sector, price, ma200w, pct_above, zone, score, roe, margin, market_cap, de_ratio):
    """Build a context dict with all stock data for prompt templates."""
    return {
        "ticker": ticker,
        "name": name,
        "sector": sector,
        "price": f"${price:,.2f}",
        "ma200w": f"${ma200w:,.2f}",
        "pct_above": f"{pct_above:+.1f}%",
        "zone": zone,
        "score": score,
        "roe": f"{(roe*100):+.1f}%" if roe else "n/a",
        "margin": f"{(margin*100):+.1f}%" if margin else "n/a",
        "market_cap": f"${market_cap/1e9:.1f}B" if market_cap else "n/a",
        "de_ratio": f"{de_ratio:.2f}x" if de_ratio else "n/a",
    }


def get_holistic_prompts(ctx):
    """Return list of (title, prompt_text) tuples for holistic analysis stacks."""
    return [
        (
            "🏢 Company Deep-Dive",
            f"Conduct a comprehensive financial deep-dive on {ctx['name']} ({ctx['ticker']}):\n\n"
            f"Stock Context:\n"
            f"- Current Price: {ctx['price']} (200-week MA: {ctx['ma200w']}, {ctx['pct_above']} vs MA)\n"
            f"- Sector: {ctx['sector']}\n"
            f"- Market Cap: {ctx['market_cap']}\n"
            f"- Quality Score: {ctx['score']}/5 (ROE: {ctx['roe']}, Net Margin: {ctx['margin']})\n\n"
            f"Analyze: (1) Revenue & earnings trends (5 years), (2) Profitability metrics, (3) Cash flow health, "
            f"(4) Balance sheet strength, (5) Capital structure—debt-to-equity ({ctx['de_ratio']}), "
            f"(6) Valuation multiples vs historical and peers.\n\n"
            f"Provide: Financial Health (1-10), Growth Quality (1-10), Valuation (1-10)."
        ),
        (
            "📊 Investor Sentiment View",
            f"Analyze institutional investor positioning and sentiment for {ctx['name']} ({ctx['ticker']}):\n\n"
            f"Stock Context:\n"
            f"- Sector: {ctx['sector']}\n"
            f"- Market Cap: {ctx['market_cap']}\n"
            f"- Quality Score: {ctx['score']}/5\n\n"
            f"Evaluate: (1) Earnings performance—beat/miss trends, guidance, revisions momentum, "
            f"(2) Institutional ownership—13F changes, accumulation vs distribution, "
            f"(3) Key investor positioning, (4) Analyst sentiment, (5) Insider trading, (6) Key catalysts.\n\n"
            f"Assess: Investor conviction level and near-term price drivers."
        ),
        (
            "🌍 Macro Context & Peer Landscape",
            f"Analyze {ctx['name']} ({ctx['ticker']}) in its macroeconomic and competitive context:\n\n"
            f"Company Context:\n"
            f"- Sector: {ctx['sector']}\n"
            f"- Market Cap: {ctx['market_cap']}\n"
            f"- Valuation: {ctx['pct_above']} vs 200-week MA\n\n"
            f"Analyze: (1) Macroeconomic exposure, (2) Sector tailwinds/headwinds, "
            f"(3) Peer comparison vs 3-5 competitors, (4) Market share trends, "
            f"(5) Industry cycle position, (6) Geopolitical/regulatory risks.\n\n"
            f"Conclusion: Is the company well-positioned in its macro environment?"
        ),
        (
            "🛡️ Innovation & Moat Analysis",
            f"Assess the competitive advantages and moat strength of {ctx['name']} ({ctx['ticker']}):\n\n"
            f"Business Context:\n"
            f"- Sector: {ctx['sector']}\n"
            f"- Quality Score: {ctx['score']}/5\n"
            f"- Net Margin: {ctx['margin']}\n\n"
            f"Evaluate: (1) Competitive moat, (2) R&D quality, (3) Product differentiation, "
            f"(4) Customer concentration, (5) Disruption risk, (6) Management quality on innovation.\n\n"
            f"Rate moat strength and defensibility of competitive position."
        ),
        (
            "📈 Secular Trend Alignment",
            f"Analyze how {ctx['name']} ({ctx['ticker']}) aligns with long-term secular trends:\n\n"
            f"Company Context:\n"
            f"- Sector: {ctx['sector']}\n"
            f"- Growth indicators (ROE: {ctx['roe']}, Margin: {ctx['margin']})\n\n"
            f"Assess positioning relative to: (1) Demographic trends, (2) Technological adoption, "
            f"(3) Consumer behavior shifts, (4) Structural economic changes, (5) Regulatory/social trends.\n\n"
            f"Long-term outlook: Is the company positioned to benefit from major trends? 10-year CAGR potential?"
        ),
        (
            "💰 Capital Allocation Strategy",
            f"Evaluate management's capital allocation quality for {ctx['name']} ({ctx['ticker']}):\n\n"
            f"Management Context:\n"
            f"- Market Cap: {ctx['market_cap']}\n"
            f"- ROE: {ctx['roe']} (capital efficiency indicator)\n\n"
            f"Analyze: (1) Organic growth investment, (2) M&A strategy, (3) Dividend policy, "
            f"(4) Share buybacks, (5) Debt management, (6) Strategic capital allocation.\n\n"
            f"Assessment: Is capital being deployed well? Shareholder-friendly?"
        ),
    ]


def get_targeted_prompts(ctx):
    """Return list of (title, prompt_text) tuples for targeted analysis prompts."""
    return [
        (
            "📄 SEC Filings Review",
            f"Deep-dive into recent SEC filings for {ctx['name']} ({ctx['ticker']}):\n\n"
            f"Analyze latest 10-K and recent 10-Qs for: (1) Risk factor changes, (2) Segment performance, "
            f"(3) MD&A tone and concerns, (4) Off-balance sheet obligations, (5) Accounting policy changes, "
            f"(6) Related party transactions, (7) Executive compensation alignment.\n\n"
            f"Red flags: unusual related-party deals, audit delays, frequent accounting changes."
        ),
        (
            "🏛️ Institutional 13F Tracking",
            f"Analyze institutional positioning in {ctx['name']} ({ctx['ticker']}) from 13F filings:\n\n"
            f"Research: (1) Top 10 institutional holders, (2) Recent 13F changes—who's accumulating/selling, "
            f"(3) Notable recent trades by smart money, (4) Ownership concentration risks, "
            f"(5) Activist investor involvement, (6) Short interest trends.\n\n"
            f"Conclusion: Do smart investors see opportunity or are they fleeing?"
        ),
        (
            "💪 Balance Sheet Health",
            f"Evaluate the financial strength and solvency of {ctx['name']} ({ctx['ticker']}):\n\n"
            f"Key Metrics:\n"
            f"- Debt / Equity: {ctx['de_ratio']}\n"
            f"- Market Cap: {ctx['market_cap']}\n\n"
            f"Analyze: (1) Current ratio & quick ratio, (2) Debt maturity profile, (3) Interest coverage, "
            f"(4) Cash conversion cycle, (5) Pension obligations, (6) Contingent liabilities.\n\n"
            f"Risk rating: Low / Moderate / High. Bankruptcy/stress risk?"
        ),
        (
            "📊 Valuation Metrics",
            f"Comprehensive valuation analysis of {ctx['name']} ({ctx['ticker']}):\n\n"
            f"Current Valuation:\n"
            f"- Price: {ctx['price']} ({ctx['pct_above']} vs 200-week MA, Zone: {ctx['zone']})\n"
            f"- Quality Score: {ctx['score']}/5\n\n"
            f"Calculate & assess: (1) P/E ratio vs historical and sector, (2) Price-to-Book, "
            f"(3) EV/EBITDA, (4) Price-to-Sales, (5) Free Cash Flow yield, (6) PEG ratio.\n\n"
            f"Intrinsic value via DCF. Fair value: Overvalued / Fairly Valued / Undervalued?"
        ),
        (
            "📰 Earnings Digest",
            f"Analyze most recent earnings for {ctx['name']} ({ctx['ticker']}):\n\n"
            f"Key Points: (1) Revenue growth—beat/miss, guidance, (2) Earnings growth—EPS beat/miss, margins, "
            f"(3) Forward guidance tone, (4) Segment performance, (5) Cash generation, "
            f"(6) Shareholder questions tone, (7) What changed and why.\n\n"
            f"Earnings quality: High / Medium / Low. Are earnings sustainable?"
        ),
        (
            "📈 ROIC Calculation",
            f"Detailed Return on Invested Capital (ROIC) analysis for {ctx['name']} ({ctx['ticker']}):\n\n"
            f"Reference:\n"
            f"- ROE: {ctx['roe']}\n"
            f"- Net Margin: {ctx['margin']}\n\n"
            f"Calculate: (1) NOPAT, (2) Invested Capital, (3) ROIC = NOPAT / Invested Capital, "
            f"(4) WACC, (5) ROIC vs WACC spread.\n\n"
            f"Trend analysis: 5-year ROIC trend. Does the company earn returns above its cost of capital?"
        ),
        (
            "🎯 Peer Benchmarking",
            f"Peer comparison for {ctx['name']} ({ctx['ticker']}) in {ctx['sector']}:\n\n"
            f"Performance vs 3-5 peers: (1) Revenue growth (3yr, 1yr), (2) Profitability—gross/operating/net margins, "
            f"(3) Efficiency—ROE, ROIC, asset turnover, (4) Valuation multiples, "
            f"(5) Financial health—debt ratios, cash generation, (6) Management quality—execution vs peers.\n\n"
            f"Relative positioning: Best-in-class, in-line, or lagging? Premium or discount valuation justified?"
        ),
        (
            "💡 Stock Price Explanation",
            f"Why is {ctx['name']} ({ctx['ticker']}) priced at {ctx['price']} today?\n\n"
            f"Current Valuation Context:\n"
            f"- 200-week MA: {ctx['ma200w']} ({ctx['pct_above']} vs current, Zone: {ctx['zone']})\n"
            f"- Quality Score: {ctx['score']}/5\n\n"
            f"Analyze: (1) Recent catalysts—news, earnings, macro events, (2) Market sentiment, "
            f"(3) Technical picture, (4) Relative strength, (5) Supply/demand dynamics, "
            f"(6) What's priced in for the future?\n\n"
            f"What would drive price up/down 20% in 12 months?"
        ),
        (
            "⚠️ Risk & Catalyst Identification",
            f"Identify risks and catalysts for {ctx['name']} ({ctx['ticker']}):\n\n"
            f"Downside Risks: (1) Business risks, (2) Operational risks, (3) Financial risks, "
            f"(4) Market risks, (5) Regulatory/legal risks, (6) Geopolitical risks, (7) Technology risk.\n\n"
            f"Upside Catalysts (next 12-24 months): (1) Revenue catalysts, (2) Margin catalysts, "
            f"(3) M&A opportunity, (4) Valuation re-rating, (5) Macro tailwinds.\n\n"
            f"Risk/Reward: Balanced, skewed to upside, or skewed to downside?"
        ),
        (
            "🎯 ETF Theme Screening",
            f"Assess fit of {ctx['name']} ({ctx['ticker']}) within growth theme ETFs:\n\n"
            f"Company Profile:\n"
            f"- Sector: {ctx['sector']}\n"
            f"- Quality Score: {ctx['score']}/5\n"
            f"- Growth: {ctx['margin']} margins\n\n"
            f"Fit assessment for: (1) Digital Transformation, (2) Energy Transition, "
            f"(3) Healthcare Evolution, (4) E-commerce/Digital Economy, (5) Sustainability/ESG, "
            f"(6) Cybersecurity & Privacy, (7) Emerging Markets.\n\n"
            f"Theme alignment: Strong / Moderate / Weak. Upside from trend exposure?"
        ),
        (
            "🌐 Macro-to-Micro Impact",
            f"How do macroeconomic conditions affect {ctx['name']} ({ctx['ticker']})?\n\n"
            f"Macro Factors & Impact: (1) Interest rates, (2) Inflation, (3) Currency, "
            f"(4) Commodity prices, (5) GDP growth / recession, (6) Credit conditions, (7) Unemployment.\n\n"
            f"Base case scenarios:\n"
            f"- Soft landing (2-3% growth, stable rates)\n"
            f"- Recession (negative growth, rate cuts)\n"
            f"- Stagflation (high inflation + slow growth)\n\n"
            f"How well does the business weather macro downturns?"
        ),
        (
            "🆕 IPO / New Position Screening",
            f"Position sizing and entry strategy for {ctx['name']} ({ctx['ticker']}):\n\n"
            f"Entry Metrics:\n"
            f"- Current Price: {ctx['price']}\n"
            f"- 200-week MA: {ctx['ma200w']}\n"
            f"- Zone: {ctx['zone']}\n"
            f"- Quality Score: {ctx['score']}/5\n\n"
            f"Assess: (1) Quality confirmation, (2) Valuation adequacy, (3) Margin of safety, "
            f"(4) Catalysts timeline, (5) Position sizing, (6) Entry strategy, (7) Exit criteria.\n\n"
            f"Risk/Reward Assessment: Is this position worth taking now? Target price and holding period?"
        ),
    ]
