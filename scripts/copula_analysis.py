"""
Copula Dependence Analysis: NEPSE–India
=========================================
Tests tail dependence and non-linear dependence structure between
NEPSE and India markets using copula models.

1. Empirical copula and rank scatter
2. Parametric copula fitting (Gaussian, Clayton, Gumbel, Frank, Student-t)
3. Tail dependence coefficients
4. Time-varying copula correlation
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp_stats
from scipy.optimize import minimize

warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ALIGNED_FILE = os.path.join(DATA_DIR, "data_aligned_nepse_india.csv")


# ── Copula Functions ──────────────────────────────────────────────────

def to_uniform(x):
    """Transform to pseudo-uniform using empirical CDF (rank transform)."""
    n = len(x)
    ranks = sp_stats.rankdata(x)
    return ranks / (n + 1)  # Avoid 0 and 1


def gaussian_copula_nll(rho, u, v):
    """Negative log-likelihood for Gaussian copula."""
    rho = np.clip(rho, -0.999, 0.999)
    x = sp_stats.norm.ppf(u)
    y = sp_stats.norm.ppf(v)
    nll = 0.5 * np.log(1 - rho**2) + (rho**2 * (x**2 + y**2) - 2 * rho * x * y) / (2 * (1 - rho**2))
    return np.sum(nll)


def student_t_copula_nll(params, u, v):
    """Negative log-likelihood for Student-t copula (approximate)."""
    rho, nu = params
    rho = np.clip(rho, -0.999, 0.999)
    nu = max(nu, 2.01)

    x = sp_stats.t.ppf(u, df=nu)
    y = sp_stats.t.ppf(v, df=nu)

    # Bivariate t density / product of marginal t densities
    from scipy.special import gammaln
    n = len(u)

    log_c = (gammaln((nu + 2) / 2) - gammaln(nu / 2) - np.log(nu * np.pi) -
             0.5 * np.log(1 - rho**2))
    kernel = -(nu + 2) / 2 * np.log(1 + (x**2 + y**2 - 2 * rho * x * y) / (nu * (1 - rho**2)))
    marginal = ((nu + 1) / 2) * (np.log(1 + x**2 / nu) + np.log(1 + y**2 / nu))

    nll = -(log_c + kernel + marginal)
    return np.sum(nll)


def clayton_copula_nll(theta, u, v):
    """Negative log-likelihood for Clayton copula (lower tail dependence)."""
    theta = max(theta, 0.001)
    n = len(u)

    log_density = (np.log(1 + theta) +
                   -(1 + theta) * (np.log(u) + np.log(v)) +
                   -(2 + 1/theta) * np.log(u**(-theta) + v**(-theta) - 1))
    return -np.sum(log_density)


def gumbel_copula_nll(theta, u, v):
    """Negative log-likelihood for Gumbel copula (upper tail dependence)."""
    theta = max(theta, 1.001)

    lu = -np.log(u)
    lv = -np.log(v)

    A = (lu**theta + lv**theta)**(1/theta)

    # Log of copula density (simplified)
    log_density = (-A + (theta - 1) * (np.log(lu) + np.log(lv)) +
                   np.log(A + theta - 1) +
                   (1/theta - 2) * np.log(lu**theta + lv**theta) -
                   np.log(u * v))

    # Filter valid
    valid = np.isfinite(log_density)
    return -np.sum(log_density[valid])


def frank_copula_nll(theta, u, v):
    """Negative log-likelihood for Frank copula (symmetric dependence)."""
    if abs(theta) < 0.001:
        theta = 0.001

    num = -theta * np.exp(-theta * (u + v)) * (1 - np.exp(-theta))
    denom = ((1 - np.exp(-theta)) - (1 - np.exp(-theta * u)) * (1 - np.exp(-theta * v)))**2

    valid = (num > 0) & (denom > 0) & np.isfinite(num) & np.isfinite(denom)
    log_density = np.log(num[valid]) - np.log(denom[valid])

    return -np.sum(log_density)


def tail_dependence(copula_type, params):
    """Compute tail dependence coefficients."""
    if copula_type == "Gaussian":
        rho = params[0]
        return {"lower": 0.0, "upper": 0.0}  # Gaussian has zero tail dependence
    elif copula_type == "Student-t":
        rho, nu = params
        # λ_L = λ_U = 2 · t_{ν+1}(-√((ν+1)(1-ρ)/(1+ρ)))
        arg = -np.sqrt((nu + 1) * (1 - rho) / (1 + rho))
        td = 2 * sp_stats.t.cdf(arg, df=nu + 1)
        return {"lower": td, "upper": td}
    elif copula_type == "Clayton":
        theta = params[0]
        return {"lower": 2**(-1/theta), "upper": 0.0}
    elif copula_type == "Gumbel":
        theta = params[0]
        return {"lower": 0.0, "upper": 2 - 2**(1/theta)}
    elif copula_type == "Frank":
        return {"lower": 0.0, "upper": 0.0}
    return {"lower": np.nan, "upper": np.nan}


def fit_copulas(u, v):
    """Fit all copula models and return comparison table."""
    results = []

    # 1. Gaussian
    try:
        res = minimize(gaussian_copula_nll, x0=0.0, args=(u, v),
                       bounds=[(-0.99, 0.99)], method="L-BFGS-B")
        rho = res.x[0]
        aic = 2 * 1 + 2 * res.fun
        bic = np.log(len(u)) * 1 + 2 * res.fun
        td = tail_dependence("Gaussian", [rho])
        results.append({"Copula": "Gaussian", "Params": f"ρ={rho:.4f}",
                        "NLL": res.fun, "AIC": aic, "BIC": bic,
                        "Lower_Tail": td["lower"], "Upper_Tail": td["upper"]})
    except Exception as e:
        results.append({"Copula": "Gaussian", "Params": f"Error: {e}"})

    # 2. Student-t
    try:
        res = minimize(student_t_copula_nll, x0=[0.0, 5.0], args=(u, v),
                       bounds=[(-0.99, 0.99), (2.01, 50)], method="L-BFGS-B")
        rho, nu = res.x
        aic = 2 * 2 + 2 * res.fun
        bic = np.log(len(u)) * 2 + 2 * res.fun
        td = tail_dependence("Student-t", [rho, nu])
        results.append({"Copula": "Student-t", "Params": f"ρ={rho:.4f}, ν={nu:.1f}",
                        "NLL": res.fun, "AIC": aic, "BIC": bic,
                        "Lower_Tail": td["lower"], "Upper_Tail": td["upper"]})
    except Exception as e:
        results.append({"Copula": "Student-t", "Params": f"Error: {e}"})

    # 3. Clayton
    try:
        res = minimize(clayton_copula_nll, x0=0.5, args=(u, v),
                       bounds=[(0.001, 20)], method="L-BFGS-B")
        theta = res.x[0]
        aic = 2 * 1 + 2 * res.fun
        bic = np.log(len(u)) * 1 + 2 * res.fun
        td = tail_dependence("Clayton", [theta])
        results.append({"Copula": "Clayton", "Params": f"θ={theta:.4f}",
                        "NLL": res.fun, "AIC": aic, "BIC": bic,
                        "Lower_Tail": td["lower"], "Upper_Tail": td["upper"]})
    except Exception as e:
        results.append({"Copula": "Clayton", "Params": f"Error: {e}"})

    # 4. Gumbel
    try:
        res = minimize(gumbel_copula_nll, x0=1.5, args=(u, v),
                       bounds=[(1.001, 20)], method="L-BFGS-B")
        theta = res.x[0]
        aic = 2 * 1 + 2 * res.fun
        bic = np.log(len(u)) * 1 + 2 * res.fun
        td = tail_dependence("Gumbel", [theta])
        results.append({"Copula": "Gumbel", "Params": f"θ={theta:.4f}",
                        "NLL": res.fun, "AIC": aic, "BIC": bic,
                        "Lower_Tail": td["lower"], "Upper_Tail": td["upper"]})
    except Exception as e:
        results.append({"Copula": "Gumbel", "Params": f"Error: {e}"})

    # 5. Frank
    try:
        res = minimize(frank_copula_nll, x0=1.0, args=(u, v),
                       bounds=[(-30, 30)], method="L-BFGS-B")
        theta = res.x[0]
        aic = 2 * 1 + 2 * res.fun
        bic = np.log(len(u)) * 1 + 2 * res.fun
        td = tail_dependence("Frank", [theta])
        results.append({"Copula": "Frank", "Params": f"θ={theta:.4f}",
                        "NLL": res.fun, "AIC": aic, "BIC": bic,
                        "Lower_Tail": td["lower"], "Upper_Tail": td["upper"]})
    except Exception as e:
        results.append({"Copula": "Frank", "Params": f"Error: {e}"})

    return pd.DataFrame(results)


def rolling_kendall_tau(x, y, window=126):
    """Rolling Kendall's tau (rank correlation) for time-varying dependence."""
    n = len(x)
    tau = np.full(n, np.nan)
    for i in range(window, n):
        t, _ = sp_stats.kendalltau(x[i-window:i], y[i-window:i])
        tau[i] = t
    return tau


