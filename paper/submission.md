# Submission materials

Drafts. Journal-specific formatting is not applied — that waits until a target is chosen.

---

## Data availability statement

The replication package is public at
`https://github.com/anamgiri91/nepal-stock-market-research`. It contains the full analysis
pipeline, the instrument classifier, all cleaning rules, the test suite, and the code that
generates every table and figure in the paper. `./run_pipeline.sh` reproduces every exhibit from
raw inputs.

Raw NEPSE daily files are not redistributed here. Their provenance and redistribution terms have
not been established, and the paper's position is that unresolved redistribution rights are a
reason to withhold data rather than a formality to work around. The pipeline reads them from a
local vault whose contents are checksummed; the manifest of file hashes ships with the package so
a third party who obtains the same files can verify they hold the same inputs. NIFTY 50 and India
VIX series are third-party data obtained under their own terms.

Every build writes `BUILD-MANIFEST.json` recording the git commit and working-tree state, an
aggregate hash of the raw inputs, a hash of the cleaning code, the version of each cleaning rule
in force, and the shape of every artifact produced.

---

## Cover letter — draft

Dear Editor,

Please consider the enclosed manuscript, *What Looks Like Illiquidity: Instrument Composition and
Range-Based Volatility Estimation in a Frontier Market*.

The paper documents a failure mode in empirical volatility work on frontier markets. The Nepal
Stock Exchange publishes ordinary equity, corporate debentures, closed-end mutual funds and
restricted promoter shares in a single daily file carrying no instrument-type field. Sorting that
pooled universe on trading intensity reproduces the textbook picture of range-based estimators
breaking down under illiquidity: in the thinnest decile the Parkinson estimator returns exactly
zero on 53.9% of stock-days. That decile is 94.3% non-equity. Restricted to the 291 ordinary
equities, the picture inverts — participation is 1.000 in every liquidity quintile, the zero-range
rate falls from 5.70% to 0.28%, and Rogers–Satchell against a matched open-to-close benchmark is
0.998 on a variance scale.

I want to be direct with you about what is and is not new here, because the paper is direct about
it. Restricting samples to ordinary common shares is long-standing practice in the emerging-market
liquidity literature. The zero-range case and its origin in sparse trading are documented in the
bid–ask spread literature, which works on the same daily inputs. The paper proposes no new
estimator and no correction. What it contributes is a measured account of the downstream
consequence of omitting a familiar filter in a market where it cannot be applied mechanically —
and the observation that the filter protects a different conclusion than the one it was designed
for. The liquidity literature applies it to keep non-equity instruments out of a liquidity
*measure*; the same omission determines whether one concludes that range-based estimators are
usable in the market at all.

A second result stands independently. The additive bias correction of Kumar and Maheswaran (2014)
overstates at every equity liquidity level we can measure, from 1.149 to 1.323 against a matched
benchmark, while performing as designed on the NIFTY 50 at 1.005. This follows from the
correction's premise rather than from any defect in it: the correction is non-negative by
construction, so wherever Rogers–Satchell is not downward-biased in expectation, adding it
overshoots in expectation. We decompose where the correction's mass actually comes from and find
that frequency of correction, absolute correction mass, and correction relative to the estimator
point in three different directions.

The manuscript states its limits explicitly. One hypothesis was evaluated on held-out data and its
confirmatory provenance carries two stated qualifications. A censored-normal model of the pre-open
price band fails an out-of-sample test we ran against a subsequent regime change, and is reported
as description rather than identification. There is no security-level cross-market comparison. Four
primary texts remain unread and are named. I would rather these appear in the paper than in a
referee report.

The work has not been submitted elsewhere and is not under consideration by another journal.

Yours sincerely,
Anam Giri

---

## Target journals, in order

| journal | fit |
|---|---|
| **International Review of Financial Analysis** | Publishes Agarwalla, Jacob and Pandey (2015) and the Kumar–Maheswaran line the paper engages with. The most natural home. |
| **Emerging Markets Review** | Frontier-market methodology is on-topic rather than a curiosity. |
| **J. International Financial Markets, Institutions and Money** | Published Ibikunle (2015), cited in §3. |
| **Finance Research Letters** | If a short-format note on the composition result alone is preferred to the full paper. |

Not attempted: JF, JFE, RFS, JFQA, *Journal of Econometrics*, *Journal of Financial Econometrics*.
These require a theoretical or methodological contribution the paper does not make, and the
charter records that judgement rather than leaving the earlier target standing.

---

## Pre-submission checklist

**Science**
- [ ] Benchmark Shaik and Maheswaran (2020), or state explicitly that §8 bounds AddRS alone
- [ ] Decide §9: model the ±2% band and ±10% limit jointly, or cut to a short descriptive note
- [ ] Four primary texts — AddRS derivation, Parkinson, Garman–Klass, Rogers–Satchell §3
- [ ] HO-3 acquisition, or accept that no security-level cross-market comparison exists

**Manuscript**
- [x] Figures restored and numbered
- [x] Robustness section
- [x] Conclusion
- [ ] Full read-through by a human
- [ ] Abstract settled — rewritten three times on 2026-08-29
- [ ] Author affiliation, JEL codes, keywords

**Mechanics**
- [x] Build path — `paper/build.py`, HTML then browser Print to PDF
- [ ] `brew install pango` for a direct PDF write, if wanted
- [ ] Journal formatting once a target is chosen
- [x] Data availability statement
- [x] Cover letter draft
- [ ] PAP-v5 amendment filed
