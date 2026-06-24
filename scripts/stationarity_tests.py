"""
Enhanced Descriptive Statistics & Stationarity Tests for NEPSE
===============================================================
Covers the statistical foundations missing from the original analysis:
1. ADF / KPSS tests on index levels, log-returns, realized volatility
2. Ljung-Box Q(10) on returns and squared returns
3. Engle's ARCH-LM test (lags 1, 5, 10)
4. Zivot-Andrews structural break test
5. Extended descriptive statistics (all series)

Output:
  - table_stationarity_tests.csv
  - table_descriptive_stats_extended.csv
  - table_arch_lm_tests.csv
"""

import os
import warnings
import numpy as np
import pandas as pd
from scipy import stats as sp_stats
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch

warnings.filterwarnings("ignore")

# ── Configuration ─────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
NEPSE_FILE = os.path.join(BASE_DIR, "nepse_index_history.csv")
FULL_SAMPLE_START = "2010-01-03"


def load_nepse():
    """Load and prepare NEPSE data."""
    df = pd.read_csv(NEPSE_FILE)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    # Log returns
    df["log_return"] = np.log(df["Close"] / df["Close"].shift(1))

    # Realized volatility (22-day rolling std of log returns, annualized)
    df["rv_22d"] = df["log_return"].rolling(22).std() * np.sqrt(252)

    # Calendar gap (days between trading dates)
    df["gap_days"] = (df["Date"] - df["Date"].shift(1)).dt.days

    return df


def descriptive_stats(series: pd.Series, name: str) -> dict:
    """Compute descriptive statistics for a return series."""
    s = series.dropna()
    n = len(s)

    # Jarque-Bera test
    jb_stat, jb_pval = sp_stats.jarque_bera(s)

    return {
        "Series": name,
        "N": n,
        "Mean": s.mean(),
        "Std_Dev": s.std(),
        "Skewness": s.skew(),
        "Excess_Kurtosis": s.kurtosis(),
        "Min": s.min(),
        "Max": s.max(),
        "JB_Stat": jb_stat,
        "JB_pvalue": jb_pval,
    }


def stationarity_tests(series: pd.Series, name: str) -> list[dict]:
    """Run ADF and KPSS tests on a series."""
    s = series.dropna()
    results = []

    # ADF test (H0: unit root)
    try:
        adf_result = adfuller(s, autolag="AIC")
        results.append({
            "Series": name,
            "Test": "ADF",
            "Statistic": adf_result[0],
            "p_value": adf_result[1],
            "Lags_Used": adf_result[2],
            "Critical_1pct": adf_result[4]["1%"],
            "Critical_5pct": adf_result[4]["5%"],
            "Critical_10pct": adf_result[4]["10%"],
            "Conclusion": "Stationary" if adf_result[1] < 0.05 else "Non-stationary",
        })
    except Exception as e:
        results.append({
            "Series": name, "Test": "ADF", "Statistic": np.nan,
            "p_value": np.nan, "Conclusion": f"Error: {e}"
        })

    # KPSS test (H0: stationary)
    try:
        kpss_result = kpss(s, regression="c", nlags="auto")
        results.append({
            "Series": name,
            "Test": "KPSS",
            "Statistic": kpss_result[0],
            "p_value": kpss_result[1],
            "Lags_Used": kpss_result[2],
            "Critical_1pct": kpss_result[3].get("1%", np.nan),
            "Critical_5pct": kpss_result[3].get("5%", np.nan),
            "Critical_10pct": kpss_result[3].get("10%", np.nan),
            "Conclusion": "Stationary" if kpss_result[1] > 0.05 else "Non-stationary",
        })
    except Exception as e:
        results.append({
            "Series": name, "Test": "KPSS", "Statistic": np.nan,
            "p_value": np.nan, "Conclusion": f"Error: {e}"
        })

    return results


def ljung_box_test(series: pd.Series, name: str, lags: int = 10) -> dict:
    """Ljung-Box Q test for autocorrelation."""
    s = series.dropna()
    try:
        lb = acorr_ljungbox(s, lags=[lags], return_df=True)
        return {
            "Series": name,
            "Test": f"Ljung-Box Q({lags})",
            "Statistic": lb["lb_stat"].iloc[0],
            "p_value": lb["lb_pvalue"].iloc[0],
            "Conclusion": "Autocorrelated" if lb["lb_pvalue"].iloc[0] < 0.05 else "No autocorrelation",
        }
    except Exception as e:
        return {"Series": name, "Test": f"Ljung-Box Q({lags})", "Conclusion": f"Error: {e}"}


