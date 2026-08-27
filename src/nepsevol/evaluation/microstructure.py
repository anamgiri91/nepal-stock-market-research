"""Microstructure diagnostics used to identify the UPWARD friction (U1).

The range-estimator bias decomposition leaves one force measured only by inference:
noise in the observed extremes. These estimators measure it directly.

Roll (1984): under a bid-ask bounce model the transaction-price return series has
negative first-order autocovariance, and the effective spread is
    s = 2 * sqrt(-Cov(r_t, r_{t-1}))
The estimator is undefined when the covariance is positive, which happens whenever
genuine price continuation dominates the bounce -- common in trending thin markets,
so the fraction of undefined cases is itself reported rather than silently dropped.

Corwin & Schultz (2012) estimate the spread from two-day high-low ranges. Included
deliberately as a cross-check: it is itself range-based, so it inherits the very
biases under study and should NOT be treated as independent evidence.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["roll_spread", "corwin_schultz", "variance_ratio", "amihud"]


def roll_spread(returns: pd.Series, min_obs: int = 30) -> float:
    """Roll (1984) effective spread. NaN where the autocovariance is non-negative."""
    r = pd.Series(returns).dropna()
    if len(r) < min_obs:
        return np.nan
    cov = r.cov(r.shift(1))
    return 2.0 * np.sqrt(-cov) if cov < 0 else np.nan


def corwin_schultz(high: pd.Series, low: pd.Series, min_obs: int = 30) -> float:
    """Corwin-Schultz (2012) high-low spread estimator (mean of daily estimates)."""
    h, l = pd.Series(high).astype(float), pd.Series(low).astype(float)
    if len(h) < min_obs:
        return np.nan
    ok = (h > 0) & (l > 0)
    h, l = h.where(ok), l.where(ok)
    beta = (np.log(h / l) ** 2) + (np.log(h.shift(1) / l.shift(1)) ** 2)
    h2 = pd.concat([h, h.shift(1)], axis=1).max(axis=1)
    l2 = pd.concat([l, l.shift(1)], axis=1).min(axis=1)
    gamma = np.log(h2 / l2) ** 2
    k = 3.0 - 2.0 * np.sqrt(2.0)
    alpha = (np.sqrt(2.0 * beta) - np.sqrt(beta)) / k - np.sqrt(gamma / k)
    s = 2.0 * (np.exp(alpha) - 1.0) / (1.0 + np.exp(alpha))
    return float(np.nanmean(s.where(s > 0)))


def variance_ratio(returns: pd.Series, q: int = 5, min_obs: int = 60) -> float:
    """Lo-MacKinlay variance ratio Var(q-period)/(q*Var(1-period)).

    VR < 1 -> negative autocorrelation (bid-ask bounce / overreaction)
    VR > 1 -> positive autocorrelation (stale prices / partial adjustment)
    """
    r = pd.Series(returns).dropna()
    if len(r) < min_obs:
        return np.nan
    v1 = r.var(ddof=1)
    vq = r.rolling(q).sum().dropna().var(ddof=1)
    return float(vq / (q * v1)) if v1 > 0 else np.nan


def amihud(returns: pd.Series, turnover: pd.Series, min_obs: int = 30) -> float:
    """Amihud (2002) illiquidity: mean |return| per unit turnover, scaled 1e6."""
    r, t = pd.Series(returns).abs(), pd.Series(turnover)
    ok = t > 0
    if ok.sum() < min_obs:
        return np.nan
    return float((r[ok] / t[ok]).mean() * 1e6)
