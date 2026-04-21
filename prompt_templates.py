"""
Investment AI Prompt Templates

Pre-filled prompts for deep investment analysis, auto-populated with stock data.
Based on the Investment AI Prompt Toolkit from:
https://gregoryrobinson.substack.com/p/the-investment-ai-prompt-toolkit
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
    prompts = [
        (
            "🏢 Company Deep-Dive",
            f"""Conduct a comprehensive financial deep-dive on {ctx['name']} ({ctx['ticker']}):

Stock Context:
- Current Price: {ctx['price']} (200-week MA: {ctx['ma200w']}, {ctx['pct_above']} vs MA, Zone: {ctx['zone']})
- Sector: {ctx['sector']}
- Market Cap: {ctx['market_cap']}
- Quality Score: {ctx['score']}/5 (ROE: {ctx['roe']}, Net Margin: {ctx['margin']})

Analyze:
1. Revenue & earnings trends (last 5 years) — growth rate, consistency, seasonality
2. Profitability metrics — gross margin, operating margin, net margin trends
3. Cash flow health — operating CF, free CF, CF conversion
4. Balance sheet strength — debt levels, liquidity, working capital
5. Capital structure — debt-to-equity ({ctx['de_ratio']}), interest coverage
6. Valuation multiples — P/E, P/B, EV/EBITDA vs historical and peers

Provide a scoring: Financial Health (1-10), Growth Quality (1-10), Valuation (1-10)."""
        ),
        (
            "📊 Investor Sentiment View",
            f"""Analyze institutional investor positioning and sentiment for {ctx['name']} ({ctx['ticker']}):

Stock Context:
- Sector: {ctx['sector']}
- Market Cap: {ctx['market_cap']}
- Quality Score: {ctx['score']}/5

Evaluate:
1. Earnings performance — beat/miss trends, guidance changes, revisions momentum
2. Institutional ownership — recent 13F changes, accumulation vs distribution
3. Key investor positioning — who's buying/selling, whale movements
4. Analyst sentiment — average target price, rating changes, price target revisions
5. Insider trading — executive buys/sells, option exercises, confidence signals
6. Key catalysts — upcoming earnings, product launches, regulatory decisions, macroeconomic factors

Assess: Investor conviction level (bullish/neutral/bearish) and near-term price drivers."""
        ),
        (
            "🌍 Macro Context & Peer Landscape",
            f"""Analyze {ctx['name']} ({ctx['ticker']}) in its macroeconomic and competitive context:

Company Context:
- Sector: {ctx['sector']}
- Market Cap: {ctx['market_cap']}
- Valuation: {ctx['pct_above']} vs 200-week MA

Analyze:
1. Macroeconomic exposure — GDP sensitivity, interest rate exposure, FX risk
2. Sector tailwinds/headwinds — structural growth/decline, regulatory changes
3. Peer comparison — revenue, profitability, growth vs 3-5 direct competitors
4. Market share trends — gaining or losing share? Why?
5. Industry cycle position — early, mid, late cycle? Cyclicality?
6. Geopolitical/regulatory risks — tariffs, sanctions, compliance costs

Conclusion: Is the company well-positioned in its macro environment?"""
        ),
        (
            "🛡️ Innovation & Moat Analysis",
            f"""Assess the competitive advantages and moat strength of {ctx['name']} ({ctx['ticker']}):

Business Context:
- Sector: {ctx['sector']}
- Quality Score: {ctx['score']}/5
- Net Margin: {ctx['margin']}

Evaluate:
1. Competitive moat — brand, switching costs, network effects, cost advantages, scale
2. R&D quality — R&D as % of revenue, innovation track record, patent portfolio
3. Product differentiation — unique features, pricing power, customer stickiness
4. Customer concentration — revenue concentration, customer retention
5. Disruption risk — threat of new entrants, technological disruption, business model risk
6. Management quality on innovation — strategic direction, execution history

