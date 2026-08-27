# Measuring Volatility Without a Price Path: Range Estimators Under Illiquidity

**Draft v0.1 — 2026-08-27 · not for circulation**

> Toolchain note: drafted in Markdown because no LaTeX/pandoc/Quarto is installed on
> the working machine (charter Q6, deferred). Section structure is written for a
> straightforward conversion.

---

## Abstract *(placeholder — write last)*

Range-based volatility estimators are the standard recommendation for markets without
options. We show that this recommendation rests on an assumption that fails precisely
where it is invoked. Parkinson, Garman–Klass, and Rogers–Satchell estimators assume the
reported daily high and low are the supremum and infimum of a continuously observed
diffusion. In an illiquid market they are the extremes of a small, unevenly spaced
sample of transactions. We decompose the resulting error into three frictions acting in
two directions, and show that the net bias is **non-monotonic in liquidity** — so no
single monotone correction can repair it. Using 178,203 stock-days from the Nepal Stock
Exchange, a market with no derivatives of any kind, we find that at the tenth percentile
of trading intensity (4 trades per day) range estimators recover well under half of true
volatility, while close-to-close variance remains unbiased throughout. We characterize
the crossover point N\* below which the textbook efficiency ranking reverses, and find
that **25% of NEPSE stock-days fall below it**.

---

## 1. Introduction

*(to draft)* Core claims to establish, in order:

1. The toolkit for markets without derivatives is the range-based family, and its appeal
   is an efficiency argument: Parkinson is roughly 5× as efficient as close-to-close,
   Garman–Klass ~7×, Yang–Zhang up to ~14×.
2. Every one of those efficiency factors is derived under continuous observation of the
   price path.
3. That assumption is not a technicality. It is the first thing to fail in the markets
   where the estimators are most needed.
4. We decompose the failure into three separately identified frictions, two downward and
   one upward, and show the net bias is non-monotonic.
5. The practical consequence inverts standard advice: **below N\* trades per day, the
   naive close-to-close estimator dominates every range-based alternative.**

**Contribution altitude.** The result is not about Nepal. It concerns range estimators
under illiquidity, and applies wherever trading is thin — small-cap equities, corporate
bonds, emerging-market FX, private-market marks, and early-stage crypto. NEPSE is used
because it is an extreme case that identifies the effect sharply, and because the absence
of derivatives removes the usual escape route of backing volatility out of option prices.

---

## 2. Institutional setting: NEPSE

*(to draft — several items require the deep dives listed in the charter)*

- No derivatives of any kind. No options, no futures, no ETFs. Volatility cannot be
  extracted from any traded instrument.
- **Sunday–Thursday trading week.** Across 3,759 index sessions from 2010 to 2026,
  Friday appears 24 times (rare special sessions) and Saturday never. The annualization
  factor is not 252; the weekend gap runs Thursday close → Sunday open.
- Daily price limits and index-level circuit breakers. **[Q7 — rules and their revision
  history must be established before this section can be written correctly.]**
- Structural closures: the 2015 Gorkha earthquake (31 days), COVID-19 (~98 days across
  two 2020 gaps), and annual Dashain/Tihar closures of 8–12 days.
- No short selling.

---

## 3. Theory: three frictions, two directions

Let the efficient log price follow a diffusion with daily volatility $\sigma$. An
estimator sees not the path but $N$ transactions at times $0 \le t_1 < \dots < t_N \le 1$,
each observed with error.

### D1 · Undersampling within the traded window

The observed range is the range of an $N$-sample, not of the path. Since the sample
maximum is bounded above by the path supremum and the sample minimum bounded below by
the path infimum, the observed range is **weakly smaller** than the true range, with the
gap decreasing in $N$. Range-based variance is biased **down**.

### D2 · Traded-window truncation *(new, and specific to illiquid markets)*

The reported open is the **first trade**, not the price at the opening bell; the reported
close is the **last trade**. When a security trades rarely, $[t_1, t_N]$ is a strict — and
possibly small — subinterval of the session. Every OHLC-derived quantity therefore
describes a shorter interval than the calendar day against which it is compared.

Simulation gives the magnitude directly. The fraction of daily variance spanned by the
traded window is:

| Trades/day | 2 | 4 | 6 | 10 | 15 | 30 | 73 | 113 | 569 |
|---|---|---|---|---|---|---|---|---|---|
| Variance captured | 0.579 | 0.776 | 0.846 | 0.905 | 0.936 | 0.968 | 0.989 | 0.993 | 0.998 |

