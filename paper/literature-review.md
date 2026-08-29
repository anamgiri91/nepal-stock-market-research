# Literature review

**Companion to `main.md`. Draft 2026-08-29.**

This document exists because §3 of the paper cannot carry the whole review, and because the
project's earlier literature note contained a citation that was wrong in two fields while marked
"Verified." Everything below therefore carries an explicit verification status, and the standard
is stated once here rather than implied.

**Verification levels used throughout.**

| level | meaning |
|---|---|
| **RECORD VERIFIED** | authors, title, journal, volume, issue, year and pages confirmed against a publisher or RePEc listing |
| **CLAIM VERIFIED** | the record is verified *and* the specific sentence attributed to the source was checked against the source's own abstract or publisher summary |
| **EQUATION UNVERIFIED** | the record is verified but the mathematics was not read from the primary text |
| **UNVERIFIED** | neither confirmed |

Nothing in this project may be cited at CLAIM level on the strength of a secondary summary of a
paywalled paper. Where an equation is implemented in code, its status is tracked separately in
`private/audit/EQUATION-CODE-MAP.md`.

---

## A. The range-based family and what it assumes

The estimators this paper uses all replace the squared return with a function of the daily bar.

**Parkinson (1980)**, *Journal of Business* 53(1), 61–65 — RECORD VERIFIED, EQUATION UNVERIFIED.
The high–low range estimator, `σ² = ln(H/L)²/(4 ln 2)`. Its efficiency advantage over
close-to-close is derived under **zero drift and continuous observation** of the price path.

**Garman and Klass (1980)**, *Journal of Business* 53(1), 67–78 — RECORD VERIFIED, EQUATION
UNVERIFIED. Adds the open and close. Two distinct forms circulate: a full expression with
coefficients 0.511 / 0.019 / 0.383, and a simplified `0.5 ln(H/L)² − (2 ln 2 − 1) ln(C/O)²`.
**We implement the simplified form**, and which of the two the original paper designates as its
recommended estimator has not been established from the primary text. This matters enough to be
flagged rather than glossed.

**Meilijson (2008)**, "The Garman–Klass volatility estimator revisited", arXiv:0807.3492 —
CLAIM VERIFIED (abstract read in full). Useful to us on three counts. It confirms the Garman–Klass
efficiency figure of **7.4** relative to `(CLOSE−OPEN)²`, and states that GK "is widely believed to
be of minimal variance". It then **disproves that belief**, exhibiting an unbiased estimator with
efficiency 7.7322 against a Cramér–Rao bound of 8.471 that cannot be attained. And it reports that
regression-fitted estimators on its compressed statistic "markedly out-perform" the Garman–Klass
family **when increments are heavy-tailed** — which is precisely the regime AddRS assumes, since
its maintained model is a symmetric double-exponential random walk. Notably it does **not** mention
the 0.511 / 0.019 / 0.383 coefficients, so that form's provenance remains unestablished.

**Rogers and Satchell (1991)**, *Annals of Applied Probability* 1(4), 504–512,
DOI 10.1214/aoap/1177005835 — CLAIM VERIFIED (abstract read in full). Drift-independence is the
paper's stated contribution: the estimator is unbiased "whatever the drift c", under log price
following a **Brownian motion with drift, observed continuously**. Two things in that abstract
matter for us and are easy to miss:

1. Unbiasedness is *with respect to drift*, under a maintained continuous-observation model. It
   is not unbiasedness in general, and the paper should never say "RS is unbiased" unqualified.
2. **The authors identify the discrete-extrema problem themselves** — approximating the true
   extrema of the drifting Brownian motion by those of a random walk "introduces error, often
   quite a serious error" — **and state that a simple correction can largely overcome it.**
   Attributing the discretisation correction to a later source is a priority error, and the
   project made exactly that error before this review.

**Yang and Zhang (2000)**, *Journal of Business* — RECORD VERIFIED, EQUATION UNVERIFIED.
Drift-independent and handles opening jumps; requires a window because two of its components are
cross-day variances.

