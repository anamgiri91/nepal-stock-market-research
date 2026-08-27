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


if __name__ == "__main__":
    print("Building panels from", RAW)
    long_ = build_long();  diagnose(long_, "PANEL A - long history (no trade counts)")
    trades = build_trades(); diagnose(trades, "PANEL B - with trade counts")

    long_.to_parquet(OUT / "panel_long.parquet", index=False)
    trades.to_parquet(OUT / "panel_trades.parquet", index=False)
    print(f"\nwrote {OUT/'panel_long.parquet'}")
    print(f"wrote {OUT/'panel_trades.parquet'}")
