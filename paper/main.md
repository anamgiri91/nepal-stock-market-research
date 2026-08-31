# Does the Bias Exist?

**Sample composition and additive corrections to range-based volatility estimators in a frontier market**

**Anam Giri**

*Draft v0.6 · 29 August 2026 · not for circulation*

**Keywords:** range-based volatility; bias correction; instrument composition; sample
construction; frontier markets; Nepal Stock Exchange

**JEL classification:** G14 (Information and Market Efficiency); G15 (International Financial
Markets); C58 (Financial Econometrics); C18 (Methodological Issues: General)

> **Affiliation and corresponding-author details to be completed before submission.**

> **Status.** Exploratory unless a claim is explicitly labelled otherwise. One hypothesis has
> been evaluated on held-out data; its confirmatory provenance carries a stated qualification
> (§10). Every ratio in this paper is labelled **variance-scale** or **SD-scale**, because the
> two differ by a square root and an earlier draft mixed them across adjacent sections.
> Section 13 states what is not established.

---

## Abstract

Additive bias corrections for range-based volatility estimators are built for a regime in which the
uncorrected estimator is downward-biased. We show what happens when no such bias is detectable, and
that whether it *appears* detectable turns on a sample-construction step the data do not supply.

On ordinary equity from the Nepal Stock Exchange — a market with no listed equity derivatives — the
additive correction of Kumar and Maheswaran (2014) **overstates at every liquidity level we can
measure**, from 1.149 in the most active quintile to 1.323 in the second against a matched
open-to-close benchmark, while performing as designed on the NIFTY 50 at 1.005. This follows from
the correction's premise rather than any defect in it, and we state it for the class: **any**
correction of the form `RS + Δ` with `Δ ≥ 0` has positive expected bias in a regime where
Rogers–Satchell is already unbiased. In thin NEPSE equity Rogers–Satchell sits at **0.998** against
a matched benchmark on a variance scale — so against the benchmark the data support, we find no
sign of the downward bias the correction exists to remove. That is weaker than saying the premise
is false, and deliberately so: the latent variance is unobserved and the benchmark is an imperfect
proxy. Stating the result for the class matters practically: it does not depend on which correction
is tested.

Whether the premise *appears* satisfied depends on how the sample is built, and that is the paper's
second result. NEPSE publishes ordinary equity, corporate debentures, closed-end mutual funds and
restricted promoter shares in one daily file with **no instrument-type field**. Sorted on trading
intensity, the thinnest decile of the pooled universe is **94.3% non-equity**, and it is there that
the estimators appear to break — the Parkinson estimator returns exactly zero on 53.9% of its
stock-days, and Rogers–Satchell reads 0.172 against the matched benchmark. Restricted to the 291
ordinary equities the picture inverts: participation is 1.000 in every liquidity quintile, the
thinnest equity quintile trades 49 times a day, `P(H = L)` falls from 5.70% to 0.28%, and the same
ratio reads 1.184. **The pooled sample displays exactly the downward bias an additive correction
exists to repair, and the equity sample does not.** The result survives every alternative equity
definition we tried, the worst case sitting five times below the pooled rate.

A decomposition of where the correction's mass comes from separates three things an aggregate
statement merges: boundary conditions fire on 92.0% of days in the thinnest quintile against 37.4%
in the most active, yet the most active quintile supplies the larger share of absolute correction
mass because squared open-to-close returns are four times larger there, while relative to
Rogers–Satchell itself the correction is 167% of it in the thinnest quintile against roughly 35–45%
elsewhere. Separately, we find the opening return carries 63.6% of close-to-close variance in thin
equity against 26.9% in dense equity; we attempted a censored-normal recovery of latent opening
dispersion behind NEPSE's ±2% pre-open band and report no estimate from it, because tested against
the April 2026 widening of the band the model predicts 0.14% of opens beyond the new boundary where
6.93% are observed.

We propose no new estimator and no correction. Restricting samples to ordinary common shares is
long-standing practice in the emerging-market liquidity literature, and the zero-range case is
documented in the bid–ask spread literature working on the same daily inputs. The contribution is a
boundary condition on a class of corrections, and a measured account of a sample-construction
omission that decides whether that boundary is visible at all.

---

## 1. Introduction

The toolkit for markets without derivatives is the range-based family. Its appeal is an
efficiency argument: Parkinson (1980) is several times as efficient as close-to-close under its
maintained model. Those efficiency results are derived under continuous observation of the price
path, and that assumption is known to fail under infrequent trading. Rogers and Satchell (1991)
say so in the paper that introduces their estimator: approximating the true extrema of a drifting
Brownian motion by those of a random walk "introduces error, often quite a serious error", and
they propose a correction for it in the same paper.

The natural next question is where those corrections stop working, and the natural place to look
is a market thin enough to strain them. This paper began as that study and arrived somewhere
else. The first finding is a warning about the design of such studies, and it is the finding we
would keep if we could keep only one.

**Contribution.**

1. **A boundary condition on additive corrections, stated for the class rather than one
   estimator.** Any correction of the form `RS + Δ` with `Δ ≥ 0` almost surely has positive
   expected bias in a regime where Rogers–Satchell is already unbiased against the target. AddRS
   is one instance: it overstates at every equity liquidity level in this market while performing
   as designed on a dense index. Stating the result for the class matters practically — it means
   the conclusion does not depend on which member is tested, including successors whose equations
   we could not obtain (§8.2).

2. **A composition artifact that mimics illiquidity, and that manufactures the premise.** Pooling
   the securities an exchange publishes, without an instrument filter the exchange does not
   supply, produces a liquidity gradient that is an asset-class gradient. On the pooled NEPSE
   universe the standard diagnostics reproduce the textbook picture of estimator breakdown; on
   ordinary equity alone they do not. **Rogers–Satchell reads 0.172 against the matched benchmark
   in the pooled thinnest quintile and 1.184 in the equity one** — the pooled sample displays
   exactly the downward bias an additive correction exists to repair, and the equity sample does
   not. The sample-construction step is therefore not housekeeping prior to the estimator
   question; it determines the answer to it.

   Restricting to ordinary common shares is standard practice in the emerging-market liquidity
   literature and we claim no credit for it, nor for the zero-range case itself, which is
   documented in the bid–ask spread literature (§3.1). What we add is that the filter is not
   mechanically available where no instrument-type field is published, and a measurement of what
   its omission costs.

3. **A separation of four distinct failure modes** that "range estimators break in illiquid
   markets" conflates: path observation, premise failure, benchmark scope, and institutional
   censoring of the opening return.

**Why this market.** NEPSE serves as a methodological laboratory, and the property that makes it
one is structural: **instrument composition is hidden in the source data.** The exchange
distributes ordinary equity, corporate debentures, closed-end mutual funds and restricted promoter
shares in one daily file with no type field, so the filter the liquidity literature prescribes
cannot be applied mechanically and must be reconstructed. That makes the counterfactual directly
observable — the same securities, the same code, the same estimators, with and without the
classification step — and lets us measure how the absence of that step propagates into estimator
evaluation. Where type ships with the data, the omission is not available to study, because a
researcher following ordinary practice does not make it.

We do not claim NEPSE is the only exchange distributing an unlabelled mixed universe, and we have
not surveyed which others do. The claim is narrower and testable: **wherever type is absent from
the feed, classification is a research decision rather than a data attribute**, and this paper
measures what that decision is worth. Whether the same artifact is latent in other emerging-market
datasets is a question this setting raises and does not answer.

The market is not chosen for thinness. On ordinary equity NEPSE is not especially thin, and that
is part of the finding rather than a caveat to it.

We do not claim to have discovered finite-sampling bias, nor its correction from daily data.
Both are established. We ask where these results cease to apply, and find that the first thing
that ceases to apply is the diagnosis.

---

## 2. Institutional setting

**No listed equity derivatives.** No equity options, futures or ETFs, so equity volatility
cannot be inferred from any traded instrument. Nepal has some commodity-derivative activity and
has announced plans for securities derivatives; the claim here is confined to listed equity
derivatives, which is all the argument requires.

**A trading week that changed inside the sample.** NEPSE traded **Sunday–Thursday** historically
and moved to **Monday–Friday** in April 2026. A fixed weekday rule is therefore wrong for any
sample spanning the change: it deletes genuine Friday sessions and retains stale Sundays.
Measured as the fraction of a date's cross-section identical to the prior dated file, where a
value near 1.0 indicates a carried-forward record rather than a session:

| | Sunday | Monday–Thursday | Friday | Saturday |
|---|---|---|---|---|
| **pre-2026-04** | 0.155 | 0.12–0.20 | **1.000** | 1.000 |
| **post-2026-04** | **0.924** | 0.04–0.10 | **0.199** | 0.933 |

Sessions are therefore detected from this staleness signature rather than assumed from weekdays,
which also removes public holidays that a weekday rule silently retains. The detector finds
**569 genuine sessions**, a rate of 230 per year.

