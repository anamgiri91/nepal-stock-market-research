"""Recovering latent opening-return volatility from a banded call auction.

The problem. NEPSE's pre-open auction accepts orders only within a band of the previous close
(+/-2% through 2026-03, +/-5% after). When the latent clearing price lies outside the band the
auction clears AT the boundary, so the observed opening return is censored at a point that is
known exactly. This is not a nuisance: the opening return carries most of the daily variance in
thin securities, and 20.6% of stock-days are pinned at the boundary.

Every existing range-estimator correction addresses discretisation of the intraday high and low.
None addresses censoring of the open, because no other studied market bands its opening auction
this tightly. The censoring point being KNOWN is what makes the problem tractable: it is a
textbook two-sided Tobit, and the latent variance is identified by maximum likelihood from the
interior observations plus the censored mass.

Model. Latent opening return r* ~ N(mu, sigma^2). Observed:

    r = r*                if  lo < r* < hi   (interior; contributes the density)
    r = hi                if  r* >= hi        (right-censored; contributes 1 - Phi((hi-mu)/sigma))
    r = lo                if  r* <= lo        (left-censored;  contributes Phi((lo-mu)/sigma))

with lo = ln(1-band) and hi = ln(1+band). These are NOT symmetric: a +/-2% price band gives
+1.9803% and -2.0203% in log terms.

The no-match case (r exactly 0, the auction found no counterparty) is NOT censoring and is
excluded by default: it reflects absent order flow rather than a truncated price move, and
treating it as an interior zero biases sigma downward.
"""
from __future__ import annotations

import numpy as np
from scipy import optimize, stats

__all__ = ["tobit_sigma", "censoring_inflation", "log_bounds"]


def log_bounds(band: float) -> tuple[float, float]:
    """Log-return censoring bounds for a band expressed as a fraction of the previous close.

    The exchange rule is stated in PRICE terms, so the bounds are NOT symmetric in logs:
    a +/-2% band gives ln(1.02) = +1.9803% and ln(0.98) = -2.0203%. Treating them as +/-0.02
    misplaces both boundaries and biases the recovered sigma.
    """
    return float(np.log(1.0 - band)), float(np.log(1.0 + band))


def _neg_loglik(params, r, lo_b, hi_b, tol):
    mu, log_sigma = params
    sigma = np.exp(log_sigma)
    if not np.isfinite(sigma) or sigma <= 0:
        return 1e10

    hi = r >= hi_b * (1 - tol)
    lo = r <= lo_b * (1 - tol)
    mid = ~(hi | lo)

    ll = 0.0
    if mid.any():
        ll += np.sum(stats.norm.logpdf(r[mid], mu, sigma))
    if hi.any():
        ll += hi.sum() * np.log(max(stats.norm.sf(hi_b, mu, sigma), 1e-300))
    if lo.any():
        ll += lo.sum() * np.log(max(stats.norm.cdf(lo_b, mu, sigma), 1e-300))
    return -ll


def tobit_sigma(returns, band: float, tol: float = 0.05,
                drop_exact_zero: bool = True, min_obs: int = 60):
    """Two-sided Tobit MLE of the latent standard deviation of a censored return series.

    Returns a dict with the latent sigma, the naive sample sigma of the observed series, their
    ratio, and the censored share. `tol` is the relative tolerance for calling an observation
    pinned at the boundary, absorbing tick rounding.
    """
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    if drop_exact_zero:
        r = r[r != 0.0]
    if len(r) < min_obs:
        return {"sigma_latent": np.nan, "sigma_naive": np.nan, "inflation": np.nan,
                "censored_share": np.nan, "n": len(r)}

    lo_b, hi_b = log_bounds(band)
    naive = float(r.std(ddof=1))
    censored = float(np.mean((r >= hi_b * (1 - tol)) | (r <= lo_b * (1 - tol))))
    start = np.array([float(r.mean()), np.log(max(naive, 1e-6))])
    res = optimize.minimize(_neg_loglik, start, args=(r, lo_b, hi_b, tol),
                            method="Nelder-Mead",
                            options={"maxiter": 4000, "xatol": 1e-9, "fatol": 1e-9})
    sigma = float(np.exp(res.x[1])) if res.success or res.status == 2 else np.nan
    return {"sigma_latent": sigma, "sigma_naive": naive,
            "inflation": sigma / naive if naive > 0 else np.nan,
            "censored_share": censored, "n": len(r)}


def censoring_inflation(sigma_true: float, band: float) -> float:
    """Analytic ratio of observed to latent sd for a mean-zero normal censored at +/-band.

    Useful as a sanity bound: with b = band/sigma, the censored variance is

        E[r^2] = sigma^2 [ (1 - 2 b phi(b) - 2 Phi(-b)) ] + 2 b^2 sigma^2 Phi(-b)

    so the understatement depends only on the ratio band/sigma.
    """
    c = np.log(1.0 + band)            # use the upper log bound; symmetric approximation
    b = c / sigma_true
    phi, Phi = stats.norm.pdf(b), stats.norm.cdf(-b)
    var_obs = sigma_true**2 * (1 - 2 * b * phi - 2 * Phi) + 2 * (c**2) * Phi
    return float(np.sqrt(var_obs) / sigma_true)
