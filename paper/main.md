# What Looks Like Illiquidity: Instrument Composition and Range-Based Volatility Estimation in a Frontier Market

**Draft v0.5 · 2026-08-29 · not for circulation**

> **Status.** Exploratory unless a claim is explicitly labelled otherwise. One hypothesis has
> been evaluated on held-out data; its confirmatory provenance carries a stated qualification
> (§10). Every ratio in this paper is labelled **variance-scale** or **SD-scale**, because the
> two differ by a square root and an earlier draft mixed them across adjacent sections.
> Section 11 states what is not established.

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
the opening return at ±2% of the previous close, and a censored-normal model estimates that the
band conceals a materially larger latent opening dispersion, roughly flat across liquidity.
That last result is model-based and exploratory.

The contribution is methodological. A frontier-market study that pools whatever an exchange
publishes will find an illiquidity result that is really a composition result, and the two are
distinguishable only with an instrument classification the exchange does not provide.

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
   diagnostics reproduce the textbook picture of estimator breakdown. On ordinary equity alone
   they do not. We show the mechanism, quantify it, and give the classification rule.
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
experiment (§11).

---

## 3. Related literature, and what is not claimed here

**Finite-sampling bias is established, and so is the discrete-extrema problem.** Rogers and
Satchell (1991) identify it in the paper introducing their estimator and offer a correction.
Martens and van Dijk (2007) state that infrequent trading biases the realized range downward and
propose a scaling correction; Christensen and Podolskij (2007) derive asymptotics; Christensen,
Podolskij and Vetter (2009) bias-correct the realized range under microstructure noise. Rogers,
Satchell and Yoon (1994) use a proxy for the number of transactions to correct discretisation
bias directly. *(Whether the 1994 transaction-proxy correction is the same construction as the
1991 paper's is not established here; we have read the 1991 abstract, not its Section 3.)*

**And bias is correctable from daily data.** Maheswaran and Kumar (2013) propose an **empirical**
automatic bias correction (ABC) for extreme-value volatility estimators that requires no
knowledge of `N`, the number of steps. Kumar and Maheswaran (2014) separately introduce the
**AddRS** estimator, derived from a reflection principle for a random walk with symmetric
double-exponential increments, and show it is exactly unbiased **under that model**. These are
two different procedures from two different papers, and we keep them apart: ABC is empirical and
approximate; AddRS is theoretical and exact under its own maintained model. We implement AddRS
and benchmark it. **We do not implement ABC and make no claim about its performance.**

**The variance ratio.** The variance-ratio statistic built from extreme prices is due to
Maheswaran, Balasubramanian and Yoonus (2011). Maheswaran and Kumar (2013) report a value of
0.82 for the Rogers–Satchell estimator against the "usual" close-to-close estimator on the Nifty
index over 1996–2011, and attribute the shortfall to the random-walk effect.

**Range estimators survive moderate illiquidity.** Jacob and Vipul (2008), benchmarking against
two-scale realized volatility, report that daily range estimators are not downwardly biased under
negative autocorrelation and low liquidity, identifying drift as the main source of Parkinson's
problems. *(We cite this from the secondary literature; the primary text is not verified.)*

**Opening call auctions are a studied object.** Work on several exchanges finds that opening-call
failures concentrate among low-volume stocks and that effectiveness depends on institutional
design. Our contribution is not that thin securities concentrate repricing at the open.

> **No novelty is claimed for the finite-sampling mechanism, nor for its correction from daily
> data.** Both are established. What we claim is narrower: that the empirical signature of that
> mechanism, in a market whose published universe mixes asset classes, is not identified without
> an instrument filter.

---

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

### 5.4 What this means for study design

The classification that separates these two tables is not in the data an exchange distributes. A
study that downloads a frontier exchange's daily files, sorts on turnover or trade count, and
reports that range estimators degrade in the thinnest bucket will produce our §5.1 table. It is
reproducible, statistically strong, and about corporate debentures.

We do not claim this contaminates any particular published paper. We claim it is available to,
and invisible in, the standard workflow, and that the check costs one classification step.

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

**The caution.** The NEPSE index sits at 0.835 while the NIFTY 50 index sits at 0.978, and both
are dense. We report this rather than omitting it: an index is a diversified portfolio and its
range behaves differently from a single security's, so an index-versus-stock comparison is not
like-for-like. **No security-level cross-market comparison exists in this paper.** Any claim that
NEPSE equities and NIFTY constituents behave identically would require constituent-level NIFTY
data with trade counts, which we do not hold (§11).

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

### 8.4 Four distinct failures

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

The inflation factor is **roughly flat in liquidity** — 1.331, 1.300, 1.262, 1.273, 1.295 across
trade-count quintiles. If the effect were a thin-trading phenomenon it should decline with
activity, and it does not.

**Limitation.** For a minority of securities the estimator returns a latent dispersion below the
raw one, which is impossible under the model: their opening returns are bimodal, with mass near
zero and mass at the band, and a single normal cannot represent that. They are excluded and
counted. Excluding them biases the reported median upward, and we note that the median over all
securities including them would be lower.

### 9.4 A rule change we do not exploit

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

## 11. What is not established

- **A causal reading of the closing-rule change.** NEPSE altered the official closing-price
  construction twice inside the panel, giving an A–B–A design. On equity the treated close-side
  indicators move as expected (`C = H`: 6.15% → 1.40% → 9.01%), **but the placebo open-side
  indicator also moves** (`H = O`: 18.96% → 19.46% → 21.91%), and the two A periods do not
  resemble each other. The design does not support causal language and we use none. Placebo
  intervention dates have not been run.
- **The Tobit result is model-based.** We have not verified that the pre-open band constitutes
  censoring in the econometric sense rather than a structural bound, nor checked the
  distributional and dependence assumptions against nonparametric alternatives.
- **Simulation evidence is illustrative, not independent validation.** We have not audited
  whether parameters were calibrated to reproduce the empirical feature the simulations are then
  used to illuminate.
- **No security-level cross-market comparison exists.** Every cross-market statement rests on
  index-versus-index or index-versus-stock contrasts. Constituent-level NIFTY data with trade
  counts would be required.
- **ABC is not implemented** and we make no claim about it.
- **The AddRS derivation is unverified from the primary source** (§8).
- **The published 0.82 comparison is unresolved by data availability**, not by method (§7).
- **The opening share of variance is bracketed, not identified** (§9.1).
- **The April 2026 rule change is confounded** and unexploited (§9.4).
- **Circuit-breaker censoring of the continuous session is unmodelled.**
- **2026-07-25's status as a special session is provisional**, pending an exchange notice.
- **Panel A's 8.05% OHLC violation rate versus panel B's 0.60% is unexplained.**
- **Several references are unverified against primary sources**, including a direct quotation
  attributed to Jacob and Vipul (2008) and the opening-auction literature in §3.

---

## References

*Verification status is tracked in the project's audit record. Entries marked (unverified) have
had metadata confirmed but their equations or quoted claims not read from the primary source.*

Cameron, A. C., Gelbach, J. B., and Miller, D. L. (2008). Bootstrap-based improvements for
inference with clustered errors. *Review of Economics and Statistics* 90(3), 414–427.

Christensen, K., and Podolskij, M. (2007). Realized range-based estimation of integrated
variance. *(unverified)*

Christensen, K., Podolskij, M., and Vetter, M. (2009). Bias-correcting the realized range-based
variance in the presence of market microstructure noise. *(unverified)*

Corsi, F. (2009). A simple approximate long-memory model of realized volatility. *(unverified)*

Garman, M. B., and Klass, M. J. (1980). On the estimation of security price volatilities from
historical data. *Journal of Business* 53(1), 67–78. *(equation unverified)*

Jacob, J., and Vipul (2008). Estimation and forecasting of stock volatility with range-based
estimators. *(unverified — including the quotation in §3)*

Kumar, D., and Maheswaran, S. (2014). A reflection principle for a random walk with implications
for volatility estimation using extreme values of asset prices. *Economic Modelling* 38, 33–44.
DOI 10.1016/j.econmod.2013.11.045. *(derivation unverified; operational equations taken from a
later author reproduction)*

Maheswaran, S., Balasubramanian, G., and Yoonus, C. A. (2011). Post-colonial finance. *Journal of
Emerging Market Finance* 10(2), 175–196. DOI 10.1177/097265271101000202.

Maheswaran, S., and Kumar, D. (2013). An automatic bias correction procedure for volatility
estimation using extreme values of asset prices. *Economic Modelling* 33, 701–712.
DOI 10.1016/j.econmod.2013.05.019.

Martens, M., and van Dijk, D. (2007). Measuring volatility with the realized range.
*(unverified)*

Parkinson, M. (1980). The extreme value method for estimating the variance of the rate of return.
*Journal of Business* 53(1), 61–65. *(equation unverified)*

Patton, A. J. (2011). Volatility forecast comparison using imperfect volatility proxies.
*(unverified)*

Rogers, L. C. G., and Satchell, S. E. (1991). Estimating variance from high, low and closing
prices. *Annals of Applied Probability* 1(4), 504–512. DOI 10.1214/aoap/1177005835.

Rogers, L. C. G., Satchell, S. E., and Yoon, Y. (1994). Estimating the volatility of stock prices:
a comparison of methods that use high and low prices. *(unverified)*

Yang, D., and Zhang, Q. (2000). Drift-independent volatility estimation based on high, low, open
and close prices. *Journal of Business*. *(equation unverified)*