At two trades per day the OHLC record describes **58%** of the day's variance before any
undersampling effect is counted. This bias is, to our knowledge, not treated in the
range-estimator literature, which is written for markets where $t_1 \approx 0$ and
$t_N \approx 1$ hold by construction.

### U1 · Microstructure noise in the extremes

Observed prices carry bid–ask bounce and transitory impact. The high and low are **order
statistics**, so they are contaminated far more than the open and close: noise can only
push the maximum up and the minimum down. Range-based variance is biased **up**, and the
distortion grows with the number of draws.

### The consequence

D1 and D2 push down and vanish as $N$ grows. U1 pushes up and grows with the number of
observations, while the per-trade noise itself falls with liquidity. The net bias is
therefore **non-monotonic in $N$** — which rules out any correction that is monotone in a
liquidity proxy, the natural first thing a practitioner would reach for.

---

## 4. Data

| Panel | Source | Coverage | Content |
|---|---|---|---|
| Index | scraped daily index series | 2010-01-03 → 2026-06-12, 3,759 sessions | OHLC + turnover |
| A · long | per-company archive | 1995 → 2026, 372 securities, 506,235 stock-days | OHLC + volume + turnover |
| B · trades | daily cross-sections | 2024-03 → 2026-08, 520 securities | adds **transaction counts** and VWAP |

Panel B supplies the trading-intensity measure the analysis requires. The analysis sample
is **178,203 stock-days across 520 securities and 551 sessions**.

### 4.1 Two data defects that must be handled before anything else

**Stale non-trading sessions.** The daily cross-section archive contains files for
Fridays and Saturdays, on which NEPSE does not trade. On Saturdays, 99.2% of closing
prices are identical to the previous session's, and on Fridays 87.5% — carried-forward
records, not sessions. Retaining them would inflate the zero-return friction measure and
manufacture spurious zero-volatility days. After filtering to Sunday–Thursday, 551
genuine sessions remain, a rate of **222 sessions per year**, consistent with the
independently sourced index series.

**Degenerate index OHLC before 2016-06-06.** Every index observation from 2010-01-03 to
2016-06-03 satisfies $O = H = L = C$ with zero reported turnover. Range-based estimators
are undefined on that stretch, reducing the usable index sample to 2,296 sessions. Whether
this reflects a vendor artifact or exchange practice is unresolved *(charter deep dive)*.

A further 69 index rows inside the usable window violate $H \ge \max(O,C)$ or
$L \le \min(O,C)$. In the stock panel the violation rate is 0.60% (Panel B) and 8.05%
(Panel A).

---

## 5. How thin is NEPSE?

*(Figure 1, Table 1)*

| Statistic | Value |
|---|---|
| Median trades per stock-day | **113** |
| 10th percentile | **4** |
| 1st percentile | **1** |
| Stock-days below 10 trades | 14.8% |
| Stock-days below 30 trades | 25.2% |
| Stock-days below 100 trades | 46.6% |

### Estimator pathologies *(Table 2, Figure 5)*

| Pathology | Share of stock-days |
|---|---|
| Zero observed range ($H = L$) → **Parkinson variance exactly zero** | 6.1% |
| Rogers–Satchell returns zero variance | 15.2% |
| Garman–Klass returns **negative** variance | 0.5% |
| Zero close-to-close return (stale price) | 4.0% |

Concentration by liquidity is stark. In the least-liquid decile (median **2** trades per
day), **Parkinson returns exactly zero on 58.2%** of stock-days. An estimator that reports
zero volatility on the majority of observations is not a noisy estimator; it is an
inapplicable one.

---

## 5b. An internal control: the estimators work where they should

*(Notebook Part 7)*

A natural objection to everything above is that something is wrong with NEPSE, or with our
code, rather than with range estimators under thin trading. The index provides the control.
It aggregates every listed security and is therefore the most densely traded series in this
market — the closest thing NEPSE has to the conditions the estimators assume.

Measured relative sampling efficiency against close-to-close on the index, versus the
textbook values derived under continuous observation:

| Estimator | Measured on NEPSE index | Textbook |
|---|---|---|
| Parkinson | **4.67×** | ≈ 5× |
| Garman–Klass | **6.48×** | ≈ 7× |
| Rogers–Satchell | 5.01× | ≈ 8× |
| Yang–Zhang | **20.4×** | up to 14× |

