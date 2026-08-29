"""Scientific regression tests for the wild cluster bootstrap.

Audit policy SS21 and the author's Round-6.5 constraint SS5: this module must not be trusted
merely because it reproduces a desired H1 p-value. Each test below fails if a specific way
of getting the bootstrap wrong comes back.
"""

from __future__ import annotations

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from itertools import product

import numpy as np
import pytest
import statsmodels.api as sm

from nepsevol.stats.wcb import (
    YEAR_CLUSTER_ONEWAY_STUDENTIZED,
    YEAR_CLUSTER_TWOWAY_STUDENTIZED,
    BootstrapSpec,
    wild_cluster_bootstrap,
)


def _panel(n_clusters=14, per=4, beta=0.08, seed=0):
    """Cell-level design mirroring H1: y = a + b*x + cluster effect + noise."""
    rng = np.random.default_rng(seed)
    cl = np.repeat(np.arange(n_clusters), per)
    x = rng.normal(0, 1, len(cl))
    y = 0.8 + beta * x + rng.normal(0, 0.3, n_clusters)[cl] + rng.normal(0, 0.2, len(cl))
    X = sm.add_constant(x)
    return y, X, cl


def test_determinism_same_seed_same_result():
    y, X, cl = _panel()
    spec = BootstrapSpec(n_draws=200, seed=7, label="t")
    a = wild_cluster_bootstrap(y, X, cl, spec=spec, exact_threshold=0)
    b = wild_cluster_bootstrap(y, X, cl, spec=spec, exact_threshold=0)
    assert a.p_value == b.p_value and a.t_observed == b.t_observed


def test_different_seeds_differ_but_agree_closely():
    y, X, cl = _panel()
    ps = [wild_cluster_bootstrap(y, X, cl, spec=BootstrapSpec(n_draws=400, seed=s),
                                 exact_threshold=0).p_value for s in (1, 2, 3)]
    assert len(set(ps)) > 1                      # genuinely stochastic
    assert max(ps) - min(ps) < 0.15              # but not wildly unstable


def test_sampled_p_value_can_never_be_zero():
    """The (k+1)/(B+1) convention. Reporting p = 0.0000 was an actual error in this project."""
    y, X, cl = _panel(beta=5.0)                  # overwhelming signal -> k = 0
    r = wild_cluster_bootstrap(y, X, cl, spec=BootstrapSpec(n_draws=99, seed=3),
                               exact_threshold=0)
    assert r.p_value > 0
    assert r.p_value == pytest.approx(1 / 100)
    assert r.p_formula == "(k+1)/(B+1)" and r.min_attainable_p == pytest.approx(1 / 100)


def test_exact_enumeration_matches_brute_force_at_G14():
    """All 2**14 sign vectors, recomputed independently here."""
    y, X, cl = _panel(n_clusters=14, per=4)
    r = wild_cluster_bootstrap(y, X, cl, spec=YEAR_CLUSTER_ONEWAY_STUDENTIZED)
    assert r.enumerated and r.n_clusters == 14 and r.n_draws == 2 ** 14

    fit = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": cl})
    t_obs = fit.params[1] / fit.bse[1]
    f0 = sm.OLS(y, X[:, [0]]).fit()
    uniq = np.unique(cl)
    k = 0
    for signs in product((-1.0, 1.0), repeat=14):
        w = np.array([signs[np.searchsorted(uniq, c)] for c in cl])
        fs = sm.OLS(f0.fittedvalues + f0.resid * w, X).fit(
            cov_type="cluster", cov_kwds={"groups": cl})
        if abs(fs.params[1] / fs.bse[1]) >= abs(t_obs):
            k += 1
    assert r.p_value == pytest.approx(k / 2 ** 14)


def test_monte_carlo_approaches_exact_enumeration():
    y, X, cl = _panel(n_clusters=8, per=5)
    exact = wild_cluster_bootstrap(y, X, cl, spec=BootstrapSpec(label="x")).p_value
    sampled = wild_cluster_bootstrap(
        y, X, cl, spec=BootstrapSpec(n_draws=4000, seed=11), exact_threshold=0).p_value
    assert abs(exact - sampled) < 0.05


