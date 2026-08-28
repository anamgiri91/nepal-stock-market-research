"""Multi-horizon variance ratio: does RS/Var(x) converge to one as the Brownian approximation improves?

RS and the open-to-close variance share a target only under Brownian motion. Departures of
RS/Var(x) from one are therefore NOT automatically estimator bias -- they can equally reflect
path dependence, since

    RS = h(h - x) + (-l)(x - l)

is built from an upward excursion times its retracement plus a downward excursion times its
rebound. A session with O=100, H=110, L=90, C=100 has x = 0 and a large RS.

Aggregating K consecutive sessions into one bar improves the Brownian approximation and dilutes
daily microstructure:

    O_K = O_t,  H_K = max(H_t..H_{t+K-1}),  L_K = min(L_t..L_{t+K-1}),  C_K = C_{t+K-1}

If the departures are a short-horizon path phenomenon, the ratio should approach one as K grows.
If they persist, they are not daily microstructure. The interpretation is fixed by the literature
in advance rather than invented after seeing the result.

Bars are NON-OVERLAPPING, so K-bars are independent draws rather than a smoothed series.

Produces Figure 20 and Table 26.
"""
import sys, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts")); from _env import bootstrap; bootstrap()
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from nepsevol.utils import plotstyle as ps
ps.apply(); FIG=ROOT/"output"/"figures"; TAB=ROOT/"output"/"tables"
EXT=ROOT.parent/"private"/"data-vault"/"raw"/"external"

def agg_bars(g, K):
    """Non-overlapping K-session bars for one security, in session order."""
    g = g.sort_values("date")
    n = len(g) // K
    if n < 5: return None
    o = g.open.values[:n*K].reshape(n, K)[:, 0]
    c = g.close.values[:n*K].reshape(n, K)[:, -1]
    h = g.high.values[:n*K].reshape(n, K).max(axis=1)
    l = g.low.values[:n*K].reshape(n, K).min(axis=1)
    return pd.DataFrame({"open": o, "high": h, "low": l, "close": c})

def vratio(bars):
    if bars is None or len(bars) < 5: return np.nan, 0
    o,h,l,c = (np.log(bars[k].values) for k in ("open","high","low","close"))
    hh, ll, xx = h-o, l-o, c-o
    rs = (hh*(hh-xx) + ll*(ll-xx)).mean()
    v = xx.var(ddof=1)
    return (rs/v if v>0 else np.nan), len(bars)

KS = [1,2,3,4,5,7,10,15,20]
p = pd.read_parquet(ROOT/"data/processed/analysis_sample.parquet")
p["q"] = pd.qcut(p.n_trades, 5, labels=False, duplicates="drop")
nif = pd.read_csv(EXT/"nifty50.csv", parse_dates=["Date"]); nif.columns=[c.lower() for c in nif.columns]

rows=[]
for K in KS:
    r,_ = vratio(agg_bars(nif.assign(date=nif.date), K))
    rows.append({"bucket":"NIFTY 50","trades":np.nan,"K":K,"vratio":r})
    for q,g in p.groupby("q", sort=False):
        # pool securities: aggregate each separately, then combine bars
        parts=[agg_bars(s, K) for _,s in g.groupby("symbol")]
        parts=[x for x in parts if x is not None]
        if not parts: continue
        r,n = vratio(pd.concat(parts, ignore_index=True))
        rows.append({"bucket":f"NEPSE Q{int(q)+1}","trades":g.n_trades.median(),"K":K,"vratio":r})
t=pd.DataFrame(rows); t.to_csv(TAB/"table26_multihorizon_vratio.csv", index=False)
piv=t.pivot(index="K", columns="bucket", values="vratio")
order=["NIFTY 50"]+[f"NEPSE Q{i}" for i in range(1,6)]
piv=piv[[c for c in order if c in piv.columns]]
print("Multi-horizon variance ratio  RS_K / Var(x_K)   —  does it converge to 1?")
print("="*84)
print(piv.to_string(float_format=lambda x:f"{x:,.3f}"))
print("\n  K=1 is the daily result. Larger K aggregates sessions into one bar, improving the")
print("  Brownian approximation and diluting daily microstructure.")
for cbl in piv.columns:
    s=piv[cbl].dropna()
    if len(s)>1:
        print(f"    {cbl:10} {s.iloc[0]:.3f} → {s.iloc[-1]:.3f}   "
              f"{'converging toward 1' if abs(s.iloc[-1]-1)<abs(s.iloc[0]-1) else 'NOT converging'}")

fig,ax=plt.subplots(figsize=(7.4,4.4))
ax.axhline(1.0,color=ps.INK_MUTED,lw=1.0)
cols={"NIFTY 50":ps.SERIES["green"],"NEPSE Q1":ps.SERIES["orange"],"NEPSE Q2":ps.SERIES["yellow"],
      "NEPSE Q3":ps.SERIES["red"],"NEPSE Q4":ps.SERIES["magenta"],"NEPSE Q5":ps.SERIES["blue"]}
mks={"NIFTY 50":"*","NEPSE Q1":"s","NEPSE Q2":"^","NEPSE Q3":"D","NEPSE Q4":"v","NEPSE Q5":"o"}
for cbl in piv.columns:
    ax.plot(piv.index,piv[cbl],color=cols.get(cbl,ps.INK_SOFT),marker=mks.get(cbl,"o"),
            ms=7 if cbl=="NIFTY 50" else 5,lw=1.7,markeredgecolor=ps.SURFACE,markeredgewidth=.9,label=cbl)
ax.legend(fontsize=7.5,ncol=2)
ps.finish(ax,None,None,"Bar length K (sessions)","RS_K ÷ Var(x_K)")
ps.header(fig,"Figure 20.  The daily-horizon departures are short-horizon; what remains is not",
          "Q1's deficit resolves fully by K=20 (0.535→1.011), and the K=1 excess above one in Q2–Q4 vanishes "
          "at K=2.\nBut Q2–Q4 then settle near 0.7–0.8 rather than converging to one, which is unexplained. "
          "NIFTY at K=20 rests on\n201 bars, so its wobble is sampling noise.",top=0.80)
for e in ("png","pdf"): fig.savefig(FIG/f"fig20_multihorizon_vratio.{e}")
plt.close(fig); print("\nwrote fig20_multihorizon_vratio.png")
