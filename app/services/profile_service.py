import json
from typing import Any

import numpy as np
import pandas as pd
from ydata_profiling import ProfileReport


PROFILE_TOP_VALUES = 5
PROFILE_MAX_ALERTS = 8


def _to_builtin(value: Any) -> Any:
    if not isinstance(value, (list, tuple, dict, set)):
        missing = pd.isna(value)
        if not isinstance(missing, (list, tuple, dict, set)) and bool(missing):
            return None
    if isinstance(value, np.generic):
        return value.item()
    return value


def _round_number(value: Any) -> Any:
    value = _to_builtin(value)
    if isinstance(value, float):
        return round(value, 4)
    return value


def _compact_variable_stats(name: str, stats: dict[str, Any]) -> dict[str, Any]:
    compact: dict[str, Any] = {
        "name": name,
        "type": stats.get("type"),
        "missing": _round_number(stats.get("n_missing")),
        "missing_percent": _round_number(stats.get("p_missing")),
        "distinct": _round_number(stats.get("n_distinct")),
    }

    if stats.get("type") == "Numeric":
        for key in ["mean", "std", "min", "max", "skewness"]:
            if key in stats:
                compact[key] = _round_number(stats.get(key))

        quantiles = stats.get("quantile")
        if isinstance(quantiles, dict):
            compact["quartiles"] = {
                str(key): _round_number(value)
                for key, value in quantiles.items()
                if str(key) in {"0.25", "0.5", "0.75", "25%", "50%", "75%"}
            }

    value_counts = stats.get("value_counts_without_nan") or stats.get("value_counts")
    if stats.get("type") != "Numeric" and isinstance(value_counts, dict):
        compact["top_values"] = [
            {"value": str(value), "count": _round_number(count)}
            for value, count in list(value_counts.items())[:PROFILE_TOP_VALUES]
        ]

    return {key: value for key, value in compact.items() if value is not None}


def _fallback_profile(df: pd.DataFrame) -> dict[str, Any]:
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    categorical_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    return {
        "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "missing_by_column": {col: int(df[col].isna().sum()) for col in df.columns},
        "columns": [
            {
                "name": col,
                "type": "Numeric" if col in numeric_cols else "Categorical",
                "missing": int(df[col].isna().sum()),
                "distinct": int(df[col].nunique(dropna=True)),
            }
            for col in df.columns
        ],
    }


def _build_descriptive_statistics(profile_json: dict[str, Any], columns: list[dict[str, Any]]) -> dict[str, Any]:
    table = profile_json.get("table", {})
    return {
        "overview": {
            "rows": _round_number(table.get("n")),
            "columns": _round_number(table.get("n_var")),
            "missing_cells": _round_number(table.get("n_cells_missing")),
            "missing_cells_percent": _round_number(table.get("p_cells_missing")),
            "duplicate_rows": _round_number(table.get("n_duplicates")),
            "duplicate_rows_percent": _round_number(table.get("p_duplicates")),
            "column_types": table.get("types", {}),
        },
        "columns": columns,
    }


def profile_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    profile = ProfileReport(
        df,
        title="Adversarial EDA Data Profile",
        explorative=True,
        progress_bar=False,
    )
    profile_json = json.loads(profile.to_json())

    table = profile_json.get("table", {})
    variables = profile_json.get("variables", {})
    alerts = profile_json.get("alerts", [])

    columns = [
        _compact_variable_stats(name, stats)
        for name, stats in variables.items()
        if isinstance(stats, dict)
    ]

    data_profile = _fallback_profile(df)
    data_profile.update(
        {
            "table": {
                key: _round_number(value)
                for key, value in table.items()
                if key
                in {
                    "n",
                    "n_var",
                    "n_cells_missing",
                    "p_cells_missing",
                    "n_duplicates",
                    "p_duplicates",
                    "memory_size",
                    "types",
                }
            },
            "columns": columns,
            "descriptive_statistics": _build_descriptive_statistics(profile_json, columns),
            "alerts": [
                str(alert)
                for alert in alerts[:PROFILE_MAX_ALERTS]
            ],
        }
    )
    return data_profile