The machinery reproduces the canonical efficiency gains almost exactly where trading is
dense. The failures documented in §5–§7 are therefore a property of thin trading, not of the
market, the data, or the implementation.

**A caution against reading the levels.** The same table shows mean annualized σ̂ of 20.2%
(close-to-close) against 16.7% (Parkinson), 15.3% (Garman–Klass), and 14.7%
(Rogers–Satchell). Most of that gap is *not* bias: close-to-close includes overnight
variance while Parkinson, Garman–Klass and Rogers–Satchell measure the intraday session
only. The comparison that isolates bias is the matched open-to-close benchmark used in §7,
not this one. The one figure that resists an overnight explanation is GKYZ, which *does*
include an overnight term and still comes in at 16.0% — worth a separate look.

## 5c. Non-synchronous trading, and a sign that flips with aggregation

*(Notebook Part 4)*

The index return series is **positively autocorrelated at short lags** — lag-1 ACF ≈ +0.10,
well outside the 95% band, Ljung–Box p ≈ 4 × 10⁻⁷. In a deep market that would be a tradable
anomaly. Here it is the classic non-synchronous-trading signature: an index built from
thinly traded constituents inherits stale component prices, so part of today's information
arrives in tomorrow's index level.

The sign **flips with aggregation**, and the flip is diagnostic:

| Level | Lag-1 return autocorrelation | Mechanism |
|---|---|---|
| Individual thin securities | **−0.22** | bid-ask bounce |
| Index of those same securities | **+0.10** | stale constituent prices |

Two illiquidity mechanisms dominate at two levels of aggregation and push in opposite
directions. A correction calibrated at one level and applied at the other gets the sign
wrong — a further reason (alongside §7b) why a single scalar liquidity adjustment cannot be
made to work.


---

## 6. Simulation: bias and the crossover N\*

*(Figures 2, 3, 6; Tables 4, 5, 7)*

True $\sigma$ = 2%/day; 4,000 days × 15 replications per grid point.

**Level bias** — estimated $\sigma$ ÷ true $\sigma$:

| Trades/day | Close-to-close | Parkinson | Garman–Klass | Rogers–Satchell |
|---|---|---|---|---|
| 2 | 1.002 | 0.344 | 0.193 | 0.000 |
| 4 | 1.003 | 0.534 | 0.404 | 0.352 |
| 10 | 1.000 | 0.712 | 0.621 | 0.601 |
| 4,000 | 0.995 | 0.976 | 0.968 | 0.969 |

Close-to-close is unbiased at every trading intensity — it uses only closing prices and
so is immune to D1 and U1 alike. The range family degrades severely.

**The crossover.** Comparing RMSE of a rolling 21-day $\hat\sigma$:

| Estimator | N\* | Share of NEPSE stock-days below N\* |
|---|---|---|
| Parkinson | **33** | ~26% |
| Garman–Klass | **49** | ~31% |
| Rogers–Satchell | **73** | ~38% |

Below N\* the textbook efficiency ranking **reverses**: the estimator with no theoretical
efficiency advantage strictly dominates.

---

## 7. Does the predicted bias appear in the data?

*(Figure 4, Table 6)*

Partly. The match is close at both ends of the liquidity range and fails in the middle — and
that failure is informative rather than fatal.

Within-bucket ratio of Parkinson variance to the matched open-to-close benchmark, against
the simulated prediction. **No parameter is fitted to the NEPSE data.**

| Median trades | Observed | Predicted (D1+D2 only) |
|---|---|---|
| 6 | 0.728 | 0.734 |
| 15 | 0.867 | 0.819 |
| 30 | 0.991 | 0.870 |
| 73 | 1.076 | 0.907 |
| 1,168 | 0.968 | 0.974 |

At low liquidity the match is close to exact (0.728 observed vs 0.734 predicted at six
trades per day) and it converges again at high liquidity. In between, the observed ratio
runs **above** the prediction and rises above one — precisely the signature of U1, which
the D1+D2 prediction omits by construction. Adding microstructure noise to the simulation
reproduces the direction and shape of the gap *(Figure 6)*.

The observed pattern is therefore **hump-shaped in liquidity**, as the three-friction
account requires and as a pure undersampling account cannot produce.

> **Open issue.** The least-liquid bucket (median 1 trade/day) is not yet interpretable:
> with a single transaction, $O = H = L = C$, so numerator and denominator degenerate
> together and the ratio is not identified. It is excluded from the fit and requires a
> separate treatment.

