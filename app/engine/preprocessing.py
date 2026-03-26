import pandas as pd

from app.core.models import CleaningPlan


def apply_preprocessing(df: pd.DataFrame, plan: CleaningPlan) -> pd.DataFrame:
    out = df.copy()

    for conversion in plan.type_conversions:
        if conversion.target_dtype.startswith("float") or conversion.target_dtype.startswith("int"):
            out[conversion.column] = pd.to_numeric(out[conversion.column], errors="coerce")
            out[conversion.column] = out[conversion.column].astype(conversion.target_dtype)
        else:
            out[conversion.column] = out[conversion.column].astype(conversion.target_dtype)

    for strategy in plan.fill_strategy:
        col = strategy.column
        if strategy.method == "mean":
            out[col] = out[col].fillna(out[col].mean())
        elif strategy.method == "median":
            out[col] = out[col].fillna(out[col].median())
        elif strategy.method == "mode":
            mode = out[col].mode(dropna=True)
            if not mode.empty:
                out[col] = out[col].fillna(mode.iloc[0])
        elif strategy.method == "constant":
            out[col] = out[col].fillna(strategy.constant)

    if plan.remove_outliers:
        for col in plan.outlier_columns:
            q1 = out[col].quantile(0.25)
            q3 = out[col].quantile(0.75)
            iqr = q3 - q1
            if iqr <= 0:
                continue
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            out = out[(out[col] >= lower) & (out[col] <= upper)]

    return out.reset_index(drop=True)