**Chou, Chou and Liu**, "Range volatility: a review of models and empirical studies", *Handbook of
Financial Econometrics and Statistics*, Springer, chapter 74, pp. 2029–2050 — **CHAPTER READ**
(by the author, 2026-08-29). The standing survey of the field. What it contains matters to us on
four counts, and the third is the one that constrains us:

1. **Estimator assumptions**, as we state them: Parkinson and Garman–Klass require geometric
   Brownian motion with zero drift; Rogers–Satchell permits non-zero drift; Yang–Zhang additionally
   allows overnight jumps.
2. **Outlier sensitivity** — "the range is very sensitive to the outliers" — with Chou (2005)'s
   quantile range offered as a robust alternative. The literature already treats the raw range as
   problematic.
3. **Finite observations and downward bias.** The chapter states that only finite observations are
   available to construct the range, that this creates bias **particularly for lower-liquidity
   assets and finite transaction volume**, and that observed highs and lows can fall inside the true
   extrema, producing downward-biased estimators. **This is closer to our territory than an earlier
   draft of this review assumed**, and it means the mechanism we document is recognised in the
   standing survey, even if our particular measurement of it is not.
4. **Microstructure and bias-adjusted realized range**, citing Akay et al. (2010).

**What the chapter does *not* contain:** any correction designed for degenerate zero-range
observations, or an analogue of AddRS for the `H = L` case. That is a real negative finding — but
it establishes only that *this review* does not document it, not that nobody has. See §D.2, where
the claim it was supporting has since been retracted on other evidence.

**Akay, Griffiths and Winters (2010)**, "On the robustness of range-based volatility estimators",
*Journal of Financial Research* 33(2), 179–199 — RECORD VERIFIED. Examines Parkinson's estimator in
the federal funds market around predictable interday volatility patterns, finding range-based
estimates can remove upward bias associated with microstructure noise. **Relevant, but not a
zero-range treatment** — an earlier draft of this review flagged it as a candidate and it is not.

---

## B. Discretisation bias and its corrections from daily data

This is the strand our AddRS result speaks to.

**Rogers, Satchell and Yoon (1994)**, *Applied Financial Economics* 4(3), 241–247 — RECORD
VERIFIED; the specific treatment of discretisation attributed to it is **UNVERIFIED**. By title a
comparison of methods using high and low prices. The project previously asserted that this paper
corrects discretisation bias using a transaction-count proxy; that assertion is not supported by
anything we have read, and it is now flagged rather than repeated.

**Maheswaran and Kumar (2013)**, *Economic Modelling* 33, 701–712,
DOI 10.1016/j.econmod.2013.05.019 — CLAIM VERIFIED (abstract read verbatim). Proposes the
**automatic bias correction (ABC)** for extreme-value volatility estimators. The abstract's own
words matter: it is an *"empirical automatic bias correction procedure"*, the bias *"originates
from the random walk effect"*, the estimator *"does not require knowledge of N, the number of
steps"*, and *"the procedure works well in real life data"*. There is **no claim of exact
unbiasedness** and no theoretical guarantee stated in the abstract. ABC is empirical.

**Kumar and Maheswaran (2014)**, *Economic Modelling* 38, 33–44,
DOI 10.1016/j.econmod.2013.11.045 — RECORD VERIFIED; DERIVATION UNVERIFIED. Introduces **AddRS**
via a reflection principle for a random walk with the **symmetric double exponential
distribution**, giving a closed form for the joint probability of the running maximum and the
terminal value, and an estimator that is *"not just approximately unbiased but exactly so"*. The
maintained model is therefore **not Brownian motion**, and "AddRS is unbiased" must always carry
that qualification.

> **These are two different procedures from two different papers**, and the project conflated
> them for a period. ABC (2013) is empirical and approximate; AddRS (2014) is theoretical and
> exact under its own model. Only AddRS is implemented here.

