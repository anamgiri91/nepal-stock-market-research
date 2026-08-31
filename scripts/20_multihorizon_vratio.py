"""Multi-horizon variance ratio RS_K / Var(x_K), implemented correctly.

Rewritten after an earlier version was found invalid. Three defects are fixed here:

  1. LIQUIDITY BUCKETS WERE A STOCK-DAY PROPERTY. 77.9% of securities appeared in more than one
     bucket (median 4 of 5), so grouping by bucket and then taking consecutive rows stitched
     together NON-ADJACENT sessions -- only 67.5% of within-bucket consecutive rows were truly
     adjacent, mean gap 3.6 sessions. Buckets are now assigned ONCE per security from its median
     trade count over the whole sample, and never vary within a security.

  2. NON-OVERLAPPING BLOCKS. The published construction uses overlapping rolling windows: for every
     start T, O_K = O_T, H_K = max(H_T..H_{T+K-1}), L_K = min(L_T..L_{T+K-1}), C_K = C_{T+K-1}.
     Overlapping is now primary; non-overlapping is retained as a robustness panel. Overlapping
     also avoids the fixed-phase problem of disjoint blocks, which always start on the same
     position in the calendar.

  3. NO ADJACENCY GUARANTEE. Every bar is now asserted to span exactly K consecutive genuine
     exchange sessions, using the session ordinal from the trading calendar.

On uncertainty: overlapping windows raise the bar COUNT but not the information. Adjacent K-bars
share K-1 days, so the effective number of independent windows is still about N/K. Confidence
bands therefore come from a BLOCK bootstrap over dates with block length >= K, not from treating
overlapping bars as independent draws.

Produces Figure 20 and Table 26.
"""
import sys, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts")); from _env import bootstrap; bootstrap()
import numpy as np, pandas as pd, matplotlib.pyplot as plt
sys.path.insert(0, str(ROOT / "src"))
from nepsevol.sample import load_sample
from nepsevol.utils import plotstyle as ps
ps.apply(); FIG=ROOT/"output"/"figures"; TAB=ROOT/"output"/"tables"
EXT=ROOT.parent/"private"/"data-vault"/"raw"/"external"
KS=[1,2,3,4,5,7,10,15,20]


def bars_for_series(o,h,l,c,sr,K,overlap=True):
    """K-session OHLC bars from arrays ordered by session. `sr` is the session ordinal.

    A bar is emitted only where the K sessions are strictly consecutive (sr increments by 1),
    which is asserted rather than assumed.
    """
    n=len(o)
    if n<K: return None
    starts=range(0,n-K+1) if overlap else range(0,n-K+1,K)
    O,H,L,C=[],[],[],[]
    for t in starts:
        w=sr[t:t+K]
        if w[-1]-w[0]!=K-1:      # not K consecutive sessions
            continue
        O.append(o[t]); C.append(c[t+K-1])
        H.append(h[t:t+K].max()); L.append(l[t:t+K].min())
    if len(O)<5: return None
    return np.array(O),np.array(H),np.array(L),np.array(C)


def vr_parts(bars):
    o,h,l,c=(np.log(x) for x in bars)
    hh,ll,xx=h-o,l-o,c-o
    rs=(hh*(hh-xx)+ll*(ll-xx)).mean()
    v=xx.var(ddof=1)
    return rs, v, (rs/v if v>0 else np.nan), len(o)


def pooled(panel,K,overlap=True,date_subset=None):
    """Pool bars across securities in a bucket; returns RS, Var(x), ratio, n_bars."""
    RS=[];VX=[];N=0
    for _,g in panel.groupby("symbol",sort=False):
        g=g.sort_values("sr")
        if date_subset is not None:
            g=g[g.date.isin(date_subset)]
            if len(g)<K: continue
        b=bars_for_series(g.open.values,g.high.values,g.low.values,g.close.values,
                          g.sr.values,K,overlap)
        if b is None: continue
        o,h,l,c=b
        RS.append(np.stack([o,h,l,c],1)); N+=len(o)
    if not RS: return np.nan,np.nan,np.nan,0
    A=np.vstack(RS)
    return vr_parts((A[:,0],A[:,1],A[:,2],A[:,3]))


# ── data, with SECURITY-level liquidity assignment ──
p=load_sample(ROOT, "equity")
sess={d:i for i,d in enumerate(sorted(p.date.unique()))}
p["sr"]=p.date.map(sess)
sec_liq=p.groupby("symbol").n_trades.median()
p["bucket"]="NEPSE Q"+ (pd.qcut(sec_liq,5,labels=False,duplicates="drop")+1).astype(str).reindex(p.symbol).values
assert p.groupby("symbol").bucket.nunique().max()==1, "bucket must be constant within a security"