---

## 7b. Identifying the upward friction directly

*(Figures 7–8, Tables 8–9)*

Section 7 attributes the mid-liquidity gap to noise in the observed extremes, but infers
it from a residual. Microstructure diagnostics measure it.

**The bounce signature is unambiguous.** Per-security lag-1 return autocorrelation and
five-day variance ratios, by liquidity octile:

| Median trades/day | 2 | 8 | 37 | 85 | 134 | 186 | 265 | 455 |
|---|---|---|---|---|---|---|---|---|
| AC₁ of returns | **−0.195** | **−0.219** | −0.065 | −0.008 | +0.031 | +0.005 | +0.016 | **+0.036** |
| Variance ratio VR(5) | 0.520 | 0.533 | 0.841 | 0.941 | 0.941 | 0.972 | 1.015 | 1.073 |

Monotone from strongly negative to mildly positive. Negative autocorrelation with VR < 1
is the textbook bid-ask bounce signature, and it is concentrated exactly where the
range-estimator gap is largest.

**The bounce explains the gap.** Regressing the per-security gap (observed minus
undersampling prediction) on measured bounce, controlling for trading intensity:

| | (1) liquidity only | (2) + bounce |
|---|---|---|
| Bounce (−AC₁) | — | **0.225** (t = 6.4) |
| log trades/day | −0.005 (t = −2.0) | +0.007 (t = 2.8) |
| R² | 0.013 | **0.139** |
| N securities | 371 | 371 |

Bounce enters at p = 1.4 × 10⁻¹⁰ and raises explained variation roughly tenfold. The sign
on liquidity **flips** once bounce is included — omitted-variable bias, since spread and
trading intensity are strongly correlated. This is why a correction indexed on liquidity
alone cannot work: liquidity proxies for two frictions pulling in opposite directions.

> **Measurement choice, and why.** The primary noise proxy is −AC₁ rather than the Roll
> (1984) spread. Roll is undefined wherever the return autocovariance is non-negative,
> which is *precisely where bounce does not dominate* — it is missing non-randomly, on 41%
> of securities. Conditioning on it selects the subsample in which the hypothesised force
> is already present. On that selected subsample Roll does enter positively but only
> marginally (coefficient 2.09, t = 1.9, p = 0.052, R² = 0.040), and it is reported as a
> cross-check rather than as the test. Corwin–Schultz is deliberately **not** used as
> evidence: it is itself a range-based estimator and inherits the biases under study.

**Volatility clustering.** AC₁ of squared returns runs 0.14 in the thinnest octile against
0.23–0.27 in liquid ones — persistence is present throughout but attenuated where trading
is thin, consistent with stale prices masking the true volatility process. This bears on
whether GARCH-family models are estimable on frontier cross-sections at all.


---

## 7c. Forecast evaluation: the range information is worth having

*(Model notebook, Parts 1–3)*

Sections 5–7 measure *level bias*. This section asks a different and more practical question:
which volatility measure produces the best **forecast**? It matters because it can be answered
without ground truth. Future squared returns are a noisy but unbiased proxy for future
variance, so averaging a proxy-robust loss over many days ranks forecasts consistently — the
Andersen–Bollerslev argument. Loss choice is not free: Patton (2011) shows most intuitive
losses, including MAE and anything applied to σ rather than σ², rank forecasts incorrectly
under a noisy proxy. We use QLIKE and MSE.

Eleven forecasts, evaluated on ~690 out-of-sample days:

| Model | QLIKE | MZ slope *b* | *t*(b=1) | In 90% MCS |
|---|---|---|---|---|
| HAR–GKYZ | **−7.878** | **1.017** | 0.08 | ✓ |
| HAR–Garman–Klass | −7.873 | 0.920 | −0.40 | ✓ |
| HAR–Parkinson | −7.838 | 0.930 | −0.35 | ✓ |
| GARCH(1,1)-t | −7.836 | 0.511 | **−3.98** | ✓ |
| GJR-GARCH-t | −7.835 | 0.555 | **−3.31** | ✓ |
| EWMA (λ=0.94) | −7.707 | 0.554 | −2.80 | ✗ |
| Constant | −7.737 | — | — | ✗ (p=0.057) |
| HAR–Close-to-close | −7.330 | 0.196 | −17.2 | ✗ |

