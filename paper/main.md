# What Looks Like Illiquidity: Instrument Composition and Range-Based Volatility Estimation in a Frontier Market

**Draft v0.5 · 2026-08-29 · not for circulation**

> **Status.** Exploratory unless a claim is explicitly labelled otherwise. One hypothesis has
> been evaluated on held-out data; its confirmatory provenance carries a stated qualification
> (§10). Every ratio in this paper is labelled **variance-scale** or **SD-scale**, because the
> two differ by a square root and an earlier draft mixed them across adjacent sections.
> Section 12 states what is not established.

---

## Abstract

Range-based volatility estimators are the standard recommendation for markets without options,
and a large literature holds that infrequent trading biases them downward. We ask what that
bias looks like in a frontier market, and find first that the question is easy to answer
wrongly. Using 184,390 stock-days from the Nepal Stock Exchange, a market with no listed equity
derivatives, we show that the apparent failure of range estimators in this market is generated
almost entirely by **instrument composition rather than by illiquidity**. NEPSE publishes
ordinary equity, corporate debentures, closed-end mutual funds and restricted promoter shares
in one daily file with no instrument-type field. Sorted on trading intensity, the thinnest
decile of that pooled universe is **94.3% non-equity**, and it is there that the estimators
appear to break: the Parkinson estimator returns exactly zero on 53.9% of its stock-days.
Restricted to the 291 ordinary equities, the picture inverts. Participation is 1.000 in every
liquidity quintile, the thinnest equity quintile trades 37 times a day, `P(H = L)` is 0.28%
across the sample, and Rogers–Satchell measured against a matched open-to-close benchmark is
**0.998 on a variance scale** — a point estimate essentially at one, with no interval attached.
On the evidence available here, NEPSE's ordinary equity market is liquid enough that range
estimators work.

Three further results survive that correction. First, the additive bias correction AddRS
(Kumar and Maheswaran, 2014) **overstates at every liquidity level we can measure** — from
1.149 in the most active equity quintile to 1.323 in the second (SD-scale, against a matched
open-to-close benchmark) — while landing on 1.005 for the NIFTY 50. This is a premise failure
rather than an estimator failure: the correction is non-negative by construction, so wherever
Rogers–Satchell is not downward-biased in expectation, adding it must overshoot in expectation.
Second, a decomposition of the correction shows its boundary conditions fire on 91.9% of days
in the thinnest quintile but supply only a small absolute correction each, while the most
active quintile fires on 37.4% of days and supplies 4.5 times more per firing — so frequency of
correction, absolute correction mass, and correction relative to the estimator are three
different things and point in different directions. Third, NEPSE's pre-open call auction bands
the opening return at ±2% of the previous close, and a censored-normal model puts observed
opening dispersion about 30% below its fitted latent counterpart, roughly flat across liquidity.
We then test that model's maintained assumption against the April 2026 widening of the band to
±5% and it fails: the wider window does not reveal the distribution the narrower one implies.
We therefore report this as a within-regime description, not as recovery of a latent quantity.

The contribution is a case study, and we state its limits with it. Restricting samples to ordinary
common shares is long-standing practice in the emerging-market liquidity literature; the zero-range
case and its origin in sparse trading are documented in the bid–ask spread literature working on the
same daily inputs. **We propose no new estimator and no zero-range correction.** What we document is
the downstream consequence of omitting a familiar filter in a market where it cannot be applied
mechanically, because the exchange publishes no instrument-type field: that literature applies the
filter to protect a *liquidity measure*, and the same omission determines whether one concludes that
range-based estimators are viable in the market at all.

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

1. **A composition artifact that mimics illiquidity.** Pooling the securities an exchange
   publishes, without an instrument filter the exchange does not supply, manufactures a
   liquidity gradient that is an asset-class gradient. On the pooled NEPSE universe the standard
   diagnostics reproduce the textbook picture of estimator breakdown; on ordinary equity alone
   they do not. The remedy — restricting to ordinary common shares — is standard practice in the
   emerging-market liquidity literature and we claim no credit for it (§3.1). What we add is the
   range-estimator version of that known problem, which is sharper because a range estimator with
   `H = L` returns exactly zero rather than merely becoming noisy; the observation that the filter
   is not mechanically available where no instrument-type field is published; and a measurement of
   what its omission does.
2. **A boundary condition on the leading daily-OHLC correction.** AddRS overstates at every
   equity liquidity level in this market while performing as designed on a dense index. We show
   this follows from the correction's construction wherever its premise does not hold, and we
   decompose where its mass actually comes from.
3. **A separation of four distinct failure modes** that "range estimators break in illiquid
   markets" conflates: path observation, premise failure, benchmark scope, and institutional
   censoring of the opening return.

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

