import streamlit as st
import json
from pathlib import Path
from utils import show_feedback_form

st.set_page_config(
    page_title="Backtest Results",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Backtest Results (2000–2024)")
st.markdown("""
Historical performance of the Munger 200-week MA strategy vs S&P 500 benchmark.
21+ years of data, 13 buy signals, capital-matched comparison.
""")

# Load results
results_path = Path(__file__).parent.parent / "backtest_results.json"
with open(results_path) as f:
    results = json.load(f)

strategy = results["strategy"]
benchmark = results["benchmark_spy_matched"]
n_signals = results["n_signals"]

# ─────────────────────────────────────────────────────────────────────────────
# Headline metrics
st.subheader("📈 Performance Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Strategy CAGR",
        f"{strategy['cagr']:.2f}%",
        delta=f"+{strategy['cagr'] - benchmark['cagr']:.2f}% vs SPY"
    )

with col2:
    st.metric(
        "SPY CAGR",
        f"{benchmark['cagr']:.2f}%"
    )

with col3:
    st.metric(
        "Sharpe Ratio",
        f"{strategy['sharpe']:.3f}",
        delta=f"+{strategy['sharpe'] - benchmark['sharpe']:.3f} vs SPY"
    )

with col4:
    st.metric(
        "Max Drawdown",
        f"{strategy['max_drawdown']:.1f}%",
        delta=f"{strategy['max_drawdown'] - benchmark['max_drawdown']:.1f} vs SPY"
    )

# ─────────────────────────────────────────────────────────────────────────────
# Detailed results
st.markdown("---")
st.subheader("💼 Investment Summary")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Munger 200-Week MA Strategy")
    st.markdown(f"""
    **Period:** {strategy['n_years']:.1f} years

    **Initial Investment:** ${strategy['total_invested']:,.0f}

    **Final Value:** ${strategy['final_value']:,.0f}

    **Total Return:** {strategy['total_return']:.1f}x

    **Buy Signals:** {n_signals}
    """)

with col2:
    st.markdown("#### S&P 500 (Capital-Matched)")
    st.markdown(f"""
    **Period:** {benchmark['n_years']:.1f} years

    **Initial Investment:** ${benchmark['total_invested']:,.0f}

    **Final Value:** ${benchmark['final_value']:,.0f}

    **Total Return:** {benchmark['total_return']:.1f}x

    **Strategy Outperformance:** {(strategy['total_return'] / benchmark['total_return']):.1f}x
    """)

# ─────────────────────────────────────────────────────────────────────────────
# Chart
st.markdown("---")
st.subheader("📉 Historical Performance Chart")

chart_path = Path(__file__).parent.parent / "munger_200wma_backtest.png"
if chart_path.exists():
    st.image(str(chart_path), caption="3-panel chart: (1) growth curve, (2) returns histogram, (3) signal timeline")
else:
    st.warning("Chart image not found. Run `python3 backtest_200wma.py` to generate it.")

# ─────────────────────────────────────────────────────────────────────────────
# Methodology
st.markdown("---")
st.subheader("🔬 Methodology")

with st.expander("How the backtest works", expanded=False):
    st.markdown("""
    #### Quality Filter
    The screener applies 5 objective quality criteria to the S&P 500 constituent list
    at the beginning of each year:

    - **ROE > 15%** — Return on equity; a measure of profit generation efficiency
    - **Net Profit Margin > 15%** — Pricing power and operational discipline
    - **Market Cap > $10B** — Large-cap stocks with sufficient liquidity
    - **Debt / Equity < 2.0** — Healthy balance sheets (financials exempt)
    - **EPS positive ≥ 7 of 10 years** — Durable, repeatable earnings

    #### Buy Signals
    Stocks that pass the quality filter are monitored. A **buy signal** is generated when
    a stock's price falls to or below its 200-week simple moving average.

    #### Portfolio Management
    - Equal-weight allocation across all active signals
    - Rebalanced annually on the first trading day
    - Positions held until they rise > 20% above the 200-week MA (exit signal)
    - Benchmark: S&P 500 with matching initial capital

    #### Data Source
    - **Fundamentals:** Yahoo Finance (annual financials)
    - **Prices:** Yahoo Finance (adjusted closing prices, weekly)
    - **Universe:** S&P 500 constituents (updated annually)
    """)

# ─────────────────────────────────────────────────────────────────────────────
# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <small>
        Backtest period: 2000-01-01 through 2024-12-31<br>
        Data source: Yahoo Finance | Past performance is not indicative of future results<br>
        This is educational. Not investment advice.
    </small>
</div>
""", unsafe_allow_html=True)

# Feedback form
show_feedback_form()
