# When Continuous Price Discovery Breaks Down: Volatility Measurement in an Ultra-Thin Equity Market

**Draft v0.4 · 2026-08-27 · not for circulation**

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
more fundamental: daily price variation becomes disproportionately concentrated in the **opening
print**, produced by a call auction that NEPSE bands at ±2% of the previous close. Price discovery
at the auction is the likely economic mechanism, but with only daily OHLC we observe *where the
daily price change appears*, not when information is impounded. Between 56% and 83% of daily
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

**No listed equity derivatives.** No equity options, futures, or ETFs, so equity volatility cannot
be inferred from any traded instrument. *(Nepal has some commodity-derivative activity and has
announced plans for securities derivatives; the claim here is confined to listed equity
derivatives, which is all the argument requires.)*

**A trading week that changed inside the sample.** NEPSE traded **Sunday–Thursday** historically
and moved to **Monday–Friday** in April 2026. A fixed weekday rule is therefore wrong for any
sample spanning the change: it deletes genuine Friday sessions and retains stale Sundays.
Measured as the fraction of a date's cross-section identical to the prior dated file (near 1.0
means a carried-forward record, not a session):

| | Sunday | Monday–Thursday | Friday | Saturday |
|---|---|---|---|---|
| **pre-2026-04** | 0.155 | 0.12–0.20 | **1.000** | 1.000 |
| **post-2026-04** | **0.924** | 0.04–0.10 | **0.199** | 0.933 |

Sessions are therefore detected from this staleness signature rather than assumed from weekdays,
which also removes public holidays the weekday rule silently retained. The detector finds **569
genuine sessions** where the fixed rule kept 640, a rate of **230 per year** — not 252.

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

**Opening call auctions are themselves a studied object.** Work on the London Stock Exchange finds
that opening-call failures concentrate among low-volume stocks and that thinner stocks may reach
price efficiency only once continuous trading begins; studies of other opening calls, including
India's NSE, find their effectiveness depends heavily on institutional design and liquidity. Our
contribution is therefore **not** that thin securities concentrate repricing at the open, which is
consistent with that literature, but narrower: *in an ultra-thin, banded call-auction market, the
location and censoring of opening repricing creates a measurement problem for daily OHLC
volatility estimators that finite-sampling corrections do not address.*

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

| Property | Share of stock-days |
|---|---|
| Zero observed range (`H = L`) → **Parkinson variance exactly zero** | 6.1% |
| Rogers–Satchell exactly zero | 15.2% |
| &nbsp;&nbsp;…of which `H = L` | 40.4% |
| &nbsp;&nbsp;…remainder are **monotone days**, a known property of RS | 59.6% |
| Zero close-to-close return (stale price) | 4.1% |

Concentration is stark. In the least liquid decile — median **2** trades per day — **Parkinson
returns exactly zero on 58.2% of stock-days.** The precise claim matters: Parkinson with `H = L`
is *defined* and equals zero. It is not undefined; it is **uninformative**, which is the stronger
economic statement. An estimator reporting zero volatility on the majority of its observations is
inapplicable as a volatility proxy.

> **A correction to an earlier draft.** Negative Rogers–Satchell and Garman–Klass values were
> previously reported as estimator pathologies. That was wrong. For a valid OHLC bar both are
> **non-negative by construction**: `RS = ln(H/O)·ln(H/C) + ln(L/O)·ln(L/C)` has two non-negative
> products when `H ≥ max(O,C)` and `L ≤ min(O,C)`; and `|ln(C/O)| ≤ ln(H/L)` forces
> `GK ≥ (½ − (2ln2−1))·ln(C/O)² ≥ 0`. Cross-tabulated, **100% of negative RS and 100% of negative
> GK observations sit on OHLC-inconsistent records, and none occur among valid ones.** They are a
> data defect (0.63% of rows), not a property of the estimators. The zeros are a separate and
> genuine phenomenon — but only 40% arise from `H = L`; the rest are monotone days, a documented
> property of RS rather than evidence of thin-trading degeneracy.

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

| Market | RS ÷ CC | RS ÷ OC | OC ÷ CC | Var(open)/Var(cc) | Var(intraday)/Var(cc) | 2Cov/Var(cc) |
|---|---|---|---|---|---|---|
| **NIFTY 50 index** | 0.671 | **0.965** | 0.695 | 0.343 | 0.695 | −0.038 |
| NEPSE index | 0.534 | 0.542 | 0.985 | 0.045 | 0.985 | −0.030 |
| NEPSE stocks — dense | 1.112 | 0.965 | 1.152 | 0.279 | 1.152 | **−0.322** |
| **NEPSE stocks — thin** | **0.226** | 0.631 | **0.359** | 0.817 | 0.359 | −0.147 |

**`OC ÷ CC` is a ratio, not a variance share.** Since `r_cc = r_co + r_oc`,
`Var(cc) = Var(co) + Var(oc) + 2Cov(co, oc)`, so the ratio can exceed one — as it does for dense
NEPSE securities (1.152), offset by a strongly negative covariance (−0.322). The three components
are therefore reported separately and sum to one. Earlier drafts described `OC ÷ CC` as "the share
the estimator can see"; that was incorrect wherever the covariance is non-trivial.

**On our 2010–2026 NIFTY sample, most of the gap between Rogers–Satchell and close-to-close
variance disappears when RS is compared with a matched open-to-close benchmark** — 0.671 against
0.965.