**Kumar and Maheswaran (2014b)**, "Modeling and forecasting the additive bias corrected extreme
value volatility estimator", *International Review of Financial Analysis* 34, 166–176,
DOI 10.1016/j.irfa.2014.06.002 — RECORD VERIFIED. The downstream forecasting treatment of AddRS,
and **not** the derivation source; an earlier iteration of this project confused the two, citing
this paper's volume and pages against the reflection-principle paper's claim.

**Shaik and Maheswaran (2020)**, "A new unbiased additive robust volatility estimation using
extreme values of asset prices", *Financial Markets and Portfolio Management* 34, 313–347,
DOI 10.1007/s11408-020-00355-3 — RECORD VERIFIED. **A successor estimator from the same research
group, six years after AddRS, which this project does not test.** That is a gap a referee will
find: our §8 concludes AddRS overstates in this market, and the obvious question is whether the
2020 estimator repairs the premise problem we identify. It should be read and, if the equations are
obtainable, benchmarked alongside AddRS before the AddRS result is presented as a boundary
condition on "the" daily-OHLC correction.

**Provenance of the AddRS equations.** The 2014 article was not obtained. The operational
equations implemented in `estimators/range_.py` come from a later open-access paper by the same
author reproducing them, were checked term-for-term against that reproduction, and were verified
numerically against an independent reimplementation (exact agreement on ten synthetic boundary
cases and on all 184,391 panel rows, maximum absolute difference 3.5e-18). **The derivation and
the unbiasedness proof remain unverified from the primary source**, and no claim about the
theorem's conditions should rest on our reading.

**Maheswaran, Balasubramanian and Yoonus (2011)**, "Post-colonial finance", *Journal of Emerging
Market Finance* 10(2), 175–196, DOI 10.1177/097265271101000202 — RECORD VERIFIED. **This is the
source of the extreme-value variance ratio**, not the 2013 paper, which the project previously
credited. The 2013 paper reports a VRatio of 0.82 for Rogers–Satchell against the "usual"
close-to-close estimator on the Nifty index over 1996–2011 and attributes the shortfall to the
random-walk effect. **The 0.82 is a variance-scale ratio**; the coincidence that √0.671 = 0.819
in our own sample is a scale trap and not a replication.

---

## C. The realized range: adjacent literature, not applicable here

An entire strand corrects range-based estimators using **intraday** observations. It is important
to locate our setting against it and equally important not to import its results, because it
presumes data a market like NEPSE does not publish.

**Martens and van Dijk (2007)**, *Journal of Econometrics* 138(1), 181–207 — CLAIM VERIFIED.
Introduces the realized range: replace each intra-day squared return with the high–low range of
that period. Proposes a bias correction **scaling the realized range by the average level of the
daily range**, targeting microstructure frictions.

**Christensen and Podolskij (2007)**, *Journal of Econometrics* 141(2), 323–349 — CLAIM VERIFIED.
Probabilistic laws for estimating quadratic variation of continuous semimartingales with the
realized range-based variance, replacing every squared return of realized variance with a
normalized squared range.

**Christensen, Podolskij and Vetter (2009)**, *Finance and Stochastics* 13(2), 239–268,
DOI 10.1007/s00780-009-0089-9 — CLAIM VERIFIED. Analyses microstructure noise in the realized
range-based variance and proposes a bias correction; the corrected estimator is consistent for
integrated variance and asymptotically mixed Gaussian under simple noise.

> **Why this strand cannot solve our problem.** Every correction in it operates on intraday
> observations. The premise of the present paper is a market that publishes one OHLC bar per
> security per day. The strand tells us what is possible with better data; it does not tell us
> what to do with the data that exist.

---

## D. Liquidity measurement, zero returns, and where our composition finding actually sits

**This is the strand that constrains our contribution most, and the section a referee will reach
for first.**

**Lesmond, Ogden and Trzcinka (1999)**, "A new estimate of transaction costs", *Review of
Financial Studies* 12(5), 1113–1141 — CLAIM VERIFIED. The LOT model. Effective transaction costs
are estimated from the time series of daily returns alone; the feature that identifies them is
**the incidence of zero returns**, modelled through a **limited dependent variable** framework.
Zero returns occur when transaction costs exceed the information value to the informed trader.

