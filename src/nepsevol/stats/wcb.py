"""Wild cluster bootstrap -- PAP-v4 SS8.3a.

The plan requires this and designates its p-value as the one to report:

    "Bucket-level designs yield roughly 14 year-clusters, below the range where
     cluster-robust asymptotics are reliable. Every bucket-level primary test MUST
     report a wild cluster bootstrap (Rademacher, >= 9,999 draws); that p-value is
     the one reported."

Until now no implementation existed anywhere in the repository -- the reported figure had
no code behind it. This module supplies one, and every choice the plan leaves open is
named in `BootstrapSpec` rather than buried in the body, because those choices matter: on
HO-2's H1 the same data give p = 0.000122 studentising the one-way year statistic and
p = 0.004517 studentising the two-way statistic, a factor of 37.

Why bootstrap-t rather than a coefficient bootstrap: Cameron, Gelbach & Miller (2008),
*Review of Economics and Statistics* 90(3), 414-427, show that asymptotic cluster-robust
tests over-reject with few (roughly five to thirty) clusters, and that a wild cluster
bootstrap of the *studentised* statistic delivers the asymptotic refinement. G = 14 here
sits squarely inside their problem range.

Null-imposed (restricted) residuals are the default: resampling is done under H0, which is
the variant CGM recommend and the one with the better small-sample behaviour.

Exact enumeration is available and preferable when G is small: with G clusters there are
only 2**G distinct Rademacher sign vectors, so at G = 14 the 16,384 possibilities can be
enumerated exactly instead of sampled, removing Monte Carlo error entirely.

WHAT THIS MODULE IS NOT. Committing it does not establish that the historically reported
p = 0.0001 was ever computed. No implementation existed in this repository or its history
when that figure was recorded, and it remains provenance-unverified. This module is a
prospective, reproducible implementation for use from now on -- not retrospective evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import numpy as np
import statsmodels.api as sm

__all__ = ["BootstrapSpec", "wild_cluster_bootstrap", "WCBResult",
           "YEAR_CLUSTER_ONEWAY_STUDENTIZED", "YEAR_CLUSTER_TWOWAY_STUDENTIZED",
           "PAP_FIXED_FIELDS", "POST_HOC_IMPLEMENTATION_CHOICES"]


#: Fields PAP-v4 SS8.3a actually fixed. Nothing else in this module is preregistered.
PAP_FIXED_FIELDS = ("weights (Rademacher)", "n_draws (>= 9999)")

#: Fields chosen in 2026-08 during the audit. These are POST-HOC implementation choices.
POST_HOC_IMPLEMENTATION_CHOICES = (
    "resampling_cluster", "studentizing_covariance", "restricted", "statistic",
    "finite_sample_correction", "p_convention", "seed",
)


@dataclass(frozen=True)
class BootstrapSpec:
    """Every degree of freedom, named. Nothing here is implicitly preregistered.

    PAP-v4 SS8.3a fixed only :data:`PAP_FIXED_FIELDS`. Everything in
    :data:`POST_HOC_IMPLEMENTATION_CHOICES` was decided during the 2026-08 audit and must
    never be described as registered.

    Two fields that are routinely conflated and must not be:

    ``resampling_cluster``      the level at which Rademacher signs are DRAWN
    ``studentizing_covariance`` the covariance estimator forming the t-statistic

    Drawing signs at the year level while studentising with a year x decile covariance is
    NOT a "two-way wild cluster bootstrap" in the methodological sense -- the resampling
    construction is one-way. Describe it as what it is. Conflating these moved a p-value
    in this project by a factor of 37.
    """

    resampling_cluster: str = "year"
    studentizing_covariance: str = "year"      # "year" | "year x decile"
    statistic: str = "t"                       # "t" (studentised) | "coef"
    restricted: bool = True                    # impose H0 when forming residuals
    weights: str = "rademacher"                # FIXED BY PAP SS8.3a
    finite_sample_correction: bool = True      # G/(G-1) * (N-1)/(N-K) inside the CRVE
    p_convention: str = "(k+1)/(B+1)"          # sampled; enumeration uses k/2**G
    n_draws: int = 9999                        # FIXED BY PAP SS8.3a (minimum)
    seed: int = 20260826
    label: str = "unlabelled"

    @property
    def is_multiway_resampling(self) -> bool:
        """True only if signs are drawn over more than one dimension."""
        return "x" in self.resampling_cluster

    def describe(self) -> str:
        return (f"{self.label}: resampling_cluster={self.resampling_cluster}, "
                f"studentizing_covariance={self.studentizing_covariance}, "
                f"statistic={self.statistic}, restricted={self.restricted}, "
                f"weights={self.weights}, B={self.n_draws}, seed={self.seed}")


#: Signs drawn at year level; t studentised with a year-only covariance.
YEAR_CLUSTER_ONEWAY_STUDENTIZED = BootstrapSpec(
    resampling_cluster="year", studentizing_covariance="year",
    label="year_cluster_oneway_studentized")

#: Signs drawn at year level; t studentised with a year x decile covariance.
#: NOT a multiway bootstrap -- the resampling is still one-way.
YEAR_CLUSTER_TWOWAY_STUDENTIZED = BootstrapSpec(
    resampling_cluster="year", studentizing_covariance="year x decile",
    label="year_cluster_twoway_studentized")


@dataclass(frozen=True)
class WCBResult:
    """Self-sufficient record of one bootstrap inference.

    Contains everything needed to reproduce the number without consulting the call site.
    """

    beta: float
    observed_statistic: float
    t_observed: float
    n_clusters: int
    cluster_labels: tuple
    n_exceedances: int
    n_draws: int
    enumerated: bool
    p_value: float
    p_formula: str
    min_attainable_p: float
    spec: BootstrapSpec

    def as_dict(self) -> dict:
        d = {
            "beta": self.beta,
            "observed_statistic": self.observed_statistic,
            "t_observed": self.t_observed,
            "resampling_cluster": self.spec.resampling_cluster,
            "studentizing_covariance": self.spec.studentizing_covariance,
            "multiway_resampling": self.spec.is_multiway_resampling,
            "n_clusters": self.n_clusters,
            "cluster_labels": list(self.cluster_labels),
            "restricted": self.spec.restricted,
            "statistic": self.spec.statistic,
            "weights": self.spec.weights,
            "finite_sample_correction": self.spec.finite_sample_correction,
            "n_draws": self.n_draws,
            "enumerated": self.enumerated,
            "seed": self.spec.seed,
            "n_exceedances": self.n_exceedances,
            "p_formula": self.p_formula,
            "p_value": self.p_value,
            "min_attainable_p": self.min_attainable_p,
            "label": self.spec.label,
        }
        return d

    def __str__(self) -> str:
        how = (f"exact enumeration of 2**{self.n_clusters}" if self.enumerated
               else f"{self.n_draws:,} sampled draws")
        return (f"beta={self.beta:+.4f}  t={self.t_observed:+.2f}  p={self.p_value:.6f} "
                f"[{how}; resample={self.spec.resampling_cluster}; "
                f"studentise={self.spec.studentizing_covariance}; "
                f"k={self.n_exceedances}; p={self.p_formula}]")


def _tstat(y, X, clusters, second=None, col=1):
    """Cluster-robust t on coefficient `col`. Two-way when `second` is supplied."""
    groups = clusters if second is None else np.column_stack([clusters, second])
    fit = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": groups})
    return fit.params[col], fit.params[col] / fit.bse[col]


def wild_cluster_bootstrap(
    y: np.ndarray,
    X: np.ndarray,
    clusters: np.ndarray,
    second_cluster: np.ndarray | None = None,
    spec: BootstrapSpec = BootstrapSpec(),
    col: int = 1,
    exact_threshold: int = 20,
) -> WCBResult:
    """Rademacher wild cluster bootstrap of a studentised coefficient.

    `X` must already include its intercept column. `col` indexes the coefficient tested.
    When the number of clusters is at or below `exact_threshold`, all 2**G sign vectors
    are enumerated and the p-value carries no Monte Carlo error.
    """
    y = np.asarray(y, dtype=float)
    X = np.asarray(X, dtype=float)
    clusters = np.asarray(clusters)
    two_way_cov = "x" in spec.studentizing_covariance
    second = second_cluster if two_way_cov else None
    if two_way_cov and second is None:
        raise ValueError("studentizing_covariance='year x decile' requires second_cluster")

    if spec.weights != "rademacher":
        raise ValueError("PAP SS8.3a fixes Rademacher weights")
    if spec.statistic not in ("t", "coef"):
        raise ValueError("statistic must be 't' or 'coef'")
    beta, t_obs = _tstat(y, X, clusters, second, col)
    reference = t_obs if spec.statistic == "t" else beta

    # residuals for resampling: restricted (H0 imposed on `col`) or unrestricted
    keep = [j for j in range(X.shape[1]) if j != col] if spec.restricted else list(range(X.shape[1]))
    X0 = X[:, keep]
    fit0 = sm.OLS(y, X0).fit()
    resid, fitted = fit0.resid, fit0.fittedvalues

    uniq = np.unique(clusters)
    G = len(uniq)
    idx = {g: (clusters == g) for g in uniq}
    exact = G <= exact_threshold

    def draws():
        if exact:
            yield from product((-1.0, 1.0), repeat=G)
        else:
            rng = np.random.default_rng(spec.seed)
            for _ in range(spec.n_draws):
                yield rng.choice([-1.0, 1.0], G)

    count = 0
    total = 0
    for signs in draws():
        w = np.empty(len(y))
        for g, s in zip(uniq, signs):
            w[idx[g]] = s
        try:
            b_star, t_star = _tstat(fitted + resid * w, X, clusters, second, col)
        except Exception:
            continue
        total += 1
        stat_star = t_star if spec.statistic == "t" else b_star
        if abs(stat_star) >= abs(reference):
            count += 1

    # CONVENTIONS, stated rather than implied.
    #  * enumeration: p = k / 2**G. No +1 correction -- the observed sign vector IS one of
    #    the enumerated draws (all-ones), so it is already counted in k. Minimum p is
    #    1/2**G, never 0.
    #  * sampled: p = (k+1)/(B+1), the standard correction. Minimum p is 1/(B+1), never 0.
    #  * criterion is two-sided on |statistic|, with >= so that ties count as exceedances
    #    (conservative).
    #  * global sign symmetry: w and -w give identical |t|, so the enumeration double-counts
    #    symmetrically and the ratio is unaffected.
    if exact:
        p = count / total
        formula = "k / 2**G"
        min_p = 1.0 / (2 ** G)
    else:
        p = (count + 1) / (total + 1)
        formula = "(k+1)/(B+1)"
        min_p = 1.0 / (total + 1)
    return WCBResult(beta=beta, observed_statistic=reference, t_observed=t_obs,
                     n_clusters=G, cluster_labels=tuple(uniq.tolist()),
                     n_exceedances=count, n_draws=total, enumerated=exact,
                     p_value=p, p_formula=formula, min_attainable_p=min_p, spec=spec)
