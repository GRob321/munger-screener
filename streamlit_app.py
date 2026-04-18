import streamlit as st
import json
from pathlib import Path

st.set_page_config(
    page_title="Munger 200-Week MA System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load backtest results for headline metrics
@st.cache_data
def load_backtest_results():
    results_path = Path(__file__).parent / "backtest_results.json"
    with open(results_path) as f:
        return json.load(f)

results = load_backtest_results()
strategy = results["strategy"]
benchmark = results["benchmark_spy_matched"]

# ─────────────────────────────────────────────────────────────────────────────
# Header
st.title("📈 Munger 200-Week MA System")
st.markdown("""
### Quality × Price: A Disciplined Approach to Value Investing

Based on Charlie Munger's principle: *"If all you ever did was buy high-quality stocks
on the 200-week moving average, you would beat the S&P 500 by a large margin over time."*
""")

# ─────────────────────────────────────────────────────────────────────────────
# Headline metrics
st.subheader("📊 Historical Backtest (2000–2024)")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Strategy CAGR",
        value=f"{strategy['cagr']:.1f}%",
        delta=f"+{strategy['cagr'] - benchmark['cagr']:.1f}% vs SPY"
    )

with col2:
    st.metric(
        label="SPY CAGR",
        value=f"{benchmark['cagr']:.1f}%"
    )

with col3:
    st.metric(
        label="Sharpe Ratio",
        value=f"{strategy['sharpe']:.2f}",
        delta=f"+{strategy['sharpe'] - benchmark['sharpe']:.2f} vs SPY"
    )

with col4:
    st.metric(
        label="Total Return",
        value=f"{strategy['total_return']:.0f}x",
        delta=f"${strategy['final_value']:,.0f} on $13k invested"
    )

# ─────────────────────────────────────────────────────────────────────────────
# Strategy explanation
st.markdown("---")
st.subheader("🎯 How It Works")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **1️⃣ Quality Filter**

    Only consider stocks that meet ALL criteria:
    - ROE > 15% (efficient profit generation)
    - Net margin > 15% (pricing power)
    - Market cap > $10B (liquidity)
    - Debt/Equity < 2.0 (financial health)
    - EPS positive ≥ 7 of last 10 years
    """)

with col2:
    st.markdown("""
    **2️⃣ Price Zones**

    🟢 **BUY** — Price ≤ 200-week MA
    At or below ~4-year average

    🟡 **WATCH** — 0–20% above MA
    Approaching entry point

    ⚪ **WAIT** — > 20% above MA
    Too expensive, wait for pullback
    """)

with col3:
    st.markdown("""
    **3️⃣ Execute**

    Buy high-quality stocks only when they're
    at or below their 200-week moving average.

    Hold for the long term. Repeat.

    *Backtest shows +23% CAGR vs +11.4% SPY*
    """)

# ─────────────────────────────────────────────────────────────────────────────
# Navigation to tools
st.markdown("---")
st.subheader("🛠️ Tools")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🔍 Munger Screener
    Run the quality filter on the S&P 500 or analyse a single stock.
    See which stocks are in the BUY, WATCH, or WAIT zones today.

    **→ Go to [Munger Screener](pages/01_munger_screener.py)**
    """)

with col2:
    st.markdown("""
    ### 📊 Backtest Results
    Historical performance of the 200-week MA strategy from 2000–2024.
    Compare the strategy to S&P 500 benchmark with detailed charts.

    **→ Go to [Backtest](pages/02_backtest.py)**
    """)

# ─────────────────────────────────────────────────────────────────────────────
# Coming soon
st.markdown("---")
st.subheader("🚀 Coming Soon")

col1, col2 = st.columns(2)

with col1:
    st.info("**Portfolio Tracker** — Monitor your holdings vs their 200-week MAs")

with col2:
    st.info("**Watchlist** — Save tickers and get notified when they enter the buy zone")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <small>
        Data source: Yahoo Finance | S&P 500 constituents from Wikipedia | Fundamentals cached for 7 days<br>
        This is educational. Not investment advice. Always do your own research.
    </small>
</div>
""", unsafe_allow_html=True)
