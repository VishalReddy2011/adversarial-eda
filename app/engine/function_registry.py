import math
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats


def pearson_correlation(df: pd.DataFrame, x: str, y: str) -> dict[str, Any]:
    valid = df[[x, y]].dropna()
    if len(valid) < 3 or valid[x].nunique(dropna=True) <= 1 or valid[y].nunique(dropna=True) <= 1:
        return {
            "test": "pearson_correlation",
            "statistic": None,
            "p_value": None,
            "n": int(len(valid)),
            "note": "Requires at least 3 paired rows and non-constant numeric columns",
        }
    stat = float(np.corrcoef(valid[x], valid[y])[0, 1]) if len(valid) > 1 else 0.0
    p_value = float(scipy_stats.pearsonr(valid[x], valid[y]).pvalue) if len(valid) > 2 else corr_pvalue_normal_approx(stat, len(valid))
    return {
        "test": "pearson_correlation",
        "statistic": stat,
        "p_value": p_value,
        "n": int(len(valid)),
    }


def spearman_correlation(df: pd.DataFrame, x: str, y: str) -> dict[str, Any]:
    valid = df[[x, y]].dropna()
    if len(valid) < 3 or valid[x].nunique(dropna=True) <= 1 or valid[y].nunique(dropna=True) <= 1:
        return {
            "test": "spearman_correlation",
            "statistic": None,
            "p_value": None,
            "n": int(len(valid)),
            "note": "Requires at least 3 paired rows and non-constant numeric columns",
        }
    rx = valid[x].rank(method="average")
    ry = valid[y].rank(method="average")
    stat = float(np.corrcoef(rx, ry)[0, 1]) if len(valid) > 1 else 0.0
    p_value = float(scipy_stats.spearmanr(valid[x], valid[y]).pvalue) if len(valid) > 2 else corr_pvalue_normal_approx(stat, len(valid))
    return {
        "test": "spearman_correlation",
        "statistic": stat,
        "p_value": p_value,
        "n": int(len(valid)),
    }


def independent_t_test(df: pd.DataFrame, numeric: str, group: str) -> dict[str, Any]:
    valid = df[[numeric, group]].dropna()
    groups = list(valid[group].unique())
    if len(groups) != 2:
        return {
            "test": "independent_t_test",
            "statistic": np.nan,
            "p_value": 1.0,
            "n": int(len(valid)),
            "note": "Requires exactly 2 groups",
        }

    g1 = valid[valid[group] == groups[0]][numeric].astype(float)
    g2 = valid[valid[group] == groups[1]][numeric].astype(float)
    if len(g1) < 2 or len(g2) < 2:
        return {
            "test": "independent_t_test",
            "statistic": np.nan,
            "p_value": 1.0,
            "n": int(len(valid)),
            "group_a": str(groups[0]),
            "group_b": str(groups[1]),
            "note": "Requires at least 2 observations in each group",
        }
    stat, p_value = scipy_stats.ttest_ind(g1, g2, equal_var=False, nan_policy="omit")
    pooled_sd = math.sqrt(((len(g1) - 1) * float(g1.var(ddof=1)) + (len(g2) - 1) * float(g2.var(ddof=1))) / (len(g1) + len(g2) - 2))
    cohen_d = (float(g1.mean()) - float(g2.mean())) / pooled_sd if pooled_sd else 0.0

    return {
        "test": "independent_t_test",
        "statistic": float(stat),
        "p_value": float(p_value),
        "n": int(len(valid)),
        "group_a": str(groups[0]),
        "group_b": str(groups[1]),
        "group_a_n": int(len(g1)),
        "group_b_n": int(len(g2)),
        "cohen_d": float(cohen_d),
    }


def chi_square_independence(df: pd.DataFrame, x: str, y: str) -> dict[str, Any]:
    valid = df[[x, y]].dropna()
    contingency = pd.crosstab(valid[x], valid[y]).astype(float)
    observed = contingency.values
    row_sums = observed.sum(axis=1, keepdims=True)
    col_sums = observed.sum(axis=0, keepdims=True)
    total = observed.sum()
    expected = row_sums @ col_sums / total if total else np.zeros_like(observed)

    with np.errstate(divide="ignore", invalid="ignore"):
        chi_sq = np.nansum((observed - expected) ** 2 / np.where(expected == 0, np.nan, expected))

    dof = int((observed.shape[0] - 1) * (observed.shape[1] - 1)) if observed.size else 0
    p_value = float(scipy_stats.chi2.sf(chi_sq, dof)) if dof > 0 else None
    min_dim = min(observed.shape) - 1 if observed.size else 0
    cramers_v = math.sqrt(chi_sq / (total * min_dim)) if total and min_dim > 0 else None
    return {
        "test": "chi_square_independence",
        "statistic": float(chi_sq),
        "p_value": p_value,
        "dof": dof,
        "n": int(len(valid)),
        "cramers_v": float(cramers_v) if cramers_v is not None else None,
    }


def shapiro_wilk(df: pd.DataFrame, x: str) -> dict[str, Any]:
    valid = df[x].dropna().astype(float)
    if len(valid) < 3:
        return {
            "test": "shapiro_wilk",
            "statistic": None,
            "p_value": None,
            "n": int(len(valid)),
            "note": "Requires at least 3 observations",
        }
    stat, p_value = scipy_stats.shapiro(valid)
    return {
        "test": "shapiro_wilk",
        "statistic": float(stat),
        "p_value": float(p_value),
        "n": int(len(valid)),
    }


def linear_regression(df: pd.DataFrame, x: str, y: str) -> dict[str, Any]:
    valid = df[[x, y]].dropna()
    if len(valid) < 3 or valid[x].nunique(dropna=True) <= 1 or valid[y].nunique(dropna=True) <= 1:
        return {
            "test": "linear_regression",
            "statistic": None,
            "p_value": None,
            "n": int(len(valid)),
            "note": "Requires at least 3 paired rows and non-constant numeric columns",
        }

    result = scipy_stats.linregress(valid[x].astype(float), valid[y].astype(float))
    return {
        "test": "linear_regression",
        "statistic": float(result.slope),
        "slope": float(result.slope),
        "intercept": float(result.intercept),
        "r_value": float(result.rvalue),
        "r_squared": float(result.rvalue**2),
        "p_value": float(result.pvalue),
        "std_err": float(result.stderr),
        "n": int(len(valid)),
        "predictor": x,
        "target": y,
    }


def corr_pvalue_normal_approx(corr: float, n: int) -> float | None:
    if n <= 3:
        return None
    bounded = max(min(corr, 0.999999), -0.999999)
    t_stat = bounded * math.sqrt((n - 2) / (1 - bounded * bounded))
    return float(math.erfc(abs(t_stat) / math.sqrt(2)))


FUNCTION_REGISTRY = {
    "pearson_correlation": pearson_correlation,
    "spearman_correlation": spearman_correlation,
    "independent_t_test": independent_t_test,
    "chi_square_independence": chi_square_independence,
    "linear_regression": linear_regression,
    "shapiro_wilk": shapiro_wilk,
}


def has_function(name: str) -> bool:
    return name in FUNCTION_REGISTRY


def execute_function(name: str, df: pd.DataFrame, kwargs: dict[str, Any]) -> dict[str, Any]:
    return FUNCTION_REGISTRY[name](df=df, **kwargs)
