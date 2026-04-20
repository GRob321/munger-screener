import streamlit as st
import sys
import json
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add parent directory to path to import screener
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from screener import (
    fetch_one_fundamental,
    quality_score,
    fetch_prices_and_ma,
    fetch_fundamentals,
    QUALITY_FILTERS,
    FINANCIAL_SECTORS,
    load_cache,
    save_cache,
)

st.set_page_config(
    page_title="Munger Screener",
    page_icon="🔍",
    layout="wide",
)

# Load cached S&P 500 constituents
@st.cache_data
def load_sp500_constituents():
    """Load cached S&P 500 list from JSON file."""
    constituents_path = Path(__file__).parent.parent / "sp500_constituents.json"
    with open(constituents_path) as f:
        data = json.load(f)
    return data["tickers"], data["sectors"]

# Build company name to ticker mapping
@st.cache_data
def build_company_dropdown_mapping():
    """Build searchable dropdown options with company names."""
    tickers, _ = load_sp500_constituents()

    # Load cached fundamentals, or fetch them if not available
    fundamentals = load_cache()
    if not fundamentals:
        with st.spinner("Loading company names (this may take a minute)..."):
            fundamentals = fetch_fundamentals(tickers, force_refresh=False)

    # Check for missing names and fetch them if needed
    missing_tickers = [t for t in tickers if t not in fundamentals or not fundamentals[t].get("name")]
    if missing_tickers:
        with st.spinner(f"Fetching {len(missing_tickers)} missing company names..."):
            missing_data = fetch_fundamentals(missing_tickers, force_refresh=False)
            fundamentals.update(missing_data)

    ticker_to_name = {}  # maps ticker -> best name
    for ticker in tickers:
        if ticker in fundamentals and fundamentals[ticker].get("name"):
            name = fundamentals[ticker].get("name")
        else:
            name = ticker

        # Prefer shorter, cleaner names; keep first occurrence for same ticker
        if ticker not in ticker_to_name:
            ticker_to_name[ticker] = name
        else:
            # Keep the shorter name (usually cleaner)
            if len(name) < len(ticker_to_name[ticker]):
                ticker_to_name[ticker] = name

    # Build display map: display_name -> ticker
    ticker_map = {}
    for ticker in sorted(ticker_to_name.keys()):
        name = ticker_to_name[ticker]
        display_name = f"{name} ({ticker})"
        ticker_map[display_name] = ticker

    return ticker_map

st.title("🔍 Munger Quality Screener")
st.markdown("""
Find high-quality stocks at or near their 200-week moving averages.
Filter by the 5 quality criteria, then segment by valuation zone.
""")

# ─────────────────────────────────────────────────────────────────────────────
# Cache control
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("### Search")
with col2:
    force_refresh = st.checkbox("Force refresh cache", value=False, help="Re-fetch fundamentals (takes ~90s)")

