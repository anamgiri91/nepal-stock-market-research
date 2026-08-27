"""Build the NEPSE stock-level panels from the two raw sources.

Source A (long):   372 company files, 2010-2026, OHLC + volume + turnover. No trade counts.
Source B (trades): daily cross-sections, 2024-03 onward, adds Trans. (trade count) and VWAP.

The two-stage design this enables: estimate the trade-count relationship on the
overlap window where Trans. is observed, then use turnover/volume as a calibrated
proxy to extend the analysis back to 2010.
"""
import sys, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _env import bootstrap
bootstrap()

import numpy as np, pandas as pd

RAW = ROOT.parent / "private" / "data-vault" / "raw"
OUT = ROOT / "data" / "processed"; OUT.mkdir(parents=True, exist_ok=True)


def build_long() -> pd.DataFrame:
    frames = []
    for f in sorted((RAW / "stock-daily-long").glob("*.csv")):
        try:
            d = pd.read_csv(f)
        except Exception:
            continue
        if "published_date" not in d.columns or d.empty:
            continue
        d = d.rename(columns={"published_date": "date", "traded_quantity": "volume",
                              "traded_amount": "turnover"})
        d["symbol"] = f.stem
        frames.append(d[["date", "symbol", "open", "high", "low", "close", "volume", "turnover"]])
    p = pd.concat(frames, ignore_index=True)
    p["date"] = pd.to_datetime(p["date"], errors="coerce")
    for c in ["open", "high", "low", "close", "volume", "turnover"]:
        p[c] = pd.to_numeric(p[c], errors="coerce")
    p = p.dropna(subset=["date", "close"]).sort_values(["symbol", "date"]).reset_index(drop=True)

    # Turnover is NOT populated in the source before 2011: every zero-turnover row there has
    # POSITIVE volume (99.9% of 3,702 such rows) and 56% show High != Low, so those securities
    # traded and their prices moved. This is missingness encoded as zero. Left uncorrected, any
    # turnover-conditioned rule silently reclassifies traded days as untraded ones.
    missing_turnover = (p["turnover"] == 0) & (p["volume"] > 0)
    p.loc[missing_turnover, "turnover"] = np.nan
    p["turnover_missing"] = missing_turnover
    return p


def _num(s):
    return pd.to_numeric(s.astype(str).str.replace(",", "", regex=False), errors="coerce")


def build_trades() -> pd.DataFrame:
    frames = []
    for f in sorted((RAW / "stock-daily-trades").glob("*.csv")):
        try:
            d = pd.read_csv(f)
        except Exception:
            continue
        if d.empty or "Symbol" not in d.columns:
            continue
        d["date"] = pd.to_datetime(f.stem.replace("_", "-"), errors="coerce")
        frames.append(d)
    p = pd.concat(frames, ignore_index=True)
    ren = {"Symbol": "symbol", "Open": "open", "High": "high", "Low": "low",
           "Close": "close", "Vol": "volume", "Turnover": "turnover",
           "Trans.": "n_trades", "VWAP": "vwap", "Prev. Close": "prev_close"}
    p = p.rename(columns=ren)
    keep = ["date", "symbol", "open", "high", "low", "close", "volume",
            "turnover", "n_trades", "vwap", "prev_close"]
    p = p[[c for c in keep if c in p.columns]]
    for c in p.columns:
        if c not in ("date", "symbol"):
            p[c] = _num(p[c])
    p = p.dropna(subset=["date", "close", "symbol"]).sort_values(["symbol", "date"])
    p = p.drop_duplicates(subset=["symbol", "date"], keep="last").reset_index(drop=True)
    return p


def diagnose(p: pd.DataFrame, name: str):
    ok_hi = p["high"] >= p[["open", "close"]].max(axis=1) - 1e-9
    ok_lo = p["low"] <= p[["open", "close"]].min(axis=1) + 1e-9
    viol = ~(ok_hi & ok_lo)
    print(f"\n{name}")
    print(f"  rows            {len(p):,}")
    print(f"  symbols         {p['symbol'].nunique():,}")
    print(f"  dates           {p['date'].nunique():,}  ({p['date'].min().date()} -> {p['date'].max().date()})")
    print(f"  OHLC violations {viol.sum():,} ({100*viol.mean():.2f}%)")
    print(f"  H == L          {(p['high'] == p['low']).sum():,} ({100*(p['high']==p['low']).mean():.2f}%)")
    if "n_trades" in p.columns:
        t = p["n_trades"].dropna()
        print(f"  n_trades        median={t.median():.0f}  p10={t.quantile(.1):.0f}  p90={t.quantile(.9):.0f}  max={t.max():.0f}")
    return viol


TRADING_DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]


def clean_trades_panel(p: pd.DataFrame, stale_threshold: float = 0.98) -> pd.DataFrame:
    """Remove stale non-trading sessions from the daily cross-section archive.

    The archive contains files for Fridays and Saturdays, on which NEPSE does not trade. Those
    files carry the previous session forward: 99.2% of Saturday closes and 87.5% of Friday closes
    are identical to the prior dated file. Retained, they roughly double the measured zero-return
    friction and insert non-events into every rolling window.

    Two passes: restrict to the Sunday-Thursday week, then drop any remaining date whose whole
    cross-section is >= `stale_threshold` identical to the prior date.
    """
    q = p[p["date"].dt.day_name().isin(TRADING_DAYS)].copy()

    piv = q.pivot_table(index="date", columns="symbol", values="close")
    prev = piv.shift(1)
    both = piv.notna() & prev.notna()
    same = ((piv == prev) & both).sum(axis=1)
    frac = same / both.sum(axis=1).replace(0, np.nan)
    stale_dates = frac[frac >= stale_threshold].index
    q = q[~q["date"].isin(stale_dates)]

    n_days = q["date"].nunique()
    span = (q["date"].max() - q["date"].min()).days / 365.25
    print(f"\nPANEL B - cleaned")
    print(f"  weekday filter removed   {len(p) - len(p[p['date'].dt.day_name().isin(TRADING_DAYS)]):,} rows")
    print(f"  stale dates dropped      {len(stale_dates)}")
    print(f"  rows                     {len(q):,}")
    print(f"  sessions                 {n_days}  ({q['date'].min().date()} -> {q['date'].max().date()})")
    print(f"  sessions per year        {n_days/span:.0f}   (index reference: 222)")
    return q


if __name__ == "__main__":
    print("Building panels from", RAW)
    long_ = build_long();  diagnose(long_, "PANEL A - long history (no trade counts)")
    trades = build_trades(); diagnose(trades, "PANEL B - with trade counts")

    clean = clean_trades_panel(trades)

    long_.to_parquet(OUT / "panel_long.parquet", index=False)
    trades.to_parquet(OUT / "panel_trades.parquet", index=False)
    clean.to_parquet(OUT / "panel_trades_clean.parquet", index=False)
    print(f"\nwrote {OUT/'panel_long.parquet'}")
    print(f"wrote {OUT/'panel_trades.parquet'}")
    print(f"wrote {OUT/'panel_trades_clean.parquet'}")
