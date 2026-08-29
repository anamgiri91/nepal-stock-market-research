"""Q10b: is it the AUCTION, or is it just thinness?

DD-007 established two facts that sit side by side without a link: price discovery concentrates
at the opening auction in thin securities, and range estimators fail in thin securities. Both
correlate with trading intensity, so neither yet explains the other.

The tautology to avoid. RS/CC factors identically into (RS/OC) x (OC/CC), and (OC/CC) is one
minus the opening share. Regressing RS/CC on the opening share therefore recovers an algebraic
identity, not a mechanism, and would be worthless.

The real test uses RS/OC -- the GENUINE bias against a matched intraday benchmark, with the scope
effect already divided out. If opening concentration carries explanatory power for that, beyond
trading intensity, then the auction degrades intraday measurement itself and is not merely a
relabelling of thinness.

Produces Figure 16 and Table 21.
"""
import sys, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts")); from _env import bootstrap; bootstrap(["statsmodels"])

import numpy as np, pandas as pd, statsmodels.api as sm
sys.path.insert(0, str(ROOT / "src"))
from nepsevol.sample import load_sample
import matplotlib.pyplot as plt
from nepsevol.utils import plotstyle as ps
from nepsevol.clean.limits import flag_limits
ps.apply(); FIG=ROOT/"output"/"figures"; TAB=ROOT/"output"/"tables"
LN2=np.log(2)

p = load_sample(ROOT, "equity").sort_values(["symbol","date"])
p = flag_limits(p)
sess={d:i for i,d in enumerate(sorted(p.date.unique()))}
p["sr"]=p.date.map(sess); p["gp"]=p.groupby("symbol").sr.diff()
p["pc"]=p.groupby("symbol").close.shift(1)
d = p[(p.gp==1) & p.pc.notna() & (p.pc>0)].copy()

o,h,l,c = np.log(d.open),np.log(d.high),np.log(d.low),np.log(d.close)
d["rs"]   = (h-o)*((h-o)-(c-o)) + (l-o)*((l-o)-(c-o))
d["v_oc"] = (c-o)**2
d["v_cc"] = (np.log(d.close/d.pc))**2
d["r_co"] = np.log(d.open/d.pc)
d["zero_range"] = (d.high==d.low)

# Per-security measures. The opening share and the estimator ratio are BOTH degenerate on
# H==L days (intraday return is zero by construction), so both are computed on non-degenerate
# days only and the degenerate rate enters separately as a control.
rows=[]
for sym,g in d.groupby("symbol"):
    nz = g[~g.zero_range]
    if len(nz) < 120: continue
    rs, oc, cc = nz.rs.mean(), nz.v_oc.mean(), nz.v_cc.mean()
    if not (rs>0 and oc>0 and cc>0): continue
    rows.append({
        "symbol": sym, "n_obs": len(g),
        "n_trades": g.n_trades.median(),
        "rs_oc":  np.sqrt(rs/oc),                       # genuine bias, scope divided out
        "open_share": nz.r_co.var()/nz.v_cc.mean(),     # concentration at the auction
        "zero_rate": g.zero_range.mean(),
        "pinned":  g.open_pinned.mean(),
        "nomatch": g.open_at_prev_close.mean(),
    })
S = pd.DataFrame(rows)
S = S[np.isfinite(S.rs_oc) & (S.rs_oc<3) & np.isfinite(S.open_share) & (S.open_share<3)]
S["log_n"] = np.log(S.n_trades)
print(f"per-security sample: {len(S)} securities with >=120 non-degenerate sessions\n")

def fit(cols, label):
    X = sm.add_constant(S[cols], has_constant="add")
    r = sm.OLS(S.rs_oc, X).fit(cov_type="HC1")
    return r, label

specs = [fit(["log_n"], "(1) intensity only"),
         fit(["open_share"], "(2) auction share only"),
         fit(["log_n","open_share"], "(3) both"),
         fit(["log_n","open_share","zero_rate"], "(4) + degenerate rate"),
         fit(["log_n","open_share","zero_rate","pinned","nomatch"], "(5) + auction outcomes")]

