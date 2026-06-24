"""
Expanded GARCH Model Estimation for NEPSE
==========================================
Fits 9 GARCH specifications: 3 models × 3 error distributions.
Includes standardized residual diagnostics.

Models: GARCH(1,1), EGARCH(1,1), GJR-GARCH(1,1)
Distributions: Normal, Student-t, Skewed-t
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
from statsmodels.stats.diagnostic import acorr_ljungbox

warnings.filterwarnings("ignore")

# ── Configuration ─────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEPSE_FILE = os.path.join(BASE_DIR, "nepse_index_history.csv")
DATA_DIR = os.path.join(BASE_DIR, "data")

MODELS = ["GARCH", "EGARCH", "GJRGARCH"]
DISTRIBUTIONS = ["normal", "t", "skewt"]
MODEL_LABELS = {
    ("GARCH", "normal"): "GARCH(1,1)-N",
    ("GARCH", "t"): "GARCH(1,1)-t",
    ("GARCH", "skewt"): "GARCH(1,1)-SkewT",
    ("EGARCH", "normal"): "EGARCH(1,1)-N",
    ("EGARCH", "t"): "EGARCH(1,1)-t",
    ("EGARCH", "skewt"): "EGARCH(1,1)-SkewT",
    ("GJRGARCH", "normal"): "GJR-GARCH(1,1)-N",
    ("GJRGARCH", "t"): "GJR-GARCH(1,1)-t",
    ("GJRGARCH", "skewt"): "GJR-GARCH(1,1)-SkewT",
}


def fit_garch(returns, vol_type, dist):
    """Fit a single GARCH model specification."""
    # GJR-GARCH uses GARCH with o=1 (asymmetric/threshold order)
    if vol_type == "GJRGARCH":
        am = arch_model(
            returns * 100,
            vol="GARCH",
            p=1,
            o=1,
            q=1,
            dist=dist,
            mean="Constant",
            rescale=False,
        )
    else:
        am = arch_model(
            returns * 100,
            vol=vol_type,
            p=1,
            q=1,
            dist=dist,
            mean="Constant",
            rescale=False,
        )
    result = am.fit(disp="off", show_warning=False)
    return result


def residual_diagnostics(result, label):
    """Compute standardized residual diagnostics."""
    std_resid = result.std_resid.dropna()
    n = len(std_resid)

    # Ljung-Box on standardized residuals
    lb_resid = acorr_ljungbox(std_resid, lags=[10], return_df=True)

    # Ljung-Box on squared standardized residuals
    lb_sq = acorr_ljungbox(std_resid ** 2, lags=[10], return_df=True)

    # Normality tests on standardized residuals
    jb_stat, jb_pval = sp_stats.jarque_bera(std_resid)

    return {
        "Model": label,
        "N_Resid": n,
        "Resid_Mean": std_resid.mean(),
        "Resid_Std": std_resid.std(),
        "Resid_Skew": std_resid.skew(),
        "Resid_Kurt": std_resid.kurtosis(),
        "LB_Q10_stat": lb_resid["lb_stat"].iloc[0],
        "LB_Q10_pval": lb_resid["lb_pvalue"].iloc[0],
        "LB_Q10_sq_stat": lb_sq["lb_stat"].iloc[0],
        "LB_Q10_sq_pval": lb_sq["lb_pvalue"].iloc[0],
        "JB_stat": jb_stat,
        "JB_pval": jb_pval,
        "Adequate_Resid": "Yes" if lb_resid["lb_pvalue"].iloc[0] > 0.05 else "No",
        "Adequate_ARCH": "Yes" if lb_sq["lb_pvalue"].iloc[0] > 0.05 else "No",
    }


def main():
    print("=" * 70)
    print("NEPSE Expanded GARCH Estimation (3 Models × 3 Distributions)")
    print("=" * 70)

    # Load data
    df = pd.read_csv(NEPSE_FILE)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    df["log_return"] = np.log(df["Close"] / df["Close"].shift(1))
    returns = df["log_return"].dropna()

    print(f"Observations: {len(returns)}")
    print(f"Date range: {df['Date'].iloc[1].date()} → {df['Date'].iloc[-1].date()}")

    # ── Fit all 9 specifications ──────────────────────────────────
    selection_rows = []
    diag_rows = []
    cond_vol_dict = {"Date": df["Date"].iloc[1:].values}
    all_results = {}

    for vol_type in MODELS:
        for dist in DISTRIBUTIONS:
            label = MODEL_LABELS[(vol_type, dist)]
            print(f"\n  Fitting {label}...", end=" ", flush=True)

            try:
                result = fit_garch(returns, vol_type, dist)
                all_results[(vol_type, dist)] = result

                # Model selection criteria
                row = {
                    "Model": label,
                    "Vol_Type": vol_type,
                    "Distribution": dist,
                    "LogLik": result.loglikelihood,
                    "AIC": result.aic,
                    "BIC": result.bic,
                    "Num_Params": result.num_params,
                }

                # Extract key parameters
                params = result.params
                for pname in params.index:
                    row[f"param_{pname}"] = params[pname]

                selection_rows.append(row)

                # Conditional volatility (annualized)
                cond_var = result.conditional_volatility / 100  # Undo percentage scaling
                cond_vol_dict[f"{label}_vol"] = cond_var.values

                # Diagnostics
                diag = residual_diagnostics(result, label)
                diag_rows.append(diag)

                print(f"AIC={result.aic:.1f} BIC={result.bic:.1f} ✅")

            except Exception as e:
                print(f"FAILED: {e}")
                selection_rows.append({
                    "Model": label, "Vol_Type": vol_type,
                    "Distribution": dist, "LogLik": np.nan,
                    "AIC": np.nan, "BIC": np.nan,
                })

    # ── Save model selection table ────────────────────────────────
    sel_df = pd.DataFrame(selection_rows).sort_values("AIC")
    sel_path = os.path.join(BASE_DIR, "table_garch_model_selection_expanded.csv")
    sel_df.to_csv(sel_path, index=False)
    print(f"\n{'─'*70}")
    print("Model Selection (sorted by AIC):")
    print(sel_df[["Model", "LogLik", "AIC", "BIC"]].to_string(index=False))
    print(f"  ✅ Saved → table_garch_model_selection_expanded.csv")

    # Best model
    best = sel_df.iloc[0]
    print(f"\n  🏆 Best model by AIC: {best['Model']} (AIC={best['AIC']:.1f})")

    # ── Save conditional volatility ───────────────────────────────
    os.makedirs(DATA_DIR, exist_ok=True)
    vol_df = pd.DataFrame(cond_vol_dict)
    vol_path = os.path.join(DATA_DIR, "data_garch_expanded.csv")
    vol_df.to_csv(vol_path, index=False)
    print(f"  ✅ Conditional volatility saved → data/data_garch_expanded.csv")

    # ── Save diagnostics ──────────────────────────────────────────
    diag_df = pd.DataFrame(diag_rows)
    diag_path = os.path.join(BASE_DIR, "table_garch_diagnostics.csv")
    diag_df.to_csv(diag_path, index=False)
    print(f"\n{'─'*70}")
    print("Residual Diagnostics:")
    print(diag_df[["Model", "Resid_Skew", "Resid_Kurt", "LB_Q10_pval",
                    "LB_Q10_sq_pval", "Adequate_Resid", "Adequate_ARCH"]].to_string(index=False))
    print(f"  ✅ Saved → table_garch_diagnostics.csv")

    # ── Generate diagnostic plots ─────────────────────────────────
    print(f"\n{'─'*70}")
    print("Generating diagnostic plots...")

    # Plot for the top 3 models by AIC
    top3 = sel_df.head(3)

    fig, axes = plt.subplots(3, 3, figsize=(18, 14), dpi=150)
    fig.suptitle("GARCH Standardized Residual Diagnostics (Top 3 by AIC)",
                 fontsize=14, fontweight="bold", y=0.98)

    for i, (_, model_row) in enumerate(top3.iterrows()):
        key = (model_row["Vol_Type"], model_row["Distribution"])
        if key not in all_results:
            continue
        result = all_results[key]
        std_resid = result.std_resid.dropna()
        label = model_row["Model"]

        # Time series of standardized residuals
        ax1 = axes[i, 0]
        ax1.plot(std_resid.index, std_resid, linewidth=0.3, color="#333")
        ax1.axhline(y=0, color="red", linewidth=0.5, alpha=0.5)
        ax1.axhline(y=2, color="orange", linewidth=0.5, linestyle="--", alpha=0.5)
        ax1.axhline(y=-2, color="orange", linewidth=0.5, linestyle="--", alpha=0.5)
        ax1.set_title(f"{label}: Standardized Residuals", fontsize=9)
        ax1.set_ylabel("Std. Residual")

        # Q-Q plot
        ax2 = axes[i, 1]
        sp_stats.probplot(std_resid, dist="norm", plot=ax2)
        ax2.set_title(f"{label}: Q-Q Plot", fontsize=9)
        ax2.get_lines()[0].set_markersize(1)

        # ACF of squared residuals
        ax3 = axes[i, 2]
        from statsmodels.graphics.tsaplots import plot_acf
        plot_acf(std_resid ** 2, lags=20, ax=ax3, alpha=0.05, title="")
        ax3.set_title(f"{label}: ACF of Squared Residuals", fontsize=9)
        ax3.set_ylabel("Autocorrelation")

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig_path = os.path.join(BASE_DIR, "garch_residual_diagnostics.png")
    fig.savefig(fig_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✅ Diagnostics figure → garch_residual_diagnostics.png")

    # ── Conditional volatility comparison plot ────────────────────
    fig2, ax = plt.subplots(figsize=(16, 6), dpi=150)
    dates = pd.to_datetime(vol_df["Date"])

    colors = ["#e63946", "#457b9d", "#2a9d8f", "#e9c46a", "#264653",
              "#f4a261", "#a8dadc", "#6b5b95", "#d4a5a5"]

    for idx, (_, model_row) in enumerate(sel_df.head(4).iterrows()):
        col = f"{model_row['Model']}_vol"
        if col in vol_df.columns:
            ax.plot(dates, vol_df[col], linewidth=0.7,
                    color=colors[idx % len(colors)], label=model_row["Model"], alpha=0.8)

    ax.set_title("NEPSE Conditional Volatility — Top 4 GARCH Models (Annualized)",
                 fontsize=12, fontweight="bold")
    ax.set_ylabel("Conditional Volatility (daily σ)")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    fig2_path = os.path.join(BASE_DIR, "garch_conditional_volatility_comparison.png")
    fig2.savefig(fig2_path, bbox_inches="tight")
    plt.close(fig2)
    print(f"  ✅ Volatility comparison → garch_conditional_volatility_comparison.png")

    print(f"\n{'═'*70}")
    print("Expanded GARCH estimation complete.")


if __name__ == "__main__":
    main()
