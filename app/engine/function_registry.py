import math
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats


def pearson_correlation(df: pd.DataFrame, x: str, y: str) -> dict[str, Any]:
    valid = df[[x, y]].dropna()
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
    stat, p_value = scipy_stats.ttest_ind(g1, g2, equal_var=False, nan_policy="omit")

    return {
        "test": "independent_t_test",
        "statistic": float(stat),
        "p_value": float(p_value),
        "n": int(len(valid)),
        "group_a": str(groups[0]),
        "group_b": str(groups[1]),
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
    return {
        "test": "chi_square_independence",
        "statistic": float(chi_sq),
        "p_value": p_value,
        "dof": dof,
        "n": int(len(valid)),
    }


def shapiro_wilk(df: pd.DataFrame, x: str) -> dict[str, Any]:
    valid = df[x].dropna().astype(float)
    stat, p_value = scipy_stats.shapiro(valid)
    return {
        "test": "shapiro_wilk",
        "statistic": float(stat),
        "p_value": float(p_value),
        "n": int(len(valid)),
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
    "shapiro_wilk": shapiro_wilk,
}


def has_function(name: str) -> bool:
    return name in FUNCTION_REGISTRY


def execute_function(name: str, df: pd.DataFrame, kwargs: dict[str, Any]) -> dict[str, Any]:
    return FUNCTION_REGISTRY[name](df=df, **kwargs)