Rate moat strength: Very Strong / Strong / Moderate / Weak. How defensible is competitive position?"""
        ),
        (
            "📈 Secular Trend Alignment",
            f"""Analyze how {ctx['name']} ({ctx['ticker']}) aligns with long-term secular trends:

Company Context:
- Sector: {ctx['sector']}
- Growth implied by quality metrics (ROE: {ctx['roe']}, Margin: {ctx['margin']})

Assess positioning relative to:
1. Demographic trends — aging populations, urbanization, generational shifts
2. Technological adoption — cloud, AI, automation, digital transformation
3. Consumer behavior shifts — e-commerce, sustainability, wellness, experience economy
4. Structural economic changes — reshoring, energy transition, healthcare costs
5. Regulatory/social trends — ESG, privacy, antitrust, labor changes

Long-term outlook: Is the company positioned to benefit from or resist major trends?
10-year CAGR potential assessment."""
        ),
        (
            "💰 Capital Allocation Strategy",
            f"""Evaluate management's capital allocation quality for {ctx['name']} ({ctx['ticker']}):

Management Context:
- Market Cap: {ctx['market_cap']}
- ROE: {ctx['roe']} (indicator of capital efficiency)

Analyze:
1. Organic growth investment — CapEx levels, R&D spending, strategic investments
2. M&A strategy — acquisition track record, integration success, overpayment risk
3. Dividend policy — yield, growth, payout ratio sustainability, history
4. Share buybacks — timing quality (buying high vs low), amount, impact on EPS
5. Debt management — refinancing activity, leverage optimization, covenant flexibility
6. Strategic capital allocation — balance between growth, returns to shareholders, debt reduction

Assessment: Is capital being deployed well? Shareholder-friendly or not?"""
        ),
    ]
    return prompts


def get_targeted_prompts(ctx):
    """Return list of (title, prompt_text) tuples for targeted analysis prompts."""
    prompts = [
        (
            "📄 SEC Filings Review",
            f"""Deep-dive into recent SEC filings for {ctx['name']} ({ctx['ticker']}):

Analyze the latest 10-K and recent 10-Qs. Look for:
1. Risk factor changes — new/heightened risks disclosed
2. Segment performance — revenue breakdown, margin trends by segment
3. Management's Discussion & Analysis (MD&A) — tone, management's own concerns
4. Off-balance sheet obligations — operating leases, pension obligations, contingencies
5. Accounting policy changes — conservative vs aggressive estimates
6. Related party transactions — conflicts of interest indicators
7. Executive compensation — alignment with performance, red flags

Red flags: unusual related-party deals, repeated audit delays, frequent accounting policy changes."""
        ),
        (
            "🏛️ Institutional 13F Tracking",
            f"""Analyze institutional positioning in {ctx['name']} ({ctx['ticker']}) based on 13F filings:

Research:
1. Top 10 institutional holders — who owns this stock?
2. Recent 13F changes — who's accumulating, who's selling? Direction?
3. Notable recent trades — Berkshire, Vanguard, Fidelity, other value funds
4. Ownership concentration — risk if major holder exits?
5. Activist investor involvement — any activist stakes? Positions, demands?
6. Short interest trends — high short interest = contrarian opportunity or red flag?

Conclusion: Do smart institutional investors see opportunity or are they fleeing?"""
        ),
        (
            "💪 Balance Sheet Health",
            f"""Evaluate the financial strength and solvency of {ctx['name']} ({ctx['ticker']}):

Key Metrics:
- Debt / Equity: {ctx['de_ratio']}
- Market Cap: {ctx['market_cap']}

Analyze:
1. Current ratio & quick ratio — short-term liquidity adequacy
2. Debt maturity profile — refinancing risk in next 2-3 years
3. Interest coverage ratio — ability to service debt from operations
4. Cash conversion cycle — working capital efficiency
5. Pension obligations & retirement liabilities — unfunded risks
6. Contingent liabilities — guarantees, litigation, environmental cleanup

