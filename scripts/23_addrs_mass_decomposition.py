"""Where AddRS's correction mass actually comes from, decomposed exactly.

Manuscript section 8.3. Written 2026-08-29 to give that section generating code: its table had
been prose-only, and a recomputation did not reproduce it (audit A-053).

The correction is the difference AddRS - RS, which the identity in `estimators/range_.py` gives
in closed form:

    AddRS - RS = (x^2 / 2) * (1{H=O or C=H} + 1{L=O or C=L}),   x = ln(C/O)

so total correction mass factorises exactly, per liquidity bucket q:

    mass_q = n_q * P(fire | q) * E[correction | fires, q]

and the share of mass is mass_q / sum_q mass_q. The factorisation is an identity, so it closes
to machine precision -- the assertion at the end of this file enforces that rather than trusting
it.

Two properties are worth stating because an earlier draft asserted the opposite of the first:

  * A degenerate bar (H = L) forces O = H = L = C, hence x = 0, hence correction EXACTLY zero.
    Degenerate bars therefore contribute NO correction mass, necessarily and not empirically.
  * Both indicators fire on a fully monotone bar, giving AddRS = x^2.

Sample is the POOLED universe at stock-day level, which is what section 8.3 reports; it is not
the equity sample that carries section 8.1's headline result. That distinction is now stated in
the section itself.

    python scripts/23_addrs_mass_decomposition.py
"""
import sys, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts")); from _env import bootstrap; bootstrap()

import numpy as np, pandas as pd, matplotlib.pyplot as plt
sys.path.insert(0, str(ROOT / "src"))
from nepsevol.sample import load_sample
from nepsevol.estimators import range_ as RG
from nepsevol.utils import plotstyle as ps

ps.apply()
FIG = ROOT / "output" / "figures"; TAB = ROOT / "output" / "tables"

d = load_sample(ROOT, "full").copy()

# The correction, taken as AddRS - RS through the shipped estimators rather than re-derived here,
# so this script cannot drift from the implementation the paper's other exhibits use.
add, rs = RG.add_rs(d), RG.rogers_satchell(d)
d = d.assign(corr=(add - rs).values, rs=rs.values)

o, h, l, c = (d[k].values for k in ("open", "high", "low", "close"))
x = np.log(c / o)
close_to = lambda p, q: np.abs(p - q) <= 1e-12 * np.abs(q)
d["fires"] = (close_to(h, o) | close_to(c, h)) | (close_to(l, o) | close_to(c, l))
d["x2"] = x ** 2
d["degenerate"] = h == l

d["q"] = pd.qcut(d.n_trades, 5, labels=False, duplicates="drop") + 1
total = d["corr"].sum()

rows = []
for q, g in d.groupby("q"):
    fired = g[g.fires]
    rows.append(dict(
        quintile=q,
        n=len(g),
        median_trades=g.n_trades.median(),
        obs_share=len(g) / len(d),
        firing_prob=g.fires.mean(),
        mean_corr_given_firing=fired["corr"].mean(),
        corr_over_rs=g["corr"].sum() / g.rs.sum(),
        mean_x2=g.x2.mean(),
        share_of_mass=g["corr"].sum() / total,
    ))
t = pd.DataFrame(rows)

# The factorisation is an identity; verify it rather than assert it in prose.
recon = t.n * t.firing_prob * t.mean_corr_given_firing
t["share_reconstructed"] = recon / recon.sum()
max_gap = (t.share_of_mass - t.share_reconstructed).abs().max()

t.to_csv(TAB / "table28_addrs_mass_decomposition.csv", index=False)

print("AddRS correction mass, decomposed by liquidity quintile (pooled universe, stock-day)")
print(t.to_string(index=False, float_format=lambda v: f"{v:,.4f}"))
print(f"\nfactorisation closes to {max_gap:.2e} (identity, so machine precision)")
print(f"shares sum to {t.share_of_mass.sum():.6f}")

