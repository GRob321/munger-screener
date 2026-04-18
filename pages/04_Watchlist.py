import streamlit as st

st.set_page_config(
    page_title="Watchlist",
    page_icon="⭐",
    layout="wide",
)

st.title("⭐ Watchlist")

st.info(
    "🚀 **Coming Soon**\n\n"
    "Save your favorite tickers and monitor them for buy/watch/wait signals. "
    "Persistent watchlist with automatic quality rescoring and price alerts."
)

st.markdown("""
### What This Tool Will Do

- **Create custom watchlists** — organize tickers by theme (tech, healthcare, etc.)
- **Auto-analyse each position** — quality score + current zone (BUY/WATCH/WAIT)
- **Price alerts** — get notified when a watched stock enters the buy zone
- **Historical signals** — see when each ticker last triggered a buy or sell signal
- **Bulk export** — download your watchlist as CSV or Excel
- **Persistent storage** — your lists are saved between sessions

### Example Workflow

1. Add 50 high-quality companies to a "Quality Dividend Payers" watchlist
2. Run the screener — see which ones are in the BUY zone today
3. Set up alerts for the WATCH zone stocks
4. When a stock pulls back to its 200-week MA, get notified
5. Review the full quality report and make an informed buy decision

---

*Check back soon!*
""")
