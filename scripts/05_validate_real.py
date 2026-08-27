"""Does the simulated discretisation bias actually appear in NEPSE data?

The theory predicts a specific, falsifiable pattern: within liquidity buckets, the
ratio of a range-based variance to an unbiased benchmark should decline with the
trade count, tracing out the curve measured in simulation.

Benchmark choice matters. Parkinson estimates the OPEN-TO-CLOSE variance, so the
matched unbiased benchmark is the mean squared open-to-close return, NOT the
close-to-close return -- the latter also contains overnight variance and would
manufacture a spurious ratio below one even absent any discretisation bias.

Produces Figure 4 and Table 6.
"""
import sys, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _env import bootstrap
bootstrap()

import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from nepsevol.utils import plotstyle as ps
from nepsevol.estimators import range_ as R
from nepsevol.estimators.simulate import simulate_observed_ohlc

ps.apply()
FIG = ROOT / "output" / "figures"; TAB = ROOT / "output" / "tables"

p = pd.read_parquet(ROOT / "data/processed/analysis_sample.parquet")
p["var_oc"] = p["c"] ** 2                      # matched unbiased benchmark (open-to-close)
p = p[p["c"].abs() < 0.5]

NB = 14
p["bucket"] = pd.qcut(p["n_trades"], NB, labels=False, duplicates="drop")

def ratio(g, col):
    num, den = g[col].mean(), g["var_oc"].mean()
    return np.sqrt(num / den) if den > 0 and num > 0 else np.nan

obs = p.groupby("bucket").apply(lambda g: pd.Series({
    "n_med":  g["n_trades"].median(),
    "n_obs":  len(g),
    "Parkinson":       ratio(g, "var_pk"),
    "Garman-Klass":    ratio(g, "var_gk"),
    "Rogers-Satchell": ratio(g, "var_rs"),
})).reset_index()

# ---- simulated prediction evaluated at each bucket's median trade count
print("Simulating predictions at each observed liquidity bucket...")
EST = {"Parkinson": R.parkinson, "Garman-Klass": R.garman_klass,
       "Rogers-Satchell": R.rogers_satchell}
pred_rows = []
for _, r in obs.iterrows():
    n_tr = max(int(round(r["n_med"])), 2)
    accum = {k: [] for k in EST}
    for rep in range(12):
        df = simulate_observed_ohlc(4000, 0.02, n_tr, noise_sd=0.0,
                                    seed=7000 + rep * 97 + n_tr)
        oc = np.nanmean(np.log(df['close']/df['open'])**2)
        for k, fn in EST.items():
            v = np.nanmean(np.asarray(fn(df), dtype=float))
            accum[k].append(np.sqrt(v / oc) if v > 0 and oc > 0 else np.nan)
    pred_rows.append({"bucket": r["bucket"], "n_med": r["n_med"],
                      **{k: np.nanmean(v) for k, v in accum.items()}})
pred = pd.DataFrame(pred_rows)

merged = obs.merge(pred, on=["bucket", "n_med"], suffixes=("_obs", "_pred"))
merged.to_csv(TAB / "table6_observed_vs_predicted.csv", index=False)

print("\n=== TABLE 6: observed vs predicted bias ratio, by NEPSE liquidity bucket ===")
show = merged[["n_med", "n_obs", "Parkinson_obs", "Parkinson_pred",
               "Rogers-Satchell_obs", "Rogers-Satchell_pred"]]
print(show.to_string(index=False, float_format=lambda x: f"{x:,.3f}"))

for e in EST:
    corr = merged[f"{e}_obs"].corr(merged[f"{e}_pred"])
    mae  = (merged[f"{e}_obs"] - merged[f"{e}_pred"]).abs().mean()
    print(f"\n{e:18} corr(observed, predicted) = {corr:.3f}   mean |gap| = {mae:.3f}")

# ---------------------------------------------------------------- FIGURE 4
fig, ax = plt.subplots(figsize=(6.8, 4.2))
ax.axhline(1.0, color=ps.INK_MUTED, linewidth=0.8, zorder=1)
for e in ["Parkinson", "Garman-Klass", "Rogers-Satchell"]:
    c, ls, mk = ps.STYLE[e]
    ax.plot(merged["n_med"], merged[f"{e}_pred"], color=c, linestyle=ls,
            linewidth=1.5, alpha=0.55, zorder=2)
    ax.plot(merged["n_med"], merged[f"{e}_obs"], color=c, linestyle="none",
            marker=mk, markersize=6, markeredgecolor=ps.SURFACE,
            markeredgewidth=1.1, label=e, zorder=4)
ax.plot([], [], color=ps.INK_MUTED, linestyle="-", alpha=0.55,
        label="— predicted by simulation")
ax.plot([], [], color=ps.INK_MUTED, linestyle="none", marker="o",
        label="●  observed in NEPSE data")

ax.set_xscale("log"); ps.plain_log_axis(ax, "x")
ax.set_ylim(0.3, 1.12)
ax.legend(loc="lower right", ncol=1, fontsize=7.5)
ps.finish(ax, None, None, "Median trades per day in bucket (log scale)",
          r"Range estimator ÷ open-to-close benchmark")
ps.header(fig, "Figure 4.  Predicted at the extremes, divergent in the middle",
          f"NEPSE stock-days in {NB} liquidity buckets ({len(p):,} obs). Lines = simulated undersampling "
          "prediction; markers = observed.\nNothing is fitted to NEPSE. The middle-range gap is the "
          "signature of a friction the prediction omits.", top=0.80)
for ext in ("png", "pdf"): fig.savefig(FIG / f"fig4_observed_vs_predicted.{ext}")
plt.close(fig)
print(f"\nwrote {FIG/'fig4_observed_vs_predicted.png'}")