**Lesmond (2005)**, "Liquidity of emerging markets", *Journal of Financial Economics* 77(2),
411–452 — RECORD VERIFIED; the market count CLAIM VERIFIED. **The two figures in circulation are
both correct and describe different things**, which is worth recording because a careless citation
picks one and implies the other is wrong. The full sample in which liquidity estimators are analysed
is **31 emerging markets**. The model-selection and regression tests, which require bid–ask spread
data, run on the **23** of those markets where spreads are available — and the Stoll-variable
comparison on **10** of those 23. Cite 31 for the study's coverage, 23 for the spread-validated
results.

**Bekaert, Harvey and Lundblad (2007)**, "Liquidity and expected returns: lessons from emerging
markets", *Review of Financial Studies* 20(6), 1783–1831 — CLAIM VERIFIED. **The primary liquidity
measure is a transformation of the proportion of zero daily firm returns**, averaged over the
month; it significantly predicts future returns where turnover does not.

### D.1 What this means for us

Three implications, and the first is uncomfortable.

**1. The remedy we propose is standard practice, and we must say so.** The zero-return proxy is
known to be contaminated by instrument composition, and the cleaning protocol in this literature
restricts samples to **ordinary common shares** for exactly that reason. Our §5 finding — that
pooling debentures, closed-end funds and promoter shares manufactures a spurious liquidity
gradient — is a specific instance of a problem this literature already solved. A referee who
raises this is right, and the paper concedes it in §3.1 rather than waiting to be told.

**2. RETRACTED — the zero-range case IS documented, in the spread literature.** See §D.2. An
earlier version of this review claimed the zero-**range** analogue of the zero-**return** proxy was
undocumented. That claim does not survive.

**3. LOT's limited-dependent-variable model is the right comparison for our §9.** Both LOT and our
censored-open estimator model an *unobserved* price movement through a *censored* observable. The
parallel is close enough that a revision should draw it explicitly — and close enough that LOT's
identification concerns transfer. Our §9.4 finding that the censoring assumption fails to
extrapolate across the April 2026 band change is precisely the kind of check the LOT literature
would demand.

### D.2 The claim we had to retract

Our headline novelty claim was that the zero-**range** rate `P(H = L)`, as the range-estimator
counterpart of the contaminated zero-**return** liquidity proxy, was undocumented. **It is
documented, and we withdraw the claim.** The treatment sits in the bid–ask spread literature, which
works on the same daily high–low data we do.

**Corwin and Schultz (2012)**, "A simple way to estimate bid–ask spreads from daily high and low
prices", *Journal of Finance* 67(2) — CLAIM VERIFIED. Their estimator derives the spread from
high–low ratios over one- and two-day intervals, exploiting that the variance component of the
high–low ratio scales with the interval while the spread component does not. Critically for us,
they address the degenerate case explicitly: with very infrequent trading there are sometimes no
transactions, or only one trade in a day, giving **identical high and low prices and zero range**.
Their prescription is a rule, not an omission: the previous day's high, low and close are retained,
**with a further adjustment specific to zero-range days**. So the case is not merely acknowledged in
passing — it has dedicated handling, which makes our withdrawn claim clearly wrong rather than
arguably so.

**Ardia, Guidotti and Kroencke (2024)**, "Efficient estimation of bid–ask spreads from open, high,
low, and close prices", *Journal of Financial Economics* 161, 103916,
DOI 10.1016/j.jfineco.2024.103916 — CLAIM VERIFIED. Popular spread estimators are **downward biased
when trading is infrequent**; the paper derives asymptotically unbiased estimators by explicitly
accounting for discretely observed prices, and reports them unbiased even in simulations where a
single trade per period is expected. Related work extends the Corwin–Schultz construction to days
with no trade at all, and to corporate bonds.

