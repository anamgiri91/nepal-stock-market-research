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
    "gkyz", "yang_zhang", "realized_range",
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
