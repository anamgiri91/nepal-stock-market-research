# NEPSE Frontier-Market Volatility Research Project

## Working Title

**Can volatility estimation methods developed for options-rich markets be adapted for frontier markets without derivatives? Evidence from NEPSE.**

## Abstract

This project studies whether volatility estimation methods originally designed for options-rich markets can be adapted for a frontier market without listed derivatives. The empirical case is the Nepal Stock Exchange (NEPSE), using daily index data from 2015-01-01 through 2026-06-03. Because NEPSE does not have a liquid options market or a VVIX-style benchmark, the project constructs realized volatility-of-volatility benchmarks and compares historical, hybrid-adapted, and GARCH-family model-based estimates.

## Core Idea

Options-rich markets can use implied-volatility and option-based volatility-of-volatility measures. NEPSE does not have a liquid derivatives/options market, so this project tests whether those methods can be adapted using realized volatility and GARCH-family proxies.

## Research Question

Can volatility and volatility-of-volatility methods developed for derivatives-rich markets be meaningfully adapted to a frontier equity market without listed options?

## Main Contribution

The key methodological contribution is the **MIVV-adapted** approach: replacing option-implied volatility with GARCH conditional volatility as a proxy for latent implied volatility in a no-derivatives market.

## Data

Current local NEPSE dataset:

- File: `nepse_index_2015-01-01_to_2026-06-03.csv`
- Date range: 2015-01-01 to 2026-06-03
- Scraped rows: 2,596 observations
- Columns: `date_ad`, `index_value`, `absolute_change`, `percentage_change`

The original research plan expected 2,598 records. The current scraper returned 2,596 records through 2026-06-03, so the notebooks report the observed count directly and keep the data audit transparent.

Planned comparison datasets:

- India's NIFTY VIX
- S&P 500 VIX
- Nepal Rastra Bank T-bill rates

These are not required for the core NEPSE volatility models, but they are needed for the spillover and risk-free-rate sections.

## Methodology

The project adapts Yuan-style volatility-of-volatility methods as follows:

| Method | Original setting | NEPSE adaptation |
|---|---|---|
| STVV | Historical volatility dynamics | Directly computed from NEPSE returns |
| EMVV | Uses VIX log-return inputs | Replaces VIX input with NEPSE realized-volatility changes |
| MIVV | Uses option-implied volatility | Replaces implied volatility with GARCH conditional volatility |
| RNVV | Requires options data | Replaced by GARCH, EGARCH, and GJR-GARCH model-based estimates |

Primary benchmark:

`Realized volatility-of-volatility = rolling variance of 30-day realized volatility`

Evaluation metrics:

- MAE
- MSE
- MAPE
- WMAPE
- Spearman correlation
- Low, medium, and high volatility-regime comparisons

## Notebook Roadmap

1. `01_data_cleaning_nepse.ipynb` - clean NEPSE index data, audit duplicates and missing trading days.
2. `02_descriptive_analysis.ipynb` - returns, summary statistics, ARCH test, event-period charts.
3. `03_garch_models.ipynb` - GARCH(1,1), EGARCH(1,1), and GJR-GARCH(1,1).
4. `04_volatility_of_volatility_methods.ipynb` - STVV, EMVV-adapted, MIVV-adapted, and realized VoV benchmark.
5. `05_benchmark_comparison.ipynb` - MAE, MSE, MAPE, WMAPE, Spearman correlation, volatility regimes.
6. `06_spillover_analysis.ipynb` - NIFTY VIX / VIX integration and Granger causality template.
7. `07_robustness_checks.ipynb` - rolling-window, pre/post-COVID, and distributional robustness.

## Repository Layout

```text
.
├── README.md
├── README_research_project.md
├── nepse_index_2015-01-01_to_2026-06-03.csv
├── data_nepse_cleaned.csv
├── data_nepse_returns.csv
├── data_garch_volatility_estimates.csv
├── data_vov_methods.csv
├── table_garch_model_selection.csv
├── table_method_comparison.csv
├── table_method_comparison_by_regime.csv
├── 02_descriptive_analysis.png
├── nepse_volatility_analysis.png
├── notebooks/
│   ├── 01_data_cleaning_nepse.ipynb
│   ├── 02_descriptive_analysis.ipynb
│   ├── 03_garch_models.ipynb
│   ├── 04_volatility_of_volatility_methods.ipynb
│   ├── 05_benchmark_comparison.ipynb
│   ├── 06_spillover_analysis.ipynb
│   └── 07_robustness_checks.ipynb
└── scrape_nepse_indices.py
```

## Reproducibility

Recommended Python packages:

```bash
pip install pandas numpy matplotlib scipy statsmodels arch nbformat nbclient ipykernel
```

To refresh the NEPSE dataset:

```bash
python scrape_nepse_indices.py --start 2015-01-01 --end 2026-06-03
```

To rerun the notebooks, open them in Jupyter and execute in numerical order from `01` to `07`.

## Research Status

Completed:

- NEPSE daily index dataset through 2026-06-03
- Data cleaning and audit notebook
- Descriptive statistics and ARCH-effect test
- GARCH, EGARCH, and GJR-GARCH model estimation
- Adapted volatility-of-volatility methods
- Benchmark comparison tables
- Robustness and spillover-analysis notebook templates

Next steps:

- Add NIFTY VIX, S&P 500 VIX, and NRB T-bill datasets
- Complete spillover analysis and Granger causality tests
- Add copula dependence analysis
- Write the literature review and final empirical paper
