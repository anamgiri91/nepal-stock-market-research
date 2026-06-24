"""
Range-Based Volatility Estimators for NEPSE
=============================================
Computes Parkinson, Garman-Klass, Rogers-Satchell, and Yang-Zhang
volatility estimators using OHLC data from nepse_index_history.csv.

Only uses data from 2016-06-06 onward (where OHLC data has actual range).

Output: data/data_range_based_volatility.csv
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# ── Configuration ─────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
NEPSE_FILE = os.path.join(BASE_DIR, "nepse_index_history.csv")
OUTPUT_CSV = os.path.join(DATA_DIR, "data_range_based_volatility.csv")
OUTPUT_FIG = os.path.join(BASE_DIR, "range_based_volatility_comparison.png")

OHLC_START_DATE = "2016-06-06"  # First date with genuine H ≠ L
WINDOWS = [5, 10, 22, 63]       # 1-week, 2-week, 1-month, 1-quarter
ANNUALIZATION = 252              # Trading days per year


# ── Estimator Functions ───────────────────────────────────────────────

def close_to_close_vol(close: pd.Series, window: int) -> pd.Series:
    """Standard close-to-close realized volatility (annualized)."""
    log_returns = np.log(close / close.shift(1))
    return log_returns.rolling(window).std() * np.sqrt(ANNUALIZATION)


def parkinson_vol(high: pd.Series, low: pd.Series, window: int) -> pd.Series:
    """
    Parkinson (1980) range-based estimator.
    σ² = (1 / 4·ln2) · E[(ln(H/L))²]
    Annualized: σ = sqrt(252 · σ²_daily)
    ~5× more efficient than close-to-close.
    """
    log_hl_sq = np.log(high / low) ** 2
    factor = 1.0 / (4.0 * np.log(2))
    daily_var = factor * log_hl_sq.rolling(window).mean()
    return np.sqrt(daily_var * ANNUALIZATION)


def garman_klass_vol(
    open_: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series, window: int
) -> pd.Series:
    """
    Garman-Klass (1980) OHLC estimator.
    σ² = 0.5·(ln H/L)² − (2ln2 − 1)·(ln C/O)²
    Annualized: σ = sqrt(252 · σ²_daily)
    ~7.4× more efficient than close-to-close.
    """
    log_hl_sq = np.log(high / low) ** 2
    log_co_sq = np.log(close / open_) ** 2
    daily_var = 0.5 * log_hl_sq - (2.0 * np.log(2) - 1.0) * log_co_sq
    return np.sqrt(daily_var.rolling(window).mean().clip(lower=0) * ANNUALIZATION)


def rogers_satchell_vol(
    open_: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series, window: int
) -> pd.Series:
    """
    Rogers-Satchell (1991) estimator.
    σ² = ln(H/C)·ln(H/O) + ln(L/C)·ln(L/O)
    Drift-independent — does not assume zero mean.
    """
    daily_var = (
        np.log(high / close) * np.log(high / open_)
        + np.log(low / close) * np.log(low / open_)
    )
    return np.sqrt(daily_var.rolling(window).mean().clip(lower=0) * ANNUALIZATION)


def yang_zhang_vol(
    open_: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series, window: int
) -> pd.Series:
    """
    Yang-Zhang (2000) estimator.
    Combines overnight (open-to-previous-close), close-to-close,
    and Rogers-Satchell components.
    σ² = σ²_overnight + k·σ²_close-to-close + (1−k)·σ²_RS
    where k = 0.34 / (1.34 + (n+1)/(n-1))
    Drift-independent + captures overnight jumps.
    """
    n = window

    # Overnight return: ln(Open_t / Close_{t-1})
    log_overnight = np.log(open_ / close.shift(1))

    # Close-to-open (intraday proxy): ln(Close_t / Open_t)
    log_co = np.log(close / open_)

    # Rogers-Satchell daily variance
    rs_daily = (
        np.log(high / close) * np.log(high / open_)
        + np.log(low / close) * np.log(low / open_)
    )

    # Rolling variances
    sigma2_overnight = log_overnight.rolling(window).var()
    sigma2_close = log_co.rolling(window).var()
    sigma2_rs = rs_daily.rolling(window).mean()

    # Yang-Zhang weighting factor
    k = 0.34 / (1.34 + (n + 1) / (n - 1))

    sigma2_yz = sigma2_overnight + k * sigma2_close + (1 - k) * sigma2_rs
    return np.sqrt(sigma2_yz.clip(lower=0) * ANNUALIZATION)


# ── Main ──────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("NEPSE Range-Based Volatility Estimators")
    print("=" * 60)

    # Load NEPSE data
    df = pd.read_csv(NEPSE_FILE)
    df["Date"] = pd.to_datetime(df["Date"])

    # Filter to genuine OHLC period
    df = df[df["Date"] >= OHLC_START_DATE].copy()
    df = df.sort_values("Date").reset_index(drop=True)
    print(f"Using {len(df)} observations from {OHLC_START_DATE}")
    print(f"Date range: {df['Date'].iloc[0].date()} → {df['Date'].iloc[-1].date()}")

    # Validate OHLC — check for rows where H = L (no range)
    flat_mask = df["High"] == df["Low"]
    n_flat = flat_mask.sum()
    if n_flat > 0:
        print(f"⚠️  {n_flat} rows still have H=L (no intraday range) — range estimators will be 0 for those days")

    # Check for zero/negative prices
    for col in ["Open", "High", "Low", "Close"]:
        bad = (df[col] <= 0).sum()
        if bad > 0:
            print(f"⚠️  {bad} non-positive values in {col}")

    # Build output DataFrame
    result = df[["Date"]].copy()

    # Add close price for reference
    result["Close"] = df["Close"].values

    # Compute each estimator at each window
    for w in WINDOWS:
        print(f"\n  Window = {w} days:")

        # Close-to-close (benchmark)
        cc = close_to_close_vol(df["Close"], w)
        col_cc = f"CC_vol_{w}d"
        result[col_cc] = cc.values
        print(f"    Close-to-Close:    {cc.dropna().median():.4f} (median annualized)")

        # Parkinson
        pk = parkinson_vol(df["High"], df["Low"], w)
        col_pk = f"Parkinson_{w}d"
        result[col_pk] = pk.values
        print(f"    Parkinson:         {pk.dropna().median():.4f}")

        # Garman-Klass
        gk = garman_klass_vol(df["Open"], df["High"], df["Low"], df["Close"], w)
        col_gk = f"GarmanKlass_{w}d"
        result[col_gk] = gk.values
        print(f"    Garman-Klass:      {gk.dropna().median():.4f}")

        # Rogers-Satchell
        rs = rogers_satchell_vol(df["Open"], df["High"], df["Low"], df["Close"], w)
        col_rs = f"RogersSatchell_{w}d"
        result[col_rs] = rs.values
        print(f"    Rogers-Satchell:   {rs.dropna().median():.4f}")

        # Yang-Zhang
        yz = yang_zhang_vol(df["Open"], df["High"], df["Low"], df["Close"], w)
        col_yz = f"YangZhang_{w}d"
        result[col_yz] = yz.values
        print(f"    Yang-Zhang:        {yz.dropna().median():.4f}")

    # Save CSV
    os.makedirs(DATA_DIR, exist_ok=True)
    result.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ Saved {len(result)} rows → {OUTPUT_CSV}")

    # ── Generate Comparison Figure ──────────────────────────────────
    print("\nGenerating comparison figure...")

    fig, axes = plt.subplots(2, 2, figsize=(16, 10), dpi=150)
    fig.suptitle(
        "NEPSE Range-Based Volatility Estimators (Annualized)",
        fontsize=14,
        fontweight="bold",
        y=0.98,
    )

    colors = {
        "CC": "#888888",
        "Parkinson": "#e63946",
        "GarmanKlass": "#457b9d",
        "RogersSatchell": "#2a9d8f",
        "YangZhang": "#e9c46a",
    }

    dates = pd.to_datetime(result["Date"])

    for idx, w in enumerate(WINDOWS):
        ax = axes[idx // 2, idx % 2]

        for est_name, color in colors.items():
            col = f"{est_name}_vol_{w}d" if est_name == "CC" else f"{est_name}_{w}d"
            if col in result.columns:
                vals = result[col].dropna()
                ax.plot(
                    dates[vals.index],
                    vals,
                    color=color,
                    alpha=0.8,
                    linewidth=0.7,
                    label=est_name.replace("_", " "),
                )

        ax.set_title(f"{w}-Day Rolling Window", fontsize=11, fontweight="bold")
        ax.set_ylabel("Annualized Volatility")
        ax.legend(fontsize=8, loc="upper right")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUTPUT_FIG, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Figure saved → {OUTPUT_FIG}")

    # ── Summary Statistics ──────────────────────────────────────────
    print(f"\n{'═'*60}")
    print("Summary: 22-Day Window Comparison")
    print(f"{'═'*60}")
    summary_cols = [c for c in result.columns if "22d" in c]
    summary = result[summary_cols].describe().round(4)
    print(summary.to_string())


if __name__ == "__main__":
    main()
