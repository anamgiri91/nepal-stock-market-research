"""Time-series diagnostics: ACF structure, calendar effects, and whether the
model-based escape route (GARCH) survives thin trading.

Motivation. Every range estimator in the paper assumes a Gaussian diffusion. Every
model-based alternative assumes an estimable volatility process. Both assumptions are
checked here against liquidity, because if the model-based route also fails on thin
stocks then the paper's negative result is much broader than "use close-to-close".

Produces Figures 9-11 and Tables 10-12.
"""
import sys, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _env import bootstrap
bootstrap(["statsmodels", "arch"])

import numpy as np, pandas as pd
sys.path.insert(0, str(ROOT / "src"))
from nepsevol.sample import load_sample
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import acf
from statsmodels.stats.diagnostic import acorr_ljungbox
from scipy import stats as sps
from arch import arch_model
from nepsevol.utils import plotstyle as ps

ps.apply()
FIG = ROOT/"output"/"figures"; TAB = ROOT/"output"/"tables"
p = load_sample(ROOT, "equity").sort_values(["symbol","date"])

# stratify securities into three liquidity groups by median trade count
med = p.groupby("symbol")["n_trades"].median()
cnt = p.groupby("symbol").size()
elig = med[cnt >= 200].sort_values()
GROUPS = {"Thin (bottom third)":   elig.iloc[:len(elig)//3].index,
          "Middle third":          elig.iloc[len(elig)//3:2*len(elig)//3].index,
          "Liquid (top third)":    elig.iloc[2*len(elig)//3:].index}
COL = {"Thin (bottom third)": ps.SERIES["orange"], "Middle third": ps.SERIES["aqua"],
       "Liquid (top third)": ps.SERIES["blue"]}
MK  = {"Thin (bottom third)": "s", "Middle third": "^", "Liquid (top third)": "o"}
print("liquidity groups:", {k: f"{len(v)} securities, median {med[v].median():.0f} trades/day"
                            for k, v in GROUPS.items()})

NLAG = 25
def group_acf(syms, col, square=False):
    """Average ACF across securities in a group (each security's own ACF, then averaged)."""
    out = []
    for s in syms:
        r = p.loc[p.symbol == s, col].dropum() if False else p.loc[p.symbol == s, col].dropna()
        if len(r) < 150: continue
        x = r.values**2 if square else r.values
        out.append(acf(x, nlags=NLAG, fft=True))
    return (np.nanmean(np.vstack(out), axis=0), len(out)) if out else (None, 0)

# ---------------------------------------------------------------- FIGURE 9: ACF plots
fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.4))
lags = np.arange(NLAG+1)
rows = []
for sq, ax, ttl in [(False, axes[0], "A. Returns"), (True, axes[1], "B. Squared returns")]:
    for gname, syms in GROUPS.items():
        a, n = group_acf(syms, "cc", square=sq)
        if a is None: continue
        ax.plot(lags[1:], a[1:], color=COL[gname], marker=MK[gname], ms=3.5,
                lw=1.4, markeredgecolor=ps.SURFACE, markeredgewidth=0.6, label=gname)
        rows += [{"series": "squared" if sq else "returns", "group": gname,
                  "lag": int(l), "acf": float(v)} for l, v in zip(lags[1:6], a[1:6])]
    nobs = int(cnt.median())
    band = 1.96/np.sqrt(nobs)
    ax.axhspan(-band, band, color=ps.GRID, zorder=0)
    ax.axhline(0, color=ps.INK_MUTED, lw=0.8)
    ps.finish(ax, ttl, None, "Lag (trading days)", "Autocorrelation")
axes[0].legend(loc="lower right", fontsize=7.5)
axes[0].text(NLAG*0.98, 1.96/np.sqrt(int(cnt.median()))*1.15, "95% band", ha="right",
             fontsize=7, color=ps.INK_SOFT)
ps.header(fig, "Figure 9.  Autocorrelation structure by liquidity",
          "Mean per-security ACF within each liquidity third. Thin stocks show strong negative "
          "first-order return\nautocorrelation (bid-ask bounce) and weaker volatility persistence.", top=0.82)
for e in ("png","pdf"): fig.savefig(FIG/f"fig9_acf.{e}")
plt.close(fig)
pd.DataFrame(rows).to_csv(TAB/"table10_acf.csv", index=False)

# ---------------------------------------------------------------- FIGURE 10: calendar effects
p["dow"] = p["date"].dt.day_name()
ORDER = ["Sunday","Monday","Tuesday","Wednesday","Thursday"]
dw = p[p.dow.isin(ORDER)].groupby("dow").agg(
    abs_ret=("cc", lambda s: s.abs().mean()),
    rng=("hl","mean"), trades=("n_trades","median"), zero=("cc", lambda s: (s==0).mean()*100)
).reindex(ORDER).reset_index()
dw.to_csv(TAB/"table11_calendar.csv", index=False)

fig, axes = plt.subplots(1, 3, figsize=(7.8, 2.9))
for ax, col, lbl, colr in [(axes[0],"abs_ret","Mean |return|",ps.SERIES["blue"]),
                           (axes[1],"rng","Mean ln(H/L)",ps.SERIES["orange"]),
                           (axes[2],"zero","Zero-return days (%)",ps.SERIES["aqua"])]:
    bars = ax.bar(range(5), dw[col], color=colr, width=0.62)
    ax.set_xticks(range(5)); ax.set_xticklabels([d[:3] for d in ORDER])
    for i,(b,v) in enumerate(zip(bars, dw[col])):
        ax.text(b.get_x()+b.get_width()/2, v, f"{v:.3f}" if col!="zero" else f"{v:.1f}",
                ha="center", va="bottom", fontsize=7, color=ps.INK_SOFT)
    ax.margins(y=0.18)
    ps.finish(ax, lbl, None, None, None)
ps.header(fig, "Figure 10.  Calendar effects under a Sunday–Thursday week",
          "Sunday follows a two-day weekend; Thursday precedes it. Any annualization or "
          "overnight-return\nconvention borrowed from a Monday–Friday market misallocates this variance.", top=0.78)
for e in ("png","pdf"): fig.savefig(FIG/f"fig10_calendar.{e}")
plt.close(fig)

# ---------------------------------------------------------------- FIGURE 11: GBM + GARCH viability
res = []
rng = np.random.default_rng(3)
for gname, syms in GROUPS.items():
    pick = rng.choice(np.array(syms), size=min(45, len(syms)), replace=False)
    for s in pick:
        r = p.loc[p.symbol == s, "cc"].dropna()
        if len(r) < 250: continue
        lb = acorr_ljungbox(r**2, lags=[10], return_df=True)["lb_pvalue"].iloc[0]
        ok, alpha_beta = False, np.nan
        try:
            fit = arch_model(r*100, vol="Garch", p=1, q=1, dist="normal").fit(disp="off", show_warning=False)
            pr = fit.params
            alpha_beta = float(pr.get("alpha[1]",np.nan) + pr.get("beta[1]",np.nan))
            ok = bool(fit.convergence_flag == 0 and np.isfinite(alpha_beta) and alpha_beta < 1.0)
        except Exception:
            pass
        res.append({"group":gname,"symbol":s,"kurtosis":float(sps.kurtosis(r,fisher=False)),
                    "jb_p":float(sps.jarque_bera(r)[1]),"lb_sq_p":float(lb),
                    "garch_ok":ok,"persistence":alpha_beta})
g = pd.DataFrame(res)
g.to_csv(TAB/"table12_garch_viability.csv", index=False)
summ = g.groupby("group").agg(
    n=("symbol","size"), kurtosis=("kurtosis","median"),
    normal_pct=("jb_p", lambda s: 100*(s>0.05).mean()),
    arch_pct=("lb_sq_p", lambda s: 100*(s<0.05).mean()),
    garch_ok_pct=("garch_ok", lambda s: 100*s.mean()),
    persistence=("persistence","median")).reindex(list(GROUPS)).reset_index()

fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.2))
ax = axes[0]
bars = ax.bar(range(3), summ["kurtosis"], color=[COL[k] for k in summ["group"]], width=0.6)
ax.axhline(3, color=ps.SERIES["red"], ls="--", lw=1.2)
ax.text(2.45, 3, " Gaussian = 3", va="bottom", ha="right", fontsize=7.5,
        color=ps.SERIES["red"], fontweight="bold")