> **What this costs us and what it leaves.** The zero-range phenomenon, its origin in sparse
> trading, and the need to handle it are all established — in a neighbouring literature using the
> same inputs, in the *Journal of Finance* and the *Journal of Financial Economics*. A referee who
> knows the spread literature would have raised this immediately, and the paper must not claim
> otherwise.
>
> Two things survive, and they are about **sample construction rather than estimator theory**.
> First, we are not aware of this being connected to the *composition* problem: that in an exchange
> feed publishing no instrument-type field, the zero-range rate sorts securities by asset class
> rather than by liquidity, so a liquidity gradient built from it is an asset-class gradient.
> Second, the quantification — pooled 5.70% against 0.28% on ordinary equity, and a thinnest decile
> that is 94.3% non-equity.
>
> **We propose no zero-range correction and should stop implying we might.** Our contribution is
> diagnostic: what a sample looks like when the filter the liquidity literature already prescribes
> is not applied, and cannot be applied mechanically. That is smaller than the earlier framing and
> it is what the evidence supports.

---

## E. Non-synchronous and thin trading

The classical treatment of what infrequent trading does to estimated moments.

**Scholes and Williams (1977)**, "Estimating betas from nonsynchronous data", *Journal of
Financial Economics* 5(3), 309–327 — CLAIM VERIFIED. OLS estimates of market-model parameters are
biased and inconsistent under non-synchronous trading; their correction sums coefficients on
lagged, coincident and leading market returns.

**Lo and MacKinlay (1990)**, "An econometric analysis of nonsynchronous trading", *Journal of
Econometrics* 45(1–2), 181–211 — CLAIM VERIFIED. Non-synchronous trading generates **spurious
serial dependence**; they report a weekly first-order autocorrelation of 46% for a portfolio of
small firms.

**Relevance and a caution.** This strand concerns *cross-security* non-synchronicity and its
effect on covariances and autocorrelations. Our problem is *within-security* discretisation of a
single price path. The two are related but not the same, and the paper should not lean on
Lo–MacKinlay as though it addressed range estimators. It is useful mainly as evidence that thin
trading distorts second moments in ways that look like real economics — which is the general form
of the trap §5 documents.

---

## F. Institutions: call auctions and price limits

**Ibikunle (2015)**, "Opening and closing price efficiency: do financial markets need the call
auction?", *Journal of International Financial Markets, Institutions and Money* 34, 208–227,
DOI 10.1016/j.intfin.2014.11.014 — CLAIM VERIFIED. On the London Stock Exchange the opening
auction delivers highly efficient prices for the **highest-volume** stocks, while lower-volume
stocks reach comparable efficiency **only after continuous trading begins**, with a high rate of
failure to open at the call concentrated among low-volume securities.

> This is the closest published analogue to our §9, and it cuts in a useful direction: our
> observation that thin NEPSE securities concentrate repricing at the open, and that the auction
> often fails to clear (10.8% no-match overall), is *consistent with an established finding
> elsewhere*. **We should therefore not present it as novel**, and §3 says so.

**Agarwalla, Jacob and Pandey (2015)**, "Impact of the introduction of call auction on price
discovery: evidence from the Indian stock market using high-frequency data", *International Review
of Financial Analysis* 39, 167–178 — CLAIM VERIFIED. *(This fills the gap an earlier draft of this
review flagged as needing a proper citation.)* Studying the 2010 reintroduction of the opening call
auction on the NSE, they find the auctions **attract very little volume**, the intraday pattern of
volume and volatility in the continuous market is **unchanged**, and **a large fraction of price
discovery still occurs in the first fifteen minutes of continuous trading** rather than at the call.

> This is the sharpest available comparator for our §9, and it cuts *against* a strong reading of
> our result. On the NSE — our own cross-market benchmark — the opening auction is largely
> bypassed. Our NEPSE finding is that the opening return carries 63.6% of close-to-close variance
> in thin equity. Whether that reflects genuine price discovery at the NEPSE auction, or simply the
> mechanical fact that a thinly traded security's whole daily move is booked at its one clearing
> event, is exactly the distinction §9.1 says we cannot identify. Agarwalla et al. show the
> question is live in a neighbouring market with far better data.
>
> Note also that **Joshy Jacob is an author of both this paper and Jacob and Vipul (2008)**, whose
> finding that range estimators survive moderate illiquidity our equity results agree with.

