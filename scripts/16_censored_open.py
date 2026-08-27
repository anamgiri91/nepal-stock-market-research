"""Recovering latent opening volatility from the banded call auction.

The pre-open band censors the opening return at a KNOWN point, and the opening return carries
most of the daily variance in thin securities. Two-sided Tobit recovers the latent standard
deviation; validated in tests/test_models.py to within ~1% even at 74% censoring.

Restricted to the pre-2026-04 regime (band = 2%) so the two censoring regimes are not mixed.

Produces Figure 17 and Table 22.
"""
import sys, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts")); from _env import bootstrap; bootstrap()
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from nepsevol.utils import plotstyle as ps
from nepsevol.models.censored import tobit_sigma
ps.apply(); FIG=ROOT/"output"/"figures"; TAB=ROOT/"output"/"tables"
BAND=0.02

p=pd.read_parquet(ROOT/"data/processed/analysis_sample.parquet").sort_values(["symbol","date"])
p=p[p.date < pd.Timestamp("2026-04-01")]                       # single censoring regime
sess={d:i for i,d in enumerate(sorted(p.date.unique()))}
p["sr"]=p.date.map(sess); p["gp"]=p.groupby("symbol").sr.diff()
p["pc"]=p.groupby("symbol").close.shift(1)
d=p[(p.gp==1)&p.pc.notna()&(p.pc>0)].copy()
d["r_co"]=np.log(d.open/d.pc)
d["r_cc"]=np.log(d.close/d.pc)

rows=[]
for sym,g in d.groupby("symbol"):
    out=tobit_sigma(g.r_co.values, band=BAND)
    if not np.isfinite(out["sigma_latent"]): continue
    rows.append({"symbol":sym,"n_trades":g.n_trades.median(),
                 "sigma_naive":out["sigma_naive"],"sigma_latent":out["sigma_latent"],
                 "inflation":out["inflation"],"censored_share":out["censored_share"],
                 "nomatch":float((g.r_co==0).mean()),"n":out["n"],
                 "sd_cc":g.r_cc.std()})
S=pd.DataFrame(rows)
S=S[(S.inflation>0.5)&(S.inflation<10)]
# A single normal cannot fit a BIMODAL opening return -- mass near zero plus mass pinned at the
# band. Where that shape occurs the MLE fits the tight interior, under-predicts the boundary
# mass, and returns sigma BELOW the raw sd, which is impossible under the model. Those cases are
# misspecification rather than correction and are excluded, with the count reported.
n_misfit = int((S.inflation < 1.0).sum())
S = S[S.inflation >= 1.0]
print(f"  excluded {n_misfit} securities where the normal Tobit is misspecified "
      f"(latent < observed, bimodal opening return)")
S.to_csv(TAB/"table22_censored_open.csv",index=False)

print(f"Latent vs observed opening volatility  ({len(S)} securities, band = {BAND:.0%}, "
      f"pre-2026-04)")
print("="*80)
print(f"  median share of opens pinned at the band : {S.censored_share.median():.1%}")
print(f"  median inflation factor (latent ÷ naive) : {S.inflation.median():.3f}")
print(f"  mean   inflation factor                  : {S.inflation.mean():.3f}")
print(f"  90th percentile                          : {S.inflation.quantile(.90):.3f}")
print(f"  securities understated by >25%           : {(S.inflation>1.25).mean():.1%}")

S["q"]=pd.qcut(S.n_trades,5,labels=False,duplicates="drop")
g=S.groupby("q").agg(trades=("n_trades","median"),cens=("censored_share","median"),
                     infl=("inflation","median"),naive=("sigma_naive","median"),
                     latent=("sigma_latent","median"))
g.index=[f"Q{i+1}" for i in g.index]
print("\nBy liquidity quintile:")
print(g.to_string(float_format=lambda x:f"{x:,.4f}"))

# how much of daily variance does the censoring hide?
S["share_hidden"]=(S.sigma_latent**2 - S.sigma_naive**2)/(S.sd_cc**2)
print(f"\n  Variance hidden by the band, as a share of total daily variance:")
print(f"    median {S.share_hidden.median():.1%}   mean {S.share_hidden.mean():.1%}   "
      f"p90 {S.share_hidden.quantile(.9):.1%}")

fig,axes=plt.subplots(1,2,figsize=(10.2,4.0))
ax=axes[0]
ax.scatter(S.censored_share*100,S.inflation,s=20,color=ps.SERIES["blue"],alpha=.65,
           edgecolors=ps.SURFACE,linewidths=.4)
ax.axhline(1.0,color=ps.INK_MUTED,lw=.9)
ax.set_yscale("log"); ps.plain_log_axis(ax,"y")
ps.finish(ax,"A. The more censoring, the larger the correction",None,
          "Share of opens pinned at the band (%)","Latent σ ÷ observed σ (log)")
ax=axes[1]
w=.38; ix=np.arange(len(g))
ax.bar(ix-w/2,g.naive*100,w,color=ps.SERIES["orange"],label="observed (censored)")
ax.bar(ix+w/2,g.latent*100,w,color=ps.SERIES["aqua"],label="latent (Tobit)")
for i,(a,b) in enumerate(zip(g.naive*100,g.latent*100)):
    ax.text(i-w/2,a,f"{a:.2f}",ha="center",va="bottom",fontsize=7,color=ps.INK_SOFT)
    ax.text(i+w/2,b,f"{b:.2f}",ha="center",va="bottom",fontsize=7,color=ps.INK_SOFT)
ax.set_xticks(ix); ax.set_xticklabels([f"{r.trades:.0f}\ntrades/day" for _,r in g.iterrows()],fontsize=7.5)
ax.legend(fontsize=7.5); ax.margins(y=.18)
ps.finish(ax,"B. Opening volatility, observed vs latent",None,None,"Daily σ of opening return (%)")
ps.header(fig,"Figure 17.  The pre-open band hides opening volatility, and the censoring point is known exactly",
          "Two-sided Tobit recovers the latent standard deviation from the interior observations plus the "
          "censored mass.\nValidated to within ~1% at censoring rates up to 74%.",top=0.82)
for e in ("png","pdf"): fig.savefig(FIG/f"fig17_censored_open.{e}")
plt.close(fig); print("\nwrote fig17_censored_open.png")
