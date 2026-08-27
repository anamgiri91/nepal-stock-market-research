"""Estimators are validated against a case with a KNOWN answer.

With a densely-observed path (high n_trades), every estimator must recover the
true sigma. If these fail, nothing downstream is trustworthy.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pytest
from nepsevol.estimators import range_ as R
from nepsevol.estimators.simulate import simulate_ohlc

TRUE_SIGMA = 0.02
DENSE = 2000


@pytest.fixture(scope="module")
def dense():
    return simulate_ohlc(n_days=8000, sigma_daily=TRUE_SIGMA, n_trades=DENSE, seed=42)


@pytest.mark.parametrize("name,fn,tol", [
    ("close_to_close", R.close_to_close, 0.05),
    ("parkinson",      R.parkinson,      0.03),
    ("garman_klass",   R.garman_klass,   0.03),
    ("rogers_satchell",R.rogers_satchell,0.03),
])
def test_recovers_true_sigma(dense, name, fn, tol):
    """Densely observed -> unbiased. This is the textbook claim being checked."""
    sigma_hat = np.sqrt(np.nanmean(fn(dense)))
    rel = abs(sigma_hat - TRUE_SIGMA) / TRUE_SIGMA
    assert rel < tol, f"{name}: sigma_hat={sigma_hat:.5f} true={TRUE_SIGMA} rel_err={rel:.3%}"


def test_parkinson_zero_when_no_range():
    """H == L (a real occurrence on 5% of NEPSE stock-days) -> Parkinson is exactly 0."""
    import pandas as pd
    df = pd.DataFrame({"open": [100., 100.], "high": [100., 100.],
                       "low": [100., 100.], "close": [100., 100.]})
    assert float(R.parkinson(df).iloc[-1]) == 0.0


def test_range_estimators_more_efficient_when_dense(dense):
    """The textbook efficiency claim: range estimators have lower sampling variance
    than close-to-close WHEN the path is densely observed."""
    cc = R.close_to_close(dense).dropna()
    pk = R.parkinson(dense).dropna()
    assert pk.var() < cc.var(), "Parkinson should be more efficient than CC under dense sampling"


def test_discretisation_bias_is_downward():
    """The paper's core mechanism: sparse observation biases the range DOWNWARD."""
    sparse = simulate_ohlc(n_days=8000, sigma_daily=TRUE_SIGMA, n_trades=10, seed=7)
    sigma_sparse = np.sqrt(np.nanmean(R.parkinson(sparse)))
    assert sigma_sparse < TRUE_SIGMA * 0.9, f"expected downward bias, got {sigma_sparse:.5f}"


def test_close_to_close_survives_sparsity():
    """Close-to-close uses only closes, so it should be ~unaffected by trade count."""
    sparse = simulate_ohlc(n_days=8000, sigma_daily=TRUE_SIGMA, n_trades=10, seed=7)
    sigma_cc = np.sqrt(np.nanmean(R.close_to_close(sparse)))
    assert abs(sigma_cc - TRUE_SIGMA) / TRUE_SIGMA < 0.05
