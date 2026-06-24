"""
Spillover Analysis: India VIX → NEPSE
=======================================
1. Granger causality tests
2. Bivariate VAR model
3. India VIX as implied volatility proxy for NEPSE
4. Rolling correlation analysis

Uses the aligned NEPSE–India dataset from Phase 1.
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import grangercausalitytests, adfuller
import statsmodels.api as sm
from scipy import stats as sp_stats

warnings.filterwarnings("ignore")

# ── Configuration ─────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ALIGNED_FILE = os.path.join(DATA_DIR, "data_aligned_nepse_india.csv")
INDIA_VIX_FILE = os.path.join(DATA_DIR, "data_india_vix.csv")
NIFTY_FILE = os.path.join(DATA_DIR, "data_nifty50_ohlcv.csv")
NEPSE_FILE = os.path.join(BASE_DIR, "nepse_index_history.csv")


def load_aligned():
    """Load aligned NEPSE–India dataset and compute derived series."""
    df = pd.read_csv(ALIGNED_FILE)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    # NEPSE log returns
    df["NEPSE_ret"] = np.log(df["NEPSE_Close"] / df["NEPSE_Close"].shift(1))

    # NIFTY log returns
    df["NIFTY_ret"] = np.log(df["NIFTY_Close"] / df["NIFTY_Close"].shift(1))

    # NEPSE realized volatility (22-day rolling)
    df["NEPSE_rv"] = df["NEPSE_ret"].rolling(22).std() * np.sqrt(252)

    # India VIX change
    df["IndiaVIX_ret"] = np.log(df["IndiaVIX_Close"] / df["IndiaVIX_Close"].shift(1))

    return df


def granger_causality(df, max_lag=10):
    """Run Granger causality tests for India VIX → NEPSE RV and vice versa."""
    print(f"\n{'─'*60}")
    print("1. Granger Causality Tests")
    print(f"   Max lag: {max_lag}")

    results = []

    # Test: India VIX → NEPSE RV
    data1 = df[["NEPSE_rv", "IndiaVIX_Close"]].dropna()
    if len(data1) > max_lag + 50:
        print(f"\n  India VIX → NEPSE RV (n={len(data1)}):")
        try:
            gc1 = grangercausalitytests(data1.values, maxlag=max_lag, verbose=False)
            for lag in [1, 2, 5, 10]:
                if lag <= max_lag:
                    f_stat = gc1[lag][0]["ssr_ftest"][0]
                    p_val = gc1[lag][0]["ssr_ftest"][1]
                    sig = "***" if p_val < 0.01 else "**" if p_val < 0.05 else "*" if p_val < 0.1 else ""
                    print(f"    Lag {lag:2d}: F={f_stat:8.3f}, p={p_val:.4f} {sig}")
                    results.append({
                        "Direction": "IndiaVIX → NEPSE_RV",
                        "Lag": lag, "F_Stat": f_stat, "p_value": p_val,
                        "Significant_5pct": "Yes" if p_val < 0.05 else "No",
                    })
        except Exception as e:
            print(f"    Error: {e}")

    # Test: NEPSE RV → India VIX
    data2 = df[["IndiaVIX_Close", "NEPSE_rv"]].dropna()
    if len(data2) > max_lag + 50:
        print(f"\n  NEPSE RV → India VIX (n={len(data2)}):")
        try:
            gc2 = grangercausalitytests(data2.values, maxlag=max_lag, verbose=False)
            for lag in [1, 2, 5, 10]:
                if lag <= max_lag:
                    f_stat = gc2[lag][0]["ssr_ftest"][0]
                    p_val = gc2[lag][0]["ssr_ftest"][1]
                    sig = "***" if p_val < 0.01 else "**" if p_val < 0.05 else "*" if p_val < 0.1 else ""
                    print(f"    Lag {lag:2d}: F={f_stat:8.3f}, p={p_val:.4f} {sig}")
                    results.append({
                        "Direction": "NEPSE_RV → IndiaVIX",
                        "Lag": lag, "F_Stat": f_stat, "p_value": p_val,
                        "Significant_5pct": "Yes" if p_val < 0.05 else "No",
                    })
        except Exception as e:
            print(f"    Error: {e}")

    # Test: NIFTY returns → NEPSE returns
    data3 = df[["NEPSE_ret", "NIFTY_ret"]].dropna()
    if len(data3) > max_lag + 50:
        print(f"\n  NIFTY returns → NEPSE returns (n={len(data3)}):")
        try:
            gc3 = grangercausalitytests(data3.values, maxlag=max_lag, verbose=False)
            for lag in [1, 2, 5]:
                if lag <= max_lag:
                    f_stat = gc3[lag][0]["ssr_ftest"][0]
                    p_val = gc3[lag][0]["ssr_ftest"][1]
                    sig = "***" if p_val < 0.01 else "**" if p_val < 0.05 else "*" if p_val < 0.1 else ""
                    print(f"    Lag {lag:2d}: F={f_stat:8.3f}, p={p_val:.4f} {sig}")
                    results.append({
                        "Direction": "NIFTY_ret → NEPSE_ret",
                        "Lag": lag, "F_Stat": f_stat, "p_value": p_val,
                        "Significant_5pct": "Yes" if p_val < 0.05 else "No",
                    })
        except Exception as e:
            print(f"    Error: {e}")

    return pd.DataFrame(results)


def var_analysis(df):
    """Fit bivariate VAR on [NEPSE_RV, India VIX]."""
    print(f"\n{'─'*60}")
    print("2. Bivariate VAR Analysis")

    data = df[["NEPSE_rv", "IndiaVIX_Close"]].dropna()
    print(f"   Observations: {len(data)}")

    # Check stationarity — use first differences if needed
    adf_nepse = adfuller(data["NEPSE_rv"])[1]
    adf_vix = adfuller(data["IndiaVIX_Close"])[1]
    print(f"   ADF p-values — NEPSE_RV: {adf_nepse:.4f}, IndiaVIX: {adf_vix:.4f}")

    if adf_vix > 0.05:
        print("   India VIX is non-stationary — using first differences")
        data = data.copy()
        data["IndiaVIX_Close"] = data["IndiaVIX_Close"].diff()
        data = data.dropna()

    # Fit VAR with lag selection
    model = VAR(data)

    # Select lag order
    lag_order = model.select_order(maxlags=10)
    print(f"\n   Lag order selection:")
    print(f"     AIC:  {lag_order.aic}")
    print(f"     BIC:  {lag_order.bic}")
    print(f"     HQIC: {lag_order.hqic}")

    optimal_lag = lag_order.aic
    print(f"   Using optimal lag (AIC): {optimal_lag}")

    if optimal_lag < 1:
        optimal_lag = 1

    # Fit VAR
    results = model.fit(optimal_lag)
    print(f"\n   VAR({optimal_lag}) Summary:")
    print(f"     Log-likelihood: {results.llf:.1f}")

    # Impulse Response
    print(f"\n   Impulse Response Functions (10-step):")
    irf = results.irf(10)

    return results, irf, data


def india_vix_proxy(df):
    """
    Test India VIX as forward-looking implied volatility proxy for NEPSE.
    Regress: NEPSE_RV_{t+h} = α + β·IndiaVIX_t + ε
    """
    print(f"\n{'─'*60}")
    print("3. India VIX as Implied Volatility Proxy for NEPSE")

    proxy_rows = []

    for h in [1, 5, 22]:
        # Forward-looking RV
        data = df[["NEPSE_rv", "IndiaVIX_Close"]].copy()
        data["NEPSE_rv_fwd"] = data["NEPSE_rv"].shift(-h)
        data = data.dropna()

        if len(data) < 50:
            continue

        X = sm.add_constant(data["IndiaVIX_Close"])
        model = sm.OLS(data["NEPSE_rv_fwd"], X).fit(cov_type="HAC",
                       cov_kwds={"maxlags": max(1, h)})

        result = {
            "Horizon_h": h,
            "alpha": model.params.iloc[0],
            "beta": model.params.iloc[1],
            "beta_tstat": model.tvalues.iloc[1],
            "beta_pval": model.pvalues.iloc[1],
            "R2": model.rsquared,
            "R2_adj": model.rsquared_adj,
            "N": len(data),
        }
        proxy_rows.append(result)

        sig = "***" if result["beta_pval"] < 0.01 else "**" if result["beta_pval"] < 0.05 else "ns"
        print(f"  h={h:2d}: β={result['beta']:.6f} (t={result['beta_tstat']:.2f}, p={result['beta_pval']:.4f}) {sig}"
              f" | R²={result['R2']:.4f}")

    return pd.DataFrame(proxy_rows)


def rolling_correlation(df):
    """Compute rolling correlations between NEPSE and India markets."""
    print(f"\n{'─'*60}")
    print("4. Rolling Correlations")

    results = {}

    for window in [22, 63]:
        # Returns correlation
        corr_ret = df["NEPSE_ret"].rolling(window).corr(df["NIFTY_ret"])
        results[f"Ret_Corr_{window}d"] = corr_ret

        # NEPSE RV vs India VIX
        corr_vol = df["NEPSE_rv"].rolling(window).corr(df["IndiaVIX_Close"])
        results[f"Vol_Corr_{window}d"] = corr_vol

        avg_ret = corr_ret.dropna().mean()
        avg_vol = corr_vol.dropna().mean()
        print(f"  {window}-day avg — Returns: {avg_ret:.3f}, Vol-VIX: {avg_vol:.3f}")

    return results


def main():
    print("=" * 60)
    print("NEPSE–India Spillover Analysis")
    print("=" * 60)

    if not os.path.exists(ALIGNED_FILE):
        print(f"ERROR: Aligned dataset not found: {ALIGNED_FILE}")
        print("Run scripts/download_external_data.py first.")
        return

    df = load_aligned()
    print(f"Aligned observations: {len(df)}")
    print(f"Date range: {df['Date'].iloc[0].date()} → {df['Date'].iloc[-1].date()}")
    print(f"NEPSE return obs: {df['NEPSE_ret'].dropna().shape[0]}")
    print(f"India VIX obs: {df['IndiaVIX_Close'].dropna().shape[0]}")

    # ── 1. Granger Causality ──────────────────────────────────────
    gc_df = granger_causality(df, max_lag=10)
    gc_path = os.path.join(BASE_DIR, "table_granger_causality.csv")
    gc_df.to_csv(gc_path, index=False)
    print(f"  ✅ Saved → table_granger_causality.csv")

    # ── 2. VAR Analysis ───────────────────────────────────────────
    try:
        var_results, irf, var_data = var_analysis(df)
    except Exception as e:
        print(f"  VAR analysis error: {e}")
        var_results, irf = None, None

    # ── 3. India VIX Proxy ────────────────────────────────────────
    proxy_df = india_vix_proxy(df)
    proxy_path = os.path.join(BASE_DIR, "table_india_vix_predictive.csv")
    proxy_df.to_csv(proxy_path, index=False)
    print(f"  ✅ Saved → table_india_vix_predictive.csv")

    # ── 4. Rolling Correlations ───────────────────────────────────
    corr_results = rolling_correlation(df)

    # ── Generate Figures ──────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("Generating spillover figures...")

    fig, axes = plt.subplots(3, 1, figsize=(16, 14), dpi=150)
    fig.suptitle("NEPSE–India Market Spillover Analysis",
                 fontsize=14, fontweight="bold", y=0.98)

    dates = df["Date"]

    # Panel 1: NEPSE RV vs India VIX (normalized)
    ax1 = axes[0]
    nepse_rv_norm = df["NEPSE_rv"] / df["NEPSE_rv"].std()
    india_vix_norm = df["IndiaVIX_Close"] / df["IndiaVIX_Close"].std()
    ax1.plot(dates, nepse_rv_norm, color="#e63946", linewidth=0.6, label="NEPSE RV (normalized)", alpha=0.8)
    ax1.plot(dates, india_vix_norm, color="#457b9d", linewidth=0.6, label="India VIX (normalized)", alpha=0.8)
    ax1.set_title("NEPSE Realized Volatility vs India VIX (Standardized)")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Panel 2: Rolling return correlations
    ax2 = axes[1]
    if "Ret_Corr_22d" in corr_results:
        ax2.plot(dates, corr_results["Ret_Corr_22d"], color="#2a9d8f",
                 linewidth=0.6, label="22-day", alpha=0.8)
    if "Ret_Corr_63d" in corr_results:
        ax2.plot(dates, corr_results["Ret_Corr_63d"], color="#264653",
                 linewidth=0.8, label="63-day", alpha=0.8)
    ax2.axhline(y=0, color="gray", linewidth=0.5, linestyle="--")
    ax2.set_title("Rolling Correlation: NEPSE Returns vs NIFTY Returns")
    ax2.set_ylabel("Correlation")
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    # Panel 3: Rolling volatility correlation
    ax3 = axes[2]
    if "Vol_Corr_22d" in corr_results:
        ax3.plot(dates, corr_results["Vol_Corr_22d"], color="#e9c46a",
                 linewidth=0.6, label="22-day", alpha=0.8)
    if "Vol_Corr_63d" in corr_results:
        ax3.plot(dates, corr_results["Vol_Corr_63d"], color="#f4a261",
                 linewidth=0.8, label="63-day", alpha=0.8)
    ax3.axhline(y=0, color="gray", linewidth=0.5, linestyle="--")
    ax3.set_title("Rolling Correlation: NEPSE RV vs India VIX")
    ax3.set_ylabel("Correlation")
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)

    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.xaxis.set_major_locator(mdates.YearLocator(2))

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig_path = os.path.join(BASE_DIR, "spillover_analysis.png")
    fig.savefig(fig_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✅ Saved → spillover_analysis.png")

    # IRF figure
    if irf is not None:
        try:
            fig2 = irf.plot(orth=False, response="NEPSE_rv", signif=0.05)
            fig2.suptitle("Impulse Response: Shock → NEPSE Realized Volatility", fontsize=12)
            fig2.savefig(os.path.join(BASE_DIR, "irf_nepse_rv.png"), dpi=150, bbox_inches="tight")
            plt.close(fig2)
            print(f"  ✅ Saved → irf_nepse_rv.png")
        except Exception as e:
            print(f"  IRF plot error: {e}")

    print(f"\n{'═'*60}")
    print("Spillover analysis complete.")


if __name__ == "__main__":
    main()