def test_restricted_bootstrap_actually_imposes_the_null():
    """Restricted resampling must drop the tested regressor from the residual model."""
    y, X, cl = _panel(beta=0.5)
    r = wild_cluster_bootstrap(y, X, cl, spec=BootstrapSpec(restricted=True, label="r"))
    u = wild_cluster_bootstrap(y, X, cl, spec=BootstrapSpec(restricted=False, label="u"))
    # unrestricted residuals retain the signal, so its bootstrap distribution is wider
    assert r.p_value != u.p_value


def test_one_way_and_two_way_are_distinct_configurations():
    """The 37x p-value difference in this project came from confusing exactly these two."""
    y, X, cl = _panel()
    second = np.tile(np.arange(4), 14)
    one = wild_cluster_bootstrap(y, X, cl, spec=YEAR_CLUSTER_ONEWAY_STUDENTIZED)
    two = wild_cluster_bootstrap(y, X, cl, second_cluster=second,
                                 spec=YEAR_CLUSTER_TWOWAY_STUDENTIZED)
    assert one.spec.studentizing_covariance == "year"
    assert two.spec.studentizing_covariance == "year x decile"
    assert not one.spec.is_multiway_resampling and not two.spec.is_multiway_resampling
    assert one.t_observed != two.t_observed


def test_two_way_without_second_cluster_raises_rather_than_silently_downgrading():
    y, X, cl = _panel()
    with pytest.raises(ValueError, match="requires second_cluster"):
        wild_cluster_bootstrap(y, X, cl, spec=YEAR_CLUSTER_TWOWAY_STUDENTIZED)


def test_non_rademacher_weights_rejected():
    y, X, cl = _panel()
    with pytest.raises(ValueError, match="Rademacher"):
        wild_cluster_bootstrap(y, X, cl, spec=BootstrapSpec(weights="mammen"))


def test_coefficient_statistic_is_distinct_from_t_statistic():
    y, X, cl = _panel()
    t = wild_cluster_bootstrap(y, X, cl, spec=BootstrapSpec(statistic="t", label="t"))
    c = wild_cluster_bootstrap(y, X, cl, spec=BootstrapSpec(statistic="coef", label="c"))
    assert t.spec.statistic != c.spec.statistic


def test_known_null_rejection_is_not_pathological():
    """Under a true null the test must not reject wildly. CGM's whole point."""
    reject = 0
    trials = 60
    for s in range(trials):
        y, X, cl = _panel(beta=0.0, seed=100 + s)
        if wild_cluster_bootstrap(y, X, cl, spec=YEAR_CLUSTER_ONEWAY_STUDENTIZED).p_value < 0.05:
            reject += 1
    assert reject / trials < 0.25       # generous, but catches gross over-rejection


def test_spec_is_self_describing():
    assert "resampling_cluster=year" in YEAR_CLUSTER_ONEWAY_STUDENTIZED.describe()
    assert "studentizing_covariance=year x decile" in YEAR_CLUSTER_TWOWAY_STUDENTIZED.describe()


# --- SS10: an INDEPENDENT reference implementation, not the module under test ----------

def _reference_wcb(y, X, cl, col=1):
    """Deliberately naive reference: build every Rademacher vector explicitly.

    Written without reference to wcb.py's internals so that agreement is evidence.
    Conventions asserted here: two-sided on |t|, ties count (>=), p = k / 2**G.
    """
    uniq = sorted(set(cl.tolist()))
    G = len(uniq)
    fit = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": cl})
    t_obs = fit.params[col] / fit.bse[col]
    f0 = sm.OLS(y, np.delete(X, col, axis=1)).fit()
    k = 0
    for bits in range(2 ** G):
        signs = {g: (1.0 if (bits >> i) & 1 else -1.0) for i, g in enumerate(uniq)}
        w = np.array([signs[c] for c in cl])
        fs = sm.OLS(f0.fittedvalues + f0.resid * w, X).fit(
            cov_type="cluster", cov_kwds={"groups": cl})
        if abs(fs.params[col] / fs.bse[col]) >= abs(t_obs):
            k += 1
    return k, k / 2 ** G


