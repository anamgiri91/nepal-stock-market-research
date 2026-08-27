"""Range-based volatility estimators.

All functions return DAILY VARIANCE (not annualised, not sigma). Callers annualise
explicitly, because the annualisation factor for NEPSE is not 252 -- see
nepsevol.trading_calendar.

Notation follows the literature:
    o = ln(O_t / C_{t-1})   overnight (close-to-open) return
    u = ln(H_t / O_t)       normalised high
    d = ln(L_t / O_t)       normalised low
    c = ln(C_t / O_t)       open-to-close return

References (verify before citing in the paper):
    Parkinson (1980), J. Business
    Garman & Klass (1980), J. Business
    Rogers & Satchell (1991), Ann. Applied Probability
    Yang & Zhang (2000), J. Business
"""

from __future__ import annotations

import numpy as np
import pandas as pd

LN2 = np.log(2.0)

__all__ = [
    "close_to_close", "parkinson", "garman_klass", "rogers_satchell",
    "gkyz", "yang_zhang", "realized_range", "add_rs",
]


def _logs(df: pd.DataFrame) -> dict[str, pd.Series]:
    """Standard log transforms. Expects columns open/high/low/close."""
    o_, h, l, c_ = df["open"], df["high"], df["low"], df["close"]
    prev_c = c_.shift(1)
    return {
        "o": np.log(o_ / prev_c),
        "u": np.log(h / o_),
        "d": np.log(l / o_),
        "c": np.log(c_ / o_),
        "hl": np.log(h / l),
        "cc": np.log(c_ / prev_c),
    }


def close_to_close(df: pd.DataFrame, window: int | None = None) -> pd.Series:
    """Close-to-close variance. The friction-robust baseline: uses no range data,
    so it is immune to discretisation bias in the observed high and low."""
    r = _logs(df)["cc"]
    if window is None:
        return r.pow(2)
    return r.rolling(window).var(ddof=1)


def parkinson(df: pd.DataFrame) -> pd.Series:
    """Parkinson (1980). Uses only the high-low range.

    sigma^2 = (1 / (4 ln2)) * [ln(H/L)]^2

    Assumes zero drift and CONTINUOUS observation of the price path. The second
    assumption is what fails in illiquid markets: with N trades the observed range
    is the range of an N-sample, which understates the true range. Returns exactly
    zero when H == L, which happens on 5% of NEPSE stock-days.
    """
    hl = _logs(df)["hl"]
    return hl.pow(2) / (4.0 * LN2)


def garman_klass(df: pd.DataFrame) -> pd.Series:
    """Garman & Klass (1980). Uses the full OHLC set.

    sigma^2 = 0.5*[ln(H/L)]^2 - (2 ln2 - 1)*[ln(C/O)]^2

    Assumes zero drift and no opening jump. Can return NEGATIVE values when the
    close-open move is large relative to the observed range -- a pathology that
    becomes common when the range is truncated by thin trading or price limits.
    """
    L = _logs(df)
    return 0.5 * L["hl"].pow(2) - (2.0 * LN2 - 1.0) * L["c"].pow(2)


def rogers_satchell(df: pd.DataFrame) -> pd.Series:
    """Rogers & Satchell (1991). Drift-independent.

    sigma^2 = u(u - c) + d(d - c)

    The drift-independence matters for NEPSE, which trends persistently. Unlike
    Garman-Klass it is non-negative by construction, but it still inherits the
    discretisation bias of the observed extremes.
    """
    L = _logs(df)
    u, d, c = L["u"], L["d"], L["c"]
    return u * (u - c) + d * (d - c)


def gkyz(df: pd.DataFrame) -> pd.Series:
    """Garman-Klass-Yang-Zhang: Garman-Klass with an overnight term.

    sigma^2 = o^2 + 0.5*(u - d)^2 - (2 ln2 - 1)*c^2

    The overnight term o spans Thursday close -> Sunday open on NEPSE weekends,
    which is a three-calendar-day gap rather than the one day the derivation assumes.
    """
    L = _logs(df)
    return L["o"].pow(2) + 0.5 * (L["u"] - L["d"]).pow(2) - (2.0 * LN2 - 1.0) * L["c"].pow(2)


def yang_zhang(df: pd.DataFrame, window: int = 21) -> pd.Series:
    """Yang & Zhang (2000). Minimum-variance, drift-independent, jump-robust.

    sigma^2 = sigma_o^2 + k*sigma_c^2 + (1-k)*sigma_rs^2
    k = 0.34 / (1.34 + (n+1)/(n-1))

    Requires a window because sigma_o^2 and sigma_c^2 are cross-day variances.
    Its overnight component makes it the most exposed of the family to NEPSE's
    Sunday-Thursday calendar.
    """
    L = _logs(df)
    n = window
    k = 0.34 / (1.34 + (n + 1) / (n - 1))
    var_o = L["o"].rolling(n).var(ddof=1)
    var_c = L["c"].rolling(n).var(ddof=1)
    var_rs = rogers_satchell(df).rolling(n).mean()
    return var_o + k * var_c + (1.0 - k) * var_rs


def realized_range(df: pd.DataFrame, window: int = 21) -> pd.Series:
    """Rolling mean of Parkinson daily variance -- a smoothed range measure."""
    return parkinson(df).rolling(window).mean()


def add_rs(df: pd.DataFrame, rtol: float = 1e-12) -> pd.Series:
    """AddRS — the additively bias-corrected Rogers-Satchell estimator.

    Kumar & Maheswaran (2014), derived from a reflection principle for a random walk. With
    b = ln(H/O), c = ln(L/O), x = ln(C/O) and u = 2b - x, v = 2c - x:

        Add_ux = 0.5(u^2 - x^2) + x^2 * 1{H = O or C = H}
        Add_vx = 0.5(v^2 - x^2) + x^2 * 1{L = O or C = L}
        AddRS  = 0.5(Add_ux + Add_vx)

    The construction reduces exactly. Since 0.5(u^2 - x^2) = 2b(b - x) and likewise for v, the
    indicator-free part is identically Rogers-Satchell, so

        AddRS = RS + (x^2 / 2) * (1{H=O or C=H} + 1{L=O or C=L}).

    That is what the correction does: on a MONOTONE day the observed extremes coincide with the
    open and close, RS collapses to zero, and AddRS substitutes the squared open-to-close return.
    Both indicators fire on a fully monotone bar, giving AddRS = x^2.

    This matters directly here: Rogers-Satchell is exactly zero on 15.2% of NEPSE stock-days, and
    59.6% of those are monotone rather than degenerate. AddRS is designed for precisely that case.

    Indicators are evaluated on RAW PRICES rather than on log differences, because testing a
    floating-point log against zero is unreliable; `rtol` sets the relative tolerance.
    """
    o_, h, l, c_ = df["open"], df["high"], df["low"], df["close"]
    b, c, x = np.log(h / o_), np.log(l / o_), np.log(c_ / o_)
    u, v = 2 * b - x, 2 * c - x

    close_to = lambda p, q: (p - q).abs() <= rtol * q.abs()
    ind_u = close_to(h, o_) | close_to(c_, h)      # H = O  or  C = H
    ind_v = close_to(l, o_) | close_to(c_, l)      # L = O  or  C = L

    add_ux = 0.5 * (u**2 - x**2) + x**2 * ind_u.astype(float)
    add_vx = 0.5 * (v**2 - x**2) + x**2 * ind_v.astype(float)
    return 0.5 * (add_ux + add_vx)