**Kim and Rhee (1997)**, "Price limit performance: evidence from the Tokyo Stock Exchange",
*Journal of Finance* — RECORD VERIFIED (volume and pages not yet confirmed). Volatility does not
return to normal after limits are hit; limits delay price discovery and interfere with trading.
The subsequent "magnet effect" literature (Du and others) finds prices accelerate toward limits as
they approach.

**Why this matters more than the paper currently admits.** NEPSE operates *both* a ±2% pre-open
order band *and* a ±10% daily price limit, and the two are separate mechanisms with separate
literatures. Our §9 models the first as censoring and does not model the second at all. A magnet
effect would make the observed opening distribution reflect *strategic* order placement rather
than a truncated latent variable — which is one concrete mechanism that could explain why our
censoring model fails to extrapolate across the April 2026 change (§9.4). **This is the most
promising unexplored lead in the review.**

---

## G. NEPSE-specific work

**Dangal and Gajurel (2021)**, "Volatility of daily Nepal Stock Exchange (NEPSE) index return: a
GARCH family models", *Tribhuvan University Journal* — RECORD VERIFIED. 3,392 daily observations,
2006-06-01 to 2021-04-07; symmetric GARCH(1,1) and GARCH-M against asymmetric TGARCH, EGARCH and
PGARCH. Finds volatility clustering and leverage effects; symmetric models fit the full sample
better while asymmetric models fit the pre- and post-earthquake sub-periods better.

Several further NEPSE GARCH studies exist in Nepalese journals (Adhikari; *Research Journal of
Padmakanya Multiple Campus*; and others), broadly finding volatility clustering and persistence.

**What this tells us about our own positioning.** The existing NEPSE literature is almost entirely
**index-level GARCH**. We have found no study that:

- works at the **security level** across the NEPSE cross-section;
- uses **range-based** estimators on NEPSE at all;
- addresses the **instrument-composition** problem in NEPSE's published files;
- models the **pre-open band**.

That is a genuine gap, and it is a better statement of our empirical contribution than any claim
about frontier markets in general. It also raises an obvious question a referee will ask: *do the
existing index-level GARCH results survive the composition problem?* The index is value-weighted
across the same mixed universe. We have not checked, and it is worth checking.

---

## H. Econometric method

**Cameron, Gelbach and Miller (2008)**, *Review of Economics and Statistics* 90(3), 414–427 —
CLAIM VERIFIED. Cluster-robust standard errors presume many clusters; asymptotic tests over-reject
with **few (five to thirty) clusters**. A pairs cluster bootstrap should work in principle but a
**wild cluster bootstrap performs better** in practice, reducing rejection rates from ten percent
or more to five for nominal-size-0.05 tests. Our design has G = 14, squarely inside their problem
range, which is what justifies PAP §8.3a's requirement.

**Not yet verified, and needed.** MacKinnon and Webb on wild bootstrap inference with wildly
different cluster sizes, and on few treated clusters. Our cluster sizes run 1 to 8 with a
singleton, so the first is directly relevant. Cameron, Gelbach and Miller (2011) on multiway
clustering is needed before any two-way covariance is defended in print.

**Patton (2011)**, "Volatility forecast comparison using imperfect volatility proxies", *Journal
of Econometrics* 160(1), 246–256 — CLAIM VERIFIED. A conditionally unbiased but imperfect
volatility proxy distorts standard forecast comparisons; the paper derives necessary and
sufficient conditions on the loss function for rankings to be robust to proxy noise. This is the
authority for restricting losses to QLIKE and MSE on the variance scale, and it applies directly:
**every ratio in our paper is measured against an imperfect proxy** — squared open-to-close
returns — and the same logic that constrains loss functions should make us cautious about reading
small departures from one as estimator bias.

