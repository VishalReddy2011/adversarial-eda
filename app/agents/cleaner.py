from typing import Any

import pandas as pd

from app.core.models import CleaningPlan, FillStrategy, TypeConversion


def build_cleaning_plan(profile: dict[str, Any], df: pd.DataFrame) -> CleaningPlan:
    _ = profile
    fill_strategy: list[FillStrategy] = []
    type_conversions: list[TypeConversion] = []

    for col in df.columns:
        series = df[col]
        if series.isna().any():
            if pd.api.types.is_numeric_dtype(series):
                fill_strategy.append(FillStrategy(column=col, method="median"))
            else:
                fill_strategy.append(FillStrategy(column=col, method="mode"))

        if pd.api.types.is_object_dtype(series):
            numeric_conversion = pd.to_numeric(series, errors="coerce")
            converted_ratio = float(numeric_conversion.notna().mean())
            if converted_ratio > 0.95:
                type_conversions.append(TypeConversion(column=col, target_dtype="float64"))

    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    outlier_columns = []
    for col in numeric_cols:
        q1 = float(df[col].quantile(0.25))
        q3 = float(df[col].quantile(0.75))
        iqr = q3 - q1
        if iqr <= 0:
            continue
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outlier_ratio = float(((df[col] < lower) | (df[col] > upper)).mean())
        if outlier_ratio > 0.05:
            outlier_columns.append(col)

    return CleaningPlan(
        fill_missing=bool(fill_strategy),
        fill_strategy=fill_strategy,
        remove_outliers=bool(outlier_columns),
        outlier_columns=outlier_columns,
        type_conversions=type_conversions,
    )