def main():
    print("=" * 70)
    print("NEPSE–India Copula Dependence Analysis")
    print("=" * 70)

    if not os.path.exists(ALIGNED_FILE):
        print("ERROR: Aligned data not found. Run download_external_data.py first.")
        return

    # Load aligned data
    df = pd.read_csv(ALIGNED_FILE)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    # Compute returns
    df["NEPSE_ret"] = np.log(df["NEPSE_Close"] / df["NEPSE_Close"].shift(1))
    df["NIFTY_ret"] = np.log(df["NIFTY_Close"] / df["NIFTY_Close"].shift(1))

    # Drop NaN
    clean = df[["Date", "NEPSE_ret", "NIFTY_ret"]].dropna()
    clean = clean[np.isfinite(clean["NEPSE_ret"]) & np.isfinite(clean["NIFTY_ret"])]

    print(f"Observations: {len(clean)}")
    print(f"Date range: {clean['Date'].iloc[0].date()} → {clean['Date'].iloc[-1].date()}")

    # ── 1. Rank correlation measures ──────────────────────────────
    print(f"\n{'─'*70}")
    print("1. Rank Correlation Measures")

    pearson = clean["NEPSE_ret"].corr(clean["NIFTY_ret"])
    spearman, sp_p = sp_stats.spearmanr(clean["NEPSE_ret"], clean["NIFTY_ret"])
    kendall, kt_p = sp_stats.kendalltau(clean["NEPSE_ret"], clean["NIFTY_ret"])

    print(f"  Pearson:  {pearson:.4f}")
    print(f"  Spearman: {spearman:.4f} (p={sp_p:.4f})")
    print(f"  Kendall:  {kendall:.4f} (p={kt_p:.4f})")

    # ── 2. Transform to uniform marginals ─────────────────────────
    u = to_uniform(clean["NEPSE_ret"].values)
    v = to_uniform(clean["NIFTY_ret"].values)

    # ── 3. Fit copulas ────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("2. Copula Model Comparison")

    copula_df = fit_copulas(u, v)
    copula_df = copula_df.sort_values("AIC")

    copula_path = os.path.join(BASE_DIR, "table_copula_comparison.csv")
    copula_df.to_csv(copula_path, index=False)

    print(copula_df[["Copula", "Params", "AIC", "Lower_Tail", "Upper_Tail"]].to_string(index=False))
    print(f"  ✅ Saved → table_copula_comparison.csv")

    if not copula_df.empty and "AIC" in copula_df.columns:
        best = copula_df.dropna(subset=["AIC"]).iloc[0]
        print(f"\n  🏆 Best copula by AIC: {best['Copula']} ({best['Params']})")

    # ── 4. Time-varying dependence ────────────────────────────────
    print(f"\n{'─'*70}")
    print("3. Time-Varying Dependence (Rolling Kendall's τ)")

    tau_126 = rolling_kendall_tau(clean["NEPSE_ret"].values,
                                  clean["NIFTY_ret"].values, window=126)
    tau_252 = rolling_kendall_tau(clean["NEPSE_ret"].values,
                                  clean["NIFTY_ret"].values, window=252)

    print(f"  126-day avg τ: {np.nanmean(tau_126):.4f} (range: {np.nanmin(tau_126):.4f} to {np.nanmax(tau_126):.4f})")
    print(f"  252-day avg τ: {np.nanmean(tau_252):.4f} (range: {np.nanmin(tau_252):.4f} to {np.nanmax(tau_252):.4f})")

    # ── 5. Tail concentration analysis ────────────────────────────
    print(f"\n{'─'*70}")
    print("4. Empirical Tail Concentration")

    # Check joint extreme events
    for q in [0.05, 0.10]:
        nepse_low = clean["NEPSE_ret"] <= clean["NEPSE_ret"].quantile(q)
        nifty_low = clean["NIFTY_ret"] <= clean["NIFTY_ret"].quantile(q)
        joint_low = (nepse_low & nifty_low).sum()
        expected = q * q * len(clean)
        ratio = joint_low / expected if expected > 0 else np.nan

        nepse_high = clean["NEPSE_ret"] >= clean["NEPSE_ret"].quantile(1-q)
        nifty_high = clean["NIFTY_ret"] >= clean["NIFTY_ret"].quantile(1-q)
        joint_high = (nepse_high & nifty_high).sum()

        print(f"  {q*100:.0f}% tail:")
        print(f"    Joint lower: {joint_low} (expected under independence: {expected:.0f}, ratio: {ratio:.2f})")
        print(f"    Joint upper: {joint_high} (expected: {expected:.0f}, ratio: {joint_high/expected:.2f})")

    # ── 6. Generate figures ───────────────────────────────────────
    print(f"\n{'─'*70}")
    print("Generating copula figures...")

    fig, axes = plt.subplots(2, 2, figsize=(14, 12), dpi=150)
    fig.suptitle("NEPSE–India Copula Dependence Analysis",
                 fontsize=14, fontweight="bold", y=0.98)

    # Panel 1: Rank scatter (empirical copula)
    ax1 = axes[0, 0]
    ax1.scatter(u, v, alpha=0.15, s=3, color="#457b9d")
    ax1.set_xlabel("NEPSE Return (rank)")
    ax1.set_ylabel("NIFTY Return (rank)")
    ax1.set_title("Empirical Copula (Rank Scatter)", fontsize=10, fontweight="bold")
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.plot([0, 1], [0, 1], "k--", alpha=0.3, linewidth=0.5)

    # Panel 2: Joint return scatter
    ax2 = axes[0, 1]
    ax2.scatter(clean["NEPSE_ret"]*100, clean["NIFTY_ret"]*100, alpha=0.15, s=3, color="#e63946")
    ax2.set_xlabel("NEPSE Return (%)")
    ax2.set_ylabel("NIFTY Return (%)")
    ax2.set_title(f"Return Scatter (ρ={pearson:.3f}, τ={kendall:.3f})",
                  fontsize=10, fontweight="bold")
    ax2.axhline(0, color="gray", linewidth=0.3)
    ax2.axvline(0, color="gray", linewidth=0.3)

    # Panel 3: Rolling Kendall's tau
    ax3 = axes[1, 0]
    dates = clean["Date"].values
    ax3.plot(dates, tau_126, linewidth=0.6, color="#2a9d8f", alpha=0.8, label="126-day")
    ax3.plot(dates, tau_252, linewidth=0.9, color="#264653", alpha=0.8, label="252-day")
    ax3.axhline(0, color="gray", linewidth=0.5, linestyle="--")
    ax3.set_ylabel("Kendall's τ")
    ax3.set_title("Time-Varying Dependence", fontsize=10, fontweight="bold")
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)

    # Panel 4: Copula AIC comparison
    ax4 = axes[1, 1]
    valid_copulas = copula_df.dropna(subset=["AIC"]).sort_values("AIC")
    if not valid_copulas.empty:
        colors = ["#2a9d8f", "#457b9d", "#e63946", "#e9c46a", "#264653"]
        ax4.barh(valid_copulas["Copula"], valid_copulas["AIC"],
                 color=colors[:len(valid_copulas)], alpha=0.8)
        ax4.set_xlabel("AIC")
        ax4.set_title("Copula Model Comparison", fontsize=10, fontweight="bold")
        ax4.invert_yaxis()

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig_path = os.path.join(BASE_DIR, "copula_analysis.png")
    fig.savefig(fig_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✅ Saved → copula_analysis.png")

    print(f"\n{'═'*70}")
    print("Copula dependence analysis complete.")


if __name__ == "__main__":
    main()
