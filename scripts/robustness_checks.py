"""
Robustness Checks for NEPSE Volatility Research
=================================================
1. Sub-sample stability: Pre-COVID vs Post-COVID OOS evaluation
2. Alternative rolling windows: 10, 22, 44, 63 days
3. Alternative GARCH orders: GARCH(1,2), GARCH(2,1)
4. Bootstrap confidence intervals for Diebold-Mariano statistics
5. HAR-RV model (Heterogeneous Autoregressive)
6. Sensitivity to India-Nepal alignment: forward-fill vs intersection
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from arch import arch_model
from scipy import stats as sp_stats
import statsmodels.api as sm

warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
NEPSE_FILE = os.path.join(BASE_DIR, "nepse_index_history.csv")
RANGE_FILE = os.path.join(DATA_DIR, "data_range_based_volatility.csv")
ALIGNED_FILE = os.path.join(DATA_DIR, "data_aligned_nepse_india.csv")


def load_nepse():
    df = pd.read_csv(NEPSE_FILE)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    df["log_return"] = np.log(df["Close"] / df["Close"].shift(1))
    df["rv_daily"] = df["log_return"] ** 2
    return df


# ══════════════════════════════════════════════════════════════════════
# 1. SUB-SAMPLE STABILITY
# ══════════════════════════════════════════════════════════════════════

def subsample_stability(df):
    """Compare OOS forecast accuracy across Pre-COVID and Post-COVID sub-periods."""
    print(f"\n{'═'*70}")
    print("1. Sub-Sample Stability: Pre-COVID vs Post-COVID")
    print(f"{'═'*70}")

    periods = {
        "Pre-COVID (2015-2019)": ("2015-01-01", "2017-12-31", "2018-01-01", "2019-12-31"),
        "Post-COVID (2020-2026)": ("2015-01-01", "2021-12-31", "2022-01-01", "2026-12-31"),
    }

    results = []
    for label, (train_start, train_end, test_start, test_end) in periods.items():
        train = df[(df["Date"] >= train_start) & (df["Date"] <= train_end)]
        test = df[(df["Date"] >= test_start) & (df["Date"] <= test_end)]

        if len(train) < 200 or len(test) < 50:
            print(f"  {label}: Insufficient data (train={len(train)}, test={len(test)})")
            continue

        print(f"\n  {label}:")
        print(f"    Train: {train['Date'].iloc[0].date()} → {train['Date'].iloc[-1].date()} ({len(train)} obs)")
        print(f"    Test:  {test['Date'].iloc[0].date()} → {test['Date'].iloc[-1].date()} ({len(test)} obs)")

        # Fit GARCH on training data
        train_ret = train["log_return"].dropna()
        train_clean = train_ret[np.isfinite(train_ret)] * 100

        for vol_type, dist, name in [
            ("GARCH", "skewt", "GARCH-SkewT"),
            ("GARCH", "normal", "GARCH-N"),
        ]:
            try:
                am = arch_model(train_clean.values, vol=vol_type, p=1, q=1,
                                dist=dist, mean="Constant", rescale=False)
                res = am.fit(disp="off", show_warning=False)
                fcast = res.forecast(horizon=1, reindex=False)
                forecast_var = fcast.variance.iloc[-1, 0] / 10000

                # Simple evaluation: use last forecast for all test obs
                test_rv = test["rv_daily"].dropna()
                mse_val = np.mean((forecast_var - test_rv) ** 2)
                mae_val = np.mean(np.abs(forecast_var - test_rv))

                results.append({
                    "Period": label, "Model": name,
                    "Train_N": len(train), "Test_N": len(test),
                    "MSE": mse_val, "MAE": mae_val,
                })
                print(f"    {name}: MSE={mse_val:.2e}, MAE={mae_val:.6f}")
            except Exception as e:
                print(f"    {name}: Error — {e}")

        # Historical RV benchmark
        hist_rv = train["log_return"].rolling(22).var().iloc[-1]
        test_rv = test["rv_daily"].dropna()
        mse_val = np.mean((hist_rv - test_rv) ** 2)
        mae_val = np.mean(np.abs(hist_rv - test_rv))
        results.append({
            "Period": label, "Model": "HistRV_22d",
            "Train_N": len(train), "Test_N": len(test),
            "MSE": mse_val, "MAE": mae_val,
        })
        print(f"    HistRV_22d: MSE={mse_val:.2e}, MAE={mae_val:.6f}")

    return pd.DataFrame(results)


# ══════════════════════════════════════════════════════════════════════
# 2. ALTERNATIVE ROLLING WINDOWS
# ══════════════════════════════════════════════════════════════════════

def alternative_windows(df):
    """Compare range-based estimators across different rolling windows."""
    print(f"\n{'═'*70}")
    print("2. Alternative Rolling Windows for Realized Volatility")
    print(f"{'═'*70}")

    windows = [10, 22, 44, 63]
    results = []

    # Use post-2016 data for range-based
    ohlc = df[df["Date"] >= "2016-06-06"].copy()
    ohlc = ohlc.dropna(subset=["Open", "High", "Low", "Close"])

    for w in windows:
        # Close-to-close RV
        cc = ohlc["log_return"].rolling(w).std() * np.sqrt(252)

        # Parkinson
        log_hl = np.log(ohlc["High"] / ohlc["Low"])
        pk = np.sqrt((1 / (4 * np.log(2))) * (log_hl ** 2).rolling(w).mean() * 252)

        # Garman-Klass
        log_hl_sq = np.log(ohlc["High"] / ohlc["Low"]) ** 2
        log_co_sq = np.log(ohlc["Close"] / ohlc["Open"]) ** 2
        gk_daily = 0.5 * log_hl_sq - (2 * np.log(2) - 1) * log_co_sq
        gk = np.sqrt(gk_daily.rolling(w).mean().clip(lower=0) * 252)

        # Correlation between CC and range-based
        corr_pk = cc.corr(pk)
        corr_gk = cc.corr(gk)

        results.append({
            "Window": w,
            "CC_median": cc.median(),
            "Parkinson_median": pk.median(),
            "GarmanKlass_median": gk.median(),
            "Corr_CC_Parkinson": corr_pk,
            "Corr_CC_GarmanKlass": corr_gk,
            "N_valid": cc.dropna().shape[0],
        })

        print(f"  {w:2d}-day: CC={cc.median():.4f} PK={pk.median():.4f} GK={gk.median():.4f} "
              f"| ρ(CC,PK)={corr_pk:.3f} ρ(CC,GK)={corr_gk:.3f}")

    return pd.DataFrame(results)


# ══════════════════════════════════════════════════════════════════════
# 3. ALTERNATIVE GARCH ORDERS
# ══════════════════════════════════════════════════════════════════════

def alternative_garch_orders(df):
    """Fit GARCH(1,2), GARCH(2,1), GARCH(2,2) to check order sensitivity."""
    print(f"\n{'═'*70}")
    print("3. Alternative GARCH Orders")
    print(f"{'═'*70}")

    returns = df["log_return"].dropna()
    returns = returns[np.isfinite(returns)] * 100
    results = []

    specs = [
        (1, 1, "GARCH(1,1)"),
        (1, 2, "GARCH(1,2)"),
        (2, 1, "GARCH(2,1)"),
        (2, 2, "GARCH(2,2)"),
    ]

    for p, q, name in specs:
        for dist in ["skewt", "t"]:
            label = f"{name}-{dist}"
            try:
                am = arch_model(returns.values, vol="GARCH", p=p, q=q,
                                dist=dist, mean="Constant", rescale=False)
                res = am.fit(disp="off", show_warning=False)
                results.append({
                    "Model": label, "p": p, "q": q, "dist": dist,
                    "LogLik": res.loglikelihood,
                    "AIC": res.aic, "BIC": res.bic,
                    "Num_Params": res.num_params,
                })
                print(f"  {label:20s}: AIC={res.aic:.1f}  BIC={res.bic:.1f}  params={res.num_params}")
            except Exception as e:
                print(f"  {label:20s}: Error — {e}")

    return pd.DataFrame(results)


# ══════════════════════════════════════════════════════════════════════
# 4. BOOTSTRAP CONFIDENCE INTERVALS FOR DM STATISTICS
# ══════════════════════════════════════════════════════════════════════

def bootstrap_dm(df, n_boot=1000):
    """Bootstrap confidence intervals for key Diebold-Mariano test statistics."""
    print(f"\n{'═'*70}")
    print(f"4. Bootstrap Confidence Intervals for DM Statistics (B={n_boot})")
    print(f"{'═'*70}")

    # Split
    split_date = "2022-01-01"
    test = df[df["Date"] >= split_date].copy()
    test_rv = test["rv_daily"].values

    # Compute forecast errors for two key models
    # HistRV
    hist_rv = df["log_return"].rolling(22).var().shift(1)
    hist_err = hist_rv[df["Date"] >= split_date].values - test_rv

    # Parkinson (from range file)
    range_df = None
    if os.path.exists(RANGE_FILE):
        range_df = pd.read_csv(RANGE_FILE)
        range_df["Date"] = pd.to_datetime(range_df["Date"])
        merged = df[["Date"]].merge(range_df[["Date", "Parkinson_22d"]], on="Date", how="left")
        pk_var = (merged["Parkinson_22d"].shift(1) / np.sqrt(252)) ** 2
        pk_err = pk_var[df["Date"] >= split_date].values - test_rv

    if range_df is None:
        print("  Range data not available, skipping bootstrap")
        return pd.DataFrame()

    # Clean
    mask = np.isfinite(hist_err) & np.isfinite(pk_err)
    e1 = hist_err[mask]
    e2 = pk_err[mask]
    n = len(e1)

    # Original DM stat
    d = e1 ** 2 - e2 ** 2
    dm_orig = np.mean(d) / (np.std(d, ddof=1) / np.sqrt(n))

    # Bootstrap
    np.random.seed(42)
    dm_boot = np.zeros(n_boot)
    for b in range(n_boot):
        idx = np.random.randint(0, n, size=n)
        d_b = d[idx]
        dm_boot[b] = np.mean(d_b) / (np.std(d_b, ddof=1) / np.sqrt(n))

    ci_lower = np.percentile(dm_boot, 2.5)
    ci_upper = np.percentile(dm_boot, 97.5)
    boot_pval = np.mean(np.abs(dm_boot) >= np.abs(dm_orig))

    print(f"  HistRV vs Parkinson:")
    print(f"    DM statistic:   {dm_orig:.4f}")
    print(f"    95% CI:         [{ci_lower:.4f}, {ci_upper:.4f}]")
    print(f"    Bootstrap p:    {boot_pval:.4f}")
    print(f"    Conclusion:     {'Parkinson better' if dm_orig > 0 else 'HistRV better'}"
          f" {'(significant)' if boot_pval < 0.05 else '(not significant)'}")

    return pd.DataFrame([{
        "Comparison": "HistRV_vs_Parkinson",
        "DM_Original": dm_orig,
        "CI_Lower": ci_lower,
        "CI_Upper": ci_upper,
        "Bootstrap_p": boot_pval,
        "N_Boot": n_boot,
        "N_Obs": n,
    }])


# ══════════════════════════════════════════════════════════════════════
# 5. HAR-RV MODEL
# ══════════════════════════════════════════════════════════════════════

def har_rv_model(df):
    """
    Heterogeneous Autoregressive Realized Volatility (Corsi, 2009).
    RV_t+1 = β0 + β_d·RV_t^(d) + β_w·RV_t^(w) + β_m·RV_t^(m) + ε_t
    where RV^(d)=daily, RV^(w)=5-day avg, RV^(m)=22-day avg.
    """
    print(f"\n{'═'*70}")
    print("5. HAR-RV Model (Corsi, 2009)")
    print(f"{'═'*70}")

    # Compute RV components
    df = df.copy()
    df["rv_d"] = df["log_return"] ** 2  # Daily RV proxy (squared return)
    df["rv_w"] = df["rv_d"].rolling(5).mean()  # Weekly (5-day avg)
    df["rv_m"] = df["rv_d"].rolling(22).mean()  # Monthly (22-day avg)
    df["rv_target"] = df["rv_d"].shift(-1)  # 1-step-ahead target

    # Drop NaN
    har_data = df[["Date", "rv_d", "rv_w", "rv_m", "rv_target"]].dropna()

    # Split
    split_date = "2022-01-01"
    train = har_data[har_data["Date"] < split_date]
    test = har_data[har_data["Date"] >= split_date]

    print(f"  Train: {len(train)} obs | Test: {len(test)} obs")

    # In-sample fit
    X_train = sm.add_constant(train[["rv_d", "rv_w", "rv_m"]])
    y_train = train["rv_target"]
    model = sm.OLS(y_train, X_train).fit(cov_type="HAC", cov_kwds={"maxlags": 5})

    print(f"\n  In-Sample HAR-RV Regression:")
    print(f"    β_0 (const):  {model.params.iloc[0]:.6f}  (p={model.pvalues.iloc[0]:.4f})")
    print(f"    β_d (daily):  {model.params.iloc[1]:.4f}  (p={model.pvalues.iloc[1]:.4f})")
    print(f"    β_w (weekly): {model.params.iloc[2]:.4f}  (p={model.pvalues.iloc[2]:.4f})")
    print(f"    β_m (monthly):{model.params.iloc[3]:.4f}  (p={model.pvalues.iloc[3]:.4f})")
    print(f"    R²:           {model.rsquared:.4f}")
    print(f"    Adj R²:       {model.rsquared_adj:.4f}")

    # Out-of-sample forecast
    X_test = sm.add_constant(test[["rv_d", "rv_w", "rv_m"]])
    y_test = test["rv_target"]
    y_pred = model.predict(X_test)

    mse = np.mean((y_pred - y_test) ** 2)
    mae = np.mean(np.abs(y_pred - y_test))

    # Mincer-Zarnowitz
    X_mz = sm.add_constant(y_pred)
    mz = sm.OLS(y_test, X_mz).fit()

    print(f"\n  Out-of-Sample Performance:")
    print(f"    MSE:  {mse:.2e}")
    print(f"    MAE:  {mae:.6f}")
    print(f"    MZ α: {mz.params.iloc[0]:.6f}  β: {mz.params.iloc[1]:.4f}  R²: {mz.rsquared:.4f}")

    return pd.DataFrame([{
        "Model": "HAR-RV",
        "IS_R2": model.rsquared,
        "IS_AdjR2": model.rsquared_adj,
        "OOS_MSE": mse,
        "OOS_MAE": mae,
        "MZ_alpha": mz.params.iloc[0],
        "MZ_beta": mz.params.iloc[1],
        "MZ_R2": mz.rsquared,
        "beta_d": model.params.iloc[1],
        "beta_w": model.params.iloc[2],
        "beta_m": model.params.iloc[3],
        "beta_d_pval": model.pvalues.iloc[1],
        "beta_w_pval": model.pvalues.iloc[2],
        "beta_m_pval": model.pvalues.iloc[3],
    }])


# ══════════════════════════════════════════════════════════════════════
# 6. ALIGNMENT SENSITIVITY
# ══════════════════════════════════════════════════════════════════════

def alignment_sensitivity():
    """Compare intersection vs forward-fill for India-Nepal alignment."""
    print(f"\n{'═'*70}")
    print("6. Alignment Sensitivity: Intersection vs Forward-Fill")
    print(f"{'═'*70}")

    if not os.path.exists(ALIGNED_FILE):
        print("  Aligned data not found, skipping")
        return pd.DataFrame()

    # Load raw data
    nepse = pd.read_csv(NEPSE_FILE)
    nepse["Date"] = pd.to_datetime(nepse["Date"])
    nepse = nepse.set_index("Date").sort_index()

    india_vix_file = os.path.join(DATA_DIR, "data_india_vix.csv")
    if not os.path.exists(india_vix_file):
        print("  India VIX data not found, skipping")
        return pd.DataFrame()

    india = pd.read_csv(india_vix_file)
    india["Date"] = pd.to_datetime(india["Date"])
    india = india.set_index("Date").sort_index()

    # Method 1: Intersection (already done)
    common_dates = nepse.index.intersection(india.index)
    n_intersect = len(common_dates)

    # Method 2: Forward-fill — union of dates, fill gaps
    all_dates = nepse.index.union(india.index)
    nepse_ff = nepse["Close"].reindex(all_dates).ffill()
    india_ff = india["Close"].reindex(all_dates).ffill()
    ff_clean = pd.DataFrame({"NEPSE": nepse_ff, "IndiaVIX": india_ff}).dropna()
    n_ffill = len(ff_clean)

    # Compute log returns and correlation for both methods
    # Intersection
    nepse_int = nepse.loc[common_dates, "Close"]
    india_int = india.loc[common_dates, "Close"]
    ret_nepse_int = np.log(nepse_int / nepse_int.shift(1)).dropna()
    ret_india_int = np.log(india_int / india_int.shift(1)).dropna()
    corr_int = ret_nepse_int.corr(ret_india_int)

    # Forward-fill
    ret_nepse_ff = np.log(ff_clean["NEPSE"] / ff_clean["NEPSE"].shift(1)).dropna()
    ret_india_ff = np.log(ff_clean["IndiaVIX"] / ff_clean["IndiaVIX"].shift(1)).dropna()
    common_ff = ret_nepse_ff.index.intersection(ret_india_ff.index)
    corr_ff = ret_nepse_ff.loc[common_ff].corr(ret_india_ff.loc[common_ff])

    print(f"  Intersection: {n_intersect} common dates | Return corr: {corr_int:.4f}")
    print(f"  Forward-fill: {n_ffill} dates          | Return corr: {corr_ff:.4f}")
    print(f"  Difference:   {abs(corr_int - corr_ff):.4f} (small = robust)")

    return pd.DataFrame([
        {"Method": "Intersection", "N_Dates": n_intersect, "Return_Corr": corr_int},
        {"Method": "Forward-Fill", "N_Dates": n_ffill, "Return_Corr": corr_ff},
    ])


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("NEPSE Volatility Research — Robustness Checks")
    print("=" * 70)

    df = load_nepse()
    print(f"Loaded {len(df)} observations")

    all_results = {}

    # 1. Sub-sample stability
    all_results["subsample"] = subsample_stability(df)

    # 2. Alternative windows
    all_results["windows"] = alternative_windows(df)

    # 3. Alternative GARCH orders
    all_results["garch_orders"] = alternative_garch_orders(df)

    # 4. Bootstrap DM
    all_results["bootstrap_dm"] = bootstrap_dm(df, n_boot=2000)

    # 5. HAR-RV
    all_results["har_rv"] = har_rv_model(df)

    # 6. Alignment sensitivity
    all_results["alignment"] = alignment_sensitivity()

    # ── Save all results ──────────────────────────────────────────
    print(f"\n{'═'*70}")
    print("Saving Results")
    print(f"{'═'*70}")

    for name, result_df in all_results.items():
        if result_df is not None and not result_df.empty:
            path = os.path.join(BASE_DIR, f"table_robustness_{name}.csv")
            result_df.to_csv(path, index=False)
            print(f"  ✅ table_robustness_{name}.csv ({len(result_df)} rows)")

    # ── Summary figure ────────────────────────────────────────────
    print("\nGenerating robustness summary figure...")

    fig, axes = plt.subplots(2, 2, figsize=(16, 10), dpi=150)
    fig.suptitle("NEPSE Volatility — Robustness Checks Summary",
                 fontsize=14, fontweight="bold", y=0.98)

    # Panel 1: GARCH order comparison
    ax1 = axes[0, 0]
    if not all_results["garch_orders"].empty:
        garch = all_results["garch_orders"].sort_values("AIC")
        ax1.barh(garch["Model"], garch["AIC"], color="#457b9d", alpha=0.8)
        ax1.set_xlabel("AIC")
        ax1.set_title("GARCH Order Comparison", fontweight="bold", fontsize=10)
        ax1.invert_yaxis()

    # Panel 2: Window sensitivity
    ax2 = axes[0, 1]
    if not all_results["windows"].empty:
        win_df = all_results["windows"]
        x = win_df["Window"]
        ax2.plot(x, win_df["CC_median"], "o-", color="#333", label="Close-to-Close")
        ax2.plot(x, win_df["Parkinson_median"], "s-", color="#e63946", label="Parkinson")
        ax2.plot(x, win_df["GarmanKlass_median"], "^-", color="#2a9d8f", label="Garman-Klass")
        ax2.set_xlabel("Window (days)")
        ax2.set_ylabel("Median Annualized Vol")
        ax2.set_title("Window Sensitivity", fontweight="bold", fontsize=10)
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)

    # Panel 3: HAR-RV coefficients
    ax3 = axes[1, 0]
    if not all_results["har_rv"].empty:
        har = all_results["har_rv"].iloc[0]
        coefs = [har["beta_d"], har["beta_w"], har["beta_m"]]
        labels = ["Daily (β_d)", "Weekly (β_w)", "Monthly (β_m)"]
        colors = ["#e63946" if har[f"beta_{c}_pval"] < 0.05 else "#aaa"
                  for c in ["d", "w", "m"]]
        ax3.bar(labels, coefs, color=colors, alpha=0.8)
        ax3.set_ylabel("Coefficient")
        ax3.set_title(f"HAR-RV Coefficients (R²={har['IS_R2']:.3f})", fontweight="bold", fontsize=10)
        ax3.axhline(y=0, color="gray", linewidth=0.5)

    # Panel 4: Alignment sensitivity
    ax4 = axes[1, 1]
    if not all_results["alignment"].empty:
        align = all_results["alignment"]
        ax4.bar(align["Method"], align["Return_Corr"], color=["#457b9d", "#e9c46a"], alpha=0.8)
        ax4.set_ylabel("Return Correlation")
        ax4.set_title("India-Nepal Alignment Sensitivity", fontweight="bold", fontsize=10)
        for i, row in align.iterrows():
            ax4.text(i, row["Return_Corr"] + 0.001, f"n={int(row['N_Dates'])}",
                     ha="center", fontsize=9)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig_path = os.path.join(BASE_DIR, "robustness_checks_summary.png")
    fig.savefig(fig_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✅ robustness_checks_summary.png")

    print(f"\n{'═'*70}")
    print("All robustness checks complete.")


if __name__ == "__main__":
    main()
