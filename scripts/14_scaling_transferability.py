"""What does an empirical scale-to-benchmark correction do in an ultra-thin market?

The ABC procedure (Maheswaran & Kumar 2013) is described as an empirical correction that removes
the downward bias in the Rogers-Satchell estimator relative to the "usual" close-to-close
estimator, without requiring the number of steps N. Its exact form is paywalled and is NOT
reproduced here; no claim is made about their estimator.

What IS testable is the general property of ANY correction calibrated to make RS match a
close-to-close target, which we define ourselves:

    k = mean(usual) / mean(RS)      estimated on a calibration group
    RS_scaled = k * RS

Two questions follow, and both matter regardless of the specific correction used.

  1. WHAT gets imported. Section 7 showed RS/CC factors into a genuine intraday bias and the
     share of variance the estimator can observe. Scaling RS to a close-to-close target
     therefore imports overnight variance into an intraday estimator. Where overnight variance
     is small that is nearly harmless; where it dominates, the scale factor is mostly overnight.

  2. Whether k TRANSFERS. A scale factor estimated on liquid securities and applied to thin ones
     (or the reverse) will be wrong by the ratio of their observable shares.

Produces Table 20.
"""
import sys, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts")); from _env import bootstrap; bootstrap()
import numpy as np, pandas as pd
sys.path.insert(0, str(ROOT / "src"))
from nepsevol.sample import load_sample
LN2=np.log(2); TAB=ROOT/"output"/"tables"

p=load_sample(ROOT, "equity").sort_values(["symbol","date"])
sess={d:i for i,d in enumerate(sorted(p.date.unique()))}
p["sr"]=p.date.map(sess); p["gp"]=p.groupby("symbol").sr.diff()
p["pc"]=p.groupby("symbol").close.shift(1)
d=p[(p.gp==1)&p.pc.notna()&(p.pc>0)].copy()
o,h,l,c=np.log(d.open),np.log(d.high),np.log(d.low),np.log(d.close)
d["rs"]=(h-o)*((h-o)-(c-o))+(l-o)*((l-o)-(c-o))
d["v_cc"]=(np.log(d.close/d.pc))**2
d["v_oc"]=(c-o)**2
d["q"]=pd.qcut(d.n_trades,5,labels=False,duplicates="drop")

rows=[]
for q,g in d.groupby("q"):
    rs,cc,oc=g.rs.mean(),g.v_cc.mean(),g.v_oc.mean()
    rows.append({"quintile":f"Q{q+1}","median_trades":g.n_trades.median(),
                 "k_to_close_to_close":cc/rs,"k_to_open_to_close":oc/rs,
                 "overnight_share":1-oc/cc,
                 "pct_of_k_from_overnight":100*(1-(oc/rs)/(cc/rs))})
t=pd.DataFrame(rows)
t.to_csv(TAB/"table20_scaling_transferability.csv",index=False)
print("A scale-to-benchmark correction: what is the scale factor actually made of?")
print("="*88)
print(t.to_string(index=False,float_format=lambda x:f"{x:,.3f}"))
print("\n  k_to_close_to_close : the multiplier needed to make RS match total daily variance")
print("  k_to_open_to_close  : the multiplier needed to match INTRADAY variance only")
print("  pct_of_k_from_overnight : share of the correction that is overnight variance,")
print("                            not discretisation")

print("\n\nDoes a scale factor calibrated on one liquidity group transfer to another?")
print("="*88)
K={r['quintile']:r['k_to_close_to_close'] for _,r in t.iterrows()}
print(f"  {'calibrated on':16}" + "".join(f"{'→'+q:>12}" for q in K))
for src in K:
    line=f"  {src:16}"
    for tgt in K:
        err=100*(K[src]/K[tgt]-1)
        line+=f"{err:>11.0f}%"
    print(line)
print("\n  Cells are the percentage error in the corrected variance when a factor estimated on")
print("  the row group is applied to the column group. The diagonal is zero by construction.")
mx=max(abs(100*(K[a]/K[b]-1)) for a in K for b in K)
print(f"\n  Worst off-diagonal error: {mx:,.0f}%.")
print("  A single market-wide scale factor is not a safe object in this market.")
