"""
Backtest: Charlie Munger's "Buy High-Quality Stocks on the 200-Week Moving Average"

Strategy:
  - Universe: 25 well-known high-quality stocks (Berkshire favorites + blue-chip quality companies)
  - Signal: Stock price falls within TOUCH_THRESHOLD of its 200-week SMA
  - Action: Invest equal capital on each signal; hold positions indefinitely
  - Benchmark: S&P 500 (SPY) buy-and-hold with the same total capital deployed at the same times

Key Questions:
  1. Does the strategy beat S&P 500 buy-and-hold in CAGR?
  2. What is the risk profile (max drawdown, Sharpe ratio)?
  3. How often do signals fire? (signal frequency)
  4. Sensitivity to the touch threshold (5%, 10%, 15%)?
"""

import sys
import warnings
warnings.filterwarnings("ignore")

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from datetime import datetime, timedelta
import json

# ── Configuration ────────────────────────────────────────────────────────────

START_DATE = "2000-01-01"
END_DATE   = "2024-12-31"

# "High-Quality" universe: classic Berkshire Hathaway holdings + marquee blue-chips
# These represent stocks Munger/Buffett consistently praised as moat-owning, durable businesses
HIGH_QUALITY = {
    # Core Berkshire holdings (long-term)
    "KO":   "Coca-Cola",
    "AXP":  "American Express",
    "WFC":  "Wells Fargo",
    "USB":  "US Bancorp",
    "MCO":  "Moody's",
    "BK":   "Bank of NY Mellon",
    # Buffett/Munger favourites mentioned in annual letters
    "JNJ":  "Johnson & Johnson",
    "PG":   "Procter & Gamble",
    "WMT":  "Walmart",
    "HD":   "Home Depot",
    "MCD":  "McDonald's",
    "V":    "Visa",
    "MA":   "Mastercard",
    # Quality growth (added to Berkshire later)
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL":"Alphabet",
    "AMZN": "Amazon",
    # Financial quality
    "JPM":  "JPMorgan Chase",
    "BAC":  "Bank of America",
    "BRK-B":"Berkshire Hathaway",
    # Consumer/industrial quality
    "NKE":  "Nike",
    "COST": "Costco",
    "MMM":  "3M",
    "CVX":  "Chevron",
    "XOM":  "ExxonMobil",
}

BENCHMARK = "SPY"

# Touch threshold: stock is considered "at" the 200-wk MA when within this % above it
# (never fires if price is ABOVE MA by more than threshold; always fires if at or below)
TOUCH_THRESHOLD_PCT = 0.10   # 10% — primary scenario
THRESHOLDS_TO_TEST  = [0.05, 0.10, 0.15, 0.20]  # sensitivity analysis
CAPITAL_PER_SIGNAL  = 1_000  # $1,000 invested each time a signal fires


# ── Data Download ─────────────────────────────────────────────────────────────

def download_weekly(tickers, start, end):
    """Download weekly adjusted-close prices for a list of tickers."""
    print(f"Downloading weekly prices for {len(tickers)} tickers …")
    raw = yf.download(
        tickers,
        start=start,
        end=end,
        interval="1wk",
        auto_adjust=True,
        progress=False,
    )["Close"]
    # yfinance returns MultiIndex columns when >1 ticker; squeeze if single
    if isinstance(raw, pd.Series):
        raw = raw.to_frame(name=tickers[0])
    raw.index = pd.to_datetime(raw.index).tz_localize(None)
    raw = raw.sort_index()
    print(f"  Data range: {raw.index[0].date()} → {raw.index[-1].date()}, "
          f"{len(raw)} weeks, {raw.shape[1]} tickers")
    return raw


# ── Signal Engine ─────────────────────────────────────────────────────────────

def compute_signals(prices, threshold):
    """
    For each ticker, compute rolling 200-week SMA and return a boolean DataFrame
    where True means price is AT or BELOW (threshold * SMA) above the SMA.

    Signal fires on week t if:
        SMA[t] * 1.0  <=  price[t]  <=  SMA[t] * (1 + threshold)
    OR
        price[t]  <  SMA[t]   (below the MA — deep value territory)

    i.e.  price[t] / SMA[t]  <=  (1 + threshold)

    Cooldown: once a signal fires for a ticker, it cannot fire again for 52 weeks
    (prevents buying the same dip repeatedly on every weekly bar).
    """
    sma200 = prices.rolling(200, min_periods=200).mean()
    ratio  = prices / sma200                         # price / 200wk SMA
    raw_signal = (ratio <= (1 + threshold)) & ratio.notna()

    # Apply 52-week cooldown per ticker
    signals = pd.DataFrame(False, index=prices.index, columns=prices.columns)
    cooldown = {}
    for t in prices.index:
        for ticker in prices.columns:
            if pd.isna(prices.loc[t, ticker]):
                continue
            # Cooldown check
            last = cooldown.get(ticker)
            if last is not None and (t - last).days < 52 * 7:
                continue
            if raw_signal.loc[t, ticker]:
                signals.loc[t, ticker] = True
                cooldown[ticker] = t
    return signals, sma200


