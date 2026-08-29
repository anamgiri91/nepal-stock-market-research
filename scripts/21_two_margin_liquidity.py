"""SUPERSEDED 2026-08-27 by DD-018 -- DO NOT USE.

This script produced the two-margin result whose conclusion was withdrawn: in the full
universe it measured asset-class mixing, and within equity it rested on three securities
(dropping NLO, BNL and UNL takes the participation R-squared from 0.851 to 0.040).

Retained only so the retracted analysis stays reproducible. It reads the mixed universe
deliberately. Excluded from the active pipeline.
"""
import sys; sys.exit("21_two_margin_liquidity.py is SUPERSEDED (DD-018); refusing to run.")

"""Liquidity has two margins, and the paper had been measuring only one.

Every liquidity statistic in this project came from median trade count on days a security APPEARS
in the daily cross-section. That is the INTENSIVE margin -- how much it trades when it trades. It
is silent on the EXTENSIVE margin: whether it trades at all.

The two are not interchangeable. Two securities averaging five trades per exchange session can be
completely different objects:

    A  trades every session, five times          -> continuous price observation
    B  trades once in five sessions, 25 times    -> intermittent price observation

A range estimator sees a fundamentally different process in each case, yet a trade-count average
assigns them the same value.

Produces Figure 21 and Table 27.
"""
import sys, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts")); from _env import bootstrap; bootstrap(["statsmodels"])
import numpy as np, pandas as pd, statsmodels.api as sm
import matplotlib.pyplot as plt
from nepsevol.utils import plotstyle as ps
ps.apply(); FIG=ROOT/"output"/"figures"; TAB=ROOT/"output"/"tables"

p=pd.read_parquet(ROOT/"data/processed/analysis_sample.parquet")
cal=pd.read_csv(ROOT/"data/processed/nepse_trading_calendar.csv",parse_dates=["date"])
sess={d:i for i,d in enumerate(cal.loc[cal.is_session,"date"].sort_values().values)}
p["sr"]=p.date.map(sess)
LN2=np.log(2)
o,h,l,c=(np.log(p[k]) for k in ("open","high","low","close"))
p["var_pk"]=((h-l)**2)/(4*LN2); p["var_oc"]=(c-o)**2
p["rs"]=(h-o)*((h-o)-(c-o))+(l-o)*((l-o)-(c-o))
p["pk_zero"]=(p.high==p.low)

# ── per-security: the two margins ──
rec=[]
for sym,s in p.groupby("symbol"):
    lo,hi=s.sr.min(),s.sr.max(); avail=hi-lo+1
    if avail<60 or len(s)<20: continue
    oc=s.var_oc.mean()
    rec.append({"symbol":sym,
        "participation":len(s)/avail,                 # extensive margin
        "trades_active":s.n_trades.median(),          # intensive margin
        "trades_all":s.n_trades.median()*len(s)/avail,
        "pk_zero":s.pk_zero.mean(),
        "rs_oc":s.rs.mean()/oc if oc>0 else np.nan,
        "n_obs":len(s)})
S=pd.DataFrame(rec).dropna()
S=S[np.isfinite(S.rs_oc)&(S.rs_oc<5)]
print(f"per-security sample: {len(S)} securities\n")

print("Do the two margins actually vary independently?")
print("="*70)
print(f"  participation : min {S.participation.min():.2f}  p25 {S.participation.quantile(.25):.2f}  "
      f"median {S.participation.median():.2f}  max {S.participation.max():.2f}")
print(f"  trades|active : min {S.trades_active.min():.0f}  p25 {S.trades_active.quantile(.25):.0f}  "
      f"median {S.trades_active.median():.0f}  max {S.trades_active.max():.0f}")
print(f"  Spearman(participation, trades|active) = "
      f"{S.participation.corr(S.trades_active,method='spearman'):.3f}")

# ── 3x3 grid ──
S["pg"]=pd.qcut(S.participation.rank(method="first"),3,labels=["low","mid","high"])
S["ig"]=pd.qcut(S.trades_active.rank(method="first"),3,labels=["low","mid","high"])
print("\n3x3 grid: P(H=L), i.e. how often Parkinson is uninformative")
print(S.pivot_table(index="pg",columns="ig",values="pk_zero",aggfunc="median").to_string(float_format=lambda x:f"{100*x:,.1f}%"))
print("\n3x3 grid: securities per cell")
print(S.pivot_table(index="pg",columns="ig",values="symbol",aggfunc="count").to_string())
print("\n3x3 grid: RS / Var-scale open-to-close")
print(S.pivot_table(index="pg",columns="ig",values="rs_oc",aggfunc="median").to_string(float_format=lambda x:f"{x:,.3f}"))

# ── which margin dominates? ──
S["log_int"]=np.log1p(S.trades_active)
print("\n\nWhich margin explains the failure? (dependent: P(H=L) per security)")
print("="*78)
specs=[("participation only",["participation"]),
       ("intensity only",["log_int"]),
       ("both",["participation","log_int"])]
print(f"  {'specification':22}{'participation':>16}{'log intensity':>16}{'R²':>9}")
for lab,cols in specs:
    r=sm.OLS(S.pk_zero,sm.add_constant(S[cols],has_constant="add")).fit(cov_type="HC1")
    pa=f"{r.params['participation']:+.3f} ({r.tvalues['participation']:.1f})" if "participation" in r.params else "—"
    li=f"{r.params['log_int']:+.3f} ({r.tvalues['log_int']:.1f})" if "log_int" in r.params else "—"
    print(f"  {lab:22}{pa:>16}{li:>16}{r.rsquared:>9.3f}")
S.to_csv(TAB/"table27_two_margins.csv",index=False)

fig,axes=plt.subplots(1,2,figsize=(10.4,4.0))
ax=axes[0]
sc=ax.scatter(S.trades_active,S.participation,c=100*S.pk_zero,s=26,cmap="magma_r",
              alpha=.85,edgecolors=ps.SURFACE,linewidths=.4)
ax.set_xscale("log"); ps.plain_log_axis(ax,"x")
cb=fig.colorbar(sc,ax=ax); cb.set_label("P(H = L), %",fontsize=8); cb.ax.tick_params(labelsize=7)
ps.finish(ax,"A. The two margins are nearly collinear here",None,
          "Median trades on days it trades (log)","Participation rate")
ax=axes[1]
g=S.groupby(pd.qcut(S.participation,6,duplicates="drop")).agg(
    part=("participation","median"),pk=("pk_zero","median"),n=("symbol","size"))
ax.plot(100*g.part,100*g.pk,color=ps.SERIES["orange"],marker="s",ms=7,lw=1.8,
        markeredgecolor=ps.SURFACE,markeredgewidth=1.0)
for _,r in g.iterrows():
    ax.annotate(f"n={int(r.n)}",(100*r.part,100*r.pk),textcoords="offset points",
                xytext=(5,5),fontsize=7,color=ps.INK_SOFT)
ps.finish(ax,"B. Failure against the extensive margin",None,
          "Participation rate (% of sessions traded)","P(H = L), %")
ps.header(fig,"Figure 21.  Liquidity has two margins, and the paper had measured only one",
          "Every earlier statistic used trade count on days a security APPEARS — the intensive margin. "
          "Participation,\nthe extensive margin, was invisible: the thinnest bucket trades on 19.5% of sessions, "
          "once when it does.",top=0.82)
for e in ("png","pdf"): fig.savefig(FIG/f"fig21_two_margins.{e}")
plt.close(fig); print("\nwrote fig21_two_margins.png")
