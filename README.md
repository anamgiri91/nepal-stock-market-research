# NEPSE Frontier-Market Volatility Research Project

## Working Title

**Can volatility estimation methods developed for options-rich markets be adapted for frontier markets without derivatives? Evidence from NEPSE.**

## Abstract

This project studies whether volatility estimation methods originally designed for options-rich markets can be adapted for a frontier market without listed derivatives. The empirical case is the Nepal Stock Exchange (NEPSE), using daily OHLCV data from 2010-01-03 through 2026-06-12 (3,760 observations). The project compares five families of volatility estimators: close-to-close historical, range-based (Parkinson, Garman-Klass, Rogers-Satchell, Yang-Zhang), GARCH-family (9 specifications), HAR-RV, and India VIX as a cross-border implied volatility proxy.

## Key Findings

1. **Range-based estimators significantly outperform GARCH** in out-of-sample forecasting (Diebold-Mariano p < 0.01)
2. **Error distribution >> variance specification**: Skewed-t vs Gaussian (AIC gap ~400) matters 20× more than GARCH vs EGARCH vs GJR (~20)
3. **India VIX is NOT a viable implied volatility proxy** for NEPSE (R² = 1.1% at 1-day horizon, insignificant at longer horizons)
4. **GJR-GARCH(1,1)-SkewT** is the best in-sample GARCH model (AIC = 11,327.8)
5. **HAR-RV** captures heterogeneous volatility (in-sample R² = 22.5%)

## Data

### NEPSE Data
- File: `nepse_index_history.csv`
- Date range: 2010-01-03 to 2026-06-12
- Observations: 3,760
- Columns: `Date`, `Open`, `High`, `Low`, `Close`, `Change`, `Percent_Change`, `Turnover`
- Genuine OHLC (H ≠ L): from 2016-06-06 onward (2,296 observations)

### External Data (downloaded via `scripts/download_external_data.py`)
- India VIX: 4,036 observations (2010–2026)
- NIFTY 50 OHLCV: 4,037 observations
- S&P 500 VIX: 4,137 observations
- Aligned NEPSE–India intersection: 2,916 common trading dates

## Scripts

All analysis is implemented as standalone Python scripts in `scripts/`:

| Script | Purpose |
|---|---|
| `download_external_data.py` | Download India VIX, NIFTY 50, S&P 500 VIX via yfinance |
| `compute_range_volatility.py` | Parkinson, Garman-Klass, Rogers-Satchell, Yang-Zhang estimators |
| `stationarity_tests.py` | ADF, KPSS, ARCH-LM, Ljung-Box, Zivot-Andrews |
| `expanded_garch.py` | 9 GARCH specs (3 models × 3 distributions) + diagnostics |
| `oos_evaluation.py` | Out-of-sample forecast evaluation, Mincer-Zarnowitz, DM tests |
| `spillover_analysis.py` | Granger causality, bivariate VAR, India VIX proxy regressions |
| `robustness_checks.py` | Sub-sample, alt windows, alt GARCH orders, HAR-RV, bootstrap DM |

### Legacy Notebooks (in `notebooks/`)

| Notebook | Status |
|---|---|
| `01_data_cleaning_nepse.ipynb` | Original — superseded by new OHLCV dataset |
| `02_descriptive_analysis.ipynb` | Original — supplemented by `stationarity_tests.py` |
| `03_garch_models.ipynb` | Original (3 specs) — superseded by `expanded_garch.py` (9 specs) |
| `04_volatility_of_volatility_methods.ipynb` | Original STVV/EMVV/MIVV analysis |
| `05_benchmark_comparison.ipynb` | Original benchmark tables |
| `06_spillover_analysis.ipynb` | Stub — superseded by `spillover_analysis.py` |
| `07_robustness_checks.ipynb` | Stub — superseded by `robustness_checks.py` |

## Repository Layout

```text
.
├── README.md
├── .gitignore
├── requirements.txt
├── nepse_index_history.csv          # NEPSE OHLCV (3,760 rows)
├── scrape_nepse.py                  # OHLCV scraper (ShareSansar)
├── scrape_nepse_indices.py          # Original close-only scraper
├── scripts/
│   ├── download_external_data.py
│   ├── compute_range_volatility.py
│   ├── stationarity_tests.py
│   ├── expanded_garch.py
│   ├── oos_evaluation.py
│   ├── spillover_analysis.py
│   └── robustness_checks.py
├── notebooks/                       # Legacy Jupyter notebooks
│   ├── 01_data_cleaning_nepse.ipynb
│   ├── 02_descriptive_analysis.ipynb
│   ├── 03_garch_models.ipynb
│   ├── 04_volatility_of_volatility_methods.ipynb
│   ├── 05_benchmark_comparison.ipynb
│   ├── 06_spillover_analysis.ipynb
│   └── 07_robustness_checks.ipynb
└── data/                            # Generated data (gitignored)
    ├── data_india_vix.csv
    ├── data_nifty50_ohlcv.csv
    ├── data_sp500_vix.csv
    ├── data_aligned_nepse_india.csv
    ├── data_range_based_volatility.csv
    └── data_garch_expanded.csv
```

## Reproducibility

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pandas numpy matplotlib scipy statsmodels arch yfinance
```

### Run All Analysis

```bash
# 1. Download external data (requires internet)
python scripts/download_external_data.py

# 2. Compute range-based volatility
python scripts/compute_range_volatility.py

# 3. Stationarity tests
python scripts/stationarity_tests.py

# 4. Expanded GARCH models
python scripts/expanded_garch.py

# 5. Out-of-sample evaluation
python scripts/oos_evaluation.py

# 6. Spillover analysis
python scripts/spillover_analysis.py

# 7. Robustness checks
python scripts/robustness_checks.py
```

### Refresh NEPSE Data

```bash
python scrape_nepse.py
```

## Research Status

### Completed
- NEPSE daily OHLCV dataset (2010–2026, 3,760 observations)
- Descriptive statistics, stationarity tests, ARCH-effect confirmation
- Range-based volatility estimators (Parkinson, Garman-Klass, Rogers-Satchell, Yang-Zhang)
- GARCH, EGARCH, GJR-GARCH × Normal, Student-t, Skewed-t (9 specifications)
- HAR-RV model (Corsi, 2009)
- Out-of-sample forecast evaluation with Diebold-Mariano tests
- India VIX spillover analysis (Granger causality, VAR, predictive regressions)
- Robustness checks (sub-sample, alternative windows/orders, bootstrap, alignment)
- Paper draft (Sections 1–7 + references)

### Not Yet Done
- NRB 91-day T-bill rate (for excess returns / Sharpe ratios)
- Copula dependence analysis
- Final paper formatting and submission

## Key Interpretation Notes

GJR-GARCH(1,1)-SkewT has the lowest AIC (11,327.8) among all 9 GARCH specifications. However, the error distribution choice (Skewed-t vs Normal) matters approximately 20× more than the variance specification choice (GARCH vs EGARCH vs GJR) — an important finding for frontier market practitioners.

The most significant empirical result is that range-based estimators (Parkinson, Garman-Klass) significantly outperform all GARCH models in out-of-sample forecasting. This suggests that for NEPSE, the information content of intraday price extremes (OHLC) is more valuable than parametric volatility dynamics estimated from close prices alone.

India VIX cannot serve as a forward-looking implied volatility proxy for NEPSE (Granger causality p = 0.97). Return spillover exists from NIFTY to NEPSE at lag ≥ 2, but this does not translate into volatility spillover.