# ── Portfolio Simulation ───────────────────────────────────────────────────────

def simulate_strategy(prices, signals, capital_per_signal):
    """
    For each signal, invest `capital_per_signal` dollars in that stock.
    Buy at the week-end price of the signal week; hold indefinitely.
    Return weekly portfolio value time series and trade log.
    """
    trades = []   # list of dicts: {date, ticker, shares, cost_basis}
    all_dates = prices.index

    for date in all_dates:
        for ticker in prices.columns:
            if signals.loc[date, ticker]:
                price = prices.loc[date, ticker]
                if pd.isna(price) or price <= 0:
                    continue
                shares = capital_per_signal / price
                trades.append({
                    "entry_date": date,
                    "ticker":     ticker,
                    "shares":     shares,
                    "entry_price": price,
                    "cost":       capital_per_signal,
                })

    if not trades:
        return pd.Series(dtype=float), []

    # Build weekly portfolio value
    portfolio_values = pd.Series(0.0, index=all_dates)
    total_invested   = pd.Series(0.0, index=all_dates)

    for trade in trades:
        entry = trade["entry_date"]
        ticker = trade["ticker"]
        shares = trade["shares"]
        cost   = trade["cost"]
        after_entry = all_dates[all_dates >= entry]
        px = prices.loc[after_entry, ticker].fillna(method="ffill")
        portfolio_values.loc[after_entry] += px * shares
        total_invested.loc[after_entry]   += cost

    return portfolio_values, total_invested, trades


def simulate_spy_benchmark(spy_prices, signal_dates_amounts):
    """
    Buy SPY on the same dates and with the same dollar amounts as the strategy signals.
    This ensures a fair capital-matched comparison.
    """
    all_dates = spy_prices.index
    spy_values = pd.Series(0.0, index=all_dates)

    for (date, amount) in signal_dates_amounts:
        if date not in spy_prices.index:
            # find nearest date
            idx = all_dates.searchsorted(date)
            if idx >= len(all_dates):
                continue
            date = all_dates[idx]
        price = spy_prices.loc[date]
        if pd.isna(price) or price <= 0:
            continue
        shares = amount / price
        after = all_dates[all_dates >= date]
        spy_values.loc[after] += spy_prices.loc[after].fillna(method="ffill") * shares

    return spy_values


# ── Performance Metrics ────────────────────────────────────────────────────────

def cagr(values, n_years):
    if values.iloc[0] == 0 or n_years <= 0:
        return np.nan
    return (values.iloc[-1] / values.iloc[0]) ** (1 / n_years) - 1


def max_drawdown(values):
    roll_max = values.cummax()
    drawdown = (values - roll_max) / roll_max
    return drawdown.min()


def sharpe(weekly_returns, rf_weekly=0.0):
    excess = weekly_returns - rf_weekly
    if excess.std() == 0:
        return np.nan
    return (excess.mean() / excess.std()) * np.sqrt(52)


def performance_summary(label, port_values, total_invested, start, end):
    n_years = (end - start).days / 365.25
    # Trim to where we have positions
    active = port_values[port_values > 0]
    if active.empty:
        print(f"  {label}: No trades executed.")
        return {}

    first_date = active.index[0]
    years_active = (active.index[-1] - first_date).days / 365.25

    final_value  = active.iloc[-1]
    total_cost   = total_invested[total_invested > 0].iloc[-1] if (total_invested > 0).any() else 1

    weekly_ret = active.pct_change().dropna()

    metrics = {
        "label":          label,
        "n_years":        round(years_active, 1),
        "total_invested": round(total_cost, 0),
        "final_value":    round(final_value, 0),
        "total_return":   round((final_value / total_cost - 1) * 100, 1),
        "cagr":           round(cagr(active, years_active) * 100, 2),
        "max_drawdown":   round(max_drawdown(active) * 100, 2),
        "sharpe":         round(sharpe(weekly_ret), 3),
    }
    return metrics