Risk rating: Low / Moderate / High. Bankruptcy/stress risk?"""
        ),
        (
            "📊 Valuation Metrics",
            f"""Comprehensive valuation analysis of {ctx['name']} ({ctx['ticker']}):

Current Valuation:
- Price: {ctx['price']} ({ctx['pct_above']} vs 200-week MA, Zone: {ctx['zone']})
- Quality Score: {ctx['score']}/5

Calculate and assess:
1. P/E ratio — current vs historical average vs sector
2. Price-to-Book (P/B) — vs peers, tangible book value consideration
3. EV/EBITDA — adjusted for debt/cash position
4. Price-to-Sales (P/S) — less manipulable, trend analysis
5. Free Cash Flow yield — FCFF / Market Cap
6. PEG ratio — P/E vs expected growth rate

Intrinsic value estimate using DCF (conservative case, base case, bull case).
Fair value assessment: Overvalued / Fairly Valued / Undervalued."""
        ),
        (
            "📰 Earnings Digest",
            f"""Analyze the most recent earnings report for {ctx['name']} ({ctx['ticker']}):

Key Points:
1. Revenue growth — beat/miss, guidance, forward commentary
2. Earnings growth — EPS beat/miss, margin analysis
3. Forward guidance — management optimism/concern, guidance changes
4. Segment performance — which units growing, which struggling
5. Cash generation — operating cash flow, capital expenditures, free cash flow
6. Shareholder questions — tone from earnings call, management responses to concerns
7. Walk-through of changes — what changed from prior period, why

Earnings quality: High / Medium / Low. Are earnings sustainable?"""
        ),
        (
            "📈 ROIC Calculation",
            f"""Detailed Return on Invested Capital (ROIC) analysis for {ctx['name']} ({ctx['ticker']}):

Reference:
- ROE: {ctx['roe']} (related metric)
- Net Margin: {ctx['margin']}

Calculate:
1. NOPAT (Net Operating Profit After Tax) — from most recent annual financials
2. Invested Capital — equity + debt - cash & equivalents
3. ROIC = NOPAT / Invested Capital — how efficiently is capital deployed?
4. WACC (Weighted Average Cost of Capital) — cost of equity + cost of debt
5. ROIC vs WACC spread — positive spread = value creation

Trend analysis: 5-year ROIC trend. Improving or deteriorating?
Quality assessment: Is the company earning returns above its cost of capital?"""
        ),
        (
            "🎯 Peer Benchmarking",
            f"""Peer comparison analysis for {ctx['name']} ({ctx['ticker']}) in {ctx['sector']}:

Performance vs. top 3-5 peers:
1. Revenue growth rates (3yr, 1yr) — relative growth trajectory
2. Profitability — gross margin, operating margin, net margin comparison
3. Efficiency — ROE, ROIC, asset turnover vs peers
4. Valuation multiples — P/E, EV/EBITDA, P/B vs peers
5. Financial health — debt ratios, cash generation vs peers
6. Management quality — execution, consistency, capital allocation vs peers

Relative positioning:
- Is {ctx['ticker']} the best-in-class, in-line, or lagging?
- Does it deserve a premium or discount valuation?"""
        ),
        (
            "💡 Stock Price Explanation",
            f"""Why is {ctx['name']} ({ctx['ticker']}) priced at {ctx['price']} today?

Current Valuation Context:
- 200-week MA: {ctx['ma200w']} ({ctx['pct_above']} vs current, Zone: {ctx['zone']})
- Quality Score: {ctx['score']}/5

Analyze:
1. Catalyst analysis — recent news, earnings, macro events driving current price
2. Market sentiment — fear/greed indicators, sentiment indicators
3. Technical picture — chart patterns, support/resistance, trend
4. Relative strength — how is this stock performing vs its sector and the market?
5. Supply/demand — institutional flows, insider activity, short covering
6. Future expectations — what's priced in? How much growth is needed to justify current price?