def arch_lm_test(series: pd.Series, name: str, nlags: int) -> dict:
    """Engle's ARCH-LM test for conditional heteroscedasticity."""
    s = series.dropna()
    try:
        result = het_arch(s, nlags=nlags)
        return {
            "Series": name,
            "Test": f"ARCH-LM({nlags})",
            "LM_Stat": result[0],
            "LM_pvalue": result[1],
            "F_Stat": result[2],
            "F_pvalue": result[3],
            "Conclusion": "ARCH effects" if result[1] < 0.05 else "No ARCH effects",
        }
    except Exception as e:
        return {"Series": name, "Test": f"ARCH-LM({nlags})", "Conclusion": f"Error: {e}"}


def zivot_andrews_test(series: pd.Series, name: str) -> dict:
    """
    Zivot-Andrews structural break test.
    Uses statsmodels implementation if available, otherwise manual.
    """
    s = series.dropna()
    try:
        from statsmodels.tsa.stattools import zivot_andrews as za
        result = za(s, maxlag=None, regression="c", autolag="AIC")
        return {
            "Series": name,
            "Test": "Zivot-Andrews",
            "Statistic": result[0],
            "p_value": result[1],
            "Break_Index": result[3],
            "Lags_Used": result[2],
            "Critical_1pct": result[4]["1%"],
            "Critical_5pct": result[4]["5%"],
            "Conclusion": "Structural break" if result[1] < 0.05 else "No break detected",
        }
    except ImportError:
        return {"Series": name, "Test": "Zivot-Andrews", "Conclusion": "Not available (statsmodels version)"}
    except Exception as e:
        return {"Series": name, "Test": "Zivot-Andrews", "Conclusion": f"Error: {e}"}


