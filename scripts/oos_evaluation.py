"""
Out-of-Sample Forecast Evaluation for NEPSE Volatility
========================================================
Expanding-window 1-step-ahead volatility forecasts with:
- Loss functions: MSE, MAE, QLIKE
- Mincer-Zarnowitz regressions
- Diebold-Mariano pairwise tests

Train: start → 2021-12-31
Test:  2022-01-01 → end
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

# ── Configuration ─────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
NEPSE_FILE = os.path.join(BASE_DIR, "nepse_index_history.csv")
RANGE_VOL_FILE = os.path.join(DATA_DIR, "data_range_based_volatility.csv")

SPLIT_DATE = "2022-01-01"
OHLC_START = "2016-06-06"  # For range-based models


# ── Loss Functions ────────────────────────────────────────────────────

def mse(forecast, realized):
    """Mean Squared Error."""
    return np.mean((forecast - realized) ** 2)

def mae(forecast, realized):
    """Mean Absolute Error."""
    return np.mean(np.abs(forecast - realized))

def qlike(forecast_var, realized_var):
    """
    QLIKE loss: L = ln(σ²_f) + σ²_r / σ²_f
    Robust to noisy volatility proxies (Patton, 2011).
    """
    # Ensure positive values
    mask = (forecast_var > 0) & (realized_var > 0)
    f = forecast_var[mask]
    r = realized_var[mask]
    return np.mean(np.log(f) + r / f)


def mincer_zarnowitz(forecast, realized):
    """
    Mincer-Zarnowitz regression: RV = α + β·Forecast + ε
    Test H0: α=0, β=1 (forecast efficiency).
    Returns: α, β, R², F-test p-value for joint H0.
    """
    X = sm.add_constant(forecast)
    model = sm.OLS(realized, X).fit()

    # Joint test: α=0, β=1
    try:
        f_test = model.f_test("const = 0, x1 = 1")
        f_pval = float(f_test.pvalue)
    except Exception:
        f_pval = np.nan

    return {
        "alpha": model.params[0],
        "beta": model.params[1],
        "R2": model.rsquared,
        "alpha_pval": model.pvalues[0],
        "beta_pval": model.pvalues[1],
        "F_joint_pval": f_pval,
    }


def diebold_mariano(e1, e2, h=1):
    """
    Diebold-Mariano test for equal predictive accuracy.
    H0: E[d_t] = 0, where d_t = e1²_t - e2²_t (using squared errors).
    Returns: DM statistic and p-value.
    Positive DM → model 2 is better. Negative DM → model 1 is better.
    """
    d = e1 ** 2 - e2 ** 2
    d_mean = np.mean(d)
    n = len(d)

    # HAC variance (Newey-West with h-1 lags)
    gamma_0 = np.var(d, ddof=1)
    gamma_sum = 0
    for k in range(1, h):
        gamma_k = np.cov(d[:-k], d[k:])[0, 1] if k < n else 0
        gamma_sum += 2 * gamma_k

    var_d = (gamma_0 + gamma_sum) / n
    if var_d <= 0:
        return np.nan, np.nan

    dm_stat = d_mean / np.sqrt(var_d)
    p_value = 2 * sp_stats.norm.sf(np.abs(dm_stat))

    return dm_stat, p_value


# ── GARCH Expanding Window Forecast ──────────────────────────────────

def garch_expanding_forecast(returns, split_idx, vol_type, dist, o_param=0):
    """
    Expanding-window 1-step-ahead GARCH forecast.
    Re-estimates every 22 days for computational efficiency.
    """
    n = len(returns)
    forecasts = np.full(n, np.nan)
    last_result = None
    refit_interval = 22  # Re-estimate every month

    for t in range(split_idx, n):
        # Re-estimate parameters periodically
        if last_result is None or (t - split_idx) % refit_interval == 0:
            train_raw = returns[1:t] * 100  # Skip index 0 (NaN from log return)

            # Drop any remaining NaN/inf
            train = pd.Series(train_raw).dropna()
            train = train[np.isfinite(train)]
            if len(train) < 100:
                continue

            if vol_type == "GJRGARCH":
                am = arch_model(train.values, vol="GARCH", p=1, o=1, q=1, dist=dist,
                                mean="Constant", rescale=False)
            else:
                am = arch_model(train.values, vol=vol_type, p=1, q=1, dist=dist,
                                mean="Constant", rescale=False)
            try:
                last_result = am.fit(disp="off", show_warning=False)
            except Exception:
                continue

        # 1-step-ahead forecast
        try:
            fcast = last_result.forecast(horizon=1, reindex=False)
            # Variance forecast (undo percentage scaling: divide by 100²)
            forecasts[t] = fcast.variance.iloc[-1, 0] / 10000
        except Exception:
            pass

    return forecasts


def main():
    print("=" * 70)
    print("NEPSE Out-of-Sample Volatility Forecast Evaluation")
    print("=" * 70)

    # ── Load NEPSE Data ───────────────────────────────────────────
    df = pd.read_csv(NEPSE_FILE)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    df["log_return"] = np.log(df["Close"] / df["Close"].shift(1))

    # Realized variance proxy: squared log-return
    df["rv_daily"] = df["log_return"] ** 2

    # Rolling realized variance (22-day)
    df["rv_22d"] = df["log_return"].rolling(22).var()

    # Find split point
    split_mask = df["Date"] >= SPLIT_DATE
    split_idx = split_mask.idxmax()
    n_test = split_mask.sum()

    print(f"Total observations: {len(df)}")
    print(f"Train: {df['Date'].iloc[1].date()} → {df['Date'].iloc[split_idx-1].date()} ({split_idx-1} obs)")
    print(f"Test:  {df['Date'].iloc[split_idx].date()} → {df['Date'].iloc[-1].date()} ({n_test} obs)")

    test_dates = df.loc[split_mask, "Date"].values
    test_rv = df.loc[split_mask, "rv_daily"].values  # Daily realized variance (r²)
    test_rv_22d = df.loc[split_mask, "rv_22d"].values

    # ── Forecast Models ───────────────────────────────────────────
    forecasts = {}
    returns = df["log_return"].values

    # 1. Historical RV (22-day rolling)
    print(f"\n{'─'*70}")
    print("Computing forecasts...")

    hist_rv = df["log_return"].rolling(22).var().shift(1)  # Lagged 1 day
    forecasts["HistRV_22d"] = hist_rv.loc[split_mask].values
    print("  HistRV_22d: done")

    # 2. GARCH models (top 3 from expanded estimation)
    garch_specs = [
        ("GJRGARCH", "skewt", "GJR-GARCH-SkewT"),
        ("GARCH", "skewt", "GARCH-SkewT"),
        ("EGARCH", "skewt", "EGARCH-SkewT"),
        ("GARCH", "t", "GARCH-t"),
    ]

    for vol_type, dist, label in garch_specs:
        print(f"  {label}: forecasting...", end=" ", flush=True)
        fcast = garch_expanding_forecast(returns, split_idx, vol_type, dist)
        forecasts[label] = fcast[split_mask]
        valid = np.isfinite(fcast[split_mask]).sum()
        print(f"done ({valid}/{n_test} valid)")

    # 3. Range-based models (if OHLC available in test period)
    range_df = None
    if os.path.exists(RANGE_VOL_FILE):
        range_df = pd.read_csv(RANGE_VOL_FILE)
        range_df["Date"] = pd.to_datetime(range_df["Date"])

        for est in ["Parkinson_22d", "GarmanKlass_22d", "YangZhang_22d"]:
            if est in range_df.columns:
                # Merge on date and extract test period
                merged = df[["Date"]].merge(range_df[["Date", est]], on="Date", how="left")
                # Use previous day's estimate as forecast (lagged)
                merged[f"{est}_lag"] = merged[est].shift(1)
                # Convert annualized vol to daily variance: (vol/sqrt(252))²
                merged[f"{est}_var"] = (merged[f"{est}_lag"] / np.sqrt(252)) ** 2
                forecasts[est] = merged.loc[split_mask, f"{est}_var"].values
                print(f"  {est}: done")

    # ── Evaluate ──────────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("Loss Function Evaluation (forecast variance vs realized r²)")

    eval_rows = []
    errors = {}  # Store for DM tests

    for model_name, fcast in forecasts.items():
        mask = np.isfinite(fcast) & np.isfinite(test_rv)
        if mask.sum() < 50:
            print(f"  {model_name}: too few valid obs ({mask.sum()}), skipping")
            continue

        f = fcast[mask]
        r = test_rv[mask]

        mse_val = mse(f, r)
        mae_val = mae(f, r)
        qlike_val = qlike(f, r)

        eval_rows.append({
            "Model": model_name,
            "N_Valid": mask.sum(),
            "MSE": mse_val,
            "MAE": mae_val,
            "QLIKE": qlike_val,
        })
        errors[model_name] = f - r  # Forecast errors

    eval_df = pd.DataFrame(eval_rows).sort_values("QLIKE")
    eval_path = os.path.join(BASE_DIR, "table_oos_forecast_comparison.csv")
    eval_df.to_csv(eval_path, index=False)
    print(eval_df.to_string(index=False))
    print(f"  ✅ Saved → table_oos_forecast_comparison.csv")

    # ── Mincer-Zarnowitz ──────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("Mincer-Zarnowitz Regressions (RV = α + β·Forecast)")

    mz_rows = []
    for model_name, fcast in forecasts.items():
        mask = np.isfinite(fcast) & np.isfinite(test_rv)
        if mask.sum() < 50:
            continue
        mz = mincer_zarnowitz(fcast[mask], test_rv[mask])
        mz["Model"] = model_name
        mz_rows.append(mz)

    mz_df = pd.DataFrame(mz_rows)
    mz_path = os.path.join(BASE_DIR, "table_mincer_zarnowitz.csv")
    mz_df.to_csv(mz_path, index=False)
    print(mz_df[["Model", "alpha", "beta", "R2", "F_joint_pval"]].to_string(index=False))
    print(f"  ✅ Saved → table_mincer_zarnowitz.csv")

    # ── Diebold-Mariano Tests ─────────────────────────────────────
    print(f"\n{'─'*70}")
    print("Diebold-Mariano Pairwise Tests")

    model_names = list(errors.keys())
    dm_rows = []
    for i in range(len(model_names)):
        for j in range(i + 1, len(model_names)):
            m1, m2 = model_names[i], model_names[j]
            e1 = errors[m1]
            e2 = errors[m2]

            # Align lengths
            min_len = min(len(e1), len(e2))
            e1_a = e1[:min_len]
            e2_a = e2[:min_len]

            mask = np.isfinite(e1_a) & np.isfinite(e2_a)
            if mask.sum() < 50:
                continue

            dm_stat, dm_pval = diebold_mariano(e1_a[mask], e2_a[mask])
            better = m1 if dm_stat < 0 else m2
            dm_rows.append({
                "Model_1": m1,
                "Model_2": m2,
                "DM_Stat": dm_stat,
                "p_value": dm_pval,
                "Better": better,
                "Significant": "Yes" if dm_pval < 0.05 else "No",
            })

    dm_df = pd.DataFrame(dm_rows)
    dm_path = os.path.join(BASE_DIR, "table_diebold_mariano.csv")
    dm_df.to_csv(dm_path, index=False)
    if not dm_df.empty:
        print(dm_df.to_string(index=False))
    print(f"  ✅ Saved → table_diebold_mariano.csv")

    # ── Forecast Comparison Figure ────────────────────────────────
    print(f"\n{'─'*70}")
    print("Generating forecast comparison figure...")

    fig, axes = plt.subplots(2, 1, figsize=(16, 10), dpi=150)
    fig.suptitle("NEPSE Out-of-Sample Volatility Forecast Comparison",
                 fontsize=14, fontweight="bold", y=0.98)

    test_dates_dt = pd.to_datetime(test_dates)

    # Top: Realized vs forecasted variance
    ax1 = axes[0]
    # Smooth realized variance for visualization
    rv_smooth = pd.Series(test_rv).rolling(22).mean()
    ax1.plot(test_dates_dt, rv_smooth, color="#333", linewidth=1.2,
             label="Realized (22d avg)", alpha=0.8)

    colors = ["#e63946", "#457b9d", "#2a9d8f", "#e9c46a", "#f4a261", "#264653", "#6b5b95"]
    for idx, (model_name, fcast) in enumerate(forecasts.items()):
        if model_name in ["HistRV_22d", "GJR-GARCH-SkewT", "GARCH-SkewT", "Parkinson_22d"]:
            f_smooth = pd.Series(fcast).rolling(22).mean()
            ax1.plot(test_dates_dt, f_smooth, linewidth=0.8,
                     color=colors[idx % len(colors)], label=model_name, alpha=0.7)

    ax1.set_title("Forecasted vs Realized Variance (22-day smoothed)")
    ax1.set_ylabel("Variance")
    ax1.legend(fontsize=8, loc="upper right")
    ax1.grid(True, alpha=0.3)

    # Bottom: Cumulative squared forecast error
    ax2 = axes[1]
    for idx, (model_name, fcast) in enumerate(forecasts.items()):
        mask = np.isfinite(fcast) & np.isfinite(test_rv)
        if mask.sum() < 50:
            continue
        cum_se = np.nancumsum((fcast - test_rv) ** 2)
        ax2.plot(test_dates_dt, cum_se, linewidth=0.8,
                 color=colors[idx % len(colors)], label=model_name, alpha=0.8)

    ax2.set_title("Cumulative Squared Forecast Error")
    ax2.set_ylabel("Cumulative SE")
    ax2.legend(fontsize=7, loc="upper left")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig_path = os.path.join(BASE_DIR, "oos_forecast_comparison.png")
    fig.savefig(fig_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✅ Saved → oos_forecast_comparison.png")

    print(f"\n{'═'*70}")
    print("Out-of-sample evaluation complete.")


if __name__ == "__main__":
    main()