**A banded pre-open call auction.** Trading opens with a pre-open session (10:30–10:45) in which
orders may be placed only within **±2% of the previous close**. The engine clears at the
volume-maximising price, and if no orders match, the opening price is set equal to the previous
close. Section 9 shows both rules are visible in the data. The band was widened to ±5% in April
2026 as part of a bundle of simultaneous changes, which is why we do not treat it as a natural
experiment (§12).

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
§9.1 says we cannot identify.

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

This is the paper's first result and the reason for everything that follows.

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
| NEPSE equity | 701 | 0.972 | 0.00% |
| NEPSE equity | 297 | 1.028 | 0.00% |
| NEPSE equity | 165 | 1.045 | 0.00% |
| NEPSE equity | 78 | 1.058 | 0.00% |
| NEPSE equity | **33** | **0.935** | **1.63%** |
| NEPSE index (aggregate) | — | 0.835 | 0.22% |

Two things to note, and one caution.

The equity profile is **close to one throughout and is not monotone**: it rises from 0.935 at 33
trades per day to 1.058 around 78, then declines to 0.972 at 701. The thin end shows a modest
deficit, not a collapse. For comparison, the same table computed on the pooled universe puts its
thinnest bucket at 3 trades per day, a Parkinson ratio of 0.792 and a zero-range rate of 36.05%.


![Figure 4](../output/figures/fig12_cross_market.png)

**Figure 4.** Estimator ratios across three regimes under identical code. All values SD-scale. *(Generated by `scripts/09_cross_market_control.py`; source file `output/figures/fig12_cross_market.png`.)*

**The caution.** The NEPSE index sits at 0.835 while the NIFTY 50 index sits at 0.978, and both
are dense. We report this rather than omitting it: an index is a diversified portfolio and its
range behaves differently from a single security's, so an index-versus-stock comparison is not
like-for-like. **No security-level cross-market comparison exists in this paper.** Any claim that
NEPSE equities and NIFTY constituents behave identically would require constituent-level NIFTY
data with trade counts, which we do not hold (§12).

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

**Figure 5.** Decomposition of close-to-close variance into overnight, intraday and covariance components. All values variance-scale. *(Generated by `scripts/12_benchmark_diagnosis.py`; source file `output/figures/fig14_benchmark_diagnosis.png`.)*

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

## 8. AddRS: a correction whose premise does not hold here

The additive bias correction of Kumar and Maheswaran (2014) reduces exactly. With `b = ln(H/O)`,
`c = ln(L/O)`, `x = ln(C/O)`, `u = 2b − x`, `v = 2c − x`:

`AddRS = ½[½(u²−x²) + x²·1{H=O or C=H}] + ½[½(v²−x²) + x²·1{L=O or C=L}]`

Since `½(u²−x²) = 2b(b−x)`, the indicator-free part is *identically* Rogers–Satchell, so

$$\text{AddRS} = \text{RS} + \tfrac{x^2}{2}\left(\mathbb{1}_u + \mathbb{1}_v\right)$$

The correction substitutes the squared open-to-close return whenever an observed extreme
coincides with the open or the close — the monotone case where RS collapses to zero. It is
**non-negative, and exactly zero** on the 44.9% of stock-days where neither indicator fires.

*A successor we do not test.* Shaik and Maheswaran (2020) propose a further unbiased additive
estimator from the same research group. We have not read or benchmarked it, so §8's result should
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

### 8.2 Why: the premise, not the mechanism

The correction is non-negative, so it can only help where Rogers–Satchell is biased downward.
Stated at the level bias actually lives:

> Within a regime, `E[AddRS] = E[RS] + ½·E[x²(I_u + I_v)]`, and the second term is ≥ 0 with
> equality only if `x²(I_u + I_v) = 0` almost surely. So if `E[RS]` already equals the target in
> that regime, and the indicators fire with positive probability on days where `C ≠ O`, then
> `E[AddRS]` exceeds the target: **AddRS has positive expected bias in that regime.**

Table 8.1 shows `RS ÷ OC` at or above 0.98 in every equity quintile. The premise of the
correction is not satisfied anywhere in this sample, so the overshoot follows.

This is not a criticism of the estimator. It solves a different measurement problem, in a regime
this market's equity does not occupy.

### 8.3 Where the correction actually comes from

Using the identity, the total correction mass decomposes exactly as
`share = observation share × firing probability × mean correction per firing`. That factorisation
reproduces the mass column to within 0.1% in every quintile.

| quintile | median trades | firing probability | mean correction \| firing | **correction ÷ RS** | share of mass |
|---|---|---|---|---|---|
| Q1 | 5 | **0.919** | 2.581e-04 | **1.660** | 16.1% |
| Q2 | 43 | 0.566 | 5.920e-04 | 0.579 | 21.8% |
| Q3 | 112 | 0.465 | 4.898e-04 | 0.348 | 15.0% |
| Q4 | 228 | 0.424 | 6.493e-04 | 0.360 | 18.3% |
| Q5 | 590 | **0.374** | **1.159e-03** | 0.379 | **28.8%** |

