"""The paper's core experiment: estimator bias as a function of trading intensity.

Range-based estimators assume the observed daily high and low are the supremum and
infimum of a CONTINUOUS diffusion. With N discrete trades they are the max and min
of an N-sample, which understates the true range. Here the true sigma is known by
construction, so bias is measured exactly -- the one setting where "which estimator
is more accurate" has an unambiguous answer.

Produces Figure 2 (bias curve), Figure 3 (efficiency crossover), Table 4.
"""
import sys, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _env import bootstrap
bootstrap()

import numpy as np, pandas as pd
sys.path.insert(0, str(ROOT / "src"))
from nepsevol.sample import load_sample
import matplotlib.pyplot as plt
from nepsevol.utils import plotstyle as ps
from nepsevol.estimators import range_ as R
from nepsevol.estimators.simulate import simulate_observed_ohlc

ps.apply()
FIG = ROOT / "output" / "figures"; TAB = ROOT / "output" / "tables"
FIG.mkdir(parents=True, exist_ok=True); TAB.mkdir(parents=True, exist_ok=True)

TRUE_SIGMA = 0.02
N_DAYS     = 4000
N_REPS     = 15
WINDOW     = 21
GRID       = np.unique(np.round(np.logspace(np.log10(2), np.log10(4000), 20)).astype(int))

EST = {
    "Close-to-close":  R.close_to_close,
    "Parkinson":       R.parkinson,
    "Garman-Klass":    R.garman_klass,
    "Rogers-Satchell": R.rogers_satchell,
}

print(f"Simulating {len(GRID)} trade-intensity levels x {N_REPS} reps x {N_DAYS} days...")
rows = []
for n_tr in GRID:
    for rep in range(N_REPS):
        df = simulate_observed_ohlc(N_DAYS, TRUE_SIGMA, int(n_tr),
                                    noise_sd=0.0, seed=1000*rep + int(n_tr))
        for name, fn in EST.items():
            v = np.asarray(fn(df), dtype=float)
            # level bias: does the estimator recover sigma on average?
            m = np.nanmean(v)
            sigma_hat = np.sqrt(m) if m > 0 else 0.0
            # precision: RMSE of a rolling 21-day sigma estimate against the truth
            roll = pd.Series(v).rolling(WINDOW).mean()
            roll_sigma = np.sqrt(roll.clip(lower=0))
            rmse = float(np.sqrt(np.nanmean((roll_sigma - TRUE_SIGMA) ** 2)))
            rows.append({"n_trades": int(n_tr), "estimator": name, "rep": rep,
                         "bias_ratio": sigma_hat / TRUE_SIGMA, "rmse": rmse / TRUE_SIGMA})
sim = pd.DataFrame(rows)
agg = sim.groupby(["n_trades", "estimator"]).agg(
    bias=("bias_ratio", "mean"), bias_sd=("bias_ratio", "std"),
    rmse=("rmse", "mean")).reset_index()
agg.to_csv(TAB / "table4_simulated_bias.csv", index=False)

# ---- where does close-to-close overtake each range estimator? (the crossover N*)
piv = agg.pivot(index="n_trades", columns="estimator", values="rmse")
cross = {}
for e in ["Parkinson", "Garman-Klass", "Rogers-Satchell"]:
    better = piv["Close-to-close"] < piv[e]          # CC wins where its RMSE is lower
    idx = [n for n in piv.index if better.loc[n]]
    cross[e] = max(idx) if idx else None
print("\n=== Crossover N*: close-to-close beats the range estimator at or below N* trades/day ===")
for e, n in cross.items():
    print(f"  {e:18} N* = {n if n else '(never)'}")

# ---------------------------------------------------------------- FIGURE 2: bias curve
p = load_sample(ROOT, "equity")
nepse_p10, nepse_med, nepse_p90 = (p["n_trades"].quantile(q) for q in (.10, .50, .90))

fig, ax = plt.subplots(figsize=(6.6, 4.0))
ax.axhspan(0.995, 1.005, color=ps.GRID, zorder=0)
ax.axhline(1.0, color=ps.INK_MUTED, linewidth=0.8, zorder=1)
ax.axvspan(nepse_p10, nepse_p90, color=ps.SERIES["blue"], alpha=0.07, zorder=0)
ax.axvline(nepse_med, color=ps.INK_MUTED, linestyle=":", linewidth=1.0, zorder=1)