# ─────────────────────────────────────────────────────────────────────────────
# Tabs
tab_single, tab_screen = st.tabs(["Single Stock", "Full S&P 500 Screen"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: Single Stock Analysis
with tab_single:
    col1, col2 = st.columns([3, 1])

    with col1:
        ticker_map = build_company_dropdown_mapping()
        selected = st.selectbox(
            "Search by company name or ticker",
            list(ticker_map.keys()),
            placeholder="e.g., Microsoft (MSFT) or Apple (AAPL)",
            label_visibility="collapsed",
            index=None
        )
        # Get ticker from mapping
        ticker_input = ticker_map.get(selected, "") if selected else ""

    with col2:
        analyse_btn = st.button("Analyze", use_container_width=True)

    if analyse_btn and ticker_input:
        with st.spinner(f"Fetching data for {ticker_input}..."):
            # Fundamentals
            _, fund = fetch_one_fundamental(ticker_input)

            if not fund:
                st.error(f"Could not fetch data for {ticker_input}. Check ticker symbol.")
            else:
                # Price + 200-week MA
                ma_data = fetch_prices_and_ma([ticker_input])

                if ticker_input not in ma_data:
                    st.error(f"Could not fetch price data for {ticker_input}.")
                else:
                    ma = ma_data[ticker_input]
                    pct = ma["pct_above"]
                    sector = fund.get("sector", "")
                    passes, score, detail = quality_score(fund, sector)

                    # ── Zone ──────────────────────────────────────────────────
                    if pct <= 0:
                        zone = "🟢 BUY"
                        zone_desc = "At or below 200-week MA (Munger entry signal)"
                        zone_color = "green"
                    elif pct <= 20:
                        zone = "🟡 WATCH"
                        zone_desc = f"{pct:.1f}% above MA (approaching entry point)"
                        zone_color = "orange"
                    else:
                        zone = "⚪ WAIT"
                        zone_desc = f"{pct:.1f}% above MA (too far for entry)"
                        zone_color = "gray"

                    # ── Display header ────────────────────────────────────────
                    name = fund.get("name", ticker_input)

                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"## {name} ({ticker_input})")
                        st.markdown(f"*{sector}*")
                    with col2:
                        st.metric("Zone", zone, delta=zone_desc)

                    st.markdown("---")

                    # ── Price & MA ────────────────────────────────────────────
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Current Price", f"${ma['price']:,.2f}")
                    with col2:
                        st.metric("200-Week MA", f"${ma['ma200w']:,.2f}")
                    with col3:
                        st.metric("% vs MA", f"{pct:+.1f}%")

                    st.markdown("---")

                    # ── Quality criteria ──────────────────────────────────────
                    st.markdown(f"### Quality Score: {score}/5")

                    roe_ok = detail["roe"] is not None and detail["roe"] >= QUALITY_FILTERS["min_roe"]
                    mgn_ok = detail["margin"] is not None and detail["margin"] >= QUALITY_FILTERS["min_profit_margin"]
                    mc = fund.get("market_cap")
                    mc_ok = mc is not None and mc >= QUALITY_FILTERS["min_market_cap"]
                    de = detail["de_ratio"]
                    is_fin = sector in FINANCIAL_SECTORS
                    de_ok = is_fin or (de is None or de <= QUALITY_FILTERS["max_debt_equity"])
                    pos = detail["eps_pos_yrs"]
                    eps_ok = (pos is not None and pos >= QUALITY_FILTERS["min_eps_pos_years"]) or (fund.get("eps_ttm") or 0) > 0

                    # Build quality table
                    quality_data = [
                        {
                            "Criterion": "Return on Equity (ROE)",
                            "Value": f"{(detail['roe'] or 0)*100:+.1f}%" if detail["roe"] else "n/a",
                            "Threshold": "> 15%",
                            "Pass": "✅" if roe_ok else "❌"
                        },
                        {
                            "Criterion": "Net Profit Margin",
                            "Value": f"{(detail['margin'] or 0)*100:+.1f}%" if detail["margin"] else "n/a",
                            "Threshold": "> 15%",
                            "Pass": "✅" if mgn_ok else "❌"
                        },
                        {
                            "Criterion": "Market Cap",
                            "Value": f"${mc/1e9:.1f}B" if mc else "n/a",
                            "Threshold": "> $10B",
                            "Pass": "✅" if mc_ok else "❌"
                        },
                        {
                            "Criterion": "Debt / Equity" + (" (exempt)" if is_fin else ""),
                            "Value": f"{de:.2f}x" if de is not None else "n/a",
                            "Threshold": "< 2.0x",
                            "Pass": "✅" if de_ok else "❌"
                        },
                        {
                            "Criterion": "EPS Consistency",
                            "Value": f"{pos}/{detail.get('eps_tot_yrs') or 'n/a'} yrs" if pos else "n/a",
                            "Threshold": "≥ 7/10 yrs",
                            "Pass": "✅" if eps_ok else "❌"
                        },
                    ]

                    df_quality = pd.DataFrame(quality_data)
                    st.dataframe(df_quality, use_container_width=True, hide_index=True)

                    # Overall verdict
                    if passes:
                        st.success("✅ **PASSES all quality criteria**")
                    else:
                        failed = 5 - score
                        st.warning(f"❌ **FAILS quality criteria** ({failed} criterion/a not met)")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: Full S&P 500 Screen
with tab_screen:
    st.markdown("### Run Full Screener")
    st.markdown("Filter the entire S&P 500 by quality criteria and segment by valuation zone.")

    col1, col2 = st.columns([1, 3])
    with col1:
        run_screen_btn = st.button("Run Screen", use_container_width=True, key="run_screen")

    with col2:
        cache_status = st.empty()

    if run_screen_btn:
        # Check cache age
        cache = load_cache()
        if cache and not force_refresh:
            cache_status.info("✅ Using cached fundamentals (7-day TTL)")
        else:
            cache_status.warning("⚠️ Fetching fresh data from Yahoo Finance (~90 seconds)")

        with st.spinner("Loading S&P 500 constituents..."):
            tickers, wiki_sectors = load_sp500_constituents()

        with st.spinner("Applying quality filters..."):
            fundamentals = fetch_fundamentals(tickers, force_refresh=force_refresh)

            quality_pass = {}
            for ticker, f in fundamentals.items():
                sector = f.get("sector") or wiki_sectors.get(ticker, "")
                passes, score, detail = quality_score(f, sector)
                if passes:
                    quality_pass[ticker] = {
                        "fund": f,
                        "score": score,
                        "detail": detail,
                        "sector": sector
                    }

        with st.spinner("Downloading price data..."):
            q_tickers = list(quality_pass.keys())
            if not q_tickers:
                st.error("No stocks passed quality filters.")
            else:
                ma_data = fetch_prices_and_ma(q_tickers)

                # Merge results
                merged = []
                for ticker, qdata in quality_pass.items():
                    if ticker not in ma_data:
                        continue
                    merged.append({
                        "Ticker": ticker,
                        "Name": qdata["fund"]["name"][:40],
                        "Sector": qdata["sector"][:20],
                        "Price": ma_data[ticker]["price"],
                        "200W MA": ma_data[ticker]["ma200w"],
                        "% vs MA": ma_data[ticker]["pct_above"],
                        "ROE": f"{(qdata['detail']['roe'] or 0)*100:.1f}%",
                        "Margin": f"{(qdata['detail']['margin'] or 0)*100:.1f}%",
                        "D/E": f"{qdata['detail']['de_ratio']:.2f}" if qdata['detail']['de_ratio'] is not None else "n/a",
                        "ma_pct": ma_data[ticker]["pct_above"],
                        "detail": qdata["detail"],
                    })

                merged.sort(key=lambda x: x["ma_pct"])

                # Segment zones
                buy_zone = [r for r in merged if r["ma_pct"] <= 0]
                watch = [r for r in merged if 0 < r["ma_pct"] <= 20]
                wait = [r for r in merged if r["ma_pct"] > 20]

                # Display results
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Quality Pass", len(merged), f"of {len(tickers)}")
                with col2:
                    st.metric("🟢 Buy Zone", len(buy_zone))
                with col3:
                    st.metric("🟡 Watch List", len(watch))
                with col4:
                    st.metric("⚪ Wait", len(wait))

                st.markdown("---")

                # BUY zone
                with st.expander(f"🟢 **BUY ZONE** — {len(buy_zone)} stocks at or below 200-week MA", expanded=True):
                    if buy_zone:
                        df_buy = pd.DataFrame([
                            {
                                "Ticker": r["Ticker"],
                                "Name": r["Name"],
                                "Sector": r["Sector"],
                                "Price": f"${r['Price']:.2f}",
                                "200W MA": f"${r['200W MA']:.2f}",
                                "% vs MA": f"{r['% vs MA']:+.1f}%",
                                "ROE": r["ROE"],
                                "Margin": r["Margin"],
                                "D/E": r["D/E"],
                            }
                            for r in buy_zone
                        ])
                        st.dataframe(df_buy, use_container_width=True, hide_index=True)
                    else:
                        st.markdown("*None currently at or below their 200-week MA.*")

                # WATCH list
                with st.expander(f"🟡 **WATCH LIST** — {len(watch)} stocks within 0–20% above MA", expanded=len(buy_zone) == 0):
                    if watch:
                        df_watch = pd.DataFrame([
                            {
                                "Ticker": r["Ticker"],
                                "Name": r["Name"],
                                "Sector": r["Sector"],
                                "Price": f"${r['Price']:.2f}",
                                "200W MA": f"${r['200W MA']:.2f}",
                                "% vs MA": f"{r['% vs MA']:+.1f}%",
                                "ROE": r["ROE"],
                                "Margin": r["Margin"],
                                "D/E": r["D/E"],
                            }
                            for r in watch
                        ])
                        st.dataframe(df_watch, use_container_width=True, hide_index=True)
                    else:
                        st.markdown("*None in this zone.*")

                # WAIT zone
                with st.expander(f"⚪ **WAIT** — {len(wait)} quality stocks more than 20% above MA"):
                    if wait:
                        df_wait = pd.DataFrame([
                            {
                                "Ticker": r["Ticker"],
                                "Name": r["Name"],
                                "Sector": r["Sector"],
                                "Price": f"${r['Price']:.2f}",
                                "200W MA": f"${r['200W MA']:.2f}",
                                "% vs MA": f"{r['% vs MA']:+.1f}%",
                                "ROE": r["ROE"],
                                "Margin": r["Margin"],
                                "D/E": r["D/E"],
                            }
                            for r in wait
                        ])
                        st.dataframe(df_wait, use_container_width=True, hide_index=True)
                    else:
                        st.markdown("*None in this zone.*")