Three distinct facts, which an aggregate statement would merge:

- **Frequency.** Boundary conditions fire 2.5× more often in the thinnest quintile than the most
  active one — and still fire on 37% of days in the most active.
- **Absolute mass.** The most active quintile nevertheless supplies the largest share, because
  the correction term is `x²/2` per firing and mean `x²` runs 3.00e-04 in Q1 against 1.18e-03 in
  Q5. Thin securities barely move, so each firing contributes little.
- **Relative to the estimator.** In Q1 the correction is **166% of Rogers–Satchell itself**,
  against roughly 0.35–0.58 elsewhere. That is where AddRS transforms the estimate most.

Only 5.7% of the correction mass comes from degenerate (`H = L`) bars and 0.3% from one-trade
bars, so the correction is not an artifact of mechanically constrained sessions. It is also not
numerically fragile: exact price equality and a 1e-12 relative tolerance give identical results,
and widening to a full tick moves the headline by 0.63%.

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

### 9.1 The mechanical channel must be excluded first

A security that trades once has `O = H = L = C`, so its intraday return is zero *by construction*
and the whole daily move is forced into the opening return. That is not price discovery
migrating; it is intraday variance being unobservable. Removing such days is itself not clean —
it conditions on intraday movement having occurred, which deflates the opening share. The two
treatments **bracket rather than identify**, and we report the bracket.

### 9.2 Both auction rules leave fingerprints

| fingerprint | value |
|---|---|
| Non-zero opening returns within \|r_co\| ≤ 2.0% | 91.3% |
| Pile-up in (1.9%, 2.1%] — pinned at the band | 23.2% |
| p90 / p95 of \|r_co\| | 2.00% / 2.02% |
| Open exactly equal to previous close (no-match rule) | 10.8% |


![Figure 7](../output/figures/fig15_opening_auction.png)

**Figure 7.** Fingerprints of the pre-open call auction: the band pile-up and the no-match rule. *(Generated by `scripts/13_opening_auction.py`; source file `output/figures/fig15_opening_auction.png`.)*

The opening return is not overnight news. It is a composite of overnight information, auction
price discovery, correction of a stale previous close, and auction microstructure. For a security
that traded twice yesterday, the previous close is itself a poor reading of latent value.

### 9.3 Recovering what the band hides — exploratory

The band censors the opening return **at a point known exactly**, which makes a model-based
recovery available. We assume the observed opening price is a censored realization of a latent
unconstrained opening return, and estimate latent dispersion by maximum likelihood from the
interior observations plus the censored mass.

> **The maintained assumption, stated because it is doing the work.** An order-price band changes
> which orders investors may submit and plausibly which they choose to submit, so a boundary open
> does not prove that an otherwise unconstrained auction would have cleared beyond it. What
> follows is a structural estimate under that assumption. **We have not verified that the
> band constitutes censoring in the econometric sense rather than a structural bound on the
> observable, and until we do this result is exploratory and model-based, not structural
> evidence.**

On 227 equity securities in the ±2% regime:

| | |
|---|---|
| Median share of opens pinned at the band | 27.4% |
| Median latent ÷ observed opening dispersion | **1.295** |
| Securities understated by more than 25% | 64.8% |


![Figure 8](../output/figures/fig17_censored_open.png)

**Figure 8.** Latent against observed opening dispersion under the censored-normal model. Exploratory; see §9.4 for the test this model fails. *(Generated by `scripts/16_censored_open.py`; source file `output/figures/fig17_censored_open.png`.)*

The inflation factor is **roughly flat in liquidity** — 1.331, 1.300, 1.262, 1.273, 1.295 across
trade-count quintiles. If the effect were a thin-trading phenomenon it should decline with
activity, and it does not.

**Limitation.** For a minority of securities the estimator returns a latent dispersion below the
raw one, which is impossible under the model: their opening returns are bimodal, with mass near
zero and mass at the band, and a single normal cannot represent that. They are excluded and
counted. Excluding them biases the reported median upward, and we note that the median over all
securities including them would be lower.

### 9.4 The censoring assumption does not extrapolate across the band change

The maintained assumption is testable in one place. In April 2026 the band widened from ±2% to
±5%. If the band were pure censoring — a latent opening return observed through a window — the
same latent distribution should govern both regimes, and the wider window should simply reveal
more of it. We fit the censored normal on the ±2% regime (118,376 equity opens) and ask what it
predicts for the ±5% regime (24,482 opens).