def main():
    print("=" * 60)
    print("NEPSE Enhanced Descriptive Statistics & Stationarity Tests")
    print("=" * 60)

    df = load_nepse()
    print(f"Loaded {len(df)} observations")
    print(f"Date range: {df['Date'].iloc[0].date()} → {df['Date'].iloc[-1].date()}")
    print(f"Log-return obs: {df['log_return'].dropna().shape[0]}")
    print(f"RV 22d obs: {df['rv_22d'].dropna().shape[0]}")

    # ── 1. Descriptive Statistics ──────────────────────────────────
    print(f"\n{'─'*60}")
    print("1. Descriptive Statistics")

    desc_rows = []
    desc_rows.append(descriptive_stats(df["Close"], "NEPSE_Close (level)"))
    desc_rows.append(descriptive_stats(df["log_return"], "NEPSE_LogReturn"))
    desc_rows.append(descriptive_stats(df["rv_22d"], "NEPSE_RV_22d"))

    desc_df = pd.DataFrame(desc_rows)
    desc_path = os.path.join(BASE_DIR, "table_descriptive_stats_extended.csv")
    desc_df.to_csv(desc_path, index=False)
    print(desc_df.to_string(index=False))
    print(f"  ✅ Saved → table_descriptive_stats_extended.csv")

    # ── 2. Stationarity Tests ──────────────────────────────────────
    print(f"\n{'─'*60}")
    print("2. Stationarity Tests (ADF & KPSS)")

    stat_rows = []
    test_series = {
        "NEPSE_Close": df["Close"],
        "NEPSE_LogReturn": df["log_return"],
        "NEPSE_RV_22d": df["rv_22d"],
    }

    for name, series in test_series.items():
        stat_rows.extend(stationarity_tests(series, name))

    stat_df = pd.DataFrame(stat_rows)
    stat_path = os.path.join(BASE_DIR, "table_stationarity_tests.csv")
    stat_df.to_csv(stat_path, index=False)

    for _, row in stat_df.iterrows():
        print(f"  {row['Series']:20s} | {row['Test']:6s} | stat={row.get('Statistic', 'N/A'):>10} | p={row.get('p_value', 'N/A'):>8} | {row['Conclusion']}")

    print(f"  ✅ Saved → table_stationarity_tests.csv")

    # ── 3. Ljung-Box Tests ─────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("3. Ljung-Box Tests")

    lb_rows = []
    lb_rows.append(ljung_box_test(df["log_return"], "LogReturn", lags=10))
    lb_rows.append(ljung_box_test(df["log_return"] ** 2, "LogReturn²", lags=10))
    lb_rows.append(ljung_box_test(df["rv_22d"], "RV_22d", lags=10))

    lb_df = pd.DataFrame(lb_rows)
    for _, row in lb_df.iterrows():
        print(f"  {row['Series']:15s} | {row['Test']:20s} | stat={row.get('Statistic', 'N/A'):>10} | p={row.get('p_value', 'N/A'):>10} | {row['Conclusion']}")

    # ── 4. ARCH-LM Tests ──────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("4. Engle's ARCH-LM Tests (prerequisite for GARCH)")

    arch_rows = []
    for nlags in [1, 5, 10]:
        arch_rows.append(arch_lm_test(df["log_return"].dropna(), "LogReturn", nlags=nlags))

    arch_df = pd.DataFrame(arch_rows)
    arch_path = os.path.join(BASE_DIR, "table_arch_lm_tests.csv")
    arch_df.to_csv(arch_path, index=False)

    for _, row in arch_df.iterrows():
        print(f"  {row['Test']:12s} | LM={row.get('LM_Stat', 'N/A'):>10} | p={row.get('LM_pvalue', 'N/A'):>10} | {row['Conclusion']}")

    print(f"  ✅ Saved → table_arch_lm_tests.csv")

    # ── 5. Structural Break Test ──────────────────────────────────
    print(f"\n{'─'*60}")
    print("5. Zivot-Andrews Structural Break Test")

    za_rows = []
    za_result = zivot_andrews_test(df["Close"].dropna(), "NEPSE_Close")
    za_rows.append(za_result)

    if za_result.get("Break_Index") is not None:
        break_idx = int(za_result["Break_Index"])
        valid_close = df["Close"].dropna()
        if break_idx < len(valid_close):
            break_date = df.loc[valid_close.index[break_idx], "Date"]
            print(f"  Break detected at index {break_idx} → date {break_date.date()}")
            za_result["Break_Date"] = str(break_date.date())

    za_result_rv = zivot_andrews_test(df["rv_22d"].dropna(), "NEPSE_RV_22d")
    za_rows.append(za_result_rv)

    if za_result_rv.get("Break_Index") is not None:
        break_idx = int(za_result_rv["Break_Index"])
        valid_rv = df["rv_22d"].dropna()
        if break_idx < len(valid_rv):
            break_date = df.loc[valid_rv.index[break_idx], "Date"]
            print(f"  RV break detected at index {break_idx} → date {break_date.date()}")
            za_result_rv["Break_Date"] = str(break_date.date())

    for r in za_rows:
        print(f"  {r['Series']:20s} | {r.get('Statistic', 'N/A'):>10} | p={r.get('p_value', 'N/A'):>8} | {r['Conclusion']}")

    # ── 6. Calendar gap analysis ──────────────────────────────────
    print(f"\n{'─'*60}")
    print("6. Calendar Gap Analysis")

    gaps = df["gap_days"].dropna()
    long_gaps = gaps[gaps > 3]
    print(f"  Total trading days:  {len(df)}")
    print(f"  Median gap:          {gaps.median():.0f} days")
    print(f"  Max gap:             {gaps.max():.0f} days")
    print(f"  Gaps > 3 days:       {len(long_gaps)} ({100*len(long_gaps)/len(gaps):.1f}%)")

    # Key events
    events = {
        "2015-04-25": "Nepal Earthquake",
        "2020-03-22": "COVID-19 Lockdown Start",
        "2020-07-15": "NEPSE Reopening",
        "2021-08-18": "2021 Bull Market Peak",
    }
    print("\n  Key Event Periods:")
    for date_str, event in events.items():
        date = pd.Timestamp(date_str)
        nearest = df.iloc[(df["Date"] - date).abs().argsort()[:1]]
        if not nearest.empty:
            row = nearest.iloc[0]
            print(f"    {event}: {row['Date'].date()} (Close={row['Close']:.1f})")

    print(f"\n{'═'*60}")
    print("All tests complete.")


if __name__ == "__main__":
    main()