Two findings.

**Range-based HAR forecasts are the only ones that pass Mincer–Zarnowitz.** Their slopes are
statistically indistinguishable from one; every GARCH-family forecast is significantly biased,
under-responding to variation in true volatility (b ≈ 0.51–0.55).

**HAR on close-to-close is eliminated while HAR on range measures survives.** The range
information genuinely improves forecasts even though those same measures are biased in levels.

This substantially revises the practical recommendation of §8. The earlier reading — "below
N\*, abandon the range estimator for close-to-close" — is right about *levels* and wrong about
*forecasts*. The range measures are **biased but informative**; close-to-close is **unbiased but
mostly noise**. The correct response is to bias-correct the range estimator, not to discard it.
That is what "adapting the method" means, and §7d does it.

## 7d. Bias identified without ground truth, and corrected

*(Model notebook, Parts 4–6)*

Treating log-variance as a latent AR(1) observed through biased noisy measurements makes the
measurement intercepts estimates of estimator bias — recovered from data, with no ground truth.

This requires a correction that is easy to miss. E[log X] ≠ log E[X], and the Jensen gap
differs sharply between estimators: −1.27 for a squared return against ≈ −0.22 for the log
range. Fitting to raw log variances recovers *the difference in Jensen constants*, not bias —
in our first attempt this produced a spurious 1.74× "bias" for Parkinson. The constants are
properties of each estimator's sampling distribution, so they are calibrated once by simulation.

**Two independent routes to the bias curve now broadly agree.** Simulation (known truth, models
D1+D2 only) and the latent-state model (no truth, filters the data) correlate at 0.72 across
liquidity buckets. Where they diverge is itself informative: in mid-liquidity buckets the
data-derived estimate runs *above* the simulation (≈1.09 vs ≈0.92), which is exactly the U1
microstructure-noise signature that the D1+D2 simulation omits by construction — the same gap
§7 found by a completely different method.

**The correction works out of sample.** Fitted on training data only, conditioning on trading
intensity *and* bounce, and applied to a held-out period: median bias falls from 0.940 to
**0.994**, and RMSE against unbiasedness falls **17.8%**.


---

## 8. Implications

1. **For frontier-market research.** The default recommendation — use range estimators when
   there are no options — is wrong *for levels* below N\*, but the range information is still
   worth having *for forecasting* (§7c). Bias-correct the range estimator rather than discard
   it, and report trade counts alongside any range-based estimate or it cannot be assessed.
2. **No monotone correction exists.** Because the frictions act in opposite directions,
   a single liquidity-indexed adjustment cannot repair the bias.
3. **Liquidity alone is the wrong conditioning variable.** It proxies for both the downward
   frictions and the upward one. A correction must condition on trading intensity **and** a
   noise measure separately (§7b).
4. **Beyond frontier markets.** Any thinly traded asset is exposed: small caps, corporate
   bonds, emerging FX, private-market marks.
5. **D2 is general.** Traded-window truncation applies to every OHLC-derived measure in
   every market, and is invisible where trading is continuous.

---

## 9. What this draft does not yet establish

Stated plainly; each is tracked in the charter.

- **No external validation yet.** The S&P 500 and Nifty 50 rungs are not built. Until the
  extrapolation is tested one rung out, the NEPSE numbers rest on simulation plus one
  market.
- **Circuit breakers are not yet modelled** (charter Q7). Price-limit censoring is a
  fourth friction and is currently absent from the decomposition.
- **No pre-analysis plan is frozen.** Every result above is **exploratory** and may not be
  reported as a confirmatory test.
- The 1-trade bucket is unresolved (§7).
- Panel A's 8.05% OHLC violation rate is far above Panel B's 0.60% and is unexplained.
- GKYZ includes an overnight term yet still sits ~20% below close-to-close on the index (§5b);
  not yet diagnosed.
- Rogers–Satchell's measured index efficiency (5.0×) falls well short of its textbook value
  (≈ 8×) even on the densest series available. Unexplained.

---

## References *(to verify against sources before citing — none checked yet)*

Parkinson (1980) · Garman & Klass (1980) · Beckers (1983) · Rogers & Satchell (1991) ·
Yang & Zhang (2000) · Alizadeh, Brandt & Diebold (2002) · Lesmond, Ogden & Trzcinka (1999) ·
Chou (2005) · Wei (2002) on price-limit censoring · Andersen & Bollerslev on realized measures