print("Does auction concentration explain estimator bias BEYOND trading intensity?")
print("dependent variable: Rogers-Satchell / matched open-to-close benchmark, per security")
print("="*94)
hdr = f"{'':26}" + "".join(f"{s[1].split(') ')[0]+')':>13}" for s in specs)
print(hdr)
for v in ["log_n","open_share","zero_rate","pinned","nomatch"]:
    line=f"  {v:24}"
    for r,_ in specs:
        line += f"{(f'{r.params[v]:+.3f}' if v in r.params else '—'):>13}"
    print(line)
    line=f"  {'':24}"
    for r,_ in specs:
        line += f"{(f'({r.tvalues[v]:.1f})' if v in r.params else ''):>13}"
    print(line)
print(f"  {'R²':24}" + "".join(f"{r.rsquared:>13.3f}" for r,_ in specs))
print(f"  {'n':24}" + "".join(f"{int(r.nobs):>13}" for r,_ in specs))
for i,(r,lab) in enumerate(specs): print(f"    {lab}")

r3 = specs[2][0]
print(f"\n  incremental R² from adding auction share to intensity: "
      f"{r3.rsquared - specs[0][0].rsquared:+.3f}")
print(f"  open_share p-value in (3): {r3.pvalues['open_share']:.3e}")
S.to_csv(TAB/"table21_auction_mechanism.csv", index=False)

# ── Figure 16 ────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1,2, figsize=(10.2,4.0))
ax=axes[0]
sc=ax.scatter(S.open_share, S.rs_oc, c=np.log10(S.n_trades), s=22, cmap="viridis",
              alpha=.8, edgecolors=ps.SURFACE, linewidths=.4)
xs=np.linspace(S.open_share.quantile(.02), S.open_share.quantile(.98), 50)
b=specs[2][0].params
ax.plot(xs, b["const"]+b["open_share"]*xs+b["log_n"]*S.log_n.mean(),
        color=ps.SERIES["red"], lw=2.0)
cb=fig.colorbar(sc, ax=ax); cb.set_label("log₁₀ trades/day", fontsize=8)
cb.ax.tick_params(labelsize=7)
ax.axhline(1.0, color=ps.INK_MUTED, lw=.8)
ps.finish(ax,"A. Weak positive slope, wide scatter",None,
          "Share of variance realized at the open","Rogers–Satchell ÷ open-to-close")

ax=axes[1]
S["q"]=pd.qcut(S.open_share,5,labels=False,duplicates="drop")
g=S.groupby("q").agg(sh=("open_share","median"), rr=("rs_oc","median"),
                     nn=("n_trades","median"))
ax.axhline(1.0,color=ps.INK_MUTED,lw=.8)
ax.plot(g.sh, g.rr, color=ps.SERIES["orange"], marker="s", ms=7,
        markeredgecolor=ps.SURFACE, markeredgewidth=1.0)
for _,r in g.iterrows():
    ax.annotate(f"{r.nn:.0f} trades/day",(r.sh,r.rr),textcoords="offset points",
                xytext=(6,-11),fontsize=7,color=ps.INK_MUTE if hasattr(ps,'INK_MUTE') else ps.INK_SOFT)
ps.finish(ax,"B. Quintile medians — note the axis range",None,
          "Median share realized at the open","Median RS ÷ open-to-close")
ps.header(fig,"Figure 16.  Auction concentration matters statistically, and barely at all economically",
          "Each point is one security; the outcome divides out the scope effect, so this is not the identity "
          "RS/CC=(RS/OC)×(OC/CC).\nThe slope is significant (p = 2e-4) but the median ratio moves only "
          "1.01→1.06 across the full range. Note panel B's axis.", top=0.82)
for e in ("png","pdf"): fig.savefig(FIG/f"fig16_auction_mechanism.{e}")
plt.close(fig); print(f"\nwrote fig16_auction_mechanism.png")
