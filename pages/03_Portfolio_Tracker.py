import streamlit as st

st.set_page_config(
    page_title="Portfolio Tracker",
    page_icon="💼",
    layout="wide",
)

st.title("💼 Portfolio Tracker")

st.info(
    "🚀 **Coming Soon**\n\n"
    "Track your holdings against their 200-week moving averages. "
    "Get notified when a position re-enters the buy zone or exits your target zone. "
    "Visualize your portfolio's current valuation status at a glance."
)

st.markdown("""
### What This Tool Will Do

- **Import your positions** from a CSV file or manual entry
- **Calculate 200-week MAs** for each holding
- **Show valuation zones** — is each position in BUY, WATCH, or WAIT?
- **Alert thresholds** — configure notifications when positions hit key price levels
- **Historical tracking** — see how your positions have moved relative to their MAs over time
- **Sector breakdown** — understand your portfolio's quality exposure

### Why It Matters

The Munger 200-week MA strategy is most effective when you:

1. **Buy high-quality stocks** at or below their 200-week MA (entry signal)
2. **Hold them for the long term** while they appreciate
3. **Exit** when they rise > 20% above the MA (rebalance signal)

This tool helps you monitor whether your current holdings are still in alignment
with the strategy's signals, so you know when to hold and when to rebalance.

---

*Check back soon!*
""")