# ── Signal Statistics ─────────────────────────────────────────────────────────

def signal_stats(signals, prices, sma200, trades):
    n_signals = int(signals.sum().sum())
    tickers_hit = signals.any().sum()

    # Forward returns after each signal: 1yr, 2yr, 3yr
    fwd_returns = {52: [], 104: [], 156: []}
    for trade in trades:
        entry  = trade["entry_date"]
        ticker = trade["ticker"]
        for weeks, lst in fwd_returns.items():
            target_date = entry + pd.Timedelta(weeks=weeks)
            future = prices.index[prices.index >= target_date]
            if future.empty:
                continue
            future_date = future[0]
            if future_date in prices.index and not pd.isna(prices.loc[future_date, ticker]):
                ret = prices.loc[future_date, ticker] / trade["entry_price"] - 1
                lst.append(ret)

    return n_signals, tickers_hit, fwd_returns


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    tickers = list(HIGH_QUALITY.keys()) + [BENCHMARK]
    prices_all = download_weekly(tickers, START_DATE, END_DATE)

    # Separate benchmark
    spy_prices  = prices_all[BENCHMARK]
    stock_prices = prices_all[[t for t in HIGH_QUALITY if t in prices_all.columns]]

    print(f"\nStocks in universe with data: {stock_prices.shape[1]} / {len(HIGH_QUALITY)}")
    missing = [t for t in HIGH_QUALITY if t not in stock_prices.columns]
    if missing:
        print(f"  Missing: {missing}")

    # ── Primary backtest at 10% threshold ────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"PRIMARY BACKTEST  |  Touch threshold: {TOUCH_THRESHOLD_PCT*100:.0f}%  |  "
          f"Capital/signal: ${CAPITAL_PER_SIGNAL:,}")
    print(f"Period: {START_DATE} → {END_DATE}")
    print('='*60)

    signals, sma200 = compute_signals(stock_prices, TOUCH_THRESHOLD_PCT)
    port_values, total_invested, trades = simulate_strategy(
        stock_prices, signals, CAPITAL_PER_SIGNAL
    )

    # Build matched SPY benchmark (same dates, same capital)
    signal_dates_amounts = [
        (t["entry_date"], t["cost"]) for t in trades
    ]
    spy_values = simulate_spy_benchmark(spy_prices, signal_dates_amounts)
    # Also build a simple SPY buy-and-hold with same total capital at start
    total_capital = len(trades) * CAPITAL_PER_SIGNAL
    spy_start_date = trades[0]["entry_date"] if trades else pd.Timestamp(START_DATE)
    spy_simple = pd.Series(0.0, index=spy_prices.index)
    if spy_start_date in spy_prices.index:
        spy_start_price = spy_prices.loc[spy_start_date]
        spy_shares_simple = total_capital / spy_start_price
        spy_simple.loc[spy_prices.index >= spy_start_date] = (
            spy_prices.loc[spy_prices.index >= spy_start_date] * spy_shares_simple
        )

    start_dt = pd.Timestamp(START_DATE)
    end_dt   = pd.Timestamp(END_DATE)

    strat_metrics = performance_summary(
        "Munger 200-WMA Strategy", port_values, total_invested, start_dt, end_dt
    )
    spy_match_metrics = performance_summary(
        "SPY (Capital-Matched)", spy_values,
        pd.Series(total_invested.values, index=total_invested.index),
        start_dt, end_dt
    )

    # ── Print results table ───────────────────────────────────────────────────
    keys = ["total_invested", "final_value", "total_return", "cagr", "max_drawdown", "sharpe"]
    labels_fmt = {
        "total_invested": ("Total Invested ($)",      "${:>12,.0f}",    "${:>12,.0f}"),
        "final_value":    ("Final Value ($)",          "${:>12,.0f}",    "${:>12,.0f}"),
        "total_return":   ("Total Return",             "{:>12.1f}%",     "{:>12.1f}%"),
        "cagr":           ("CAGR",                     "{:>12.2f}%",     "{:>12.2f}%"),
        "max_drawdown":   ("Max Drawdown",             "{:>12.2f}%",     "{:>12.2f}%"),
        "sharpe":         ("Sharpe Ratio (weekly)",    "{:>12.3f}",      "{:>12.3f}"),
    }

    print(f"\n{'Metric':<30} {'Munger 200-WMA':>18} {'SPY Matched':>18}")
    print("-" * 68)
    for k in keys:
        lbl, fmt_s, fmt_b = labels_fmt[k]
        sv = strat_metrics.get(k, float("nan"))
        bv = spy_match_metrics.get(k, float("nan"))
        print(f"  {lbl:<28} {fmt_s.format(sv):>18} {fmt_b.format(bv):>18}")

    # Beat / lag
    cagr_diff = strat_metrics.get("cagr", 0) - spy_match_metrics.get("cagr", 0)
    print(f"\n  CAGR difference (Strategy - SPY): {cagr_diff:+.2f}%")
    if cagr_diff > 0:
        print(f"  → Strategy OUTPERFORMS SPY by {cagr_diff:.2f}% per year")
    else:
        print(f"  → Strategy UNDERPERFORMS SPY by {abs(cagr_diff):.2f}% per year")

    # ── Signal statistics ─────────────────────────────────────────────────────
    n_signals, tickers_hit, fwd_returns = signal_stats(signals, stock_prices, sma200, trades)
    print(f"\n── Signal Statistics ──")
    print(f"  Total signals fired:          {n_signals}")
    print(f"  Unique tickers with signals:  {tickers_hit}")
    print(f"  Avg signals / year:           {n_signals / 25:.1f}")
    print(f"\n  Median forward returns after a 200-WMA touch:")
    for weeks, lst in fwd_returns.items():
        yrs  = weeks // 52
        vals = [x for x in lst if not np.isnan(x)]
        if vals:
            median = np.median(vals) * 100
            hit_rate = sum(1 for x in vals if x > 0) / len(vals) * 100
            print(f"    {yrs}yr: median={median:+.1f}%,  positive={hit_rate:.0f}%,  n={len(vals)}")

    # Per-ticker signal count
    print(f"\n  Signals by ticker:")
    sig_counts = signals.sum().sort_values(ascending=False)
    for ticker, count in sig_counts.items():
        if count > 0:
            print(f"    {ticker:<8} {int(count):>3}  ({HIGH_QUALITY.get(ticker, '')})")

    # ── Sensitivity analysis ──────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("SENSITIVITY: CAGR vs Touch Threshold")
    print('='*60)
    print(f"  {'Threshold':>12}  {'Strategy CAGR':>14}  {'SPY CAGR':>10}  {'Difference':>12}  {'# Signals':>10}")
    print(f"  {'-'*12}  {'-'*14}  {'-'*10}  {'-'*12}  {'-'*10}")

    for thresh in THRESHOLDS_TO_TEST:
        s2, _ = compute_signals(stock_prices, thresh)
        pv2, ti2, tr2 = simulate_strategy(stock_prices, s2, CAPITAL_PER_SIGNAL)
        sda2 = [(t["entry_date"], t["cost"]) for t in tr2]
        sv2  = simulate_spy_benchmark(spy_prices, sda2)
        sm2  = performance_summary("", pv2, ti2, start_dt, end_dt)
        bm2  = performance_summary("", sv2, ti2, start_dt, end_dt)
        sc  = sm2.get("cagr", float("nan"))
        bc  = bm2.get("cagr", float("nan"))
        diff = sc - bc
        nsig = int(s2.sum().sum())
        print(f"  {thresh*100:>11.0f}%  {sc:>13.2f}%  {bc:>9.2f}%  {diff:>+12.2f}%  {nsig:>10}")

    # ── Comparison: Strategy vs SPY per stock ─────────────────────────────────
    print(f"\n{'='*60}")
    print("INDIVIDUAL STOCK PERFORMANCE after 200-WMA touch signals")
    print('='*60)
    print(f"  {'Ticker':<8}  {'Signals':>8}  {'Median 1yr':>11}  {'Median 3yr':>11}  {'Hit% 1yr':>9}")
    print(f"  {'-'*8}  {'-'*8}  {'-'*11}  {'-'*11}  {'-'*9}")

    per_stock = {}
    for trade in trades:
        t = trade["ticker"]
        if t not in per_stock:
            per_stock[t] = {"1yr": [], "3yr": []}
        entry = trade["entry_date"]
        # 1-year forward return
        tgt1 = entry + pd.Timedelta(weeks=52)
        fut1 = stock_prices.index[stock_prices.index >= tgt1]
        if not fut1.empty and not pd.isna(stock_prices.loc[fut1[0], t]):
            per_stock[t]["1yr"].append(stock_prices.loc[fut1[0], t] / trade["entry_price"] - 1)
        # 3-year forward return
        tgt3 = entry + pd.Timedelta(weeks=156)
        fut3 = stock_prices.index[stock_prices.index >= tgt3]
        if not fut3.empty and not pd.isna(stock_prices.loc[fut3[0], t]):
            per_stock[t]["3yr"].append(stock_prices.loc[fut3[0], t] / trade["entry_price"] - 1)

    rows = []
    for ticker, d in sorted(per_stock.items()):
        n  = len(trades) and len([tr for tr in trades if tr["ticker"] == ticker])
        m1 = np.median(d["1yr"])  * 100 if d["1yr"]  else float("nan")
        m3 = np.median(d["3yr"])  * 100 if d["3yr"]  else float("nan")
        h1 = sum(1 for x in d["1yr"] if x > 0) / len(d["1yr"]) * 100 if d["1yr"] else float("nan")
        n_sig = sum(1 for tr in trades if tr["ticker"] == ticker)
        rows.append((ticker, n_sig, m1, m3, h1))

    for r in sorted(rows, key=lambda x: x[2], reverse=True):
        ticker, n_sig, m1, m3, h1 = r
        print(f"  {ticker:<8}  {n_sig:>8}  {m1:>+10.1f}%  {m3:>+10.1f}%  {h1:>8.0f}%")

    # ── SPY comparison for same periods ──────────────────────────────────────
    spy_1yr = []
    spy_3yr = []
    for trade in trades:
        entry = trade["entry_date"]
        tgt1  = entry + pd.Timedelta(weeks=52)
        fut1  = spy_prices.index[spy_prices.index >= entry]
        fut1y = spy_prices.index[spy_prices.index >= tgt1]
        if not fut1.empty and not fut1y.empty:
            e_price = spy_prices.loc[fut1[0]]
            f_price = spy_prices.loc[fut1y[0]]
            if not pd.isna(e_price) and not pd.isna(f_price):
                spy_1yr.append(f_price / e_price - 1)
        tgt3  = entry + pd.Timedelta(weeks=156)
        fut3y = spy_prices.index[spy_prices.index >= tgt3]
        if not fut1.empty and not fut3y.empty:
            e_price = spy_prices.loc[fut1[0]]
            f_price = spy_prices.loc[fut3y[0]]
            if not pd.isna(e_price) and not pd.isna(f_price):
                spy_3yr.append(f_price / e_price - 1)

    spy_m1 = np.median(spy_1yr) * 100  if spy_1yr else float("nan")
    spy_m3 = np.median(spy_3yr) * 100  if spy_3yr else float("nan")
    spy_h1 = sum(1 for x in spy_1yr if x > 0) / len(spy_1yr) * 100 if spy_1yr else float("nan")
    print(f"\n  {'SPY (same entry dates)':<8}            {spy_m1:>+10.1f}%  {spy_m3:>+10.1f}%  {spy_h1:>8.0f}%")

    # ── Verdict ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("VERDICT")
    print('='*60)
    overall_cagr_diff = strat_metrics.get("cagr", 0) - spy_match_metrics.get("cagr", 0)
    median_1yr_all    = np.median([x for lst in fwd_returns[52]  for x in [lst] if not np.isnan(x)]) * 100 if fwd_returns[52]  else float("nan")
    median_3yr_all    = np.median([x for lst in fwd_returns[156] for x in [lst] if not np.isnan(x)]) * 100 if fwd_returns[156] else float("nan")

    print(f"""
  Munger's claim: "Buy high-quality stocks on the 200-week MA → beat S&P 500 by a large margin."

  Backtest results ({START_DATE} to {END_DATE}, {len(HIGH_QUALITY)}-stock quality universe):

  1. CAGR comparison
       Strategy CAGR:  {strat_metrics.get("cagr", float("nan")):+.2f}%
       SPY CAGR:       {spy_match_metrics.get("cagr", float("nan")):+.2f}%
       Difference:     {overall_cagr_diff:+.2f}%
       {'✓ Strategy OUTPERFORMS' if overall_cagr_diff > 0 else '✗ Strategy UNDERPERFORMS'}

  2. Median 1-year forward return after any 200-WMA touch
       Quality stocks: {median_1yr_all:+.1f}%
       SPY (same dates): {spy_m1:+.1f}%

  3. Risk-adjusted
       Strategy Sharpe: {strat_metrics.get("sharpe", float("nan")):.3f}
       SPY Sharpe:       {spy_match_metrics.get("sharpe", float("nan")):.3f}
       Max drawdown (Strategy): {strat_metrics.get("max_drawdown", float("nan")):.1f}%
       Max drawdown (SPY):      {spy_match_metrics.get("max_drawdown", float("nan")):.1f}%

  4. Signal rarity: {n_signals} total signals across {len(HIGH_QUALITY)} stocks over 25 years
       = {n_signals/25:.1f} signals / year on average
       (200-WMA touches are RARE — long periods of NO actionable signals)
    """)

    # ── Save chart ────────────────────────────────────────────────────────────
    try:
        fig = plt.figure(figsize=(14, 10))
        gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.35)

        # Panel 1: Portfolio growth comparison
        ax1 = fig.add_subplot(gs[0, :])
        active_mask  = port_values > 0
        active_spy   = spy_values  > 0
        combined_mask = active_mask & active_spy
        if combined_mask.any():
            idx = combined_mask[combined_mask].index[0]
            norm_strat = port_values[combined_mask] / port_values[idx]
            norm_spy   = spy_values[combined_mask]  / spy_values[idx]
            ax1.plot(norm_strat.index, norm_strat.values, label="Munger 200-WMA Strategy", lw=2, color="#2196F3")
            ax1.plot(norm_spy.index,   norm_spy.values,   label="SPY (Capital-Matched)",   lw=2, color="#FF9800", ls="--")
            ax1.set_title("Portfolio Growth: Munger 200-WMA Strategy vs S&P 500 (Normalized to 1.0 at first signal)", fontsize=11)
            ax1.set_ylabel("Portfolio Value (Normalized)")
            ax1.legend()
            ax1.grid(True, alpha=0.3)

        # Panel 2: Forward returns distribution (1yr)
        ax2 = fig.add_subplot(gs[1, 0])
        fwd_1yr = [x * 100 for x in fwd_returns[52] if not np.isnan(x)]
        if fwd_1yr:
            ax2.hist(fwd_1yr, bins=25, color="#2196F3", alpha=0.7, edgecolor="white")
            ax2.axvline(np.median(fwd_1yr), color="red", lw=2, label=f"Median: {np.median(fwd_1yr):.1f}%")
            ax2.axvline(0, color="black", lw=1, ls="--")
            ax2.set_title("1-Year Returns After 200-WMA Touch", fontsize=10)
            ax2.set_xlabel("Return (%)")
            ax2.set_ylabel("Frequency")
            ax2.legend(fontsize=9)

        # Panel 3: Signal timeline heatmap (signals per year per ticker)
        ax3 = fig.add_subplot(gs[1, 1])
        sig_by_year = signals.copy()
        sig_by_year.index = sig_by_year.index.year
        yearly = sig_by_year.groupby(sig_by_year.index).sum()
        tickers_with_sigs = yearly.columns[yearly.sum() > 0]
        if len(tickers_with_sigs) > 0:
            heat = yearly[tickers_with_sigs].T
            im = ax3.imshow(heat.values, aspect="auto", cmap="YlOrRd", interpolation="nearest")
            ax3.set_xticks(range(len(heat.columns)))
            ax3.set_xticklabels(heat.columns, rotation=90, fontsize=6)
            ax3.set_yticks(range(len(heat.index)))
            ax3.set_yticklabels(heat.index, fontsize=7)
            ax3.set_title("Signal Heatmap (signals per year per stock)", fontsize=10)
            plt.colorbar(im, ax=ax3, shrink=0.7)

        plt.suptitle(
            f"Charlie Munger 200-Week MA Strategy Backtest\n"
            f"{START_DATE} – {END_DATE}  |  {len(HIGH_QUALITY)}-stock quality universe  |  "
            f"{TOUCH_THRESHOLD_PCT*100:.0f}% touch threshold",
            fontsize=12, y=1.01
        )

        chart_path = "/Users/gregrobinson/Projects/Investing-200-week-avg/munger_200wma_backtest.png"
        plt.savefig(chart_path, dpi=140, bbox_inches="tight")
        print(f"\nChart saved → {chart_path}")
    except Exception as e:
        print(f"\n(Chart generation failed: {e})")

    # Save JSON results
    result = {
        "strategy": strat_metrics,
        "benchmark_spy_matched": spy_match_metrics,
        "n_signals": n_signals,
        "sensitivity": []
    }
    out_path = "/Users/gregrobinson/Projects/Investing-200-week-avg/backtest_results.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"Results saved → {out_path}\n")


if __name__ == "__main__":
    main()