One Saturday, **2026-07-25**, survives as a session: 5.9% of its closes match the prior session
against roughly 100% for a carried-forward file, 70,158 trades across 353 securities, 94.3% of
rows with `H ≠ L`, no zero-volume rows, and both the adjacent Friday and Sunday absent from the
panel. The pattern is that of a make-up session replacing a holiday Friday. We retain it and
flag its verification status as **provisional**: the data signature is unambiguous but we have
not obtained the governing exchange notice.

**Structural closures.** The 2015 Gorkha earthquake (31 days), COVID-19 (~98 days across two
2020 gaps), and annual Dashain/Tihar closures of 8–12 days.

**How the band interacts with the benchmark, measured rather than assumed.** The ±2% pre-open band
constrains the opening price, and the open is the reference point of the open-to-close benchmark
against which §8 evaluates Rogers–Satchell, so it is natural to suspect the band distorts that
denominator. It does on affected days, and not in the direction intuition suggests. On the **13.2%**
of equity stock-days where the open is pinned at the band, `Var(r_oc)` is **2.53 times** its value
on unpinned days, and close-to-close variance is likewise higher rather than suppressed. The reason
is selection rather than mechanics: the band binds on days when the latent move is large, so pinned
days are high-volatility days. A pinned open also leaves more of the day's move to be completed in
continuous trading, which is the negative opening–intraday covariance §7 reports.

The headline ratio is robust to it. Rogers–Satchell against the matched benchmark reads **1.041**
across all equity days and **1.048** excluding pinned days — a shift too small to move any
conclusion in §8.

**A banded pre-open call auction.** Trading opens with a pre-open session (10:30–10:45) in which
orders may be placed only within **±2% of the previous close**. The engine clears at the
volume-maximising price, and if no orders match, the opening price is set equal to the previous
close. Section 9 shows both rules are visible in the data. The band was widened to ±5% in April
2026 as part of a bundle of simultaneous changes, which is why we do not treat it as a natural
experiment (§13).

---

## 3. Related literature, and what is not claimed here

> A fuller review, with a verification status on every source and a ledger mapping each of this
> paper's claims to the strand that supports it, is in the companion document
> **`literature-review.md`**. This section states only what bears directly on the results.

Four strands bound this paper. The fourth is the one that constrains our contribution most, and
we take it up last rather than burying it.

