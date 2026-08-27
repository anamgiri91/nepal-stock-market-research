"""Forecasting models and proxy-robust forecast evaluation.

This module carries the project's answer to its central obstacle. NEPSE has no options and
no confirmed intraday data, so true volatility is never observed and estimators cannot be
scored against it directly.

But the squared return of the NEXT period is a **noisy yet unbiased** proxy for that
period's variance: E[r^2_{t+1} | F_t] = sigma^2_{t+1}. Its noise is enormous for any single
day, but it is centred correctly, so averaging a loss function over thousands of days ranks
competing forecasts consistently. This is the Andersen-Bollerslev argument, and it converts
"which estimator is more accurate" from unanswerable into merely noisy.

The loss function must be chosen with care. Patton (2011) shows that most intuitive losses
(including MAE and anything applied to sigma rather than sigma^2) rank forecasts INCORRECTLY
when the proxy is noisy. Only a restricted family is robust; MSE and QLIKE are the two used
here.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["har_features", "fit_har", "mincer_zarnowitz", "qlike", "mse_loss",
           "diebold_mariano", "model_confidence_set"]


def har_features(rv: pd.Series) -> pd.DataFrame:
    """Corsi (2009) HAR components: daily, weekly (5d), monthly (22d) averages."""
    rv = pd.Series(rv).astype(float)
    return pd.DataFrame({
        "d": rv,
        "w": rv.rolling(5).mean(),
        "m": rv.rolling(22).mean(),
    })


def fit_har(rv: pd.Series, target: pd.Series | None = None, split: float = 0.7):
    """Fit HAR in logs on a training split; forecast one step ahead out of sample.

    Logs are used because realized-variance series are strongly right-skewed; an OLS fit in
    levels is dominated by a handful of extreme days.
    """
    import statsmodels.api as sm

    rv = pd.Series(rv).astype(float)
    y_src = rv if target is None else pd.Series(target).astype(float)
    X = har_features(rv)
    df = pd.concat([np.log(y_src.shift(-1)).rename("y"), np.log(X)], axis=1)
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    n_tr = int(len(df) * split)
    tr, te = df.iloc[:n_tr], df.iloc[n_tr:]
    fit = sm.OLS(tr["y"], sm.add_constant(tr[["d", "w", "m"]])).fit()
    pred_log = fit.predict(sm.add_constant(te[["d", "w", "m"]]))
    # exp of a log-forecast is a median, not a mean; the Gaussian correction restores the mean
    pred = np.exp(pred_log + 0.5 * fit.mse_resid)
    return fit, pred, te.index


def mincer_zarnowitz(proxy: pd.Series, forecast: pd.Series):
    """Regress the proxy on the forecast: proxy = a + b * forecast.

    An unbiased, efficient forecast gives a = 0 and b = 1. R^2 measures how much of the
    proxy's variation the forecast explains -- necessarily small, because the proxy is
    mostly noise, but comparable ACROSS forecasts.
    """
    import statsmodels.api as sm

    d = pd.concat([pd.Series(proxy).rename("p"), pd.Series(forecast).rename("f")], axis=1).dropna()
    if d["f"].nunique() < 2:
        # A constant forecast carries no slope to identify. add_constant() would silently
        # decline to add an intercept here (has_constant="skip"), leaving a one-parameter fit.
        return {"a": np.nan, "b": np.nan, "t(a=0)": np.nan, "t(b=1)": np.nan,
                "joint p (a=0,b=1)": np.nan, "R2": 0.0, "n": int(len(d))}
    r = sm.OLS(d["p"], sm.add_constant(d[["f"]], has_constant="add")).fit(cov_type="HC1")
    a, b = r.params.iloc[0], r.params.iloc[1]
    joint = r.f_test("const = 0, f = 1")
    return {"a": a, "b": b, "t(a=0)": (a - 0) / r.bse.iloc[0],
            "t(b=1)": (b - 1) / r.bse.iloc[1],
            "joint p (a=0,b=1)": float(np.squeeze(joint.pvalue)),
            "R2": r.rsquared, "n": int(r.nobs)}


def qlike(proxy, forecast):
    """QLIKE loss: log(f) + p/f. Proxy-robust (Patton 2011). Lower is better.

    Penalises under-prediction of volatility far more than over-prediction, which matches
    the asymmetry of most risk applications.
    """
    p, f = np.asarray(proxy, float), np.asarray(forecast, float)
    ok = (f > 0) & np.isfinite(p) & np.isfinite(f)
    return np.log(f[ok]) + p[ok] / f[ok]


def mse_loss(proxy, forecast):
    """Squared-error loss on the VARIANCE scale. Proxy-robust (Patton 2011)."""
    p, f = np.asarray(proxy, float), np.asarray(forecast, float)
    ok = np.isfinite(p) & np.isfinite(f)
    return (p[ok] - f[ok]) ** 2


def diebold_mariano(loss_a, loss_b, lag: int = 5):
    """Diebold-Mariano test of equal predictive accuracy, Newey-West corrected.

    Negative statistic => model A has lower loss (A is better).
    """
    from scipy import stats as sps

    d = np.asarray(loss_a, float) - np.asarray(loss_b, float)
    d = d[np.isfinite(d)]
    n = len(d)
    if n < 20:
        return {"DM": np.nan, "p": np.nan, "n": n}
    dbar = d.mean()
    g0 = np.sum((d - dbar) ** 2) / n
    var = g0
    for k in range(1, lag + 1):
        gk = np.sum((d[k:] - dbar) * (d[:-k] - dbar)) / n
        var += 2 * (1 - k / (lag + 1)) * gk
    var = max(var, 1e-18)
    dm = dbar / np.sqrt(var / n)
    return {"DM": dm, "p": 2 * (1 - sps.norm.cdf(abs(dm))), "n": n}


def model_confidence_set(losses: pd.DataFrame, alpha: float = 0.10,
                         n_boot: int = 1000, block: int = 10, seed: int = 0):
    """Hansen-Lunde-Nason Model Confidence Set (range statistic, block bootstrap).

    Returns the set of models that cannot be distinguished from the best at level alpha.
    Reporting a SET rather than a single winner is the honest response to a noisy proxy:
    with this much measurement error, several forecasts genuinely cannot be separated.
    """
    rng = np.random.default_rng(seed)
    L = losses.dropna()
    models = list(L.columns)
    n = len(L)
    n_blocks = int(np.ceil(n / block))
    idx = np.array([np.concatenate([np.arange(s, min(s + block, n))
                                    for s in rng.integers(0, n - block, n_blocks)])[:n]
                    for _ in range(n_boot)])

    eliminated = []
    while len(models) > 1:
        sub = L[models].values
        dbar = sub.mean(axis=0)
        d_ij = dbar[:, None] - dbar[None, :]
        boot = sub[idx].mean(axis=1)                       # (n_boot, k)
        bd = boot[:, :, None] - boot[:, None, :]
        var = bd.var(axis=0) + 1e-18
        t = np.abs(d_ij) / np.sqrt(var)
        np.fill_diagonal(t, 0.0)
        T = t.max()
        boot_T = np.abs(bd - d_ij).max(axis=(1, 2)) / 1.0
        boot_T = (np.abs(bd - d_ij) / np.sqrt(var)).max(axis=(1, 2))
        p = float((boot_T >= T).mean())
        if p > alpha:
            break
        worst = int(np.argmax(dbar))                       # highest average loss
        eliminated.append((models[worst], p))
        models.pop(worst)
    return {"mcs": models, "eliminated": eliminated}
