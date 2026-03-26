import traceback

import pandas as pd

from app.core.models import ExecutionResult, FunctionCall
from app.engine.function_registry import execute_function, has_function


def run_function_call(df: pd.DataFrame, call: FunctionCall) -> ExecutionResult:
    if not has_function(call.function_name):
        return ExecutionResult(
            success=False,
            function_name=call.function_name,
            statistics={},
            error=f"Unknown function: {call.function_name}",
        )

    kwargs = call.to_kwargs()

    try:
        result = execute_function(call.function_name, df=df, kwargs=kwargs)
        return ExecutionResult(
            success=True,
            function_name=call.function_name,
            statistics=result,
            metadata={"kwargs": kwargs},
        )
    except Exception as exc:
        return ExecutionResult(
            success=False,
            function_name=call.function_name,
            statistics={},
            metadata={"kwargs": kwargs},
            error=f"{exc}\n{traceback.format_exc()}",
        )