**Corsi (2009)**, "A simple approximate long memory model of realized volatility", *Journal of
Financial Econometrics* 7(2), 174–196, DOI 10.1093/jjfinec/nbp001 — CLAIM VERIFIED. The HAR-RV
model, an additive cascade of volatility components giving an AR-type model in realized
volatility.

---

## I. What the review lets the paper claim

Stated as a ledger, so that each claim can be checked against a strand.

| paper claim | supported by | status |
|---|---|---|
| Range estimators assume continuous observation | A: Parkinson, Rogers–Satchell | safe |
| RS is unbiased *w.r.t. drift under continuous BM*, not generally | A: Rogers–Satchell abstract | safe, and the qualification is required |
| The discrete-extrema problem was identified in 1991, not later | A: Rogers–Satchell abstract | safe; corrects a project error |
| ABC and AddRS are distinct; ABC is empirical | B: both abstracts | safe |
| AddRS is exact *under a double-exponential random walk* | B: 2014 abstract | safe with the qualification; proof unread |
| The VRatio is due to the 2011 paper | B: secondary attribution, record verified | safe |
| Intraday corrections do not apply to daily-OHLC markets | C | safe |
| Restricting to ordinary equity is standard practice | D | **constrains us; must be conceded** |
| The zero-*range* analogue is undocumented | D + A survey | **provisional — check Chou et al. first** |
| Thin securities concentrate repricing at the open | F: Ibikunle | consistent with prior work; **not novel** |
| NEPSE lacks security-level range-based study | G | safe on current search |
| WCB is required at G = 14 | H: CGM 2008 | safe |
| Small departures from a ratio of one need care | H: Patton | **under-used in the current draft** |

---

## J. Gaps this review could not close

1. **Four primary texts remain unread**: the AddRS derivation, Parkinson's equation, Garman–Klass's
   equation and choice of form, and Rogers–Satchell's Section 3 correction. All are paywalled and
   all need library access.
2. **Chou, Chou and Liu has not been read.** Until it is, the claim that the zero-range analogue is
   undocumented is provisional. This is the single cheapest way to strengthen or kill our headline
   novelty claim.
3. **MacKinnon and Webb are unverified**, and our cluster sizes (1 to 8, with a singleton) are
   exactly the configuration they study.
4. ~~The NSE call-auction result has no proper citation.~~ **CLOSED** — Agarwalla, Jacob and
   Pandey (2015), *IRFA* 39, 167–178.
5. **Shaik and Maheswaran (2020) is unread.** A successor to AddRS from the same group that we do
   not test. This is now the second-most-likely thing a referee raises.
6. **Kim and Rhee's volume and pages are unconfirmed**, and the price-limit literature is barely
   engaged despite NEPSE operating a ±10% daily limit that we do not model.
7. **No search was run** on: the volatility-of-volatility literature, bid–ask bounce corrections
   beyond Roll, or frontier-market microstructure outside South Asia.

---

## K. The most valuable next reading, ranked

1. **Chou, Chou and Liu**, either version — settles whether our headline novelty claim survives.
2. **Kim and Rhee (1997)** and one magnet-effect paper — the price-limit mechanism is the most
   plausible explanation for why our censoring model fails to extrapolate (§9.4), and it is
   currently unexamined.
3. **Kumar and Maheswaran (2014)** full text, and **Shaik and Maheswaran (2020)** — the first is
   the only route to CLAIM status for the estimator the paper's second result depends on; the
   second asks whether a newer estimator from the same group already repairs the premise problem
   §8 identifies. Testing AddRS and calling it a boundary condition on daily-OHLC corrections is
   weaker if a 2020 successor exists untested.
4. **MacKinnon and Webb** — our cluster structure is their subject.
5. **The NEPSE index-level GARCH studies** — do their results survive the composition problem we
   document? If the index is value-weighted over the same mixed universe, that is a direct and
   answerable question about published work.
