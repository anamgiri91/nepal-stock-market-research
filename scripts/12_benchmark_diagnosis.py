"""Diagnosing the reported downward bias of Rogers-Satchell.

Maheswaran & Kumar (2013) report VRatio = RS / "usual" = 0.82 on the Nifty index and attribute
the shortfall to the random-walk (discrete-step) effect, motivating their ABC correction.

Rogers-Satchell is an OPEN-TO-CLOSE estimator: it is built from log(H/O), log(L/O) and log(C/O)
and cannot, by construction, see the overnight gap. The "usual" estimator is the variance of
CLOSE-TO-CLOSE returns and spans the full calendar day. Any ratio between them therefore mixes
two distinct things: discretisation bias, and the share of daily variance that occurs overnight.

This script separates them exactly:  RS/CC = (RS/OC) x (OC/CC).

Produces Figure 14 and Table 18.
"""
import sys, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
from _env import bootstrap
bootstrap()
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from nepsevol.utils import plotstyle as ps
ps.apply()
EXT=ROOT.parent/"private"/"data-vault"/"raw"/"external"
VAULT=ROOT.parent/"private"/"data-vault"/"raw"
FIG=ROOT/"output"/"figures"; TAB=ROOT/"output"/"tables"

def decompose(df, label, panel=False):
    """panel=True: close-to-close and overnight must be computed WITHIN security.
    Differencing a pooled panel differences across securities and is meaningless."""
    d=df[(df[["open","high","low","close"]]>0).all(axis=1)].copy()
    d=d.sort_values(["symbol","date"]) if panel else d.sort_values("date")
    o,h,l,c=np.log(d.open),np.log(d.high),np.log(d.low),np.log(d.close)
    rs=((h-o)*((h-o)-(c-o))+(l-o)*((l-o)-(c-o))).mean()
    if panel:
        # Restrict to strictly consecutive TRADING SESSIONS. Otherwise a thin security's
        # "overnight" return spans however many days since it last traded (mean 4.3 days in
        # the thin sixth), which mechanically inflates overnight variance.
        sess={dt:i for i,dt in enumerate(sorted(d.date.unique()))}
        sr=d.date.map(sess); ok=d.groupby("symbol")[sr.name if sr.name else "date"].transform("size")*0==0
        gap=sr.groupby(d.symbol).diff()
        prev_c=np.log(d.groupby("symbol").close.shift(1))
        r_cc=(c-prev_c).where(gap==1); r_on=(o-prev_c).where(gap==1)
    else:
        r_cc=c.diff(); r_on=(o-c.shift(1))
    r_oc=(c-o)
    v_cc,v_oc,v_on=r_cc.var(),r_oc.var(),r_on.var()
    return {"market":label,"n":len(d),"RS/close-to-close":rs/v_cc,"RS/open-to-close":rs/v_oc,
            "open-to-close ÷ close-to-close":v_oc/v_cc,"overnight share":v_on/v_cc,
            "zero-range %":100*(d.high==d.low).mean()}

nifty=pd.read_csv(EXT/"nifty50.csv",parse_dates=["Date"]); nifty.columns=[x.lower() for x in nifty.columns]
idx=pd.read_csv(VAULT/"nepse_index_history.csv",parse_dates=["Date"]); idx.columns=[x.lower() for x in idx.columns]
nep=idx[idx.date>=pd.Timestamp("2016-06-06")]
panel=pd.read_parquet(ROOT/"data/processed/analysis_sample.parquet")
thin=panel[panel.n_trades<=panel.n_trades.quantile(0.167)]
dense=panel[panel.n_trades>=panel.n_trades.quantile(0.833)]

rows=[decompose(nifty,"NIFTY 50 index"), decompose(nep,"NEPSE index"),
      decompose(dense,"NEPSE stocks — dense",panel=True), decompose(thin,"NEPSE stocks — thin",panel=True)]
t=pd.DataFrame(rows).set_index("market")
t.to_csv(TAB/"table18_benchmark_diagnosis.csv")
print("Where does the reported Rogers-Satchell 'bias' come from?")
print("  Maheswaran & Kumar (2013) report RS/usual = 0.82 on Nifty and attribute it to")
print("  the random-walk effect. Exact decomposition:  RS/CC = (RS/OC) x (OC/CC)\n")
print(t.to_string(float_format=lambda x:f"{x:,.3f}"))

fig,axes=plt.subplots(1,2,figsize=(10.4,4.0))
ax=axes[0]
ix=np.arange(len(t)); w=0.38
ax.bar(ix-w/2,t["RS/close-to-close"],w,color=ps.SERIES["orange"],label="RS ÷ close-to-close  (M&K statistic)")
ax.bar(ix+w/2,t["RS/open-to-close"],w,color=ps.SERIES["aqua"],label="RS ÷ open-to-close  (matched scope)")
ax.axhline(1.0,color=ps.INK_MUTED,lw=1.0)
for i,(a,b) in enumerate(zip(t["RS/close-to-close"],t["RS/open-to-close"])):
    ax.text(i-w/2,a,f"{a:.2f}",ha="center",va="bottom",fontsize=7,color=ps.INK_SOFT)
    ax.text(i+w/2,b,f"{b:.2f}",ha="center",va="bottom",fontsize=7,color=ps.INK_SOFT)
ax.set_xticks(ix); ax.set_xticklabels([s.replace(" — ","\n") for s in t.index],fontsize=7.5)
ax.set_ylim(0,1.35); ax.legend(fontsize=7.2,loc="upper left")
ps.finish(ax,"A. The benchmark choice drives the verdict",None,None,"Ratio")

ax=axes[1]
ax.bar(ix,t["overnight share"]*100,color=ps.SERIES["violet"],width=0.55)
for i,v in enumerate(t["overnight share"]*100):
    ax.text(i,v,f"{v:.0f}%",ha="center",va="bottom",fontsize=8,color=ps.INK_SOFT)
ax.set_xticks(ix); ax.set_xticklabels([s.replace(" — ","\n") for s in t.index],fontsize=7.5)
ax.margins(y=0.2)
ps.finish(ax,"B. Share of daily variance occurring overnight",None,None,"Percent")
ps.header(fig,"Figure 14.  Rogers-Satchell cannot see the overnight gap, so a close-to-close benchmark conflates two effects",
          "RS is built from open, high, low and close within the session. Comparing it to close-to-close variance mixes\n"
          "discretisation bias with the overnight variance share — which on NIFTY is 34% of the total.",top=0.82)
for e in ("png","pdf"): fig.savefig(FIG/f"fig14_benchmark_diagnosis.{e}")
plt.close(fig); print(f"\nwrote fig14_benchmark_diagnosis.png")
