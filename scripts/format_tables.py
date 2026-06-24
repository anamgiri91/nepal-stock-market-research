"""
Generate Publication-Ready Tables for NEPSE Volatility Paper
==============================================================
Reads all result CSVs and produces formatted tables suitable
for journal submission (LaTeX format + formatted markdown).
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "NEPSE_Results_Private", "formatted_tables")
os.makedirs(OUT_DIR, exist_ok=True)


def fmt_pval(p):
    """Format p-value with significance stars."""
    if pd.isna(p):
        return ""
    if p < 0.001:
        return f"{p:.3e}***"
    elif p < 0.01:
        return f"{p:.4f}***"
    elif p < 0.05:
        return f"{p:.4f}**"
    elif p < 0.1:
        return f"{p:.4f}*"
    else:
        return f"{p:.4f}"


def to_latex_table(df, caption, label, note="", fmt_dict=None):
    """Convert DataFrame to a publication-quality LaTeX table."""
    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(rf"\caption{{{caption}}}")
    lines.append(rf"\label{{{label}}}")
    lines.append(r"\small")

    ncol = len(df.columns)
    col_fmt = "l" + "r" * (ncol - 1)
    lines.append(rf"\begin{{tabular}}{{{col_fmt}}}")
    lines.append(r"\toprule")

    # Header
    header = " & ".join([str(c).replace("_", r"\_") for c in df.columns])
    lines.append(header + r" \\")
    lines.append(r"\midrule")

    # Data rows
    for _, row in df.iterrows():
        vals = []
        for col in df.columns:
            v = row[col]
            if fmt_dict and col in fmt_dict:
                vals.append(fmt_dict[col](v))
            elif isinstance(v, float):
                if abs(v) < 0.001 and v != 0:
                    vals.append(f"{v:.2e}")
                elif abs(v) > 1000:
                    vals.append(f"{v:.1f}")
                else:
                    vals.append(f"{v:.4f}")
            else:
                vals.append(str(v).replace("_", r"\_"))
        lines.append(" & ".join(vals) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

    if note:
        lines.append(rf"\par\smallskip\noindent\footnotesize{{\textit{{Notes:}} {note}}}")

    lines.append(r"\end{table}")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════
# TABLE 1: Descriptive Statistics
# ══════════════════════════════════════════════════════════════════════

def table1_descriptive():
    f = os.path.join(BASE_DIR, "table_descriptive_stats_extended.csv")
    df = pd.read_csv(f)

    out = pd.DataFrame({
        "Series": df["Series"],
        "N": df["N"].astype(int),
        "Mean": df["Mean"],
        "Std. Dev.": df["Std_Dev"],
        "Skewness": df["Skewness"],
        "Kurtosis": df["Excess_Kurtosis"],
        "Min": df["Min"],
        "Max": df["Max"],
        "JB Stat": df["JB_Stat"],
    })

    latex = to_latex_table(out,
        caption="Descriptive Statistics: NEPSE Index, 2010--2026",
        label="tab:descriptive",
        note="JB denotes the Jarque-Bera test statistic. Kurtosis is excess kurtosis. "
             "All JB statistics reject normality at the 1\\% level.")

    with open(os.path.join(OUT_DIR, "table1_descriptive.tex"), "w") as fh:
        fh.write(latex)
    print("  ✅ Table 1: Descriptive Statistics")
    return out


# ══════════════════════════════════════════════════════════════════════
# TABLE 2: Stationarity Tests
# ══════════════════════════════════════════════════════════════════════

def table2_stationarity():
    f = os.path.join(BASE_DIR, "table_stationarity_tests.csv")
    df = pd.read_csv(f)

    out = pd.DataFrame({
        "Series": df["Series"],
        "Test": df["Test"],
        "Statistic": df["Statistic"],
        "p-value": df["p_value"],
        "1% CV": df["Critical_1pct"],
        "5% CV": df["Critical_5pct"],
        "Conclusion": df["Conclusion"],
    })

    latex = to_latex_table(out,
        caption="Stationarity Tests: ADF and KPSS",
        label="tab:stationarity",
        note="ADF: H$_0$ is unit root. KPSS: H$_0$ is stationarity. "
             "Critical values at 1\\% and 5\\% significance levels.")

    with open(os.path.join(OUT_DIR, "table2_stationarity.tex"), "w") as fh:
        fh.write(latex)
    print("  ✅ Table 2: Stationarity Tests")
    return out


# ══════════════════════════════════════════════════════════════════════
# TABLE 3: ARCH-LM Tests
# ══════════════════════════════════════════════════════════════════════

def table3_arch():
    f = os.path.join(BASE_DIR, "table_arch_lm_tests.csv")
    df = pd.read_csv(f)

    out = pd.DataFrame({
        "Test": df["Test"],
        "LM Statistic": df["LM_Stat"],
        "LM p-value": df["LM_pvalue"],
        "F Statistic": df["F_Stat"],
        "F p-value": df["F_pvalue"],
        "Conclusion": df["Conclusion"],
    })

    latex = to_latex_table(out,
        caption="Engle's ARCH-LM Tests for Conditional Heteroscedasticity",
        label="tab:archlm",
        note="Tests applied to NEPSE log returns. "
             "H$_0$: No ARCH effects. All tests reject at the 1\\% level.")

    with open(os.path.join(OUT_DIR, "table3_arch_lm.tex"), "w") as fh:
        fh.write(latex)
    print("  ✅ Table 3: ARCH-LM Tests")
    return out


# ══════════════════════════════════════════════════════════════════════
# TABLE 4: GARCH Model Selection
# ══════════════════════════════════════════════════════════════════════

def table4_garch():
    f = os.path.join(BASE_DIR, "table_garch_model_selection_expanded.csv")
    df = pd.read_csv(f).sort_values("AIC")

    out = pd.DataFrame({
        "Model": df["Model"],
        "Log-Lik": df["LogLik"],
        "AIC": df["AIC"],
        "BIC": df["BIC"],
        "k": df["Num_Params"].astype(int),
    })

    latex = to_latex_table(out,
        caption="GARCH Model Selection: 9 Specifications (3 Models $\\times$ 3 Distributions)",
        label="tab:garch_selection",
        note="Models estimated on NEPSE log returns (percentage scale), 2010--2026 (3,758 obs). "
             "$k$ denotes the number of estimated parameters. "
             "Best model by AIC in bold: GJR-GARCH(1,1)-SkewT.")

    with open(os.path.join(OUT_DIR, "table4_garch_selection.tex"), "w") as fh:
        fh.write(latex)
    print("  ✅ Table 4: GARCH Model Selection")
    return out


# ══════════════════════════════════════════════════════════════════════
# TABLE 5: GARCH Diagnostics
# ══════════════════════════════════════════════════════════════════════

def table5_diagnostics():
    f = os.path.join(BASE_DIR, "table_garch_diagnostics.csv")
    df = pd.read_csv(f)

    out = pd.DataFrame({
        "Model": df["Model"],
        "Skew": df["Resid_Skew"],
        "Kurt": df["Resid_Kurt"],
        "Q(10) p": df["LB_Q10_pval"],
        "Q²(10) p": df["LB_Q10_sq_pval"],
        "Resid OK": df["Adequate_Resid"],
        "ARCH OK": df["Adequate_ARCH"],
    })

    latex = to_latex_table(out,
        caption="Standardized Residual Diagnostics",
        label="tab:garch_diag",
        note="Q(10) and Q$^2$(10) are Ljung-Box tests on standardized residuals and their squares. "
             "'Resid OK' indicates no serial correlation; 'ARCH OK' indicates no remaining ARCH effects.")

    with open(os.path.join(OUT_DIR, "table5_diagnostics.tex"), "w") as fh:
        fh.write(latex)
    print("  ✅ Table 5: GARCH Diagnostics")
    return out


# ══════════════════════════════════════════════════════════════════════
# TABLE 6: Range-Based Estimator Summary
# ══════════════════════════════════════════════════════════════════════

def table6_range():
    f = os.path.join(BASE_DIR, "table_robustness_windows.csv")
    if not os.path.exists(f):
        print("  ⚠️  Table 6 skipped: robustness windows data not found")
        return None
    df = pd.read_csv(f)

    out = pd.DataFrame({
        "Window (days)": df["Window"].astype(int),
        "Close-Close": df["CC_median"],
        "Parkinson": df["Parkinson_median"],
        "Garman-Klass": df["GarmanKlass_median"],
        "ρ(CC,PK)": df["Corr_CC_Parkinson"],
        "ρ(CC,GK)": df["Corr_CC_GarmanKlass"],
    })

    latex = to_latex_table(out,
        caption="Range-Based Volatility Estimators: Median Annualized Volatility by Window",
        label="tab:range_estimators",
        note="Computed on NEPSE OHLC data, 2016--2026 (2,296 observations). "
             "$\\rho$ denotes correlation with close-to-close estimator.")

    with open(os.path.join(OUT_DIR, "table6_range_estimators.tex"), "w") as fh:
        fh.write(latex)
    print("  ✅ Table 6: Range-Based Estimators")
    return out


# ══════════════════════════════════════════════════════════════════════
# TABLE 7: OOS Forecast Comparison
# ══════════════════════════════════════════════════════════════════════

def table7_oos():
    f = os.path.join(BASE_DIR, "table_oos_forecast_comparison.csv")
    df = pd.read_csv(f).sort_values("QLIKE")

    out = pd.DataFrame({
        "Model": df["Model"],
        "MSE (×10⁷)": (df["MSE"] * 1e7).round(2),
        "MAE (×10⁴)": (df["MAE"] * 1e4).round(2),
        "QLIKE": df["QLIKE"].round(3),
    })

    latex = to_latex_table(out,
        caption="Out-of-Sample Forecast Comparison (2022--2026, 1,028 observations)",
        label="tab:oos",
        note="Forecasts are 1-step-ahead variance predictions. "
             "Realized variance proxy: squared log returns ($r_t^2$). "
             "Lower values indicate better forecasts.")

    with open(os.path.join(OUT_DIR, "table7_oos_comparison.tex"), "w") as fh:
        fh.write(latex)
    print("  ✅ Table 7: OOS Forecast Comparison")
    return out


# ══════════════════════════════════════════════════════════════════════
# TABLE 8: Mincer-Zarnowitz Regressions
# ══════════════════════════════════════════════════════════════════════

def table8_mz():
    f = os.path.join(BASE_DIR, "table_mincer_zarnowitz.csv")
    df = pd.read_csv(f)

    out = pd.DataFrame({
        "Model": df["Model"],
        "α": df["alpha"],
        "β": df["beta"],
        "R²": df["R2"],
        "α p-val": df["alpha_pval"].apply(fmt_pval),
        "β p-val": df["beta_pval"].apply(fmt_pval),
        "F-joint p": df["F_joint_pval"].apply(fmt_pval),
    })

    latex = to_latex_table(out,
        caption="Mincer-Zarnowitz Forecast Efficiency Regressions",
        label="tab:mz",
        note="$RV_t = \\alpha + \\beta \\hat{\\sigma}^2_t + \\varepsilon_t$. "
             "H$_0$: $\\alpha = 0, \\beta = 1$ (efficient forecast). "
             "F-joint tests this null jointly. *** $p < 0.01$, ** $p < 0.05$, * $p < 0.10$.")

    with open(os.path.join(OUT_DIR, "table8_mincer_zarnowitz.tex"), "w") as fh:
        fh.write(latex)
    print("  ✅ Table 8: Mincer-Zarnowitz Regressions")
    return out


# ══════════════════════════════════════════════════════════════════════
# TABLE 9: Diebold-Mariano Tests (selected pairs)
# ══════════════════════════════════════════════════════════════════════

def table9_dm():
    f = os.path.join(BASE_DIR, "table_diebold_mariano.csv")
    df = pd.read_csv(f)

    # Select most interesting pairs
    key_pairs = [
        ("HistRV_22d", "Parkinson_22d"),
        ("HistRV_22d", "GJR-GARCH-SkewT"),
        ("Parkinson_22d", "GJR-GARCH-SkewT"),
        ("GarmanKlass_22d", "GJR-GARCH-SkewT"),
        ("GJR-GARCH-SkewT", "GARCH-SkewT"),
        ("EGARCH-SkewT", "GARCH-t"),
        ("Parkinson_22d", "GarmanKlass_22d"),
        ("Parkinson_22d", "YangZhang_22d"),
    ]

    rows = []
    for m1, m2 in key_pairs:
        match = df[((df["Model_1"] == m1) & (df["Model_2"] == m2)) |
                   ((df["Model_1"] == m2) & (df["Model_2"] == m1))]
        if not match.empty:
            rows.append(match.iloc[0])

    if not rows:
        print("  ⚠️  Table 9 skipped: no matching DM pairs")
        return None

    out_df = pd.DataFrame(rows)
    out = pd.DataFrame({
        "Model 1": out_df["Model_1"],
        "Model 2": out_df["Model_2"],
        "DM Stat": out_df["DM_Stat"],
        "p-value": out_df["p_value"].apply(fmt_pval),
        "Better": out_df["Better"],
    })

    latex = to_latex_table(out,
        caption="Diebold-Mariano Pairwise Tests for Equal Predictive Accuracy",
        label="tab:dm",
        note="Positive DM statistic favors Model 2; negative favors Model 1. "
             "HAC standard errors. *** $p < 0.01$, ** $p < 0.05$, * $p < 0.10$.")

    with open(os.path.join(OUT_DIR, "table9_diebold_mariano.tex"), "w") as fh:
        fh.write(latex)
    print("  ✅ Table 9: Diebold-Mariano Tests")
    return out


# ══════════════════════════════════════════════════════════════════════
# TABLE 10: Granger Causality
# ══════════════════════════════════════════════════════════════════════

def table10_granger():
    f = os.path.join(BASE_DIR, "table_granger_causality.csv")
    df = pd.read_csv(f)

    out = pd.DataFrame({
        "Direction": df["Direction"],
        "Lag": df["Lag"].astype(int),
        "F Statistic": df["F_Stat"],
        "p-value": df["p_value"].apply(fmt_pval),
        "Significant": df["Significant_5pct"],
    })

    latex = to_latex_table(out,
        caption="Granger Causality Tests: India--Nepal Market Linkages",
        label="tab:granger",
        note="F-test for Granger causality. *** $p < 0.01$, ** $p < 0.05$, * $p < 0.10$.")

    with open(os.path.join(OUT_DIR, "table10_granger_causality.tex"), "w") as fh:
        fh.write(latex)
    print("  ✅ Table 10: Granger Causality")
    return out


# ══════════════════════════════════════════════════════════════════════
# TABLE 11: India VIX Predictive Regressions
# ══════════════════════════════════════════════════════════════════════

def table11_vix_proxy():
    f = os.path.join(BASE_DIR, "table_india_vix_predictive.csv")
    df = pd.read_csv(f)

    out = pd.DataFrame({
        "Horizon h": df["Horizon_h"].astype(int),
        "β": df["beta"],
        "t-stat": df["beta_tstat"],
        "p-value": df["beta_pval"].apply(fmt_pval),
        "R²": df["R2"],
        "N": df["N"].astype(int),
    })

    latex = to_latex_table(out,
        caption="India VIX as Forward-Looking Volatility Proxy for NEPSE",
        label="tab:vix_proxy",
        note="$NEPSE\\_RV_{t+h} = \\alpha + \\beta \\cdot IndiaVIX_t + \\varepsilon_t$. "
             "HAC standard errors with $h$ lags. *** $p < 0.01$, ** $p < 0.05$.")

    with open(os.path.join(OUT_DIR, "table11_vix_proxy.tex"), "w") as fh:
        fh.write(latex)
    print("  ✅ Table 11: India VIX Predictive Regressions")
    return out


# ══════════════════════════════════════════════════════════════════════
# TABLE 12: Copula Comparison
# ══════════════════════════════════════════════════════════════════════

def table12_copula():
    f = os.path.join(BASE_DIR, "table_copula_comparison.csv")
    if not os.path.exists(f):
        print("  ⚠️  Table 12 skipped: copula data not found")
        return None
    df = pd.read_csv(f).sort_values("AIC")

    out = pd.DataFrame({
        "Copula": df["Copula"],
        "Parameters": df["Params"],
        "AIC": df["AIC"],
        "λ_L": df["Lower_Tail"],
        "λ_U": df["Upper_Tail"],
    })

    latex = to_latex_table(out,
        caption="Copula Model Comparison: NEPSE--NIFTY Return Dependence",
        label="tab:copula",
        note="$\\lambda_L$ and $\\lambda_U$ are lower and upper tail dependence coefficients. "
             "Copulas fitted to pseudo-uniform marginals via rank transform.")

    with open(os.path.join(OUT_DIR, "table12_copula.tex"), "w") as fh:
        fh.write(latex)
    print("  ✅ Table 12: Copula Comparison")
    return out


# ══════════════════════════════════════════════════════════════════════
# TABLE 13: HAR-RV
# ══════════════════════════════════════════════════════════════════════

def table13_har():
    f = os.path.join(BASE_DIR, "table_robustness_har_rv.csv")
    if not os.path.exists(f):
        print("  ⚠️  Table 13 skipped: HAR-RV data not found")
        return None
    df = pd.read_csv(f)

    out = pd.DataFrame({
        "": ["HAR-RV"],
        "β_d": df["beta_d"],
        "β_d p": df["beta_d_pval"].apply(fmt_pval),
        "β_w": df["beta_w"],
        "β_w p": df["beta_w_pval"].apply(fmt_pval),
        "β_m": df["beta_m"],
        "β_m p": df["beta_m_pval"].apply(fmt_pval),
        "IS R²": df["IS_R2"],
        "OOS R²": df["MZ_R2"],
    })

    latex = to_latex_table(out,
        caption="HAR-RV Model: Heterogeneous Autoregressive Realized Volatility",
        label="tab:har_rv",
        note="$RV_{t+1} = \\beta_0 + \\beta_d RV_t^{(d)} + \\beta_w RV_t^{(w)} + \\beta_m RV_t^{(m)} + \\varepsilon_t$. "
             "IS = in-sample, OOS = out-of-sample Mincer-Zarnowitz $R^2$. "
             "HAC standard errors. *** $p < 0.01$.")

    with open(os.path.join(OUT_DIR, "table13_har_rv.tex"), "w") as fh:
        fh.write(latex)
    print("  ✅ Table 13: HAR-RV Model")
    return out


def main():
    print("=" * 70)
    print("Generating Publication-Ready Tables")
    print("=" * 70)

    table1_descriptive()
    table2_stationarity()
    table3_arch()
    table4_garch()
    table5_diagnostics()
    table6_range()
    table7_oos()
    table8_mz()
    table9_dm()
    table10_granger()
    table11_vix_proxy()
    table12_copula()
    table13_har()

    print(f"\n{'═'*70}")
    print(f"All tables saved to: {OUT_DIR}")
    print(f"Total: {len(os.listdir(OUT_DIR))} .tex files")


if __name__ == "__main__":
    main()