for b,v in zip(bars, summ["kurtosis"]):
    ax.text(b.get_x()+b.get_width()/2, v, f"{v:.0f}", ha="center", va="bottom",
            fontsize=8, color=ps.INK_SOFT)
ax.set_xticks(range(3)); ax.set_xticklabels(["Thin","Middle","Liquid"])
ax.set_yscale("log"); ps.plain_log_axis(ax,"y"); ax.margins(y=0.25)
ps.finish(ax, "A. Return kurtosis — high everywhere", None, None, "Kurtosis")
ax = axes[1]
w=0.38; x=np.arange(3)
ax.bar(x-w/2, summ["arch_pct"], w, color=ps.SERIES["aqua"], label="ARCH effects present")
ax.bar(x+w/2, summ["garch_ok_pct"], w, color=ps.SERIES["violet"], label="GARCH(1,1) converges")
for xi,v in zip(x-w/2, summ["arch_pct"]):   ax.text(xi,v,f"{v:.0f}",ha="center",va="bottom",fontsize=7,color=ps.INK_SOFT)
for xi,v in zip(x+w/2, summ["garch_ok_pct"]):ax.text(xi,v,f"{v:.0f}",ha="center",va="bottom",fontsize=7,color=ps.INK_SOFT)
ax.set_xticks(x); ax.set_xticklabels(["Thin","Middle","Liquid"]); ax.set_ylim(0,112)
ax.legend(fontsize=7.5, loc="lower right")
ps.finish(ax, "B. The model-based route stays available", None, None, "Percent of securities")
ps.header(fig, "Figure 11.  The model-based route survives thin trading; the range route does not",
          "Returns are non-Gaussian at every liquidity level (normality rejected for 100% of securities), "
          "and kurtosis is\nnot worst in thin stocks. GARCH(1,1) converges throughout — only ARCH "
          "detectability attenuates.", top=0.80)
for e in ("png","pdf"): fig.savefig(FIG/f"fig11_gbm_garch.{e}")
plt.close(fig)

print("\n=== TABLE 11: calendar effects (Sun-Thu) ===")
print(dw.to_string(index=False, float_format=lambda x:f"{x:,.4f}"))
print("\n=== TABLE 12: distributional and GARCH viability by liquidity ===")
print(summ.to_string(index=False, float_format=lambda x:f"{x:,.1f}"))
print("\nwrote fig9_acf.png, fig10_calendar.png, fig11_gbm_garch.png")