We stop short of the stronger claim. Their 0.82 is estimated on **1996–2011**, ours on
**2010–2026**, and we have not decomposed their sample. Saying their result is "largely a
benchmark-scope artifact" would require replicating their window, which is the obvious next test:
if `RS/CC ≈ 0.82` and `RS/OC ≈ 1` on 1996–2011, the point becomes sharp. Until then the claim is
confined to our own sample.

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
> auction rather than distributed through continuous trading.**
>
> Stated carefully: this determines *how much of the day's variance an intraday estimator can
> observe* — a scope fact. It is **not** established that concentration at the open degrades
> intraday measurement itself. Tested directly, auction concentration adds statistically
> significant explanatory power for estimator bias beyond trading intensity (p = 2×10⁻⁴) but the
> effect is economically negligible: the median ratio moves only 1.011 → 1.062 across the full
> range of the variable. What does predict estimator failure is the auction **failing to clear**
> (no-match rate, t = −6.5) and the degenerate-observation rate (t = −10.9).
>
> One number from that exercise is worth carrying: **trading intensity alone explains 7.7% of the
> cross-sectional variation in estimator bias.** Every correction in the literature conditions on
> a liquidity proxy.

**And the band censors it.** The ±2% limit binds on roughly **19–28% of stock-days at every
liquidity level** — most often, in fact, for the most liquid decile (28.5%). Latent overnight moves
larger than the band cannot be incorporated at the open.

The consequence cuts against the natural remedy. Parkinson, Garman–Klass and Rogers–Satchell
cannot see the opening move at all. Yang–Zhang and GKYZ *can* — but what they see is **censored
downward on about a fifth of all stock-days**. Recommending estimator families with overnight
terms is therefore too simple: they observe the right component through a truncated window.

---

## 8.4 Recovering what the band hides

The band censors the opening return **at a point that is known exactly**, which makes a
model-based recovery of latent opening dispersion available.

> **The maintained assumption, stated because it is doing work.** We assume the observed opening
> price is a censored realization of a latent *unconstrained* opening return. That is an
> approximation, not assumption-free identification: an order-price band changes which orders
> investors may submit and plausibly which they choose to submit, so a boundary open does not
> prove that an otherwise identical unconstrained auction would have cleared beyond it. What
> follows is a structural estimate under that assumption, with sensitivity checks. When the latent clearing price lies
outside the band the auction clears at the boundary; the observed opening return is then
right- or left-censored at ±2% (±5% after April 2026). This is a two-sided Tobit, and the latent
standard deviation is recovered by maximum likelihood from the interior observations plus the
censored mass.

Validated against known answers before use: at censoring rates of 4.5%, 32%, 57% and 74% the
estimator recovers the true standard deviation to within 1.3%, while the naive sample standard
deviation understates by up to 70%. It is also verified to be harmless where censoring is light.

![Figure 17](FIG17)

On 312 securities in the ±2% regime:

| | |
|---|---|
| Median share of opens pinned at the band | **27.2%** |
| Median latent ÷ observed opening volatility | **1.282** |
| Securities understated by more than 25% | **57.1%** |
| Estimated understatement of the **opening-return variance component** | median **19.9%** of Var(cc), p90 42.2% |

The inflation factor is **roughly flat in liquidity** — 1.17, 1.32, 1.31, 1.27, 1.29 across
trade-count quintiles spanning 3 to 420 trades per day.

> **This is a market-wide institutional measurement problem, not a thin-trading one.** About a
> fifth of daily variance is hidden by the band across the entire cross-section. It is orthogonal
> to the illiquidity mechanism, it has a known censoring point, and it is identified — which no
> existing correction can claim, because none addresses the opening return.

**Limitation.** For 42 of 354 securities the estimator returns a standard deviation below the raw
one, which is impossible under the model: their opening returns are bimodal, with mass near zero
and mass at the band, and a single normal cannot represent that. They are excluded and counted. A
mixture or fat-tailed innovation would likely fit them, but choosing that distribution after
seeing which securities failed the first would be the flexibility the analysis plan exists to
prevent; it belongs in a pre-specified amendment.


### 8.3 A rule change, and a natural experiment

Monthly fingerprints locate a sharp regime change. Through 2026-03 the 95th percentile of the
opening return is pinned at 2.01% every month; from **April 2026** it jumps to ~4.9%, the boundary
pile-up collapses from ~30% to ~3%, and the share of opens exceeding the old band rises from ~0%
to ~28%. **Effective 20 April 2026, NEPSE widened the permissible pre-open price movement from ±2% to
±5%**, in a reform that simultaneously raised the continuous-session order band and the daily
individual-stock price limit. The inferred break and the documented reform coincide.

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

- **No benchmarking against ABC or AddRS.** A published exposition gives the AddRS construction
  from daily OHLC — `b = ln(H/O)`, `c = ln(L/O)`, `x = ln(C/O)`, `u = 2b − x`, `v = 2c − x` — but
  the additive correction terms themselves are still behind a paywall, so it is not yet
  implementable end to end. **This remains the single most important outstanding item**, and until
  it is run the paper must not claim that existing corrections "cease to apply"; it identifies a
  failure dimension that finite-sampling corrections do not target.
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

Beckers (1983) · Cao, Ghysels & Hatheway on opening call auctions · Christensen & Podolskij (2007) · Christensen, Podolskij & Vetter (2009) ·
Corsi (2009) · Garman & Klass (1980) · Jacob & Vipul (2008) · Kumar & Maheswaran (2014) ·
Maheswaran & Kumar (2013) · Martens & van Dijk (2007) · Parkinson (1980) · Patton (2011) ·
Rogers & Satchell (1991) · Rogers, Satchell & Yoon (1994) · Yang & Zhang (2000)
