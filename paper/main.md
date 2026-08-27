# When Continuous Price Discovery Breaks Down: Volatility Measurement in an Ultra-Thin Frontier Market

**Draft v0.3 · 2026-08-27 · not for circulation**

---

## Abstract

Range-based volatility estimators are the standard recommendation for markets without options,
and existing work has established both that infrequent trading biases them downward and that the
bias can be corrected from daily OHLC alone. We ask where those results stop holding. Using
178,203 stock-days from the Nepal Stock Exchange — a market with no derivatives of any kind,
whose median security trades 113 times a day and whose tenth percentile trades four — we document
three things. First, range estimators do not merely lose precision in this regime: in the least
liquid decile the Parkinson estimator returns *exactly zero* on 58% of stock-days. Second, the
failure tracks trading intensity rather than the market: NEPSE's most liquid securities and the
NIFTY 50 index give statistically indistinguishable estimator ratios using identical code. Third,
and most consequentially, the reported downward bias of the Rogers–Satchell estimator is largely
a **benchmark-scope artifact** — measured against a matched intraday benchmark it is 0.965 on the
NIFTY 50, essentially unbiased. What actually breaks in an ultra-thin market is different and
more fundamental: price discovery migrates out of the continuous session and into the opening
call auction, which NEPSE bands at ±2% of the previous close. Between 56% and 83% of daily
variance in the thinnest securities is realized at the open, and the band censors that opening
return on roughly a fifth of all stock-days. Estimators built on the intraday session cannot see
this component; estimators that can see it observe it through a truncated window.

> **Status.** No result below is a confirmatory test unless explicitly labelled. A pre-analysis
> plan was frozen on 2026-08-27 (`ee17b63a…`); one hypothesis has been validated on held-out data
> and one has failed. Section 10 states what is not established.

---

## 1. Introduction

*(to draft — the claims to establish, in order)*

1. The toolkit for markets without derivatives is the range-based family, whose appeal is an
   efficiency argument: Parkinson (1980) is roughly 5× as efficient as close-to-close.
2. Those efficiency results are derived under continuous observation of the price path.
3. That assumption is known to fail under infrequent trading, and the resulting bias is known to
   be correctable — but the corrections were developed and tested in markets far more liquid than
   the ones for which they are recommended.
4. We identify the regime in which they stop working, and show the binding constraint is not
   estimator bias but **where price discovery happens**.

**Contribution.** Not the discovery of finite-sampling bias, which is long established. The
boundary: how thin a market must become before the standard toolkit fails, what fails first, and
why the natural remedy — estimators carrying an overnight term — is itself compromised by the
institutional design of the opening auction.

---

## 2. Institutional setting

NEPSE is unusual on four dimensions that jointly matter, and the fourth is the paper's subject.

**No derivatives of any kind.** No options, no futures, no ETFs. Volatility cannot be extracted
from any traded instrument, which is what makes the market a clean test of estimators intended
for exactly this situation.

**A Sunday–Thursday trading week.** Across 3,759 index sessions, Friday appears 24 times (rare
special sessions) and Saturday never. The annualization factor is **222 sessions**, not 252, and
the weekend gap runs Thursday close → Sunday open. Volatility, range, and trading all peak on
Sunday, consistent with a two-day accumulation.

**Structural closures.** The 2015 Gorkha earthquake (31 days), COVID-19 (~98 days across two 2020
gaps), and annual Dashain/Tihar closures of 8–12 days.

**A banded pre-open call auction.** Trading opens with a pre-open session (10:30–10:45) in which
orders may be placed only within **±2% of the previous close**. The engine clears at the
volume-maximising price, and **if no orders match, the opening price is set equal to the previous
close.** Section 8 shows both rules are visible in the data and that they govern what any
volatility estimator can observe. *(The band was widened to ±5% in April 2026; see §8.3.)*

---

## 3. Related literature, and what is not claimed here

Three strands bound this paper, and none is disputed.

**Finite-sampling bias is established.** Martens and van Dijk (2007) state that infrequent trading
biases the realized range downward because observed extremes under- and overstate the true ones,
and propose a scaling correction. Christensen and Podolskij (2007) derive the asymptotics
independently; Christensen, Podolskij and Vetter (2009) bias-correct the realized range under
microstructure noise. Rogers, Satchell and Yoon (1994) had earlier used a proxy for the number of
transactions to correct the discretisation bias directly.

