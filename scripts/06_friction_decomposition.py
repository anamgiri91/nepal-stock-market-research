"""Decompose the three competing frictions acting on range-based estimators.

  D1  undersampling of the path within the traded window   -> biases range DOWN
  D2  traded-window truncation (window shorter than session)-> biases range DOWN
  U1  microstructure noise in the extremes                  -> biases range UP

Produces Figure 6.
"""
import sys, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _env import bootstrap
bootstrap()
import numpy as np, pandas as pd, matplotlib.pyplot as plt
sys.path.insert(0, str(ROOT / "src"))
from nepsevol.sample import load_sample
from nepsevol.utils import plotstyle as ps
from nepsevol.estimators import range_ as R
from nepsevol.estimators.simulate import simulate_observed_ohlc

ps.apply()
FIG = ROOT/"output"/"figures"; TAB = ROOT/"output"/"tables"
LN2 = np.log(2); SIG = 0.02; GRID = [2,4,6,10,15,22,30,49,73,113,167,282,569,1168,2500]

rows=[]
for n in GRID:
    for rep in range(8):
        for nz,lab in [(0.0,"D1+D2 only (no noise)"),(0.003,"+ moderate noise"),(0.008,"+ high noise")]:
            df = simulate_observed_ohlc(4000, SIG, n, noise_sd=nz, seed=31+rep*13+n)
            pk = np.nanmean(R.parkinson(df))
            oc = np.nanmean(np.log(df.close/df.open)**2)
            cc = np.nanmean(df["true_cc"]**2)
            rows.append({"n":n,"case":lab,"pk_cc":np.sqrt(pk/cc),
                         "oc_cc":np.sqrt(oc/cc),"pk_oc":np.sqrt(pk/oc)})
s = pd.DataFrame(rows).groupby(["n","case"]).mean().reset_index()
s.to_csv(TAB/"table7_friction_decomposition.csv", index=False)

base = s[s.case=="D1+D2 only (no noise)"].sort_values("n")
fig, ax = plt.subplots(figsize=(6.8,4.2))
ax.axhline(1.0, color=ps.INK_MUTED, lw=0.8)

p = load_sample(ROOT, "equity")
ax.axvspan(p["n_trades"].quantile(.10), p["n_trades"].quantile(.90),
           color=ps.SERIES["blue"], alpha=0.07, zorder=0)

ax.plot(base["n"], base["oc_cc"], color=ps.SERIES["violet"], ls="--", marker="v",
        markeredgecolor=ps.SURFACE, markeredgewidth=0.9,
        label="D2 alone: traded window ÷ calendar day")
ax.plot(base["n"], base["pk_cc"], color=ps.SERIES["orange"], ls="-", marker="s",
        markeredgecolor=ps.SURFACE, markeredgewidth=0.9,
        label="D1+D2: Parkinson ÷ close-to-close")
for nz,lab,col in [("+ moderate noise","+ noise (σ=0.3%)",ps.SERIES["aqua"]),
                   ("+ high noise","+ noise (σ=0.8%)",ps.SERIES["red"])]:
    g = s[s.case==nz].sort_values("n")
    ax.plot(g["n"], g["pk_cc"], color=col, ls=":", marker="o", ms=4,
            markeredgecolor=ps.SURFACE, markeredgewidth=0.8, label=lab)

ax.set_xscale("log"); ps.plain_log_axis(ax,"x"); ax.set_ylim(0, 2.0)
ax.legend(loc="upper left", fontsize=7.5)
ps.finish(ax, None, None, "Trades per day (log scale)", r"Ratio to true daily $\sigma$")
ps.header(fig, "Figure 6.  Three frictions, two directions",
          "Undersampling and window truncation bias the range down; noise in the extremes biases it up.\n"
          "The net bias is non-monotonic in liquidity, so no single monotone correction can work.", top=0.80)
for e in ("png","pdf"): fig.savefig(FIG/f"fig6_decomposition.{e}")
plt.close(fig)
print("wrote fig6_decomposition.png")
print("\n=== D2 alone: fraction of daily variance captured by the traded window ===")
print(base[["n","oc_cc"]].to_string(index=False, float_format=lambda x:f"{x:.3f}"))