deg_mass = d.loc[d.degenerate, "corr"].sum()
one_trade = d[d.n_trades <= 1]
print(f"\ndegenerate (H=L) bars : {d.degenerate.sum():,} rows = {100*d.degenerate.mean():.2f}% of the sample,"
      f" correction mass {deg_mass:.6g}")
print(f"one-trade bars        : {len(one_trade):,} rows, correction mass"
      f" {100*one_trade['corr'].sum()/total:.2f}% of the total")

# ------------------------------------------------------------------ FIGURE
fig, axes = plt.subplots(1, 3, figsize=(11.6, 3.6))
qs = t.quintile.values
xt = ["Q1\nthinnest", "Q2", "Q3", "Q4", "Q5\ndeepest"]

ax = axes[0]
ax.bar(qs, t.firing_prob, color=ps.SERIES["orange"], width=0.62)
for q, v in zip(qs, t.firing_prob):
    ax.annotate(f"{v:.0%}", (q, v), ha="center", va="bottom", fontsize=7.5,
                color=ps.INK_SOFT, xytext=(0, 2), textcoords="offset points")
ax.set_ylim(0, 1.05); ax.set_yticks([0, .25, .5, .75, 1.0])
ax.set_yticklabels([f"{v:.0%}" for v in (0, .25, .5, .75, 1.0)])
ax.set_xticks(qs); ax.set_xticklabels(xt, fontsize=7.5)
ps.finish(ax, "A.  Frequency", None, None, "Days on which a boundary fires")

ax = axes[1]
ax.bar(qs, t.share_of_mass * 100, color=ps.SERIES["blue"], width=0.62)
for q, v in zip(qs, t.share_of_mass * 100):
    ax.annotate(f"{v:.1f}%", (q, v), ha="center", va="bottom", fontsize=7.5,
                color=ps.INK_SOFT, xytext=(0, 2), textcoords="offset points")
ax.set_ylim(0, max(t.share_of_mass) * 118)
ax.set_yticks([0, 10, 20, 30]); ax.set_yticklabels(["0%", "10%", "20%", "30%"])
ax.set_xticks(qs); ax.set_xticklabels(xt, fontsize=7.5)
ps.finish(ax, "B.  Absolute mass", None, None, "Share of total correction mass")

ax = axes[2]
ax.axhline(1.0, color=ps.INK_MUTED, lw=1.0, zorder=0)
ax.bar(qs, t.corr_over_rs, color=ps.SERIES["aqua"], width=0.62)
for q, v in zip(qs, t.corr_over_rs):
    ax.annotate(f"{v:.2f}", (q, v), ha="center", va="bottom", fontsize=7.5,
                color=ps.INK_SOFT, xytext=(0, 2), textcoords="offset points")
ax.annotate("correction equals\nthe estimator", (5.45, 1.0), ha="right", va="bottom",
            fontsize=7, color=ps.INK_MUTED)
ax.set_ylim(0, max(t.corr_over_rs) * 1.22)
ax.set_xticks(qs); ax.set_xticklabels(xt, fontsize=7.5)
ps.finish(ax, "C.  Relative to the estimator", None, None, "Correction ÷ Rogers–Satchell")

ps.header(fig, "Three facts an aggregate statement about AddRS would merge",
          "Pooled universe, stock-day quintiles of trading intensity. The thinnest quintile fires most often and is\n"
          "transformed most, yet the deepest supplies the largest share of mass, because squared returns are larger there.",
          top=0.80)
for e in ("png", "pdf"): fig.savefig(FIG / f"fig22_addrs_mass_decomposition.{e}")
plt.close(fig)
print(f"\nwrote {FIG/'fig22_addrs_mass_decomposition.png'}")

assert max_gap < 1e-12, f"factorisation failed to close: {max_gap}"
assert abs(deg_mass) < 1e-18, f"degenerate bars must contribute exactly zero, got {deg_mass}"