**Finite-sampling bias, and the discrete-extrema problem.** Rogers and Satchell (1991) identify
the problem in the paper introducing their estimator — approximating the extrema of a drifting
Brownian motion by those of a random walk "introduces error, often quite a serious error" — and
offer a correction there. A related strand works on the **realized
range** built from intraday data rather than the daily OHLC bar we use: Martens and van Dijk
(2007) propose a bias correction that scales the realized range by the average level of the daily
range, addressing microstructure frictions; Christensen and Podolskij (2007) derive asymptotics;
Christensen, Podolskij and Vetter (2009) bias-correct the realized range under microstructure
noise. That literature is adjacent rather than directly applicable here — it presumes intraday
observations, which is precisely what a market like NEPSE does not publish — and we cite it to
locate our setting, not to import its corrections. Rogers, Satchell and Yoon (1994) compare
methods using high and low prices. *(We have read the 1991 abstract and the 1994 metadata, not
either derivation; whether the 1994 paper's treatment of discretisation is the same construction
as the 1991 paper's correction is not established here.)*

**Correction from daily data alone.** Maheswaran and Kumar (2013) propose an **empirical**
automatic bias correction (ABC) for extreme-value estimators requiring no knowledge of `N`, the
number of steps. Kumar and Maheswaran (2014) separately introduce **AddRS**, derived from a
reflection principle for a random walk with symmetric double-exponential increments, and show it
exactly unbiased **under that model**. These are two procedures from two papers and we keep them
apart: ABC is empirical and approximate, AddRS theoretical and exact under its own maintained
model. We implement and benchmark AddRS. **We do not implement ABC and make no claim about it.**
The variance-ratio statistic built from extreme prices is due to Maheswaran, Balasubramanian and
Yoonus (2011); Maheswaran and Kumar (2013) report a value of 0.82 for Rogers–Satchell against the
"usual" close-to-close estimator on the Nifty index over 1996–2011.

**Range estimators may survive moderate illiquidity.** Jacob and Vipul (2008), benchmarking
against two-scale realized volatility, report that daily range estimators are *"not downwardly
biased in the presence of negative autocorrelation and low liquidity, as generally suspected"*,
and identify **drift** as the major cause of Parkinson's poor performance. Our equity results
agree with theirs, in a market considerably thinner than the one they study.

**Opening call auctions.** Ibikunle (2015) finds on the London Stock Exchange that the opening
auction produces highly efficient prices for the highest-volume stocks, while lower-volume stocks
reach comparable efficiency only after continuous trading begins, with a high rate of failure to
open at the call among low-volume securities. Agarwalla, Jacob and Pandey (2015), studying the
2010 reintroduction of the opening call auction on India's NSE with high-frequency data, find the
auctions attract very little volume, leave the intraday pattern of volume and volatility unchanged,
and that a large fraction of price discovery still occurs in the **first fifteen minutes of
continuous trading** rather than at the call.

The second result is a direct comparator, since NIFTY is our cross-market benchmark, and it cuts
against a strong reading of §9: on the NSE the opening auction is largely bypassed. Our contribution
is therefore **not** that thin securities concentrate repricing at the open, which is consistent
with this literature; and whether NEPSE's opening share reflects genuine auction price discovery or
the mechanical booking of a thin security's daily move at its one clearing event is the distinction
§9 says we cannot identify.

### 3.1 The constraint on our contribution: composition is a known problem

The emerging-market liquidity literature already knows that instrument composition contaminates
liquidity measurement, and it already knows the fix.

Lesmond, Ogden and Trzcinka's proportion-of-zero-returns proxy, applied across emerging markets by
Lesmond (2005) and used as the primary liquidity measure by Bekaert, Harvey and Lundblad (2007),
rests on exactly the statistic our §5 examines: the frequency with which a security's price does
not move. And the standard cleaning protocol in that literature restricts samples to **ordinary
common shares**, precisely to keep non-equity instruments from driving the measure.

**So "filter to ordinary equity" is not our idea, and we claim no novelty for it.** A referee who
says this is standard practice is right.

What we add is narrower and, we think, still worth having.

1. **The zero-range case itself is documented, and we claim nothing for it.** `P(H = L)` — the
   zero-*range* rate — is the range-estimator counterpart of the contaminated zero-*return* proxy,
   and it bites harder: a range estimator with `H = L` does not become noisy, it returns exactly
   zero and stops being a volatility proxy at all. But the phenomenon, its origin in sparse
   trading, and a prescription for handling it are all established in the bid–ask spread
   literature, which works on the same daily high–low data. Corwin and Schultz (2012) note that
   with very infrequent trading there may be one trade or none, giving identical high and low
   prices; they retain the previous day's high, low and close, with a further adjustment specific
   to zero-range days. Ardia, Guidotti and Kroencke (2024) show
   popular spread estimators are downward biased under infrequent trading and derive estimators
   that account for discrete observation. **An earlier draft of this paper claimed the analogue was
   undocumented; that claim is withdrawn.**
2. **What we have not found connected to it is the composition problem.** In a feed publishing no
   instrument-type field, the zero-range rate sorts securities by *asset class* rather than by
   liquidity, so a liquidity gradient built from it is an asset-class gradient. That is a
   sample-construction claim, not a claim about estimator theory.
3. **The filter is not mechanically available here.** In the markets where this protocol was
   developed, security type comes with the data. NEPSE publishes none, so applying the standard
   cleaning rule requires reconstructing type from ticker convention and validating it against par
   value (§5). A researcher following best practice cannot execute it without building a classifier
   first, and a researcher not looking for the problem has nothing to alert them.
4. **The filter protects a different conclusion than the one it was designed to protect.** The
   emerging-market literature applies it to keep non-equity instruments out of a *liquidity
   measure*. We show the same omission determines whether a researcher concludes that
   **range-based volatility estimators are viable in the market at all** — a downstream question
   that literature was not addressing. On the pooled universe the answer is no; on ordinary equity
   it is yes, and the reversal is not marginal: the thinnest quintile's `RS ÷ Var(x)` moves from
   0.172 to 1.184, median trading intensity from 111 to 165 trades per day, and Parkinson's
   zero rate from 5.70% to 0.28%.

That fourth point is what we would defend. It is not that a proxy is noisy; it is that a
methodological conclusion inverts.

**We propose no correction for zero-range observations**, and the paper should not be read as
offering one. The contribution is diagnostic.

> **No novelty is claimed for the finite-sampling mechanism, for its correction from daily data,
> for the practice of restricting samples to ordinary equity, or for recognising that sparse
> trading produces zero ranges.** Chou, Chou and Liu's survey of the range literature states that
> finite observation biases the range downward, particularly for lower-liquidity assets. What we
> claim is that the empirical signature of estimator failure, in a market whose published universe
> mixes asset classes and labels none of them, is not identified without that restriction — and
> that the resulting artifact is large, specific, and reproducible.

## 4. Data

| Dataset | Span | Units |
|---|---|---|
| NEPSE stock panel B (with trade counts) | 2024-03-04 → 2026-08-26 | 569 sessions × 520 securities |
| NEPSE stock panel A (long, no trade counts) | 1995 → 2026 | 372 securities, 505,525 stock-days |
| NEPSE index, daily OHLC + turnover | 2010-01-03 → 2026-06-12 | 2,296 usable sessions |
| NIFTY 50 daily OHLCV | 2010-01-04 → 2026-06-12 | 4,037 sessions |
| India VIX | 2010-01-04 → 2026-06-12 | 4,036 sessions |

### 4.1 Pre-committed cleaning

Two rules are fixed in advance and applied at the source, so that every downstream analysis
inherits them identically.

**OHLC envelope repair.** Rows where `High < max(Open, Close)` or `Low > min(Open, Close)` are
inconsistent. We take Open and Close as correct and High/Low as corrupted — O and C are single
transaction prices carried from the tape, while H and L are session extrema and are the fields a
feed most often reports inconsistently — and set `H := max(H, O, C)`, `L := min(L, O, C)`. The
rule is deterministic, idempotent, leaves conforming rows bit-identical, and can only weakly
widen the observed range. Original values are retained and every repaired row is flagged: 40,531
rows in panel A, 1,716 in panel B, **122 rows (0.09%) inside the final equity sample**.

**One observation is one security-day.** Panel A carried 640 duplicated `(symbol, date)` keys.
622 agree on every field and are collapsed; 18 carry conflicting OHLC and are excluded entire,
because nothing in the data says which record is right and letting file order decide would let
row order determine the science.

After both rules the analysis samples contain **zero** OHLC violations and **zero** negative
Garman–Klass or Rogers–Satchell values. That matters because negativity in either estimator is
impossible on a valid bar: with `r = ln(H/L)` and `k = ln(C/O)`, validity gives `|k| ≤ r`, so
`GK = ½r² − (2ln2 − 1)k² ≥ (1.5 − 2ln2)k² ≈ 0.1137 k² ≥ 0`. An earlier draft reported negative
values as an estimator pathology that becomes common under thin trading. That was wrong: every
such value sat on an inconsistent record, and they are a data defect.

### 4.2 Two other defects, each material

**Genuine intraday range begins 2016-06-06** in the index series. Every earlier observation
satisfies `O = H = L = C` with zero reported turnover, so range estimators are undefined — not
imprecise — on that stretch.

**Turnover is missing before 2011 and coded as zero.** Across all 3,702 zero-turnover rows in
panel A, 99.9% have positive volume and 56% have `H ≠ L`: those securities traded and their
prices moved. Any turnover-conditioned rule misclassifies them.

---

## 5. Two universes

This is the mechanism behind §8, and the reason the estimator result needs a sample-construction
step before it can be stated at all.

NEPSE's daily files carry **no instrument-type field**. They contain ordinary equity, corporate
debentures, closed-end mutual funds and restricted promoter shares in one table. Type is
recoverable from the ticker convention and confirmable against par value, and the confirmation is
unusually clean: sorted median closes run 8.56 … 10.78, then **nothing until 100.00**, so the 51
closed-end funds (par 10) identify themselves by price alone with no judgement. Debenture tickers
land 81-of-82 inside [986, 1215], a bond distribution around par 1,000.

Of 184,390 stock-days, **143,149 (77.6%) are ordinary equity**; the remainder are 21,299 fund,
16,120 debenture and 3,822 promoter stock-days.

### 5.1 The pooled universe reproduces the textbook picture

Sorting the pooled universe on trading intensity gives exactly what a frontier-market study
expects to find:

| quintile | securities | participation | median trades/day | `P(H=L)` | RS ÷ Var(x), variance scale |
|---|---|---|---|---|---|
| **Q1** | 152 | **0.195** | **2** | **54.6%** | **0.172** |
| Q2 | 57 | 0.970 | 9 | 10.3% | 0.904 |
| Q3 | 103 | 1.000 | 56 | 0.3% | 1.201 |
| Q4 | 105 | 1.000 | 160 | 0.04% | 1.133 |
| Q5 | 103 | 1.000 | 380 | 0.01% | 0.916 |

Across the pooled sample the Parkinson estimator returns exactly zero on 5.70% of stock-days and
Rogers–Satchell on 15.25%; in the thinnest decile Parkinson returns zero on **53.9%**. Median
trading intensity is 111 trades per day and the tenth percentile is 4.

### 5.2 The gradient is an asset-class gradient

The two thinnest quintiles contain **four ordinary equities between them, out of 209 securities**.
Q1 holds exactly one.

| quintile | debenture | **equity** | fund | promoter | non-equity |
|---|---|---|---|---|---|
| **Q1** | 73 | **1** | 0 | 78 | **99.3%** |
| **Q2** | 11 | **3** | 32 | 11 | **94.7%** |
| Q3 | 0 | 80 | 19 | 4 | 22.3% |
| Q4 | 0 | 105 | 0 | 0 | 0.0% |
| Q5 | 0 | 102 | 1 | 0 | 1.0% |

![Figure 1](../output/figures/fig21_universe_composition.png)

**Figure 1.** Instrument composition of the pooled liquidity quintiles. The two thinnest quintiles hold four ordinary equities between them out of 209 securities. *(Generated by `scripts/22_universe_composition.py`; source file `output/figures/fig21_universe_composition.png`.)*


The thinnest *decile* — the one carrying the 53.9% Parkinson-zero rate — is **94.3% non-equity**:
13,422 debenture, 2,925 fund and 1,389 promoter stock-days against 1,073 equity stock-days.
Debentures and restricted promoter shares are illiquid because of what they are, not because
Nepal is a frontier market.

### 5.3 Ordinary equity, with no liquidity filter applied

| equity quintile | securities | participation | median trades/day | `P(H=L)` | RS ÷ Var(x), variance scale |
|---|---|---|---|---|---|
| Q1 | 59 | **1.000** | **49** | 1.26% | 1.184 |
| Q2 | 58 | 1.000 | 106 | 0.06% | 1.203 |
| Q3 | 59 | 1.000 | 171 | 0.03% | 1.106 |
| Q4 | 57 | 1.000 | 262 | 0.01% | 1.000 |
| Q5 | 58 | 1.000 | 486 | 0.01% | 0.857 |

Across the equity sample: median **165** trades per day, tenth percentile **37**, first
percentile 6. Only **1.6%** of equity stock-days see fewer than ten trades, against 14.8% in the
pooled universe. `P(H = L)` is **0.28%** and Parkinson returns exactly zero on the same 0.28%,
against 5.70% pooled. Rogers–Satchell returns zero on 4.35%, and most of those are monotone
sessions — a documented property of the estimator — rather than degenerate ones.

> **NEPSE's ordinary equity market is liquid enough for range estimators to work.** The estimator
> failure documented in the pooled universe is a property of instrument type.

![Figure 2](../output/figures/fig1_trading_intensity.png)

**Figure 2.** Distribution of daily trading intensity. *(Generated by `scripts/03_descriptive.py`; source file `output/figures/fig1_trading_intensity.png`.)*

![Figure 3](../output/figures/fig5_pathologies.png)

**Figure 3.** Rates at which each estimator returns a degenerate value, by liquidity decile. *(Generated by `scripts/03_descriptive.py`; source file `output/figures/fig5_pathologies.png`.)*


### 5.4 What this means for study design

The classification that separates these two tables is not in the data an exchange distributes. A
study that downloads a frontier exchange's daily files, sorts on turnover or trade count, and
reports that range estimators degrade in the thinnest bucket will produce our §5.1 table. It is
reproducible, statistically strong, and about corporate debentures.

As §3.1 sets out, the emerging-market liquidity literature already restricts samples to ordinary
common shares for exactly this reason, so the remedy is not new. Two things make the omission
easy here anyway. The filter is **not mechanically available**: with no instrument-type field
published, applying the standard rule means building and validating a classifier first. And the
diagnostic that would reveal the problem is the one the composition corrupts — a researcher who
checks whether the thin bucket looks thin will find that it does.

We do not claim this contaminates any particular published paper. We claim the artifact is large,
specific and reproducible, that it is invisible in a workflow that follows the data as published,
and that the check costs one classification step.

---

## 6. Cross-market comparison

Running identical code across three regimes is the standard reassurance that a result is not an
artifact of one market's data or one author's code. **All ratios in this section are SD-scale.**

| regime | median trades/day | Parkinson ÷ OC | zero-range days |
|---|---|---|---|
| **NIFTY 50 index** | dense | **0.978** | 0.00% |
| NEPSE equity | 789 | 0.972 | 0.00% |
| NEPSE equity | 351 | 1.000 | 0.00% |
| NEPSE equity | 208 | 1.028 | 0.00% |
| NEPSE equity | 131 | 1.045 | 0.00% |
| NEPSE equity | 78 | 1.058 | 0.00% |
| NEPSE equity | **33** | **0.935** | **1.63%** |
| NEPSE index (aggregate) | — | 0.835 | 0.22% |

Two things to note, and one caution.

The equity profile is **close to one throughout and is not monotone**: it rises from 0.935 at 33
trades per day to 1.058 around 78, then declines monotonically across the four denser buckets —
1.045, 1.028, 1.000, 0.972 — to 0.972 at 789. The thin end shows a modest deficit, not a
collapse. For comparison, the same table computed on the pooled universe puts its
thinnest bucket at 3 trades per day, a Parkinson ratio of 0.737 and a zero-range rate of 33.43%.


![Figure 4](../output/figures/fig12_cross_market.png)

**Figure 4.** Estimator ratios across three regimes under identical code. All values SD-scale. *(Generated by `scripts/09_cross_market_control.py`; source file `output/figures/fig12_cross_market.png`.)*

**The caution.** The NEPSE index sits at 0.835 while the NIFTY 50 index sits at 0.978, and both
are dense. We report this rather than omitting it: an index is a diversified portfolio and its
range behaves differently from a single security's, so an index-versus-stock comparison is not
like-for-like. **No security-level cross-market comparison exists in this paper.** Any claim that
NEPSE equities and NIFTY constituents behave identically would require constituent-level NIFTY
data with trade counts, which we do not hold (§13).

---

## 7. Benchmark scope

Rogers–Satchell is built from `ln(H/O)`, `ln(L/O)` and `ln(C/O)`. It is an **open-to-close**
estimator and cannot observe the overnight gap, while the "usual" close-to-close estimator spans
the full calendar day. Their ratio factors exactly:

$$\text{RS} / \text{CC} \;=\; \underbrace{(\text{RS}/\text{OC})}_{\text{estimator bias}} \times \underbrace{(\text{OC}/\text{CC})}_{\text{scope}}$$

**All ratios in this section are variance-scale**, which is the scale on which the published 0.82
figure is defined.

| market | RS ÷ CC | RS ÷ OC | Var(open)/Var(cc) | Var(intraday)/Var(cc) | 2Cov/Var(cc) | sum |
|---|---|---|---|---|---|---|
| **NIFTY 50 index** | 0.671 | **0.965** | 0.343 | 0.695 | −0.038 | 1.0000 |
| NEPSE index | 0.534 | 0.543 | 0.045 | 0.985 | −0.030 | 1.0000 |
| NEPSE equity — dense | 1.092 | 1.059 | 0.269 | 1.146 | −0.300 | 1.0000 |
| **NEPSE equity — thin** | **1.260** | **0.998** | **0.636** | 1.370 | −0.897 | 1.0000 |


![Figure 5](../output/figures/fig14_benchmark_diagnosis.png)

**Figure 5.** Benchmark scope: Rogers–Satchell against close-to-close and against a matched open-to-close benchmark (panel A), and the overnight share of close-to-close variance (panel B). All values variance-scale; the full three-component decomposition is in the table above. *(Generated by `scripts/12_benchmark_diagnosis.py`; source file `output/figures/fig14_benchmark_diagnosis.png`.)*

Since `r_cc = r_co + r_oc`, we have `Var(cc) = Var(co) + Var(oc) + 2Cov(co, oc)`, so `OC/CC` is a
ratio and not a variance share and can exceed one, as it does here. The three components are
reported separately and **close to 1.0000 in every row**. An earlier version of this table failed
to close by up to 11% on the panel rows because the four moments were computed on different
subsets of days; that is fixed and a test now enforces closure.

**On NIFTY, most of the gap between Rogers–Satchell and close-to-close variance is scope**:
0.671 against 0.965 once the benchmark is matched.

**On NEPSE equity there is barely any estimator bias left to explain.** RS against a matched
open-to-close benchmark is **0.998** in the thin half and 1.059 in the dense half. What is
distinctive is not the estimator but the scope: the opening return carries **63.6%** of
close-to-close variance in thin equity against 26.9% in dense equity and 34.3% on NIFTY, offset
by a strongly negative covariance between the opening and intraday components (−0.897).

### 7.1 The decomposition is sensitive to a censoring mechanism we do not model

NEPSE operates a **daily price limit** — ±10% of the previous close through March 2026, ±15%
after — separately from the ±2% pre-open band of §9. The two act on different variables. The band
censors the *opening* price; measured on equity, the daily limit binds the opening return on
**0.071%** of stock-days before April 2026 and **0.000%** after, because the band is uniformly the
tighter constraint. The limit instead binds **close-to-close** returns, on 1.24% of equity
stock-days.

That matters here because `Var(open)/Var(cc)` has the censored variable in its denominator.
Excluding limit-hit days:

| sample | n | Var(open)/Var(cc) | 2Cov/Var(cc) |
|---|---|---|---|
| thin equity, all rows | 71,608 | 0.641 | −0.862 |
| thin equity, limit-hit rows excluded | 71,071 | **0.742** | −1.179 |
| dense equity, all rows | 71,250 | 0.291 | −0.365 |
| dense equity, limit-hit rows excluded | 70,021 | 0.304 | −0.488 |

**1.2% of rows move the thin-equity opening share by 15.8%**, and the direction is informative: the
limit *deflates* the reported opening share, so the figure in the table above is conservative rather
than inflated. On 44.6% of limit-hit days the opening return was already pinned at the band, so the
two mechanisms interact rather than acting independently.

We report the uncensored figure as primary and this as its sensitivity. A full treatment would model
both constraints jointly, which we have not done.

**We stop short of a comparison with the published figure.** Maheswaran and Kumar's 0.82 is
estimated on the Nifty index over 1996–2011; our NIFTY sample begins in 2010 and covers roughly
13% of their window. Our full-sample figure is 0.671 and our 2010–2011 sub-sample gives 0.695,
but the same statistic ranges from 0.488 to 1.914 across individual years in our data, so a
difference of this size is uninformative without matching the period. Replicating their window
requires NIFTY OHLC back to 1996, which we do not hold.

*(A trap worth recording: √0.671 = 0.819, which is almost exactly 0.82. It is a coincidence of
scales and not a replication.)*

---

## 8. AddRS: a correction applied where no bias is detectable against the available benchmark

The additive bias correction of Kumar and Maheswaran (2014) reduces exactly. With `b = ln(H/O)`,
`c = ln(L/O)`, `x = ln(C/O)`, `u = 2b − x`, `v = 2c − x`:

`AddRS = ½[½(u²−x²) + x²·1{H=O or C=H}] + ½[½(v²−x²) + x²·1{L=O or C=L}]`

Since `½(u²−x²) = 2b(b−x)`, the indicator-free part is *identically* Rogers–Satchell, so

$$\text{AddRS} = \text{RS} + \tfrac{x^2}{2}\left(\mathbb{1}_u + \mathbb{1}_v\right)$$

The correction substitutes the squared open-to-close return whenever an observed extreme
coincides with the open or the close — the monotone case where RS collapses to zero. It is
**non-negative, and exactly zero** on the 44.9% of stock-days where neither indicator fires.

*The downstream literature.* Kumar and Maheswaran (2014b) develop the forecasting treatment of
AddRS. Our result concerns the estimator's premise in a particular market rather than its
forecasting performance, so the two do not conflict; but any claim about AddRS's usefulness should
be read against that work as well as against the derivation.

*A successor we do not test.* Shaik and Maheswaran (2020) propose a further additive estimator from
the same research group, which they report as unbiased under their own framework. We have not read or benchmarked it, so §8's result should
be read as a boundary condition on **AddRS specifically**, not on daily-OHLC corrections in
general.

*Provenance note.* The 2014 article was not obtained. The equations above are taken from a later
open-access paper by the same author that reproduces them, were checked term-for-term against
that source, and were verified numerically against an independent reimplementation. The
**derivation and the proof of exact unbiasedness remain unverified from the primary source**, and
that proof is stated for a random walk with symmetric double-exponential increments, not for
Brownian motion.

### 8.1 It overstates at every equity liquidity level

**SD-scale ratios against a matched open-to-close benchmark.**

| regime | median trades | Parkinson ÷ OC | RS ÷ OC | **AddRS ÷ OC** | RS = 0 |
|---|---|---|---|---|---|
| **NIFTY 50 index** | dense | 0.978 | 0.980 | **1.005** | 0.0% |
| NEPSE equity Q1 | 37 | 0.951 | 0.984 | **1.259** | 10.6% |
| NEPSE equity Q2 | 92 | 1.058 | 1.143 | **1.323** | 3.2% |
| NEPSE equity Q3 | 165 | 1.041 | 1.107 | **1.283** | 2.9% |
| NEPSE equity Q4 | 297 | 1.005 | 1.039 | **1.216** | 2.4% |
| NEPSE equity Q5 | 701 | 0.975 | 0.977 | **1.149** | 2.6% |


![Figure 6](../output/figures/fig18_addrs_benchmark.png)

**Figure 6.** AddRS against a matched open-to-close benchmark, by liquidity regime. SD-scale. *(Generated by `scripts/17_addrs_benchmark.py`; source file `output/figures/fig18_addrs_benchmark.png`.)*

**AddRS performs as designed on NIFTY**, moving Rogers–Satchell from 0.980 to 1.005. That is an
external check on our implementation as much as a result.

**On NEPSE equity it overstates everywhere**, from 1.149 where trading is most active to 1.323 in
the second quintile. The pattern is not monotone in intensity and does not disappear at 701
trades per day.

### 8.2 Why: the premise, not the mechanism — and it is not about AddRS

The correction is non-negative, so it can only help where Rogers–Satchell is biased downward.
Writing it at the level bias actually lives, and for the general case rather than one estimator:

Let $(\Omega,\mathcal{F},\{\mathcal{F}_t\},\mathbb{P})$ be a filtered probability space, with
$\mathcal{F}_t$ the information available at the start of session $t$. Write $\sigma_t^2$ for the
latent variance of session $t$, $\widehat{RS}_t$ for the Rogers–Satchell estimate formed from that
session's open, high, low and close, and

$$\widehat{\sigma}^2_{\text{corr},t} \;=\; \widehat{RS}_t + \Delta_t$$

for any additively corrected estimator, where $\Delta_t$ is $\mathcal{F}_{t+1}$-measurable and
integrable.

> **Proposition 1.** Suppose $\Delta_t \geq 0$ $\mathbb{P}$-almost surely. Then
> $$\mathbb{E}\!\left[\widehat{\sigma}^2_{\text{corr},t} \mid \mathcal{F}_t\right]
> \;=\; \mathbb{E}\!\left[\widehat{RS}_t \mid \mathcal{F}_t\right] + \mathbb{E}\!\left[\Delta_t \mid \mathcal{F}_t\right]
> \;\geq\; \mathbb{E}\!\left[\widehat{RS}_t \mid \mathcal{F}_t\right],$$
> with equality if and only if $\Delta_t = 0$ almost surely on that conditioning set. Consequently,
> if $\mathbb{E}[\widehat{RS}_t \mid \mathcal{F}_t] = \sigma_t^2$ and
> $\mathbb{P}(\Delta_t > 0 \mid \mathcal{F}_t) > 0$, then
> $$\mathbb{E}\!\left[\widehat{\sigma}^2_{\text{corr},t} \mid \mathcal{F}_t\right] > \sigma_t^2 .$$

*Proof.* Immediate from linearity of conditional expectation and the fact that a non-negative
random variable has non-negative conditional expectation, strictly positive unless the variable
vanishes almost surely. $\square$

**What the proposition does and does not deliver.** It is an implication, not an empirical finding,
and its antecedent — $\mathbb{E}[\widehat{RS}_t \mid \mathcal{F}_t] = \sigma_t^2$ — is **not
directly testable here**, because $\sigma_t^2$ is unobserved. Everything empirical in this section
concerns a proxy for that antecedent, and §8.2 states the limits of that substitution. The
proposition's value is that it holds for the whole additive class: it converts a question about
which correction one happens to test into a question about a single property of the correction
term.

AddRS is one member of that class, with `Δ = ½·x²(I_u + I_v)`, which is non-negative and strictly
positive whenever an extreme coincides with the open or close on a day with `C ≠ O`. Table 8.1
shows `RS ÷ OC` at or above 0.98 in every equity quintile.

**What that does and does not establish, stated carefully.** AddRS targets a specific bias: the
downward bias of Rogers–Satchell arising from the random-walk effect, i.e. `E[RS] < σ²` where `σ²`
is the latent variance. We do not observe `σ²`. What we observe is the ratio of RS to a matched
open-to-close benchmark — mean squared open-to-close returns — which is a conditionally unbiased
but **imperfect** proxy, and Patton (2011) shows imperfect proxies distort exactly this kind of
comparison. So the correct statement is not that the correction's premise is false in this market.
It is that **we find no evidence of the downward bias the correction targets, measured against the
only benchmark the data support**, and that a correction which is non-negative by construction will
overshoot relative to that benchmark whenever no such bias is present in it. Distinguishing the
theoretical bias from what a proxy can reveal is a limitation of the test, not a result of it.

**The argument does not depend on which correction is tested.** That matters for a reasonable
objection to this section — that Shaik and Maheswaran (2020) propose a further additive estimator
from the same research group, and we do not benchmark it. We could not obtain its equations, so we
do not claim to have tested it. But the proposition applies to **any** correction of the additive
non-negative form: the relevant question about a specific estimator is not whether it is more
efficient than AddRS, but whether its correction term can be negative. If it cannot, it overshoots
here too, for the same reason and by the same argument. We state the condition explicitly so a
reader holding any such estimator can check it directly. **Whether the 2020 estimator satisfies
`Δ ≥ 0` is unverified**, and we make no claim either way.

This is not a criticism of AddRS. It solves a different measurement problem, in a regime this
market's equity does not occupy.

### 8.3 Where the correction actually comes from

This subsection is computed on the **pooled universe at stock-day level**, not on the equity
sample that carries §8.1's result: the question here is where a correction's mass comes from
across the whole cross-section a practitioner would face, including the instrument types §5
isolates. Using the identity, total correction mass factorises exactly as

$$\text{mass}_q \;=\; n_q \times \Pr(\text{fire} \mid q) \times \mathbb{E}[\Delta \mid \text{fires}, q]$$

which closes to machine precision (5.6e-17) because it is an identity rather than an approximation.

| quintile | median trades | firing probability | mean correction \| firing | **correction ÷ RS** | share of mass |
|---|---|---|---|---|---|
| Q1 | 5 | **0.920** | 2.601e-04 | **1.667** | 17.1% |
| Q2 | 43 | 0.567 | 4.556e-04 | 0.446 | 17.7% |
| Q3 | 112 | 0.465 | 4.896e-04 | 0.348 | 15.8% |
| Q4 | 228 | 0.424 | 6.488e-04 | 0.360 | 19.2% |
| Q5 | 590 | **0.374** | **1.159e-03** | 0.379 | **30.2%** |

Three distinct facts, which an aggregate statement would merge:

- **Frequency.** Boundary conditions fire 2.5× more often in the thinnest quintile than the most
  active one — and still fire on 37% of days in the most active.
- **Absolute mass.** The most active quintile nevertheless supplies the largest share, because
  the correction term is `x²/2` per firing and mean `x²` runs 3.00e-04 in Q1 against 1.18e-03 in
  Q5. Thin securities barely move, so each firing contributes little.
- **Relative to the estimator.** In Q1 the correction is **167% of Rogers–Satchell itself**,
  against roughly 35–45% elsewhere. That is where AddRS transforms the estimate most.

![Figure 7](../output/figures/fig22_addrs_mass_decomposition.png)

**Figure 7.** The three components of AddRS's correction mass, by liquidity quintile of the pooled universe. *(Generated by `scripts/23_addrs_mass_decomposition.py`; source file `output/figures/fig22_addrs_mass_decomposition.png`.)*

Degenerate (`H = L`) bars contribute **exactly zero** correction mass, and necessarily so rather
than empirically: `H = L` forces `O = H = L = C`, hence `x = 0`, hence `Δ = x²(I_u + I_v)/2 = 0`.
They are 5.70% of the pooled sample and none of its correction. One-trade bars, 93.5% of which
are likewise fully degenerate, contribute 0.34%. The correction is therefore not an artifact of
mechanically constrained sessions — it is carried by sessions that genuinely moved. It is also
not numerically fragile: exact price equality and a 1e-12 relative tolerance give identical
results, and widening to a full tick moves the headline by 0.63%.

### 8.4 An institutional experiment on the boundary conditions

Two of AddRS's four boundary conditions involve the close and two the open, which gives a
built-in placebo when the exchange changes how the close is constructed. NEPSE did so twice
inside the panel: last traded price through 2025-03-19, a volume-weighted average of the final
15 minutes to 2025-09-22, then last traded price again.

If the close-side conditions fire because the close is a discrete terminal transaction, a VWAP
close should suppress them, and should leave the open-side conditions alone.

| | A1 last-trade | **B VWAP** | A2 last-trade | B vs flanks |
|---|---|---|---|---|
| `C = H` *(treated)* | 6.15% | **1.40%** | 9.01% | **−81.6%** |
| `C = L` *(treated)* | 6.66% | **1.19%** | 6.07% | **−81.4%** |
| `H = O` *(placebo)* | 18.96% | 19.46% | 21.91% | −4.7% |
| `L = O` *(placebo)* | 16.28% | 19.67% | 22.03% | +2.7% |
| RS ÷ OC *(SD-scale)* | 1.062 | 1.077 | 0.982 | — |
| AddRS ÷ OC *(SD-scale)* | 1.236 | 1.231 | 1.208 | — |

**The treated indicators fall by about 81% and the placebo indicators do not move materially.**

To ask whether a window of that length placed anywhere would produce a comparable contrast, we
slide the same 186-day window across every start date in the sample that does not overlap the
real intervention, giving **193 placebo windows**. Their treated-indicator effects range from
**−31.8% to +29.8%**, with a median absolute effect of 13.0%. **None reaches the real effect's
magnitude** (placebo *p* = 0.0052).

**AddRS does not respond**: 1.236 → 1.231 → 1.208, a drift smaller than the placebo spread, even
though Rogers–Satchell itself moves. The correction's inputs change sharply and its output does
not, which is what §8.2 predicts when the correction is dominated by the term the rule change
does not touch.

**What this does not establish.** The two flanking periods do not agree with each other: `C = H`
runs 6.15% before and 9.01% after, a 46% difference, so this is not a clean return to baseline
and some of the contrast reflects drift across the panel rather than the rule. The effect is
sharp, specific to the treated indicators, and far outside anything the placebo windows produce;
that is strong associational evidence and short of clean identification. We describe it that way
and draw no causal conclusion about the exchange's decision.

### 8.5 Four distinct failures

| | failure | addressed by |
|---|---|---|
| 1 | **Path observation** — too few trades to sample the latent path | AddRS targets this |
| 2 | **Premise failure** — a downward-bias correction applied where the estimator is not downward-biased | diagnosis before correction; no estimator fixes this |
| 3 | **Scope** — an open-to-close estimator cannot observe `C₋₁ → O` | nothing within-session can |
| 4 | **Institutional censoring** — the pre-open band truncates the opening return | §9 |

Separating these is the paper's conceptual contribution. "Range estimators break in illiquid
markets" conflates all four, and in this market the binding one is not the first.

---

## 9. The opening auction and its band

Section 7 showed that the opening return carries 63.6% of close-to-close variance in thin equity
against 26.9% in dense equity. This section describes the institution that produces it, and reports
what we could not establish about it.

**Both auction rules leave fingerprints.** Trading opens with a pre-open call (10:30–10:45) in
which orders may be placed only within ±2% of the previous close, clearing at the volume-maximising
price; if no orders match, the opening price is set to the previous close. Both rules are visible:

| fingerprint | value |
|---|---|
| Non-zero opening returns within \|r_co\| ≤ 2.0% | 91.3% |
| Pile-up in (1.9%, 2.1%] — pinned at the band | 23.2% |
| p90 / p95 of \|r_co\| | 2.00% / 2.02% |
| Open exactly equal to previous close (no-match rule) | 10.8% |

![Figure 8](../output/figures/fig15_opening_auction.png)

**Figure 8.** Fingerprints of the pre-open call auction: the band pile-up and the no-match rule. *(Generated by `scripts/13_opening_auction.py`; source file `output/figures/fig15_opening_auction.png`.)*

**What the opening share does and does not mean.** A security that trades once has `O = H = L = C`,
so its intraday return is zero *by construction* and the whole daily move is booked at the open.
That is not price discovery migrating; it is intraday variance being unobservable. Removing
degenerate days is not clean either — it conditions on intraday movement having occurred, which
deflates the share. The two treatments **bracket rather than identify**, and we report the bracket
rather than a point estimate. Agarwalla, Jacob and Pandey (2015) find that on India's NSE the
opening call attracts very little volume and a large fraction of price discovery still occurs in
the first fifteen minutes of continuous trading; whether NEPSE's opening share reflects genuine
auction price discovery or the mechanical booking of a thin security's daily move is exactly the
distinction we cannot make.

**A model-based recovery, attempted and not reported as a result.** The band censors the opening
return at a known point, which makes a censored-normal recovery of latent dispersion available. We
fitted one and it does not survive its own out-of-sample test. In April 2026 the band widened from
±2% to ±5%. Under pure censoring the same latent distribution should govern both regimes, and the
wider window should reveal more of it. Fitted on the ±2% regime, the model predicts **0.14%** of
opens beyond ±5%; **6.93%** are observed, while the interior *tightens* (SD 0.0095 against a
predicted 0.0153) and the no-match rate nearly doubles from 9.1% to 17.4%. Tighter centre, fatter
extreme tail, more failures to clear: that is a change in behaviour, not a wider view of an
unchanged latent variable. The April revision was a bundle — band ±2%→±5%, daily limit 10%→15%, a
new intraday circuit breaker, and round-the-clock order entry — so we cannot isolate the band as
the cause. But the test does not need to: the model does not carry across the one regime change
available, so **we report no latent-dispersion estimate.** A treatment that modelled the band and
the daily price limit jointly (§7.1) is the obvious next step and we have not attempted it.

**The rule change is not exploited.** It is sharp, exogenous and precisely dated, but the window
has been inspected, so any test run now would be exploratory, and the bundling gives no clean
treatment.

## 10. Held-out evaluation

Panel A restricted to 1995 → 2024-03-03 was not used for hypothesis testing, model selection or
visualization. Prior exposure is disclosed: its dimensions, aggregate OHLC violation rate and
zero-range rate had been computed, and the violation rate informed the choice of cleaning rule.
This is therefore **pre-specified evaluation on minimally inspected historical data**, not a
sealed hold-out.

**The hypothesis.** The ratio of mean Parkinson variance to mean squared open-to-close return,
across year × trading-intensity cells, increases in intensity within the thin region. The
dependent variable is an **SD-scale ratio**. The unit of sorting is the **stock-day**, not the
security.

**Historical record.** As executed and reported, HO-2 pooled 52 thin cells from **325,901**
stock-days and 309 securities, giving **β = +0.0804** with a two-way clustered ***t*** **= 6.69**.
Repository reconstruction establishes that **no single execution produced this combination**: the
sample size and *t* belong to one computational vintage, whose coefficient is +0.0802, and the
coefficient belongs to a later vintage, whose sample size is 325,933 and whose *t* is 6.72. The
reported values combine outputs from different vintages.

**Consequence for confirmatory status.** The reported triple therefore cannot be treated as a
fully reproducible confirmatory computation. The provenance qualification recorded in the
pre-analysis amendment remains in force, and is not repaired by anything below.

**Current reconstruction.** Applying the current deterministic pipeline to the corrected data
gives **N = 325,262**, **β = +0.0805**, ***t*** **= 6.71**. The reduction against the historical
sample is fully accounted for: **325,901 + 32 − 671 = 325,262**, where +32 is the calibration
boundary change of commit `7d35e05` and −671 is the pre-committed duplicate-key rule (640
duplicated security-days: 622 exact, collapsed, and 18 with conflicting prices, excluded whole;
710 rows leave the panel and 671 of them would otherwise have entered HO-2). Duplicate handling
moves the sample materially and the estimate almost not at all — Δβ = +1.05e-04, Δ*t* = −0.017.
**This is reported as a reconstruction under the current pipeline, not as evidence that the
historical confirmatory computation produced the original triple.** That the substantive
estimate barely moves is reassuring, but closeness does not repair provenance.

**Post-hoc adversarial diagnostics.** These are not preregistered and are reported as
alternatives, not corrections. **Their generating code is not present in the replication
package**, and they are reported as recorded rather than as reproducible:

| specification | β | note |
|---|---|---|
| registered pooled | **+0.0804** | as executed |
| within-year (year fixed effects) | **+0.0667** | absorbs between-year variation |
| Mundlak β_within | +0.0667 | equals the FE coefficient, as it must |
| Mundlak β_between | **+0.2518** | rests on 14 year-level means |
| + instrument filter and range screen | +0.0815 | |
| security-level liquidity ranking | +0.0678 | a different estimand, not a correction |

The within and between slopes differ significantly (Mundlak test, *z* = −3.02, *p* = 0.0025), so
the pooled coefficient mixes two materially different parameters. The between-year relationship is
the more exposed to any year-varying confound and **we do not interpret it causally**.

The sign is positive across every specification examined, and the association survives duplicate
resolution, prespecified support trims, leave-one-year-out, split samples, and a label-permutation
placebo. Under lagged sorting — which removes contemporaneous co-movement between trading activity
and volatility — β attenuates to +0.0624.

**Two qualifications on confirmatory status, stated plainly.**

1. The analysis plan mandated a wild cluster bootstrap and designated its p-value as the one to
   report. **No implementation of that bootstrap existed in the repository or its history when the
   result was recorded.** A bootstrap implemented subsequently gives strong rejection under one
   defensible configuration and materially weaker rejection under another — the choice of which
   covariance estimator studentises the statistic moves the p-value by a factor of 37 — and the
   plan does not fix that choice. The historical figure remains provenance-unverified.
2. The hold-out's inclusion rule is a percentile of the exploratory panel, so corrections to the
   exploratory data mechanically redefine hold-out membership. This occurred: a later calendar
   correction moved 94 observations across the boundary. The recorded result is exactly
   reproducible from the frozen code and raw data, but only by rebuilding the superseded panel.

We therefore describe this as a supported association with qualified confirmatory provenance, and
not as a confirmed hypothesis.

---

## 11. Robustness

The headline result is a contrast between an equity definition and the pooled universe, so the
obvious objection is that it depends on how we drew the line. It does not. Every reasonable
alternative definition sits far from the pooled row.

| equity definition | securities | stock-days | median trades/day | `P(H = L)` |
|---|---|---|---|---|
| baseline: ticker convention validated against par value | 291 | 143,149 | 165 | **0.28%** |
| price-only, no ticker information used | 346 | 131,923 | 167 | 1.15% |
| ticker-only, no par-value validation | 341 | 163,914 | 135 | 0.87% |
| baseline, excluding NLO, BNL and UNL | 288 | 142,236 | 166 | 0.11% |
| baseline **plus** restricted promoter shares | 385 | 146,971 | 160 | 1.06% |
| **pooled universe, for contrast** | **520** | **184,390** | **111** | **5.70%** |

The worst case for us is the price-only classifier at 1.15%, still five times below the pooled rate
and twenty times below the thinnest decile's. Dropping the three securities that dominate the
cross-sectional variance of `P(H = L)` — NLO, BNL and UNL, whose median closes run to ₨46,888
against negligible free float — moves the figure the other way, to 0.11%. Adding promoter shares
back in, which is defensible since they are equity in the same firms held under transfer
restrictions, gives 1.06%.

**The finding is a property of the instrument mix, not of our classification rule.**

Robustness of the other results is reported where they appear rather than collected here: the
support trims, leave-one-year-out, split samples, duplicate-resolution invariance and
label-permutation placebo for §10; the tolerance ladder for §8.3; and the price-limit sensitivity
for §7.1.

---

## 12. What this paper contributes

Stated once, plainly, so it can be held against the evidence.

**The boundary condition.** Any correction of the form `RS + Δ` with `Δ ≥ 0` almost surely has
positive expected bias in a regime where Rogers–Satchell is already unbiased against the target.
That is not a claim about one estimator, and it is why we can state a conclusion about corrections
whose equations we could not obtain. AddRS is the instance we can measure: it overstates from 1.149
to 1.323 across equity liquidity quintiles here, while landing on 1.005 for the NIFTY 50, and
Rogers–Satchell sits at 0.998 against a matched benchmark in thin equity.

**The limit of that test.** The correction targets `E[RS] < σ²`, and `σ²` is unobserved. Our
benchmark is mean squared open-to-close returns — conditionally unbiased but imperfect, and Patton
(2011) shows imperfect proxies distort precisely this comparison. So we report that **no downward
bias is detectable against the benchmark the data support**, not that the correction's premise is
false. Separating the theoretical bias from what a proxy can reveal would require a validation
target this market does not offer, and that is a limitation of the test rather than a finding.

**Why the sample decides whether that is visible.** When a mixed-security price feed is analysed
without security-type classification, zero-range observations concentrate heavily in non-equity
instruments. The pooled sample then displays exactly the downward bias an additive correction
exists to repair — Rogers–Satchell at 0.172 against the matched benchmark in its thinnest quintile
— while the equity sample reads 1.184. A researcher working the pooled feed would conclude the
correction's premise holds and apply it; the premise is an artifact of the sample:

| | pooled universe | ordinary equity |
|---|---|---|
| Parkinson exactly zero | 5.70% | **0.28%** |
| thinnest quintile `RS ÷ Var(x)`, variance scale | 0.172 | **1.184** |
| median trades/day | 111 | **165** |

The thinnest decile of the pooled universe — the one carrying the apparent breakdown — is 94.3%
non-equity.

**What is not ours.** Restricting samples to ordinary common shares is long-standing practice in
the emerging-market liquidity literature. The zero-range case, its origin in sparse trading, and
prescriptions for handling it are documented in the bid–ask spread literature working on the same
daily high–low inputs. That finite observation biases the range downward, particularly for
lower-liquidity assets, is stated in the standing survey of range volatility. **We propose no new
estimator, no zero-range correction, and no liquidity measure.**

**What is ours.** Quantifying the downstream methodological consequences of an otherwise familiar
sample-construction omission, in a real market where the filter cannot be applied mechanically
because the exchange publishes no instrument-type field. The liquidity literature applies that
filter to protect a *liquidity measure*; we show the same omission determines whether one concludes
that range-based estimators are viable in the market at all. That is a different downstream
question, and the answer flips.

**A second instance of the same lesson, not a second instance of the same cause.** §7.1 shows that
excluding days on which the daily price limit binds moves the thin-equity opening variance share
from 0.641 to 0.742 — 1.2% of rows moving a headline figure by 15.8%. This is a sample-definition
choice altering a headline number, which is the paper's general theme. **It is not evidence for the
composition result and we do not claim it is**: the price limit and the instrument mix are
unrelated mechanisms, and nothing here establishes a link between them.

**Size, honestly.** This is a case study. If a researcher applies the filter the liquidity
literature already prescribes, none of what §5 documents happens. The contribution is a measured
account of what the omission costs, in a setting where following best practice first requires
building a classifier — not a discovery that filtering matters.

---

## 13. What is not established

- **A causal reading of the closing-rule change.** The treated indicators fall ~81% while the
  placebo indicators move under 5%, and none of 193 placebo windows reproduces the effect
  (§8.4). But the two flanking periods differ from each other by 46% on the treated indicator,
  so the design is not a clean return to baseline. We report it as strong associational evidence
  and use no causal language.
- **The pre-open band is not shown to be censoring.** Fitted on the ±2% regime, the censored
  normal predicts 0.14% of opens beyond ±5%; 6.93% are observed, while the interior tightens
  (§9). The assumption fails the one out-of-sample test available. The April 2026 change was a
  bundle, so we cannot isolate the band as the cause — but the model does not extrapolate, so **no
  latent-dispersion estimate is reported**.
- **Simulation evidence is illustrative, not independent validation.** We audited the
  parameters for circularity and found none: the data-generating process is the textbook
  discretely-observed geometric Brownian motion the estimators are derived under, the trade grid
  spans rather than fits the empirical range, and the bias ratio is invariant to the choice of
  true sigma (identical to nine decimals across a sixteen-fold range). Two limits should be
  stated anyway. First, the latent path is itself discretised at 2,000 steps, so even dense
  observation recovers only about 97% of true sigma; the simulation's own ceiling is 0.97, not
  1.00, and the existing recovery test passes because its tolerance absorbs that. Second, and
  more substantively, **the simulation does not reproduce what we observe.** At 37 trades per day
  — the thinnest equity quintile's intensity — it predicts a Parkinson ratio of 0.857 and a zero
  `P(H = L)` rate, whereas the equity data at that intensity show `P(H = L)` of 1.26% and a ratio
  slightly above one. The denominators differ (true sigma in the simulation, a noisy open-to-close
  proxy in the data), so this is not a clean contradiction, but the discretisation mechanism does
  not by itself account for the equity pattern and we do not present it as if it did.
- **No security-level cross-market comparison exists.** Every cross-market statement rests on
  index-versus-index or index-versus-stock contrasts. Constituent-level NIFTY data with trade
  counts would be required.
- **ABC is not implemented** and we make no claim about it.
- **Shaik and Maheswaran's (2020) successor estimator is not benchmarked.** Its equations could not
  be obtained, and we do not implement estimators from secondary descriptions. §8.2's proposition
  covers it *conditionally* — if its correction term is non-negative, the argument applies — but
  **whether it satisfies that condition is unverified**, and no empirical comparison against it is
  offered. A referee is entitled to ask for one.
- **The premise test rests on an imperfect proxy.** AddRS targets `E[RS] < σ²`; we observe RS
  against mean squared open-to-close returns. Patton (2011) shows imperfect proxies distort such
  comparisons. We report no detectable downward bias against the available benchmark, which is a
  weaker statement than the premise being false, and the gap between them is not closed here.
- **The AddRS derivation is unverified from the primary source** (§8).
- **The published 0.82 comparison is unresolved by data availability**, not by method (§7).
- **The opening share of variance is bracketed, not identified** (§9).
- **The April 2026 rule change is confounded** and unexploited (§9).
- **The daily price limit is measured but not modelled.** §7.1 shows it moves the thin-equity
  opening share by 15.8%. A joint treatment of the ±2% band and the ±10% limit is the obvious next
  step and is not attempted here.
- **Circuit-breaker censoring of the continuous session is unmodelled.**
- **2026-07-25's status as a special session is provisional**, pending an exchange notice.
- **Panel A's 8.05% OHLC violation rate versus panel B's 0.60% is unexplained.**
- **Four primary texts remain unread**, and their equations are taken from secondary or
  author-reproduced sources: the AddRS derivation, Parkinson's estimator, Garman–Klass's estimator
  (where two distinct forms circulate and we implement the simplified one), and Rogers–Satchell's
  own discretisation correction. Every bibliographic record is now verified; `literature-review.md`
  §J lists what remains open. The provisional novelty claim carried by an earlier draft — that the
  zero-**range** analogue of the contaminated zero-**return** proxy was undocumented — has been
  **withdrawn**: Corwin and Schultz (2012) and Ardia, Guidotti and Kroencke (2024) document the
  zero-range case and its origin in sparse trading, and the Parkinson and Garman–Klass equations
  have been checked only against secondary sources.

---

## References

*Entries marked **(verified)** have had their bibliographic record confirmed against a
publisher or RePEc listing during this revision, and where a claim is attributed to them in the
text, that claim checked against the source's own abstract or summary. Entries marked
**(unverified)** have not.*

Bekaert, G., Harvey, C. R., and Lundblad, C. (2007). Liquidity and expected returns: lessons from
emerging markets. *Review of Financial Studies* 20(6), 1783–1831. **(verified)** — primary
liquidity measure is a transformation of the proportion of zero daily firm returns.

Cameron, A. C., Gelbach, J. B., and Miller, D. L. (2008). Bootstrap-based improvements for
inference with clustered errors. *Review of Economics and Statistics* 90(3), 414–427.
**(verified)** — asymptotic cluster-robust tests over-reject with few (roughly five to thirty)
clusters; wild cluster bootstrap-t provides the refinement.

Christensen, K., and Podolskij, M. (2007). Realized range-based estimation of integrated
variance. *Journal of Econometrics* 141(2), 323–349. **(verified)** — intraday realized range.

Christensen, K., Podolskij, M., and Vetter, M. (2009). Bias-correcting the realized range-based
variance in the presence of market microstructure noise. *Finance and Stochastics* 13(2), 239–268.
DOI 10.1007/s00780-009-0089-9. **(verified)** — intraday.

Corsi, F. (2009). A simple approximate long-memory model of realized volatility. *Journal of
Financial Econometrics* 7(2), 174–196. DOI 10.1093/jjfinec/nbp001. **(verified)**

Garman, M. B., and Klass, M. J. (1980). On the estimation of security price volatilities from
historical data. *Journal of Business* 53(1), 67–78. *(metadata verified; equation unverified —
note that two distinct forms circulate, and we implement the simplified one)*

Agarwalla, S. K., Jacob, J., and Pandey, A. (2015). Impact of the introduction of call auction on
price discovery: evidence from the Indian stock market using high-frequency data. *International
Review of Financial Analysis* 39, 167–178. **(verified)**

Ardia, D., Guidotti, E., and Kroencke, T. A. (2024). Efficient estimation of bid–ask spreads from
open, high, low, and close prices. *Journal of Financial Economics* 161, 103916.
DOI 10.1016/j.jfineco.2024.103916. **(verified)**

Akay, O., Griffiths, M. D., and Winters, D. B. (2010). On the robustness of range-based volatility
estimators. *Journal of Financial Research* 33(2), 179–199. **(verified)**

Chou, R. Y., Chou, H., and Liu, N. Range volatility: a review of models and empirical studies.
*Handbook of Financial Econometrics and Statistics*, Springer, ch. 74, 2029–2050. **(verified —
chapter read)**

Corwin, S. A., and Schultz, P. (2012). A simple way to estimate bid–ask spreads from daily high and
low prices. *Journal of Finance* 67(2). **(verified)** — prescribes carrying forward the previous
day's extrema when infrequent trading yields identical high and low prices.

Ibikunle, G. (2015). Opening and closing price efficiency: do financial markets need the call
auction? *Journal of International Financial Markets, Institutions and Money* 34, 208–227.
DOI 10.1016/j.intfin.2014.11.014. **(verified)**

Jacob, J., and Vipul (2008). Estimation and forecasting of stock volatility with range-based
estimators. *Journal of Futures Markets* 28(6), 561–581. DOI 10.1002/fut.20321. **(verified —
including the quotation in §3, and the attribution of Parkinson's poor performance to drift)**

Kumar, D., and Maheswaran, S. (2014). A reflection principle for a random walk with implications
for volatility estimation using extreme values of asset prices. *Economic Modelling* 38, 33–44.
DOI 10.1016/j.econmod.2013.11.045. **(metadata verified; derivation and unbiasedness proof
unverified — operational equations taken from a later author reproduction and checked against it)**

Meilijson, I. (2008). The Garman–Klass volatility estimator revisited. arXiv:0807.3492.
**(verified)** — confirms the efficiency figure of 7.4, shows the estimator is not minimum-variance,
and reports that heavy-tailed increments favour a different construction.

Shaik, M., and Maheswaran, S. (2020). A new unbiased additive robust volatility estimation using
extreme values of asset prices. *Financial Markets and Portfolio Management* 34, 313–347.
DOI 10.1007/s11408-020-00355-3. **(verified)** — a successor to AddRS, not tested here.

Kumar, D., and Maheswaran, S. (2014b). Modeling and forecasting the additive bias corrected
extreme value volatility estimator. *International Review of Financial Analysis* 34, 166–176.
DOI 10.1016/j.irfa.2014.06.002. **(verified)** — the downstream forecasting treatment of AddRS;
not the derivation source, which is Kumar and Maheswaran (2014) above.

Lesmond, D. A. (2005). Liquidity of emerging markets. *Journal of Financial Economics* 77(2),
411–452. **(verified)**

Lesmond, D. A., Ogden, J. P., and Trzcinka, C. A. (1999). A new estimate of transaction costs.
*Review of Financial Studies* 12(5), 1113–1141. **(verified)** — estimates transaction costs from
the incidence of zero returns via a limited dependent variable model.

Lo, A. W., and MacKinlay, A. C. (1990). An econometric analysis of nonsynchronous trading.
*Journal of Econometrics* 45(1–2), 181–211. **(verified)**

Maheswaran, S., Balasubramanian, G., and Yoonus, C. A. (2011). Post-colonial finance. *Journal of
Emerging Market Finance* 10(2), 175–196. DOI 10.1177/097265271101000202. **(verified)** — source
of the extreme-value variance ratio.

Maheswaran, S., and Kumar, D. (2013). An automatic bias correction procedure for volatility
estimation using extreme values of asset prices. *Economic Modelling* 33, 701–712.
DOI 10.1016/j.econmod.2013.05.019. **(verified)** — ABC is described by its authors as an
empirical procedure requiring no knowledge of `N`.

Martens, M., and van Dijk, D. (2007). Measuring volatility with the realized range. *Journal of
Econometrics* 138(1), 181–207. **(verified)** — proposes the realized range from intraday data,
with a bias correction scaling it by the average level of the daily range.

Parkinson, M. (1980). The extreme value method for estimating the variance of the rate of return.
*Journal of Business* 53(1), 61–65. *(metadata verified; equation unverified)*

Patton, A. J. (2011). Volatility forecast comparison using imperfect volatility proxies.
*Journal of Econometrics* 160(1), 246–256. **(verified)** — imperfect proxies distort standard
forecast comparisons; conditions on the loss function are required for robust rankings.

Rogers, L. C. G., and Satchell, S. E. (1991). Estimating variance from high, low and closing
prices. *Annals of Applied Probability* 1(4), 504–512. DOI 10.1214/aoap/1177005835.
**(verified)** — abstract read in full: unbiased whatever the drift under continuously observed
Brownian motion, and the discrete-extrema error and a correction for it are stated there.

Rogers, L. C. G., Satchell, S. E., and Yoon, Y. (1994). Estimating the volatility of stock prices:
a comparison of methods that use high and low prices. *Applied Financial Economics* 4(3), 241–247.
*(metadata verified; the specific treatment of discretisation attributed to it in §3 is not)*

Vipul, and Jacob, J. (2007). Forecasting performance of extreme-value volatility estimators.
*Journal of Futures Markets*. DOI 10.1002/fut.20283. *(metadata verified)*

Yang, D., and Zhang, Q. (2000). Drift-independent volatility estimation based on high, low, open
and close prices. *Journal of Business*. *(metadata verified; equation unverified)*
