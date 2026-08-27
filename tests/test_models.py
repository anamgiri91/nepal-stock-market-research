"""Tests for the modelling and evaluation modules.

These existed untested until now, which was a real risk: four separate bugs were found in them
by inspection rather than by test (a Jensen-constant omission that produced a spurious 1.74x
bias, correlated measurement errors collapsing the state persistence, a HAR retransform that
inflated forecasts ~11x, and a constant-forecast regression that returned one parameter).
Each of those failure modes is now pinned by a test.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pandas as pd
import pytest

from nepsevol.models import forecast as F
from nepsevol.models.statespace import log_transform_constants
from nepsevol.evaluation import microstructure as ms
from nepsevol.clean.limits import flag_limits, regime_for
from nepsevol.estimators import range_ as R


# ── forecast evaluation ────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def proxy_setup():
    rng = np.random.default_rng(7)
    n = 3000
    phi, se, mu = 0.97, 0.25, 2 * np.log(0.015)
    h = np.empty(n); h[0] = mu
    for t in range(1, n):
        h[t] = mu + phi * (h[t - 1] - mu) + rng.normal(0, se)
    true_var = np.exp(h)
    proxy = rng.normal(0, np.sqrt(true_var)) ** 2
    return true_var, proxy, rng


def test_qlike_ranks_a_known_ordering(proxy_setup):
    """The whole method rests on this: a noisy but unbiased proxy must still rank forecasts."""
    tv, proxy, rng = proxy_setup
    oracle = F.qlike(proxy, tv).mean()
    noisy = F.qlike(proxy, tv * np.exp(rng.normal(0, 0.4, len(tv)))).mean()
    const = F.qlike(proxy, np.full(len(tv), tv.mean())).mean()
    assert oracle < noisy < const


def test_mz_slope_detects_scale_bias_where_r2_cannot(proxy_setup):
    """R^2 is invariant to scaling, so only the MZ slope can see a biased forecast."""
    tv, proxy, _ = proxy_setup
    good = F.mincer_zarnowitz(pd.Series(proxy), pd.Series(tv))
    biased = F.mincer_zarnowitz(pd.Series(proxy), pd.Series(tv * 0.6))
    assert good["R2"] == pytest.approx(biased["R2"], rel=1e-6)   # R^2 blind to the bias
    assert biased["b"] > good["b"] * 1.4                          # slope is not


def test_mz_handles_a_constant_forecast(proxy_setup):
    """A constant regressor has no slope to identify; add_constant would silently return a
    one-parameter fit and raise IndexError. Must degrade gracefully instead."""
    _, proxy, _ = proxy_setup
    out = F.mincer_zarnowitz(pd.Series(proxy), pd.Series(np.full(len(proxy), 1e-4)))
    assert np.isnan(out["b"]) and out["R2"] == 0.0 and out["n"] > 0


def test_diebold_mariano_sign_convention(proxy_setup):
    """Negative statistic must mean the FIRST argument is better."""
    tv, proxy, rng = proxy_setup
    better = F.qlike(proxy, tv)
    worse = F.qlike(proxy, tv * np.exp(rng.normal(0, 0.6, len(tv))))
    assert F.diebold_mariano(better, worse)["DM"] < 0


def test_mcs_eliminates_worst_first(proxy_setup):
    tv, proxy, rng = proxy_setup
    L = pd.DataFrame({
        "oracle": F.qlike(proxy, tv),
        "noisy": F.qlike(proxy, tv * np.exp(rng.normal(0, 0.5, len(tv)))),
        "constant": F.qlike(proxy, np.full(len(tv), tv.mean())),
    })
    out = F.model_confidence_set(L, alpha=0.10, n_boot=300, seed=1)
    assert out["eliminated"] and out["eliminated"][0][0] == "constant"
    assert "oracle" in out["mcs"]


def test_har_forecasts_the_measure_not_log_squared_returns():
    """Targeting log(r^2) gives residual variance ~pi^2/2, so the lognormal retransform
    exp(.+s^2/2) inflates every forecast by roughly 11x. Guard against regressing to that."""
    rng = np.random.default_rng(3)
    rv = pd.Series(np.exp(rng.normal(np.log(4e-4), 0.4, 1200)))
    _, pred, _ = F.fit_har(rv, target=None, split=0.7)
    assert 0.3 < pred.mean() / rv.mean() < 3.0


# ── Jensen constants ───────────────────────────────────────────────────────────
def test_close_to_close_jensen_constant_matches_theory():
    """E[log chi^2_1] = -gamma - log 2. If this drifts, every state-space bias estimate is wrong."""
    est = {"cc": lambda d: np.log(d.close / d.open) ** 2}
    c = log_transform_constants(est, n_days=40_000)
    assert c["cc"] == pytest.approx(-0.5772156649 - np.log(2), abs=0.02)


def test_range_jensen_constant_is_far_smaller_than_close_to_close():
    """The whole trap: the two constants differ by ~1 log-variance unit, which masquerades
    as estimator bias if not removed."""
    est = {"cc": lambda d: np.log(d.close / d.open) ** 2, "pk": R.parkinson}
    c = log_transform_constants(est, n_days=40_000)
    assert abs(c["cc"]) > 4 * abs(c["pk"])


# ── microstructure ─────────────────────────────────────────────────────────────
def test_roll_recovers_a_known_spread():
    rng = np.random.default_rng(0)
    n, s_true = 4000, 0.01
    p = np.cumsum(rng.normal(0, 0.02, n)) + rng.choice([-1, 1], n) * s_true / 2
    assert ms.roll_spread(pd.Series(np.diff(p))) == pytest.approx(s_true, rel=0.15)


def test_roll_undefined_when_autocovariance_positive():
    """Roll is missing precisely where bounce does NOT dominate, which is why it must not be
    the primary noise proxy: conditioning on it selects on the hypothesis."""
    # Returns with POSITIVE serial correlation (partial adjustment / momentum). A trend plus
    # iid noise will not do: differencing iid noise induces NEGATIVE autocovariance, so Roll is
    # legitimately defined there.
    rng = np.random.default_rng(1)
    n = 2000
    r = np.zeros(n)
    for t in range(1, n):
        r[t] = 0.4 * r[t - 1] + rng.normal(0, 0.01)
    assert np.isnan(ms.roll_spread(pd.Series(r)))


def test_variance_ratio_below_one_under_bounce():
    rng = np.random.default_rng(5)
    n = 4000
    p = np.cumsum(rng.normal(0, 0.02, n)) + rng.choice([-1, 1], n) * 0.005
    assert ms.variance_ratio(pd.Series(np.diff(p)), q=5) < 1.0


# ── price-limit detection ──────────────────────────────────────────────────────
def test_regime_switches_at_april_2026():
    r = regime_for(pd.Series(pd.to_datetime(["2025-06-01", "2026-06-01"])))
    assert r.loc[0, "band"] == 0.02 and r.loc[0, "limit"] == 0.10
    assert r.loc[1, "band"] == 0.05 and r.loc[1, "limit"] == 0.15


def test_flag_limits_detects_a_binding_limit_and_a_pinned_open():
    df = pd.DataFrame({
        "symbol": ["A"] * 3,
        "date": pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"]),
        "open": [100.0, 102.0, 100.0],     # day 2 opens at exactly +2% (band)
        "high": [100.0, 110.0, 100.0],     # day 2 high at exactly +10% (limit)
        "low":  [100.0, 101.0, 100.0],
        "close": [100.0, 110.0, 100.0],
    })
    f = flag_limits(df)
    assert bool(f.iloc[1]["open_pinned"])
    assert bool(f.iloc[1]["high_limited"])
    assert bool(f.iloc[1]["range_censored"])
    assert not bool(f.iloc[2]["high_limited"])


def test_open_at_prev_close_flags_the_no_match_rule():
    df = pd.DataFrame({
        "symbol": ["A", "A"], "date": pd.to_datetime(["2025-01-01", "2025-01-02"]),
        "open": [50.0, 50.0], "high": [50.0, 51.0], "low": [50.0, 49.0], "close": [50.0, 50.5],
    })
    assert bool(flag_limits(df).iloc[1]["open_at_prev_close"])


# ── censored opening returns ───────────────────────────────────────────────────
def test_tobit_recovers_known_sigma_under_heavy_censoring():
    """The whole point: the censoring POINT is known, so latent sigma is identified even when
    most observations are pinned. At 57% censoring the naive sd understates by more than half."""
    from nepsevol.models.censored import tobit_sigma
    rng = np.random.default_rng(11)
    true_s, band = 0.035, 0.02
    obs = np.clip(rng.normal(0, true_s, 30_000), -band, band)
    out = tobit_sigma(obs, band=band, tol=1e-6)
    assert out["censored_share"] > 0.5
    assert out["sigma_naive"] < true_s * 0.6            # naive badly understates
    assert out["sigma_latent"] == pytest.approx(true_s, rel=0.05)


def test_tobit_is_harmless_when_censoring_is_light():
    """A correction that distorts uncensored data would be worse than none."""
    from nepsevol.models.censored import tobit_sigma
    rng = np.random.default_rng(3)
    true_s, band = 0.004, 0.02
    obs = np.clip(rng.normal(0, true_s, 20_000), -band, band)
    out = tobit_sigma(obs, band=band, tol=1e-6)
    assert out["censored_share"] < 0.01
    assert out["sigma_latent"] == pytest.approx(true_s, rel=0.05)
    assert out["inflation"] == pytest.approx(1.0, abs=0.05)


def test_tobit_excludes_no_match_zeros_by_default():
    """An exact-zero open means the auction found no counterparty, not a truncated price move.
    Counting those as interior zeros drags sigma down."""
    from nepsevol.models.censored import tobit_sigma
    rng = np.random.default_rng(5)
    r = np.clip(rng.normal(0, 0.02, 8000), -0.02, 0.02)
    padded = np.concatenate([r, np.zeros(4000)])          # 33% spurious no-match zeros
    kept = tobit_sigma(padded, band=0.02, tol=1e-6, drop_exact_zero=True)
    counted = tobit_sigma(padded, band=0.02, tol=1e-6, drop_exact_zero=False)
    assert counted["sigma_latent"] < kept["sigma_latent"] * 0.85


def test_analytic_censoring_inflation_matches_simulation():
    from nepsevol.models.censored import censoring_inflation
    rng = np.random.default_rng(7)
    true_s, band = 0.03, 0.02
    obs = np.clip(rng.normal(0, true_s, 200_000), -band, band)
    assert censoring_inflation(true_s, band) == pytest.approx(obs.std() / true_s, rel=0.02)