nif=pd.read_csv(EXT/"nifty50.csv",parse_dates=["Date"]); nif.columns=[c.lower() for c in nif.columns]
nif=nif.sort_values("date").reset_index(drop=True); nif["symbol"]="NIFTY"; nif["sr"]=np.arange(len(nif))

rows=[]
for K in KS:
    rs,v,r,n=pooled(nif,K,True); rows.append(dict(bucket="NIFTY 50",K=K,RS=rs,VarX=v,vratio=r,n_bars=n,overlap=True))
    rs,v,r,n=pooled(nif,K,False); rows.append(dict(bucket="NIFTY 50",K=K,RS=rs,VarX=v,vratio=r,n_bars=n,overlap=False))
    for bkt,g in p.groupby("bucket",sort=True):
        for ov in (True,False):
            rs,v,r,n=pooled(g,K,ov)
            rows.append(dict(bucket=bkt,K=K,RS=rs,VarX=v,vratio=r,n_bars=n,overlap=ov))
t=pd.DataFrame(rows); t.to_csv(TAB/"table26_multihorizon_vratio.csv",index=False)

ov=t[t.overlap].pivot(index="K",columns="bucket",values="vratio")
order=["NIFTY 50"]+[f"NEPSE Q{i}" for i in range(1,6)]
ov=ov[[c for c in order if c in ov.columns]]
print("OVERLAPPING rolling windows, security-level buckets, adjacency asserted")
print("="*84)
print(ov.to_string(float_format=lambda x:f"{x:,.3f}"))
nb=t[t.overlap].pivot(index="K",columns="bucket",values="n_bars")
print("\nbars (overlapping):")
print(nb[[c for c in order if c in nb.columns]].to_string())

no=t[~t.overlap].pivot(index="K",columns="bucket",values="vratio")
print("\nROBUSTNESS — non-overlapping blocks:")
print(no[[c for c in order if c in no.columns]].to_string(float_format=lambda x:f"{x:,.3f}"))

# ── block bootstrap over DATES (block length >= K) ──
print("\nBlock-bootstrap 95% bands (dates resampled in blocks; overlapping bars are NOT")
print("independent, so bar count does not buy precision)")
rng=np.random.default_rng(4)
dates=np.array(sorted(p.date.unique())); nd=len(dates)
band={}
for bkt,g in p.groupby("bucket",sort=True):
    for K in (1,20):
        B=60; blk=max(K,20); out=[]
        for _ in range(B):
            starts=rng.integers(0,nd-blk,int(np.ceil(nd/blk)))
            idx=np.unique(np.concatenate([np.arange(s,s+blk) for s in starts]))[:nd]
            _,_,r,_=pooled(g,K,True,date_subset=set(dates[idx]))
            if np.isfinite(r): out.append(r)
        if out: band[(bkt,K)]=np.percentile(out,[2.5,97.5])
    print(f"  {bkt}: " + "  ".join(
        f"K={K} [{band[(bkt,K)][0]:.2f},{band[(bkt,K)][1]:.2f}]" for K in (1,20) if (bkt,K) in band))

fig,ax=plt.subplots(figsize=(7.6,4.4))
ax.axhline(1.0,color=ps.INK_MUTED,lw=1.0)
cols={"NIFTY 50":ps.SERIES["green"],"NEPSE Q1":ps.SERIES["orange"],"NEPSE Q2":ps.SERIES["yellow"],
      "NEPSE Q3":ps.SERIES["red"],"NEPSE Q4":ps.SERIES["magenta"],"NEPSE Q5":ps.SERIES["blue"]}
mks={"NIFTY 50":"*","NEPSE Q1":"s","NEPSE Q2":"^","NEPSE Q3":"D","NEPSE Q4":"v","NEPSE Q5":"o"}
for cbl in ov.columns:
    ax.plot(ov.index,ov[cbl],color=cols.get(cbl),marker=mks.get(cbl,"o"),
            ms=8 if cbl=="NIFTY 50" else 5,lw=1.7,markeredgecolor=ps.SURFACE,markeredgewidth=.9,label=cbl)
    for K in (1,20):
        if (cbl,K) in band:
            lo,hi=band[(cbl,K)]; ax.plot([K,K],[lo,hi],color=cols.get(cbl),lw=2.4,alpha=.35,solid_capstyle="butt")
ax.legend(fontsize=7.5,ncol=2)
ps.finish(ax,None,None,"Bar length K (consecutive sessions)","RS_K ÷ Var(x_K)")
ps.header(fig,"Horizon behaviour of the variance ratio",
          "Overlapping rolling windows, buckets fixed per security, every bar asserted to span K consecutive\n"
          "sessions. Vertical bars are block-bootstrap 95% intervals at K=1 and K=20 — overlapping windows\n"
          "raise the bar count but not the information.",top=0.80)
for e in ("png","pdf"): fig.savefig(FIG/f"fig20_multihorizon_vratio.{e}")
plt.close(fig); print("\nwrote fig20_multihorizon_vratio.png")
