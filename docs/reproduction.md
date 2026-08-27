# Reproduction

## Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Python 3.14 verified working; all pinned packages have `cp314` arm64 wheels.

## Pipeline

Scripts run in numerical order from a clean state:

```bash
for s in scripts/[0-9]*.py; do python "$s"; done
```

| Script | Produces |
|---|---|
| `00_fetch_data.py` | `data/raw/` from source |
| `01_build_calendar.py` | NEPSE trading calendar, holidays, closure spans |
| `02_build_panel.py` | stock panels in `data/processed/` |
| `03_descriptive.py` | trading-intensity and pathology exhibits |
| `04_bias_curve.py` | simulated bias curve and the crossover N\* |
| `05_validate_real.py` | observed-vs-predicted bias in the real cross-section |
| `06_friction_decomposition.py` | the three-friction decomposition |
| `07_microstructure.py` | spread/bounce estimates; identification of the upward friction |
| `08_timeseries_diagnostics.py` | ACF, calendar effects, GARCH viability |

Nothing in `data/interim/`, `data/processed/`, or `output/` is authoritative. All of it is
regenerable, and if it is not, the pipeline is broken.

## Exploratory notebook

```bash
./.venv/bin/jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.kernel_name=nepsevol \
  notebooks/01_exploratory_analysis.ipynb
```

Register the kernel once with:

```bash
./.venv/bin/python -m ipykernel install --user --name nepsevol --display-name "nepsevol (.venv)"
```

## Tests

```bash
pytest
```

Estimators are checked against known answers — closed forms, simulated series with known
volatility, or published worked examples.

## Verifying inputs

```bash
shasum -a 256 -c MANIFEST.sha256
```