Is the current price justified by fundamentals, or is it driven by sentiment/momentum?
What would change the stock price up/down 20% in the next 6-12 months?"""
        ),
        (
            "⚠️ Risk & Catalyst Identification",
            f"""Identify risks and catalysts for {ctx['name']} ({ctx['ticker'])}:

Downside Risks:
1. Business risks — competition, product obsolescence, customer concentration
2. Operational risks — supply chain, key person dependencies, execution risk
3. Financial risks — high leverage, declining cash flow, refinancing risk
4. Market risks — industry downturn, secular decline, recession sensitivity
5. Regulatory/legal risks — litigation, regulatory changes, compliance costs
6. Geopolitical risks — sanctions, tariffs, political instability impact
7. Technology risk — disruption, cybersecurity, legacy system dependencies

Upside Catalysts (next 12-24 months):
1. Revenue catalysts — new products, market entry, market share gains
2. Margin catalysts — operational leverage, cost reductions, pricing power
3. M&A opportunity — acquisition target, strategic options
4. Valuation re-rating — recognition of quality, multiple expansion
5. Macro tailwinds — industry cycle recovery, regulatory changes, tax benefits

Risk/Reward: Balanced, skewed to upside, or skewed to downside?"""
        ),
        (
            "🎯 ETF Theme Screening",
            f"""Assess fit of {ctx['name']} ({ctx['ticker']}) within growth theme ETF categories:

Company Profile:
- Sector: {ctx['sector']}
- Quality Score: {ctx['score']}/5
- Growth indicated by margins: {ctx['margin']}

Fit assessment for:
1. Digital Transformation — AI, cloud, automation exposure
2. Energy Transition — clean energy, renewable energy, EV ecosystem
3. Healthcare Evolution — aging population, biotech, digital health
4. E-commerce / Digital Economy — online sales, digital marketing, logistics
5. Sustainability / ESG — carbon reduction, circular economy, governance scores
6. Cybersecurity & Data Privacy — data protection, GDPR compliance
7. Emerging Market Growth — exposure to developing countries, currency risks

Theme alignment: Strong / Moderate / Weak. How much upside from trend exposure?"""
        ),
        (
            "🌐 Macro-to-Micro Impact",
            f"""Analyze how macroeconomic conditions affect {ctx['name']} ({ctx['ticker']}):

Macro Factors & Impact:
1. Interest rates — impact on borrowing costs, discount rates, equity valuations
2. Inflation — cost pressures, pricing power, margin impact
3. Currency — FX exposure if multinational, translation risk, competitive impact
4. Commodity prices — raw material costs if applicable
5. GDP growth / recession — revenue sensitivity, demand elasticity
6. Credit conditions — financing availability, credit spreads, refinancing risk
7. Unemployment — consumer spending power, labor cost trends

Base case macro scenario — what happens to {ctx['ticker']} if:
- Soft landing (2-3% growth, stable rates)
- Recession (negative growth, rate cuts)
- Stagflation (high inflation + slow growth)

Resilience: How well does the business weather macro downturns?"""
        ),
        (
            "🆕 IPO / New Position Screening",
            f"""Position sizing and entry strategy for {ctx['name']} ({ctx['ticker']}) (New Position Screening):

Entry Metrics:
- Current Price: {ctx['price']}
- 200-week MA: {ctx['ma200w']}
- Valuation Zone: {ctx['zone']}
- Quality Score: {ctx['score']}/5

Assess:
1. Quality confirmation — do the 5 Munger criteria justify investing?
2. Valuation adequacy — is the current price a good entry point?
3. Margin of safety — how much upside per dollar of downside risk?
4. Catalysts timeline — when do we expect positive moves?
5. Position sizing — what % of portfolio is appropriate given risk/reward?
6. Entry strategy — full position, dollar-cost average, or wait for better entry?
7. Exit criteria — at what price/metrics do we take profits or cut losses?

Risk/Reward Assessment: Is this a position worth taking now?
Target price and holding period."""
        ),
    ]
    return prompts
