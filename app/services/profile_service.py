from typing import Any

import pandas as pd


def profile_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    categorical_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    missing_by_column = {col: int(df[col].isna().sum()) for col in df.columns}
    return {
        "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "missing_by_column": missing_by_column,
    }
