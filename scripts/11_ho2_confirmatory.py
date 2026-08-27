"""HO-2 stage 2: the confirmatory test of H1 and H2. Executed ONCE.

PAP-v2 §7 primary tests, §8.3 within-pillar Holm across P1 = {H1, H2}.
Cleaning per §3.1 (repair extremes, retain raw) and §2 exclusions.
N-hat enters ORDINALLY via within-year deciles, per §10.2.

Whatever this prints is the result. It is not to be re-run with different choices.
"""
import sys, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _env import bootstrap
bootstrap(["statsmodels"])

import numpy as np, pandas as pd, statsmodels.api as sm
LN2 = np.log(2); OUT = ROOT/"output"/"tables"
OV_START = pd.Timestamp("2024-03-04")

A = pd.read_parquet(ROOT/"data/processed/panel_long.parquet")
B = pd.read_parquet(ROOT/"data/processed/panel_trades_clean.parquet")

# ── refit the frozen calibration (§10.2) ──
cal = A[A.date >= OV_START].merge(B[["date","symbol","n_trades"]], on=["date","symbol"], how="inner")
cal = cal[(cal.turnover>=0)&(cal.volume>=0)&(cal.close>0)&cal.n_trades.notna()].copy()
for d in (cal,):
    d["lto"]=np.log1p(d.turnover); d["lpx"]=np.log(d.close); d["lvol"]=np.log1p(d.volume); d["year"]=d.date.dt.year
Xc = sm.add_constant(pd.get_dummies(cal[["lto","lpx","lvol","year"]], columns=["year"], drop_first=True, dtype=float), has_constant="add")
fit = sm.OLS(np.log1p(cal.n_trades), Xc).fit()
lo, hi = cal.lto.quantile(0.01), cal.lto.quantile(0.99)

# ── HO-2, cleaned per §2 / §3.1 ──
h = A[A.date < OV_START].copy()
h = h[(h[["open","high","low","close"]] > 0).all(axis=1)]
h["high_raw"], h["low_raw"] = h.high, h.low                      # §3.1 raw preserved
h["high"] = h[["high","open","close"]].max(axis=1)               # H := max(H,O,C)
h["low"]  = h[["low","open","close"]].min(axis=1)                # L := min(L,O,C)
h["ohlc_repaired"] = (h.high != h.high_raw) | (h.low != h.low_raw)
h = h.sort_values(["symbol","date"])
h["cc"] = h.groupby("symbol").close.transform(lambda s: np.log(s).diff())
h = h[h.cc.abs() < 0.5]                                          # §2 exclusion, frozen at 0.5

h["lto"]=np.log1p(h.turnover.clip(lower=0)); h["lpx"]=np.log(h.close); h["lvol"]=np.log1p(h.volume.clip(lower=0))
h["year"]=h.date.dt.year
h = h[(h.lto >= lo) & (h.lto <= hi)]                             # §10.2 support restriction
Xh = pd.get_dummies(h[["lto","lpx","lvol","year"]], columns=["year"], drop_first=True, dtype=float)
for c in Xc.columns:
    if c not in Xh.columns and c != "const": Xh[c] = 0.0
Xh = sm.add_constant(Xh[[c for c in Xc.columns if c != "const"]], has_constant="add")
h["nhat"] = np.expm1(fit.predict(Xh)).clip(lower=0.5)

print(f"HO-2 analysis sample : {len(h):,} stock-days · {h.symbol.nunique()} securities "
      f"· {h.date.min().date()} → {h.date.max().date()}")
print(f"OHLC rows repaired   : {h.ohlc_repaired.sum():,} ({100*h.ohlc_repaired.mean():.2f}%)")

# ── per-stock-day variances, then within-year deciles of N-hat (§10.2 ordinal use) ──
hl=np.log(h.high/h.low); c=np.log(h.close/h.open)
h["var_pk"]=(hl**2)/(4*LN2); h["var_oc"]=c**2
h["dec"] = h.groupby("year").nhat.transform(lambda s: pd.qcut(s, 10, labels=False, duplicates="drop"))
g = h.groupby(["year","dec"]).agg(pk=("var_pk","mean"), oc=("var_oc","mean"),
                                  nhat=("nhat","median"), n=("var_pk","size")).reset_index()
g = g[(g.pk>0)&(g.oc>0)&(g.n>=50)]
g["ratio"]=np.sqrt(g.pk/g.oc); g["ln_n"]=np.log(g.nhat)
print(f"buckets (year × decile): {len(g)}  |  N̂ range {g.nhat.min():.1f} – {g.nhat.max():.0f}")

def clustered(y, X, groups):
    return sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": groups})

# ── H1 : thin region, ratio increasing in intensity ──
thin = g[g.nhat < 30]
r1 = clustered(thin.ratio, sm.add_constant(thin[["ln_n"]], has_constant="add"),
               np.column_stack([thin.year.factorize()[0], thin.dec.factorize()[0]]))
b1, t1, p1 = r1.params["ln_n"], r1.tvalues["ln_n"], r1.pvalues["ln_n"]

# ── H2 : non-monotone over the full range (concavity) ──
g2 = g.copy(); g2["ln_n2"] = g2.ln_n**2
r2 = clustered(g2.ratio, sm.add_constant(g2[["ln_n","ln_n2"]], has_constant="add"),
               np.column_stack([g2.year.factorize()[0], g2.dec.factorize()[0]]))
b2, t2, p2 = r2.params["ln_n2"], r2.tvalues["ln_n2"], r2.pvalues["ln_n2"]

# ── Holm within pillar P1 ──
raw = {"H1": p1, "H2": p2}
order = sorted(raw, key=raw.get); m = len(order)
adj, run = {}, 0.0
for i, k in enumerate(order):
    run = max(run, (m - i) * raw[k]); adj[k] = min(run, 1.0)

print("\n" + "="*78)
print("CONFIRMATORY RESULT — HO-2, pillar P1, Holm-adjusted within pillar")
print("="*78)
print(f"{'':4}{'primary statistic':38}{'coef':>10}{'t':>8}{'p raw':>10}{'p Holm':>10}  verdict")
v1 = "SUPPORTED" if (b1 > 0 and adj["H1"] < 0.05) else "NOT SUPPORTED"
v2 = "SUPPORTED" if (b2 < 0 and adj["H2"] < 0.05) else "NOT SUPPORTED"
print(f"H1  {'β₁ on ln N̂, buckets N̂<30':38}{b1:>10.4f}{t1:>8.2f}{p1:>10.2e}{adj['H1']:>10.2e}  {v1}")
print(f"H2  {'β₂ on (ln N̂)², full range':38}{b2:>10.4f}{t2:>8.2f}{p2:>10.2e}{adj['H2']:>10.2e}  {v2}")
print(f"\nH1 requires β₁ > 0 : observed {b1:+.4f}   ({len(thin)} thin buckets)")
print(f"H2 requires β₂ < 0 : observed {b2:+.4f}   ({len(g2)} buckets)")
if b2 < 0:
    turn = np.exp(-r2.params['ln_n']/(2*b2))
    print(f"   implied interior maximum at N̂ ≈ {turn:.0f} trades/day")

print("\n=== observed ratio profile by N̂ (descriptive) ===")
g["nb"] = pd.qcut(g.nhat, 8, labels=False, duplicates="drop")
print(g.groupby("nb").agg(median_nhat=("nhat","median"), mean_ratio=("ratio","mean"),
                          buckets=("ratio","size")).to_string(float_format=lambda x:f"{x:,.3f}"))
g.to_csv(OUT/"table17_ho2_confirmatory.csv", index=False)