**And it is correctable from daily data.** Maheswaran and Kumar (2013) propose an automatic bias
correction (ABC) for the Rogers–Satchell estimator that requires **no** knowledge of the number of
steps and **no** volume-based proxy for it; Kumar and Maheswaran (2014) extend this to the AddRS
estimator, proved unbiased under a reflection principle, using daily OHLC alone.

**Range estimators survive moderate illiquidity.** Jacob and Vipul (2008), benchmarking against
two-scale realized volatility, find daily range estimators *"not downwardly biased in the presence
of negative autocorrelation and low liquidity, as generally suspected"*, identifying **drift** as
the main source of Parkinson's problems.

> **No novelty is claimed for the finite-sampling mechanism, nor for its correction from daily
> data.** Both are established. This paper asks where these results cease to apply, and identifies
> a distinct failure — the location of price discovery — that no existing correction addresses.

---

## 4. Data

| Dataset | Span | Units |
|---|---|---|
| NEPSE index, daily OHLC + turnover | 2010-01-03 → 2026-06-12 | 3,759 sessions |
| NEPSE stock panel B (with trade counts) | 2024-03-04 → 2026-08-26 | 551 sessions × 520 securities |
| NEPSE stock panel A (long, no trade counts) | 1995 → 2026 | 372 securities, 506,235 stock-days |
| NIFTY 50 daily OHLCV | 2010-01-04 → 2026-06-12 | 4,037 sessions |
| India VIX | 2010-01-04 → 2026-06-12 | 4,036 sessions |

### 4.1 Three data defects, each material

**Genuine intraday range begins 2016-06-06.** Every earlier index observation satisfies
`O = H = L = C` with zero reported turnover, so range estimators are undefined — not imprecise —
on that stretch. The usable index sample is **2,296 sessions**.

**Stale non-trading sessions.** The daily cross-section archive contains files for Fridays and
Saturdays, on which the exchange does not trade. On Saturdays **99.2%** of closing prices are
identical to the previous session and on Fridays **87.5%**: these are carried-forward records, not
sessions. Retaining them roughly doubles the measured zero-return friction and inserts non-events
into every rolling window. After filtering to Sunday–Thursday, 551 genuine sessions remain — a
rate of 222 per year, matching the independently sourced index.

**Turnover is missing before 2011 and coded as zero.** Across all 3,702 zero-turnover rows in
panel A, **99.9% have positive volume** and 56% have `H ≠ L`: those securities traded and their
prices moved. Any turnover-conditioned rule misclassifies them. The affected window is small
(3,700 rows, 11 securities) but the coding must be corrected.

---

## 5. How thin is NEPSE, and what breaks

![Figure 1](FIG1)

**Trading intensity.** Median **113** trades per stock-day; tenth percentile **4**; first
percentile **1**. Below 10 trades: 14.8% of stock-days. Below 30: 25.2%. Below 100: 46.6%.

![Figure 5](FIG5)

**The estimators do not degrade gracefully — they become undefined.**

| Pathology | Share of stock-days |
|---|---|
| Zero observed range (`H = L`) → **Parkinson variance exactly zero** | 6.1% |
| Rogers–Satchell returns zero or negative variance | 15.2% |
| Garman–Klass returns **negative** variance | 0.5% |
| Zero close-to-close return (stale price) | 4.0% |

Concentration is stark. In the least liquid decile — median **2** trades per day — **Parkinson
returns exactly zero on 58.2% of stock-days.** An estimator reporting zero volatility on the
majority of its observations is not noisy; it is inapplicable.

---

## 6. Cross-market control: the failure tracks trading intensity, not the market

The most damaging objection is that something is wrong with NEPSE, its data, or our code rather
than with range estimators under thin trading. Running identical code across three regimes answers
it with real data.

![Figure 12](FIG12)

| Regime | Trades/day | Parkinson ÷ open-to-close | Zero-range days |
|---|---|---|---|
| **NIFTY 50 index** | dense | **0.978** | 0.00% |
| NEPSE stocks | ~679 | **0.977** | 0.00% |
| NEPSE stocks | ~153 | 1.050 | 0.01% |
| NEPSE stocks | ~30 | 0.897 | 0.11% |
| NEPSE stocks | ~3 | **0.796** | **36.21%** |

