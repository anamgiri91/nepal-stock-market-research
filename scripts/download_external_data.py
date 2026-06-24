"""
Download External Market Data for NEPSE Volatility Research
============================================================
Downloads India VIX, NIFTY 50, and S&P 500 VIX data via yfinance.
Produces aligned NEPSE–India dataset using date intersection.

Usage:
    pip install yfinance pandas
    python scripts/download_external_data.py
"""

import os
import sys
import pandas as pd

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance not installed. Run: pip install yfinance")
    sys.exit(1)

# ── Configuration ─────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
NEPSE_FILE = os.path.join(DATA_DIR, "nepse_index_history.csv")
# Also check root
NEPSE_FILE_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nepse_index_history.csv")

START_DATE = "2010-01-01"
END_DATE = "2026-06-13"  # One day after last NEPSE date to include 2026-06-12

TICKERS = {
    "india_vix": {
        "ticker": "^INDIAVIX",
        "output": "data_india_vix.csv",
        "description": "India VIX (daily close)",
    },
    "nifty50": {
        "ticker": "^NSEI",
        "output": "data_nifty50_ohlcv.csv",
        "description": "NIFTY 50 Index (OHLCV)",
    },
    "sp500_vix": {
        "ticker": "^VIX",
        "output": "data_sp500_vix.csv",
        "description": "CBOE S&P 500 VIX (daily close)",
    },
}


def download_ticker(ticker_id: str, config: dict) -> pd.DataFrame | None:
    """Download a single ticker and save to CSV."""
    print(f"\n{'─'*60}")
    print(f"Downloading: {config['description']}")
    print(f"  Ticker: {config['ticker']}")
    print(f"  Range:  {START_DATE} → {END_DATE}")

    try:
        data = yf.download(
            config["ticker"],
            start=START_DATE,
            end=END_DATE,
            auto_adjust=True,
            progress=False,
        )
    except Exception as e:
        print(f"  ❌ Download failed: {e}")
        return None

    if data.empty:
        print(f"  ❌ No data returned for {config['ticker']}")
        return None

    # Flatten multi-level columns if present (yfinance sometimes returns MultiIndex)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Reset index to make Date a column
    data = data.reset_index()
    data.rename(columns={"index": "Date"}, inplace=True)

    # Ensure Date column exists
    if "Date" not in data.columns:
        # Try to find it
        for col in data.columns:
            if "date" in str(col).lower():
                data.rename(columns={col: "Date"}, inplace=True)
                break

    # Ensure Date is datetime then format
    data["Date"] = pd.to_datetime(data["Date"]).dt.strftime("%Y-%m-%d")

    # Save
    output_path = os.path.join(DATA_DIR, config["output"])
    data.to_csv(output_path, index=False)

    print(f"  ✅ {len(data)} rows saved → {config['output']}")
    print(f"     Range: {data['Date'].iloc[0]} → {data['Date'].iloc[-1]}")

    return data


def align_nepse_india(india_vix: pd.DataFrame, nifty50: pd.DataFrame):
    """
    Create aligned NEPSE–India dataset using date intersection.
    Nepal trades Sun–Thu; India trades Mon–Fri.
    Only common calendar dates are kept (intersection approach).
    """
    print(f"\n{'═'*60}")
    print("Aligning NEPSE and India data (intersection method)")

    # Load NEPSE data
    nepse_path = NEPSE_FILE if os.path.exists(NEPSE_FILE) else NEPSE_FILE_ROOT
    if not os.path.exists(nepse_path):
        print("  ❌ NEPSE data not found. Skipping alignment.")
        return

    nepse = pd.read_csv(nepse_path)
    nepse["Date"] = pd.to_datetime(nepse["Date"]).dt.strftime("%Y-%m-%d")

    # Rename NEPSE columns to avoid collision
    nepse_cols = {
        "Open": "NEPSE_Open",
        "High": "NEPSE_High",
        "Low": "NEPSE_Low",
        "Close": "NEPSE_Close",
        "Turnover": "NEPSE_Turnover",
    }
    nepse = nepse.rename(columns=nepse_cols)
    nepse = nepse[["Date"] + [c for c in nepse_cols.values() if c in nepse.columns]]

    # Prepare India VIX
    vix = india_vix[["Date", "Close"]].copy()
    vix = vix.rename(columns={"Close": "IndiaVIX_Close"})

    # Prepare NIFTY 50
    nifty = nifty50[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
    nifty = nifty.rename(
        columns={
            "Open": "NIFTY_Open",
            "High": "NIFTY_High",
            "Low": "NIFTY_Low",
            "Close": "NIFTY_Close",
            "Volume": "NIFTY_Volume",
        }
    )

    # Merge — inner join = intersection of dates
    merged = nepse.merge(vix, on="Date", how="inner")
    merged = merged.merge(nifty, on="Date", how="inner")
    merged = merged.sort_values("Date").reset_index(drop=True)

    output_path = os.path.join(DATA_DIR, "data_aligned_nepse_india.csv")
    merged.to_csv(output_path, index=False)

    print(f"  NEPSE dates:      {len(nepse)}")
    print(f"  India VIX dates:  {len(vix)}")
    print(f"  NIFTY 50 dates:   {len(nifty)}")
    print(f"  Common dates:     {len(merged)}")
    if len(merged) > 0:
        print(f"  Aligned range:    {merged['Date'].iloc[0]} → {merged['Date'].iloc[-1]}")
    print(f"  ✅ Saved → data_aligned_nepse_india.csv")

    return merged


def main():
    print("=" * 60)
    print("NEPSE Volatility Research — External Data Download")
    print("=" * 60)

    os.makedirs(DATA_DIR, exist_ok=True)

    results = {}
    for ticker_id, config in TICKERS.items():
        results[ticker_id] = download_ticker(ticker_id, config)

    # Alignment
    if results.get("india_vix") is not None and results.get("nifty50") is not None:
        align_nepse_india(results["india_vix"], results["nifty50"])
    else:
        print("\n⚠️  Cannot align — India VIX or NIFTY 50 data missing")

    # Summary
    print(f"\n{'═'*60}")
    print("Download Summary")
    print(f"{'═'*60}")
    for ticker_id, config in TICKERS.items():
        status = "✅" if results.get(ticker_id) is not None else "❌"
        count = len(results[ticker_id]) if results.get(ticker_id) is not None else 0
        print(f"  {status} {config['description']}: {count} rows")

    print(f"\nAll files saved to: {DATA_DIR}/")


if __name__ == "__main__":
    main()