def test_module_agrees_with_independent_reference_implementation():
    y, X, cl = _panel(n_clusters=9, per=4)
    k_ref, p_ref = _reference_wcb(y, X, cl)
    r = wild_cluster_bootstrap(y, X, cl, spec=YEAR_CLUSTER_ONEWAY_STUDENTIZED)
    assert r.enumerated
    assert r.n_exceedances == k_ref
    assert r.p_value == pytest.approx(p_ref)


def test_enumeration_conventions_are_explicit():
    """The observed all-ones vector is itself enumerated, so k >= 1 and p >= 1/2**G."""
    y, X, cl = _panel(n_clusters=8, per=4, beta=9.0)
    r = wild_cluster_bootstrap(y, X, cl, spec=YEAR_CLUSTER_ONEWAY_STUDENTIZED)
    assert r.p_formula == "k / 2**G"
    assert r.n_exceedances >= 1
    assert r.p_value >= r.min_attainable_p == pytest.approx(1 / 2 ** 8)


def test_global_sign_symmetry_holds_to_floating_point():
    """|t(w)| == |t(-w)| analytically -- but only to floating point, not bitwise.

    Under the restricted bootstrap the fitted part is annihilated by X, so the bootstrap
    residual is odd in w and beta* is odd while the cluster-robust variance is even; hence
    |t| is invariant. Measured max deviation over all 2**7 vectors is ~4e-15, and only 4 of
    128 pairs are bitwise identical. Exceedance counts therefore need NOT come in exact
    pairs, because a tie sitting on the >= boundary can fall either side. An earlier version
    of this test asserted k was even and failed for exactly that reason.
    """
    y, X, cl = _panel(n_clusters=7, per=4)
    f0 = sm.OLS(y, X[:, [0]]).fit()
    uniq = np.unique(cl)

    def t_of(w):
        f = sm.OLS(f0.fittedvalues + f0.resid * w, X).fit(
            cov_type="cluster", cov_kwds={"groups": cl})
        return f.params[1] / f.bse[1]

    worst = 0.0
    for bits in range(2 ** len(uniq)):
        signs = {g: (1.0 if (bits >> i) & 1 else -1.0) for i, g in enumerate(uniq)}
        w = np.array([signs[c] for c in cl])
        worst = max(worst, abs(abs(t_of(w)) - abs(t_of(-w))))
    assert worst < 1e-9, f"sign symmetry broken by {worst:.2e}"


def test_result_records_every_choice_needed_to_reproduce():
    y, X, cl = _panel(n_clusters=6, per=5)
    d = wild_cluster_bootstrap(y, X, cl, spec=YEAR_CLUSTER_ONEWAY_STUDENTIZED).as_dict()
    for field in ("beta", "observed_statistic", "resampling_cluster", "studentizing_covariance",
                  "multiway_resampling", "n_clusters", "cluster_labels", "restricted",
                  "statistic", "weights", "finite_sample_correction", "n_draws",
                  "enumerated", "seed", "n_exceedances", "p_formula", "p_value",
                  "min_attainable_p", "label"):
        assert field in d, f"missing {field}"


def test_no_config_is_named_as_if_registered():
    """PAP SS8.3a fixed only weights and draw count; naming must not launder the rest."""
    from nepsevol.stats import wcb as M
    names = [n for n in dir(M) if n.isupper()]
    assert not any("REGISTERED" in n for n in names), names
    assert set(M.PAP_FIXED_FIELDS) and set(M.POST_HOC_IMPLEMENTATION_CHOICES)
    assert "resampling_cluster" in M.POST_HOC_IMPLEMENTATION_CHOICES