for name in EST:
    g = agg[agg.estimator == name].sort_values("n_trades")
    c, ls, mk = ps.STYLE[name]
    ax.plot(g["n_trades"], g["bias"], color=c, linestyle=ls, marker=mk,
            markeredgecolor=ps.SURFACE, markeredgewidth=0.9, label=name, zorder=3)
    ax.annotate(name, (g["n_trades"].iloc[0], g["bias"].iloc[0]),
                textcoords="offset points", xytext=(7, -3 if name != "Close-to-close" else 5),
                fontsize=7.5, color=c, fontweight="bold", zorder=4,
                bbox=dict(fc=ps.SURFACE, ec="none", pad=1.0))

ax.set_xscale("log"); ps.plain_log_axis(ax, "x")
ax.set_ylim(0.25, 1.12)
ax.text(nepse_med*1.12, 0.30, f"NEPSE median\n{nepse_med:.0f} trades/day",
        fontsize=7.5, color=ps.INK_SOFT)
ax.text(nepse_p10*1.05, 1.075, "NEPSE 10th–90th percentile", fontsize=7.5,
        color=ps.SERIES["blue"], fontweight="bold")
ax.text(GRID[-1]*0.42, 1.012, "unbiased", fontsize=7.5, color=ps.INK_SOFT, ha="right")
ax.legend(loc="lower right", ncol=1)
ps.finish(ax, None, None, "Trades per day (log scale)",
          r"Estimated $\sigma$ ÷ true $\sigma$")
ps.header(fig, "Range-based estimators collapse where NEPSE actually trades",
          f"Simulated GBM, true σ = {TRUE_SIGMA:.0%}/day, {N_DAYS:,} days × {N_REPS} replications per point. "
          "Shaded band is NEPSE's observed trading intensity.", top=0.84)
for ext in ("png", "pdf"): fig.savefig(FIG / f"fig2_bias_curve.{ext}")
plt.close(fig)
print(f"\nwrote {FIG/'fig2_bias_curve.png'}")

# ---------------------------------------------------------------- FIGURE 3: efficiency crossover
fig, ax = plt.subplots(figsize=(6.6, 4.0))
ax.axvspan(nepse_p10, nepse_p90, color=ps.SERIES["blue"], alpha=0.07, zorder=0)
for name in EST:
    g = agg[agg.estimator == name].sort_values("n_trades")
    c, ls, mk = ps.STYLE[name]
    ax.plot(g["n_trades"], g["rmse"], color=c, linestyle=ls, marker=mk,
            markeredgecolor=ps.SURFACE, markeredgewidth=0.9, label=name, zorder=3)
npk = cross["Parkinson"]
if npk:
    ax.axvline(npk, color=ps.SERIES["red"], linewidth=1.1, linestyle="--", zorder=2)
    ax.annotate(f"N* ≈ {npk}\nbelow this, close-to-close\nbeats Parkinson",
                (npk, ax.get_ylim()[1]*0.72), textcoords="offset points", xytext=(9, 0),
                fontsize=7.5, color=ps.SERIES["red"], fontweight="bold",
                bbox=dict(fc=ps.SURFACE, ec="none", pad=1.5))
ax.set_xscale("log"); ps.plain_log_axis(ax, "x")
ax.set_yscale("log"); ps.plain_log_axis(ax, "y")
ax.legend(loc="upper right")
ps.finish(ax, None, None, "Trades per day (log scale)",
          r"RMSE of rolling 21-day $\hat{\sigma}$, ÷ true $\sigma$")
ps.header(fig, "The efficiency advantage of range estimators reverses below N*",
          "Lower is better. The textbook 5× efficiency gain of Parkinson holds only in the dense-trading limit.",
          top=0.84)
for ext in ("png", "pdf"): fig.savefig(FIG / f"fig3_crossover.{ext}")
plt.close(fig)
print(f"wrote {FIG/'fig3_crossover.png'}")

print("\n=== TABLE 4 (excerpt): simulated bias ratio by trading intensity ===")
show = agg.pivot(index="n_trades", columns="estimator", values="bias")
print(show.loc[[n for n in [2,4,10,30,113,300,1000,4000] if n in show.index]]
      .to_string(float_format=lambda x: f"{x:.3f}"))
pd.Series(cross).to_csv(TAB / "table5_crossover.csv")
