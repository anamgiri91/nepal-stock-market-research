# Volatility Estimation in a Market Without Derivatives: Evidence from NEPSE

> **Status: exploratory.** No pre-analysis plan is frozen, so no result here may be read as a
> confirmatory test. This repository is the public replication package; `./run_pipeline.sh`
> reproduces every exhibit from raw data.

### Relationship to the earlier iteration

This repository was restructured on 2026-08-27. The previous flat-layout project remains
reachable in git history at `7ebb37a` and is not deleted. Two of its conclusions are
reproduced independently by the rebuilt pipeline and are carried forward:

- range-based estimators outperform GARCH in out-of-sample forecasting
- genuine intraday range begins 2016-06-06, giving 2,296 usable index sessions

One of its findings closes off a line of enquiry and should be cited rather than
re-discovered: **India VIX is not a viable implied-volatility proxy for NEPSE**
(R² ≈ 1.1% at one day, insignificant at longer horizons).

Data files from that iteration are held outside version control while their redistribution
rights are resolved.

## Research question

Can volatility estimation methods developed for options-rich markets be adapted for frontier
markets without derivatives?

Most of the modern volatility toolkit was built where options exist. Implied volatility needs an
options market. Realized-volatility methods need dense intraday data. Range-based estimators
(Parkinson, Garman–Klass, Rogers–Satchell, Yang–Zhang) need only OHLC prices — but their
derivations assume frictionless continuous trading, which is exactly what a frontier exchange does
not provide. The Nepal Stock Exchange (NEPSE) has no derivatives of any kind, binding daily price
limits, thin trading, and a Sunday–Thursday week. It is a clean setting for asking which parts of
the toolkit survive, which fail, and why.

## Repository layout

```
config/        run configuration — paths, parameters, seeds
data/
  raw/         immutable inputs (see data/raw/README.md for current status)
  interim/     intermediate, fully regenerable
  processed/   analysis-ready, fully regenerable
  external/    macro series, holiday calendars
src/nepsevol/
  ingest/      data acquisition and parsing
  trading_calendar/  NEPSE calendar — Sun–Thu week, holidays, closures
  clean/       OHLC validation and cleaning rules
  estimators/  volatility estimators
  evaluation/  loss functions, spread estimators, microstructure diagnostics
  models/      latent-state volatility model, HAR, proxy-robust forecast evaluation
  utils/
scripts/       numbered pipeline; runs top to bottom from a clean state
tests/         unit tests, incl. estimators checked against known answers
notebooks/     01_exploratory_analysis.ipynb, 02_models.ipynb
output/        figures, tables, logs (all regenerable)
paper/         manuscript source
docs/          data dictionary, methodology, reproduction instructions
```

## Reproduction

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

for s in scripts/[0-9]*.py; do python "$s"; done
```

Or simply:

```bash
./run_pipeline.sh
```

See `docs/reproduction.md`. If the pipeline does not reproduce every exhibit from a clean state,
that is a defect in the pipeline, not an acceptable state.

### Exploratory notebook

`notebooks/01_exploratory_analysis.ipynb` is the diagnostic companion to the paper: data
integrity, distributional tests, autocorrelation and stationarity, structural breaks, the
Sunday–Thursday calendar, liquidity measures, estimator comparison, GARCH-family fits, and
the bias-versus-trading-intensity result. It is stored **executed**, so every figure and
table can be read without running anything.

```bash
./.venv/bin/jupyter lab notebooks/01_exploratory_analysis.ipynb
```

### Model notebook

`notebooks/02_models.ipynb` builds and evaluates the models. Its premise is that NEPSE has no
observable ground truth, so two devices carry the work:

- **Future squared returns as a noisy but unbiased proxy**, scored with proxy-robust losses
  (MSE, QLIKE per Patton 2011), a Diebold–Mariano test, and a Model Confidence Set — which
  reports a *set* of indistinguishable models rather than a spurious single winner.
- **A latent-state model** in which log-variance is an unobserved AR(1) and each estimator is
  a biased, noisy measurement of it, so the measurement intercepts identify estimator bias
  from data alone.

Both are validated against known answers before being applied: the evaluation machinery must
recover a known forecast ranking, and the state-space model must recover a known simulated
bias, before either is trusted on real data.

Models compared: HAR (Corsi) on each of five variance measures · EWMA/RiskMetrics ·
GARCH(1,1)-t · GJR-GARCH-t · random walk · constant.

The notebooks explore; they do not define the pipeline. Anything load-bearing lives in
`src/nepsevol/` and `scripts/`.

## Data

The primary input is the NEPSE daily index series (OHLC + turnover), 2010-01-03 → 2026-06-12.

Three properties of this data drive much of the design and are documented in `docs/data_dictionary.md`:

1. **Genuine intraday extremes begin only 2016-06-06.** Earlier rows carry `Open == High == Low == Close`,
   which makes every range-based estimator undefined. The usable sample is 2,296 trading days.
2. **The trading week is Sunday–Thursday.** Annualization and overnight-return conventions both
   differ from the Monday–Friday standard the estimators were written for.
3. **69 rows violate OHLC consistency** within the usable window and require a pre-committed
   handling rule.

Raw-data redistribution rights are unresolved; `data/raw/README.md` records the current state.

## Requirements

Python 3.14 (verified working). See `requirements.txt`.

## Licence

Code: MIT (see `LICENSE`). Data: subject to source terms — see `data/raw/README.md`.