NEPSE's most liquid securities and the NIFTY 50 are **statistically indistinguishable**. The point
agreement should not be over-read: a block bootstrap puts NIFTY's own 95% interval at
**[0.947, 1.021]**, so agreement to three decimals is far finer than the sampling uncertainty
supports and is coincidence. Indistinguishability is the defensible claim, and it suffices —
identical code gives the same answer wherever trading is dense, so departures elsewhere are a
property of trading intensity.

---

## 7. Diagnosing the reported bias: benchmark scope

Maheswaran and Kumar (2013) report a variance ratio of **0.82** for the Rogers–Satchell estimator
against the "usual" close-to-close estimator on the Nifty index, attributing the shortfall to the
random-walk effect. Attempting to replicate this exposes a decomposition.

Rogers–Satchell is built from `ln(H/O)`, `ln(L/O)` and `ln(C/O)`. It is an **open-to-close**
estimator and cannot observe the overnight gap. The "usual" estimator spans the full calendar day.
Their ratio factors exactly:

$$\text{RS} / \text{CC} \;=\; \underbrace{(\text{RS}/\text{OC})}_{\text{genuine bias}} \times \underbrace{(\text{OC}/\text{CC})}_{\text{share the estimator can see}}$$

![Figure 14](FIG14)

| Market | RS ÷ CC | RS ÷ OC | OC ÷ CC | Overnight share |
|---|---|---|---|---|
| **NIFTY 50 index** | 0.671 | **0.965** | 0.695 | **34.3%** |
| NEPSE index | 0.534 | 0.542 | 0.985 | 4.5% |
| NEPSE stocks — dense | 1.084 | 0.968 | 1.120 | 28.0% |
| **NEPSE stocks — thin** | **0.222** | 0.643 | **0.346** | **82.3%** |

**On the NIFTY 50, Rogers–Satchell measured against a matched intraday benchmark is 0.965 —
essentially unbiased.** The reported shortfall is overwhelmingly the third of daily variance that
occurs overnight, which the estimator cannot observe by construction. *(Our level is 0.671 against
their 0.82 on a different window, 2010–2026 versus 1996–2011; the levels are not comparable but
the decomposition is exact regardless.)*

This is not a criticism of ABC or AddRS. **They solve a different measurement problem**: they
correct the measurement of within-session volatility, and do not claim to convert a within-session
estimator into a full close-to-close estimator when opening repricing is economically large.

---

## 8. Where price discovery actually happens

### 8.1 The mechanical channel must be excluded first

A security that trades **once** has `O = H = L = C`, so its intraday return is zero *by
construction* and the entire daily move is forced into the opening return. That is not price
discovery migrating; it is intraday variance being unobservable. It applies to 22.3% of thin
stock-days.

Removing degenerate days is itself not clean — it conditions on intraday movement having
occurred, which deflates the opening share. The two treatments **bracket** rather than identify:

> For the thinnest NEPSE securities the opening share of daily variance lies between roughly
> **56% and 83%**, against **21%** for the most liquid. The contrast is large and robust; the
> point estimate is **not identified** by either treatment.

### 8.2 The opening auction, and its band

![Figure 15](FIG15)

Both auction rules leave clear fingerprints:

| Fingerprint | Value |
|---|---|
| Non-zero opening returns within \|r_co\| ≤ 2.0% | **91.3%** |
| Pile-up in (1.9%, 2.1%] — pinned at the band | **23.2%** |
| p90 / p95 of \|r_co\| | 2.00% / 2.02% |
| Open exactly equal to previous close (no-match rule) | 10.8% (17.3% in the thinnest decile) |

The opening return is therefore not overnight news. It is a composite of overnight information,
opening-auction price discovery, correction of a stale previous close, and auction microstructure.
For a security that traded twice yesterday, the previous close is itself a poor reading of latent
value; the auction aggregates accumulated interest and corrects it.

> **In ultra-thin securities, price discovery is disproportionately concentrated at the opening
> auction rather than distributed through continuous trading.** This is a market-microstructure
> result, not merely a volatility-estimator result.

**And the band censors it.** The ±2% limit binds on roughly **19–28% of stock-days at every
liquidity level** — most often, in fact, for the most liquid decile (28.5%). Latent overnight moves
larger than the band cannot be incorporated at the open.

