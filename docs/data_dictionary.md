# Data Dictionary

## `nepse_index_history.csv` — NEPSE daily index

3,759 rows, 2010-01-03 → 2026-06-12. No duplicate dates; chronologically sorted.

| Column | Type | Description |
|---|---|---|
| `Date` | ISO date | Trading session date |
| `Open` | float | Index level at session open |
| `High` | float | Intraday maximum |
| `Low` | float | Intraday minimum |
| `Close` | float | Index level at session close |
| `Change` | float | Absolute change from previous close |
| `Percent_Change` | float | Percentage change from previous close |
| `Turnover` | float | Session turnover, NPR |

## Verified data characteristics

Computed directly from the file on 2026-08-26.

### Degenerate OHLC before 2016-06-06

| Year | Sessions | `O==H==L==C` | `Turnover==0` |
|---|---|---|---|
| 2010 | 228 | 228 | 228 |
| 2011 | 227 | 227 | 227 |
| 2012 | 230 | 230 | 230 |
| 2013 | 231 | 231 | 231 |
| 2014 | 229 | 229 | 229 |
| 2015 | 217 | 217 | 217 |
| 2016 | 231 | 105 | 95 |
| 2017–2026 | 2,166 | 1 | 0 |

The first session with `High != Low` is **2016-06-06**. `Turnover == 0` coincides almost exactly
with the degenerate window, which suggests one upstream data-source change rather than two
independent problems.

**Consequence:** range-based estimators (Parkinson, Garman–Klass, Rogers–Satchell, Yang–Zhang)
are undefined before 2016-06-06. Usable sample: **2,296 sessions**.

One isolated degenerate row remains at 2018-11-06 and needs individual inspection.

### Trading calendar

| Day | Sessions |
|---|---|
| Sunday | 727 |
| Monday | 746 |
| Tuesday | 758 |
| Wednesday | 757 |
| Thursday | 747 |
| Friday | 24 |
| Saturday | 0 |

A Sunday–Thursday week. The 24 Friday sessions are rare specials and need identifying
individually. **The annualization factor is not 252**, and the weekend gap runs Thursday close →
Sunday open.

### OHLC consistency violations

**69 rows** in 2016-06-06 → 2026-06-12 violate `Low <= min(Open, Close)` or
`High >= max(Open, Close)` — roughly 3% of the usable sample, concentrated in the earlier part of
the window. Range-based estimators can return negative variance on these rows.

### Structural closures (gaps > 7 calendar days)

| From | To | Days | Cause |
|---|---|---|---|
| 2015-04-23 | 2015-05-24 | 31 | Gorkha earthquake |
| 2020-03-22 | 2020-05-12 | 51 | COVID-19 lockdown |
| 2020-05-13 | 2020-06-29 | 47 | COVID-19 lockdown |
| 2022-09-29 | 2022-10-09 | 10 | Dashain |
| 2022-10-23 | 2022-10-31 | 8 | Tihar |
| 2023-10-19 | 2023-10-29 | 10 | Dashain |
| 2023-11-09 | 2023-11-20 | 11 | Tihar |
| *(and 7 further gaps of 8–12 days)* | | | Festival closures |

Both natural experiments for volatility and a complication for rolling windows.
