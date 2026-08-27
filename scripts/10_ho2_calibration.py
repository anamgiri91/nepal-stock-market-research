"""HO-2 stage 1: turnover-proxy calibration and the pre-set abandonment gate.

Executes PAP-v2 §10.2 exactly. Produces ONLY proxy diagnostics — calibration fit, N-hat
against realized N, and out-of-support share. Per §10.2 these are diagnostics of the proxy,
not of the hypotheses, and disclosing them does not open HO-2.

GATE: calibration R^2 < 0.50 => the proxy is too weak and HO-2 is ABANDONED, not used.
Fixed in advance so a weak proxy cannot be rationalised after the fact.
"""
import sys, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _env import bootstrap
bootstrap(["statsmodels"])

import numpy as np, pandas as pd, statsmodels.api as sm

OUT = ROOT/"output"/"tables"
A = pd.read_parquet(ROOT/"data/processed/panel_long.parquet")
B = pd.read_parquet(ROOT/"data/processed/panel_trades_clean.parquet")

OV_START = pd.Timestamp("2024-03-04")          # panel B begins here; overlap = calibration
print("PAP-v2 §10.2 — turnover-proxy calibration\n" + "="*72)

# ── calibration sample: panel A overlap rows matched to panel B trade counts ──
a_ov = A[A.date >= OV_START].copy()
cal = a_ov.merge(B[["date","symbol","n_trades"]], on=["date","symbol"], how="inner")
cal = cal[(cal.turnover >= 0) & (cal.volume >= 0) & (cal.close > 0) & cal.n_trades.notna()]
print(f"calibration rows      : {len(cal):,}   securities: {cal.symbol.nunique()}")
print(f"calibration window    : {cal.date.min().date()} → {cal.date.max().date()}")

cal["y"]    = np.log1p(cal.n_trades)
cal["lto"]  = np.log1p(cal.turnover)
cal["lpx"]  = np.log(cal.close)
cal["lvol"] = np.log1p(cal.volume)
cal["year"] = cal.date.dt.year

X = pd.get_dummies(cal[["lto","lpx","lvol","year"]], columns=["year"], drop_first=True, dtype=float)
X = sm.add_constant(X, has_constant="add")
fit = sm.OLS(cal["y"], X).fit(
    cov_type="cluster",
    cov_kwds={"groups": np.column_stack([cal.symbol.factorize()[0], cal.date.factorize()[0]])},
)
R2 = fit.rsquared
print(f"\ncalibration R²        : {R2:.4f}")
print(f"  β1  ln(1+turnover)  : {fit.params['lto']:+.4f}  (t = {fit.tvalues['lto']:.1f})")
print(f"  β2  ln(price)       : {fit.params['lpx']:+.4f}  (t = {fit.tvalues['lpx']:.1f})")
print(f"  β3  ln(1+volume)    : {fit.params['lvol']:+.4f}  (t = {fit.tvalues['lvol']:.1f})")

# ── N-hat vs realized N inside the calibration window ──
cal["nhat"] = np.expm1(fit.predict(X)).clip(lower=0)
sp = np.corrcoef(cal.nhat.rank(), cal.n_trades.rank())[0,1]
print(f"\nN̂ vs realized N       : Pearson(log) {np.corrcoef(np.log1p(cal.nhat), cal.y)[0,1]:.3f} | "
      f"Spearman {sp:.3f}")
dec = pd.qcut(cal.nhat, 10, labels=False, duplicates="drop")
agree = (pd.qcut(cal.n_trades, 10, labels=False, duplicates="drop") == dec).mean()
print(f"decile agreement (N̂ vs N): {100*agree:.1f}%  — relevant because N̂ is used ORDINALLY")

# ── out-of-support share in HO-2 ──
lo, hi = cal.lto.quantile(0.01), cal.lto.quantile(0.99)
ho2 = A[A.date < OV_START].copy()
ho2["lto"] = np.log1p(ho2.turnover.clip(lower=0))
in_sup = (ho2.lto >= lo) & (ho2.lto <= hi)
print(f"\nHO-2 rows              : {len(ho2):,}  ({ho2.symbol.nunique()} securities, "
      f"{ho2.date.min().date()} → {ho2.date.max().date()})")
print(f"  inside support       : {in_sup.sum():,} ({100*in_sup.mean():.1f}%)")
print(f"  OUTSIDE support      : {(~in_sup).sum():,} ({100*(~in_sup).mean():.1f}%)  → excluded, not extrapolated")

pd.DataFrame({"metric":["calibration_R2","n_cal_rows","n_cal_securities","spearman_nhat_n",
                        "decile_agreement","ho2_rows","ho2_in_support_pct"],
              "value":[R2,len(cal),cal.symbol.nunique(),sp,agree,len(ho2),100*in_sup.mean()]}
             ).to_csv(OUT/"table16_ho2_calibration.csv", index=False)

print("\n" + "="*72)
if R2 < 0.50:
    print(f"GATE FAILED. R² = {R2:.4f} < 0.50.")
    print("Per PAP-v2 §10.2 the proxy is too weak to support H1/H2 on HO-2.")
    print("HO-2 IS ABANDONED. It is not to be used, salvaged, or re-specified.")
else:
    print(f"GATE PASSED. R² = {R2:.4f} ≥ 0.50. HO-2 may be opened, once.")