| quantity | predicted from ±2% fit | observed under ±5% |
|---|---|---|
| share beyond ±5% | **0.14%** | **6.93%** |
| \|r_co\| 90th percentile | 0.0259 | **0.0476** |
| \|r_co\| 95th percentile | 0.0307 | 0.0493 |
| SD of interior (\|r\| < 2%) opens | 0.0153 | **0.0095** |
| share in the newly opened 2–5% corridor | 19.4% | 23.4% |

**The extrapolation fails, and it fails in a diagnostic direction.** Under the wider band the
interior of the distribution became *tighter* (SD 0.0095 against a predicted 0.0153) while far
more mass sits at or beyond the new boundary than censoring predicts — 6.93% against 0.14%, a
factor of roughly fifty. The no-match rate also rose from 9.1% to 17.4%. Tighter centre, fatter
extreme tail, more failures to clear: that is a change in behaviour, not a wider view of an
unchanged latent variable.

**What we can and cannot conclude.** We cannot attribute this to the band alone, because the
April 2026 revision was a bundle — band ±2%→±5%, daily price limit 10%→15%, a new intraday
circuit breaker, and round-the-clock order entry. Any of those could alter opening behaviour. But
the test does not depend on isolating the cause: it shows that the pure-censoring model does not
carry across the one regime change we can observe.

**We therefore report §9.3 as a within-regime descriptive summary of how much dispersion the
observed opening returns understate under a fixed band, and not as recovery of a structural
latent quantity.** The number is a model-based description; treating it as identification of
suppressed volatility would require the assumption this test declines to support.

### 9.5 A rule change we do not exploit

Monthly fingerprints locate a sharp regime change: through 2026-03 the 95th percentile of the
opening return is pinned at 2.01% every month; from April 2026 it jumps to ~4.9% and the boundary
pile-up collapses from ~30% to ~3%. The reform is real, sharp and precisely dated. **It is not
exploited here**, for two reasons: the window has been inspected, so any test run now would be
exploratory; and the April 2026 revision was a bundle — band ±2%→±5%, daily price limit 10%→15%,
a new intraday circuit breaker, and round-the-clock order entry. Four simultaneous changes give
no clean treatment.

---

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

**Registered result.** Pooled across 52 thin cells from 325,901 stock-days and 309 securities:
**β = +0.0804**, two-way clustered *t* = 6.69.

**Post-hoc adversarial diagnostics.** These are not preregistered and are reported as
alternatives, not corrections:

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

## 11. What this paper contributes

Stated once, plainly, so it can be held against the evidence.

**The failure mode.** When a mixed-security price feed is analysed without security-type
classification, zero-range observations become heavily concentrated in non-equity instruments.
That concentration distorts volatility diagnostics and can reverse the conclusion a researcher
draws about estimator performance. In this market it does reverse it:

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

## 12. What is not established

- **A causal reading of the closing-rule change.** The treated indicators fall ~81% while the
  placebo indicators move under 5%, and none of 193 placebo windows reproduces the effect
  (§8.4). But the two flanking periods differ from each other by 46% on the treated indicator,
  so the design is not a clean return to baseline. We report it as strong associational evidence
  and use no causal language.
- **The pre-open band is not shown to be censoring.** Fitted on the ±2% regime, the censored
  normal predicts 0.14% of opens beyond ±5%; 6.93% are observed, while the interior tightens
  (§9.4). The assumption fails the one out-of-sample test available. The April 2026 change was a
  bundle, so we cannot isolate the band as the cause — but the model does not extrapolate, and
  §9.3 is reported as description rather than identification.
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
- **ABC is not implemented** and we make no claim about it. Nor is Shaik and Maheswaran's (2020)
  successor estimator, so §8 bounds AddRS and not the wider family of daily-OHLC corrections.
- **The AddRS derivation is unverified from the primary source** (§8).
- **The published 0.82 comparison is unresolved by data availability**, not by method (§7).
- **The opening share of variance is bracketed, not identified** (§9.1).
- **The April 2026 rule change is confounded** and unexploited (§9.4).
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
including the quotation in §3, and the attribution of Parkinson's poor performance to drift)*

Kumar, D., and Maheswaran, S. (2014). A reflection principle for a random walk with implications
for volatility estimation using extreme values of asset prices. *Economic Modelling* 38, 33–44.
DOI 10.1016/j.econmod.2013.11.045. **(metadata verified; derivation and unbiasedness proof
unverified — operational equations taken from a later author reproduction and checked against it)*

Meilijson, I. (2008). The Garman–Klass volatility estimator revisited. arXiv:0807.3492.
**(verified)** — confirms the efficiency figure of 7.4, shows the estimator is not minimum-variance,
and reports that heavy-tailed increments favour a different construction.

Shaik, M., and Maheswaran, S. (2020). A new unbiased additive robust volatility estimation using
extreme values of asset prices. *Financial Markets and Portfolio Management* 34, 313–347.
DOI 10.1007/s11408-020-00355-3. **(verified)** — a successor to AddRS, not tested here.

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
