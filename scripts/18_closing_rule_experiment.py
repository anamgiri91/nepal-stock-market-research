"""Why does AddRS overshoot? An A-B-A experiment inside the same market.

NEPSE changed how the official closing price is constructed, twice, inside our panel:

    through 2025-03-19   last traded price
    2025-03-20 - 09-22   volume-weighted average of the final 15 minutes
    from 2025-09-23      last traded price again  (SEBON directive, 20 Sep)

AddRS = RS + (x^2/2)(I_u + I_v), where I_u fires on {H=O or C=H} and I_v on {L=O or C=L}. Two of
those four conditions involve the CLOSE and two involve the OPEN. If the overshoot is driven by
the close being a discrete terminal transaction, the VWAP regime should suppress the close-side
indicators and the overshoot with them, while leaving the open-side conditions untouched.

The open-side conditions are therefore a built-in placebo: nothing about this rule change should
move them.

Produces Figure 19 and Table 24.
"""
import sys, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts")); from _env import bootstrap; bootstrap()
import numpy as np, pandas as pd, matplotlib.pyplot as plt
sys.path.insert(0, str(ROOT / "src"))
from nepsevol.sample import load_sample
from nepsevol.estimators.ratios import sd_ratio
from nepsevol.utils import plotstyle as ps
from nepsevol.estimators import range_ as R
ps.apply(); FIG=ROOT/"output"/"figures"; TAB=ROOT/"output"/"tables"

VWAP_START=pd.Timestamp("2025-03-20"); VWAP_END=pd.Timestamp("2025-09-22")
p=load_sample(ROOT, "equity")
p["regime"]=np.where(p.date<VWAP_START,"A1 last-trade (pre)",
             np.where(p.date<=VWAP_END,"B  VWAP 15-min","A2 last-trade (post)"))
eq=lambda a,b:(a-b).abs()<=1e-12*b.abs()
p["CH"]=eq(p.close,p.high); p["CL"]=eq(p.close,p.low)
p["HO"]=eq(p.high,p.open);  p["LO"]=eq(p.low,p.open)
p["Iu"]=p.HO|p.CH; p["Iv"]=p.LO|p.CL
p["x2"]=np.log(p.close/p.open)**2
p["rs"]=R.rogers_satchell(p); p["addrs"]=R.add_rs(p)
p["corr_term"]=0.5*p.x2*(p.Iu.astype(float)+p.Iv.astype(float))

rows=[]
for r,g in p.groupby("regime"):
    oc=g.x2.mean()
    rows.append({"regime":r,"n":len(g),"days":g.date.nunique(),
        "C=H %":100*g.CH.mean(),"C=L %":100*g.CL.mean(),
        "H=O %":100*g.HO.mean(),"L=O %":100*g.LO.mean(),
        "RS/OC_sd_ratio":sd_ratio(g.rs,oc)[0],"AddRS/OC_sd_ratio":sd_ratio(g.addrs,oc)[0],
        # the overshoot is fully observable: (AddRS-RS)/OC in variance terms
        "correction/OC":g.corr_term.mean()/oc,
        "E[x²|boundary]/E[x²]":g.loc[g.Iu|g.Iv,"x2"].mean()/oc})
t=pd.DataFrame(rows).sort_values("regime"); t.to_csv(TAB/"table24_closing_rule.csv",index=False)
print("A-B-A experiment: NEPSE's closing-price construction changed twice inside the panel")
print("="*104)
print(t.to_string(index=False,float_format=lambda x:f"{x:,.3f}"))

a1,b,a2=(t[t.regime.str.startswith(k)].iloc[0] for k in ("A1","B","A2"))
print(f"\n  CLOSE-side indicators (treated):")
print(f"    C=H   {a1['C=H %']:.1f}%  →  {b['C=H %']:.1f}%  →  {a2['C=H %']:.1f}%     "
      f"({100*(b['C=H %']/a1['C=H %']-1):+.0f}% then {100*(a2['C=H %']/b['C=H %']-1):+.0f}%)")
print(f"    C=L   {a1['C=L %']:.1f}%  →  {b['C=L %']:.1f}%  →  {a2['C=L %']:.1f}%")
print(f"  OPEN-side indicators (placebo — should not move):")
print(f"    H=O   {a1['H=O %']:.1f}%  →  {b['H=O %']:.1f}%  →  {a2['H=O %']:.1f}%")
print(f"    L=O   {a1['L=O %']:.1f}%  →  {b['L=O %']:.1f}%  →  {a2['L=O %']:.1f}%")
print(f"\n  AddRS/OC (SD scale)   {a1['AddRS/OC_sd_ratio']:.3f}  →  {b['AddRS/OC_sd_ratio']:.3f}  →  {a2['AddRS/OC_sd_ratio']:.3f}")
print(f"  RS/OC    (SD scale)   {a1['RS/OC_sd_ratio']:.3f}  →  {b['RS/OC_sd_ratio']:.3f}  →  {a2['RS/OC_sd_ratio']:.3f}")

# x^2-weighted decomposition by boundary type
print("\n\nWhich boundary drives the correction? (x²-weighted, not mere frequency)")
print("="*104)
dec=[]
for r,g in p.groupby("regime"):
    oc=g.x2.mean(); row={"regime":r}
    for nm,col in [("H=O","HO"),("C=H","CH"),("L=O","LO"),("C=L","CL")]:
        sel=g[g[col]]
        row[f"{nm} freq%"]=100*g[col].mean()
        row[f"{nm} E[x²]/E[x²]"]=sel.x2.mean()/oc if len(sel) else np.nan
        row[f"{nm} contrib"]=(g[col].mean()*sel.x2.mean()/oc) if len(sel) else np.nan
    dec.append(row)
d=pd.DataFrame(dec).sort_values("regime")
print(d[["regime"]+[c for c in d.columns if "contrib" in c or "E[x²]" in c]].to_string(index=False,float_format=lambda x:f"{x:,.3f}"))
print("\n  'contrib' = frequency x conditional E[x²]/E[x²]; this is what actually enters the")
print("  correction. Frequency alone is not enough: a rare boundary on high-|x| days matters more.")