The consequence cuts against the natural remedy. Parkinson, Garman–Klass and Rogers–Satchell
cannot see the opening move at all. Yang–Zhang and GKYZ *can* — but what they see is **censored
downward on about a fifth of all stock-days**. Recommending estimator families with overnight
terms is therefore too simple: they observe the right component through a truncated window.

### 8.3 A rule change, and a natural experiment

Monthly fingerprints locate a sharp regime change. Through 2026-03 the 95th percentile of the
opening return is pinned at 2.01% every month; from **April 2026** it jumps to ~4.9%, the boundary
pile-up collapses from ~30% to ~3%, and the share of opens exceeding the old band rises from ~0%
to ~28%. This is consistent with the pre-open band being widened from ±2% to ±5%.

This is a sharp, exogenous, precisely-dated change in censoring width with a natural
treatment-intensity measure. **It is not exploited here:** the window has been inspected, so any
test run now would be exploratory, and the governing circular has not been read — if trading hours
or continuous-session limits changed simultaneously, the treatment is confounded.

---

## 9. Validation on held-out data

Panel A restricted to **1995 → 2024-03-03** was not used for hypothesis testing, model selection,
or visualization. Prior exposure is disclosed: its dimensions, aggregate OHLC violation rate
(8.05%) and zero-range rate (4.12%) had been computed, and the violation rate informed the choice
of cleaning rule. This is therefore **pre-specified validation on minimally inspected historical
data**, not a sealed confirmatory hold-out.

![Figure 13](FIG13)

Executed once, under the frozen plan, on **325,901 stock-days across 309 securities**:

| Hypothesis | Primary statistic | Result |
|---|---|---|
| **H1** — the ratio increases with trading intensity in the thin region | β₁ on ln N̂, buckets N̂ < 30 | **+0.0802**, wild cluster bootstrap **p = 0.0001** — SUPPORTED |
| **H2** — the net bias is non-monotonic in intensity | β₂ on (ln N̂)² | **FAILED** |

**H1 is robust.** Under a pre-specified robustness check bucketing on raw turnover — no
calibration, no generated regressor, no functional form — the profile is monotone across all ten
deciles (0.740 → 0.966, Spearman +0.514, p = 8×10⁻¹¹) and the coefficient strengthens (t = 9.19).
Inference was audited: with only 14 year-clusters the asymptotic cluster p-value (8×10⁻²²) is
optimistic; the bootstrap figure is the one reported.

**H2 failed and the verdict is permanent.** The pre-registered quadratic cannot distinguish an
interior maximum from simple concavity: its implied turning point is N̂ ≈ 1129, outside the
observed range and 7× the descriptive peak, and under turnover ranking the profile has no peak at
all. The hypothesis is neither confirmed nor rejected — the *test* was uninformative about the
claim it was meant to adjudicate. No re-specification was attempted.

---

## 10. What is not established

Stated plainly.

- **No benchmarking against ABC or AddRS.** Their formulae were not obtainable. No comparative
  claim about any correction proposed here is admissible until this is done. **This is the
  single most important outstanding item.**
- **The opening share of variance is bracketed, not identified** (§8.1).
- **The `C → O_auction → P_first-continuous → C` decomposition** that would separate auction price
  discovery from overnight information requires transaction data not held.
- **A no-match open cannot be cleanly distinguished** from an auction clearing at the previous
  close without pre-open session identifiers; `O = C₋₁` is a noisy indicator.
- **The April 2026 rule change is unverified against the governing circular** and unexploited.
- **Circuit-breaker censoring of the continuous session is unmodelled.**
- **H2 is unresolved**, deferred to a hold-out with genuine trade counts.
- Panel A's 8.05% OHLC violation rate versus panel B's 0.60% is unexplained.

---

## References

*(to verify against sources before submission)*

Beckers (1983) · Christensen & Podolskij (2007) · Christensen, Podolskij & Vetter (2009) ·
Corsi (2009) · Garman & Klass (1980) · Jacob & Vipul (2008) · Kumar & Maheswaran (2014) ·
Maheswaran & Kumar (2013) · Martens & van Dijk (2007) · Parkinson (1980) · Patton (2011) ·
Rogers & Satchell (1991) · Rogers, Satchell & Yoon (1994) · Yang & Zhang (2000)
