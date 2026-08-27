"""NEPSE trading calendar — detected from data, not assumed from a weekday rule.

A fixed weekday rule is wrong for this market. NEPSE traded **Sunday-Thursday** historically and
switched to **Monday-Friday** in April 2026. A hard-coded Sun-Thu filter therefore deletes genuine
Friday sessions and retains stale Sundays after the change, contaminating exactly the window that
contains the widened price-band regime.

Evidence from the panel, measured as the fraction of a date's cross-section whose close is
identical to the prior dated file (near 1.0 means the file repeats the previous session and is
not a trading day):

                 pre-2026-04     post-2026-04
    Sunday          0.155           0.924        <- stops trading
    Monday          0.203           0.038
    Tuesday         0.119           0.097
    Wednesday       0.151           0.043
    Thursday        0.203           0.094
    Friday          1.000           0.199        <- starts trading
    Saturday        1.000           0.933

The detector below infers sessions from that staleness signature instead of hard-coding weekdays,
so it survives further schedule changes without silently corrupting the sample.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["SCHEDULES", "expected_weekdays", "detect_sessions", "session_index"]

# Documented schedule regimes, used only as a cross-check on the detector.
SCHEDULES = [
    (pd.Timestamp("1900-01-01"), ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]),
    (pd.Timestamp("2026-04-01"), ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]),
]


def expected_weekdays(date) -> list[str]:
    """The scheduled trading weekdays in force on a date."""
    d = pd.Timestamp(date)
    out = SCHEDULES[0][1]
    for start, days in SCHEDULES:
        if d >= start:
            out = days
    return out


def detect_sessions(panel: pd.DataFrame, stale_threshold: float = 0.90,
                    price_col: str = "close") -> pd.DataFrame:
    """Classify each dated file as a genuine session or a carried-forward record.

    Returns one row per date with the staleness fraction, the scheduled-weekday flag, and the
    final `is_session` verdict. A date is a session when it is NOT stale; the scheduled weekday
    is reported alongside so disagreements between rule and data are visible rather than silent.
    """
    piv = panel.pivot_table(index="date", columns="symbol", values=price_col)
    prev = piv.shift(1)
    both = piv.notna() & prev.notna()
    same = ((piv == prev) & both).sum(axis=1)
    n = both.sum(axis=1).replace(0, np.nan)
    stale = (same / n).rename("stale_frac")

    out = stale.to_frame()
    out["weekday"] = out.index.day_name()
    out["scheduled"] = [wd in expected_weekdays(d) for d, wd in zip(out.index, out.weekday)]
    out["is_session"] = (out.stale_frac < stale_threshold) | out.stale_frac.isna()
    out["rule_data_disagree"] = out.scheduled != out.is_session
    return out


def session_index(dates: pd.Series, sessions: pd.DataFrame) -> pd.Series:
    """Consecutive-session ordinal for each date, counting only genuine sessions.

    Downstream code must use THIS rather than a raw date difference: a security's "previous
    session" is the previous genuine session, which is not the previous calendar day and, across
    a schedule change, not a fixed weekday offset either.
    """
    live = sessions.index[sessions.is_session]
    rank = {d: i for i, d in enumerate(sorted(live))}
    return pd.Series(dates).map(rank)
