"""Latent stochastic-volatility model with multiple noisy measurements.

The problem this solves: NEPSE has no options and no confirmed intraday data, so true
volatility is never observed and estimator accuracy cannot be scored directly.

The model treats log-variance as an unobserved state and each volatility estimator as a
biased, noisy reading of it:

    state        h_t = mu + phi * (h_{t-1} - mu) + eta_t,      eta_t ~ N(0, sigma_eta^2)
    measurement  y_jt = alpha_j + h_t + eps_jt,                eps_jt ~ N(0, sigma_j^2)

where y_jt = log of estimator j's daily variance.

Identification. The level of h is pinned by fixing alpha_1 = 0 for a reference estimator,
so the remaining alpha_j are biases RELATIVE to that reference. Choosing close-to-close as
the reference is deliberate: simulation shows it is unbiased at every trading intensity,
which makes the alpha_j interpretable as absolute log-variance bias.

Note on the log transform. log of a squared standard normal has mean -1.27 (= -gamma - log 2)
and variance pi^2/2, so the raw log of a one-day squared return is a badly behaved
measurement. alpha_j absorbs the constant; the excess variance shows up in sigma_j^2 and is
exactly the "inefficiency" the range estimators were meant to reduce.

Following Alizadeh, Brandt & Diebold (2002), the log RANGE is far closer to Gaussian than
the log squared return, which is why range measures behave well here despite their bias.

IMPORTANT -- one range measure at a time. Parkinson, Garman-Klass and Rogers-Satchell are
all built from the SAME daily high and low, so their measurement errors are strongly
correlated. This model assumes a DIAGONAL observation covariance, and stacking several range
measures violates that badly enough to corrupt the state estimate: in simulation with true
phi = 0.97, fitting close-to-close plus one range measure recovers phi = 0.96, while fitting
all four at once returns phi = 0.73 and degrades the correlation between the filtered state
and the true one from 0.96 to 0.87. Fit each range estimator in its own two-measurement model.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.mlemodel import MLEModel

__all__ = ["LatentVolModel", "fit_latent_vol"]


class LatentVolModel(MLEModel):
    """AR(1) latent log-variance observed through k biased, noisy measurements."""

    def __init__(self, endog, ref: int = 0):
        endog = np.asarray(endog, dtype=float)
        k = endog.shape[1]
        super().__init__(endog, k_states=1, k_posdef=1,
                         initialization="stationary")
        self.ref = ref
        self.k_meas = k
        self["design"] = np.ones((k, 1, 1))
        self["selection", 0, 0] = 1.0
        self["obs_cov"] = np.zeros((k, k))

    @property
    def param_names(self):
        names = ["phi", "sigma_eta", "mu"]
        names += [f"alpha_{j}" for j in range(self.k_meas) if j != self.ref]
        names += [f"sigma_{j}" for j in range(self.k_meas)]
        return names

    @property
    def start_params(self):
        y = np.asarray(self.endog, dtype=float)
        m = np.nanmean(y[:, self.ref])
        offs = [np.nanmean(y[:, j]) - m for j in range(self.k_meas) if j != self.ref]
        sds = [max(np.nanstd(y[:, j]) * 0.7, 0.1) for j in range(self.k_meas)]
        return np.array([0.95, 0.3, m] + offs + sds)

    def transform_params(self, u):
        p = u.copy()
        p[0] = np.tanh(u[0])                     # |phi| < 1  (stationary state)
        p[1] = np.exp(u[1])                      # sigma_eta > 0
        p[-self.k_meas:] = np.exp(u[-self.k_meas:])   # measurement sds > 0
        return p

    def untransform_params(self, p):
        u = p.copy()
        u[0] = np.arctanh(np.clip(p[0], -0.999, 0.999))
        u[1] = np.log(max(p[1], 1e-8))
        u[-self.k_meas:] = np.log(np.maximum(p[-self.k_meas:], 1e-8))
        return u

    def update(self, params, **kwargs):
        params = super().update(params, **kwargs)
        phi, s_eta, mu = params[0], params[1], params[2]
        n_off = self.k_meas - 1
        offs = params[3:3 + n_off]
        sds = params[3 + n_off:]

        self["transition", 0, 0] = phi
        self["state_intercept", 0, 0] = mu * (1.0 - phi)
        self["state_cov", 0, 0] = s_eta ** 2

        d = np.zeros(self.k_meas)
        it = iter(offs)
        for j in range(self.k_meas):
            d[j] = 0.0 if j == self.ref else next(it)
        self["obs_intercept"] = d.reshape(-1, 1)
        self["obs_cov"] = np.diag(sds ** 2)


def fit_latent_vol(log_measures: pd.DataFrame, ref_col: str = "Close-to-close",
                   constants: pd.Series | None = None, disp: bool = False):
    """Fit the model to a frame of log daily variances (columns = estimators).

    Returns (results, tidy_frame). The tidy frame reports, per estimator:
      alpha      -- log-variance bias relative to the reference
      bias_ratio -- exp(alpha/2), i.e. the multiplicative bias in SIGMA units
      sigma_meas -- measurement noise sd (lower = more efficient)
      signal_pct -- share of that measurement's variance attributable to true volatility
    """
    if constants is not None:
        # Remove each estimator's Jensen constant so alpha_j measures BIAS, not the
        # log-transform gap. See log_transform_constants(). Omitting this step makes
        # the fitted intercepts meaningless.
        log_measures = log_measures.sub(
            pd.Series({c: constants.get(c, 0.0) for c in log_measures.columns}), axis=1)

    cols = list(log_measures.columns)
    range_based = [c for c in cols if c in
                   ("Parkinson", "Garman-Klass", "Rogers-Satchell", "GKYZ", "Yang-Zhang")]
    if len(range_based) > 1:
        import warnings as _w
        _w.warn(
            f"{len(range_based)} range-based measures passed together ({range_based}). "
            "They share the same high and low, so their errors are correlated and the "
            "diagonal observation covariance is misspecified — the state estimate will be "
            "distorted. Fit one range measure at a time.", RuntimeWarning, stacklevel=2)
    ref = cols.index(ref_col)
    mod = LatentVolModel(log_measures.values, ref=ref)
    res = mod.fit(disp=disp, maxiter=2000)

    p = res.params
    n_off = len(cols) - 1
    offs, sds = p[3:3 + n_off], p[3 + n_off:]
    alpha, it = [], iter(offs)
    for j in range(len(cols)):
        alpha.append(0.0 if j == ref else next(it))
    alpha = np.array(alpha)

    phi, s_eta = p[0], p[1]
    var_h = s_eta ** 2 / (1 - phi ** 2)          # unconditional variance of the state
    tidy = pd.DataFrame({
        "estimator": cols,
        "alpha": alpha,
        "bias_ratio": np.exp(alpha / 2.0),
        "sigma_meas": sds,
        "signal_pct": 100 * var_h / (var_h + sds ** 2),
    }).set_index("estimator")
    return res, tidy


def log_transform_constants(estimators: dict, sigma: float = 0.02, n_days: int = 200_000,
                            dense_trades: int = 4000, seed: int = 12345) -> pd.Series:
    """Calibration constants c_j = E[log(sigma_hat_j^2)] - log(sigma^2) under IDEAL conditions.

    This correction is NOT optional and its omission silently invalidates the model.
    E[log X] != log E[X], and the Jensen gap differs sharply across estimators: for a squared
    normal return E[log chi^2_1] = -gamma - log 2 ~= -1.27, whereas the log range is far closer
    to Gaussian and carries a much smaller constant (Alizadeh-Brandt-Diebold 2002).

    Fitting the state-space model to raw log variances therefore recovers the DIFFERENCE IN
    JENSEN CONSTANTS, not estimator bias. Subtracting c_j first makes the measurement
    intercepts alpha_j interpretable as genuine log-variance bias.

    The constants are properties of each estimator's sampling distribution, not of the data,
    so they are computed once by simulation at dense sampling where every estimator is unbiased.
    """
    from nepsevol.estimators.simulate import simulate_observed_ohlc

    # Chunked: the fine-grained path array is n_days x fine_steps, so a single large
    # call exhausts memory long before it exhausts patience.
    CHUNK = 20_000
    acc = {name: [] for name in estimators}
    done = 0
    while done < n_days:
        m = min(CHUNK, n_days - done)
        df = simulate_observed_ohlc(m, sigma, dense_trades, noise_sd=0.0,
                                    seed=seed + done, fine_steps=1000)
        for name, fn in estimators.items():
            v = np.asarray(fn(df), dtype=float)
            v = v[np.isfinite(v) & (v > 0)]
            acc[name].append(np.log(v))
        done += m
    return pd.Series({name: float(np.concatenate(v).mean() - np.log(sigma ** 2))
                      for name, v in acc.items()}, name="log_constant")


def log_constants_for_average(estimators: dict, n_series: int, sigma: float = 0.02,
                              n_days: int = 20_000, dense_trades: int = 4000,
                              seed: int = 999) -> pd.Series:
    """Jensen constants for a measure AVERAGED across `n_series` independent securities.

    The single-series constants from log_transform_constants() DO NOT APPLY to a
    cross-sectional average. Averaging k independent estimates shrinks the sampling noise
    by roughly 1/k, and since the Jensen gap E[log X] - log E[X] scales with the variance
    of X, the constant shrinks toward zero as k grows. Applying the single-series constant
    (-1.27 for close-to-close) to an average over 50 securities overstates the correction
    enormously and manufactures spurious bias.

    Here the same averaging structure used on the data is reproduced in simulation.
    """
    from nepsevol.estimators.simulate import simulate_observed_ohlc

    acc = {name: [] for name in estimators}
    CHUNK = 4000
    done = 0
    while done < n_days:
        m = min(CHUNK, n_days - done)
        per = {name: [] for name in estimators}
        for s in range(n_series):
            df = simulate_observed_ohlc(m, sigma, dense_trades, noise_sd=0.0,
                                        seed=seed + done * 131 + s, fine_steps=500)
            for name, fn in estimators.items():
                per[name].append(np.asarray(fn(df), dtype=float))
        for name in estimators:
            avg = np.nanmean(np.vstack(per[name]), axis=0)
            avg = avg[np.isfinite(avg) & (avg > 0)]
            acc[name].append(np.log(avg))
        done += m
    return pd.Series({name: float(np.concatenate(v).mean() - np.log(sigma ** 2))
                      for name, v in acc.items()}, name=f"log_constant_k{n_series}")
