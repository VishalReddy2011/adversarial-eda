from typing import Any

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from app.core.models import CleaningPlan, ExecutionResult, FunctionCall, Insight, SkepticResult


class EDAState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dataset_name: str
    raw_df: pd.DataFrame
    cleaned_df: pd.DataFrame | None = None
    data_profile: dict[str, Any] = Field(default_factory=dict)
    cleaning_plan: CleaningPlan | None = None
    show_execution_order: bool = False

    insight_ledger: list[Insight] = Field(default_factory=list)
    accepted_count: int = 0
    function_calls: int = 0

    current_hypothesis: str = ""
    current_specialist: str = ""
    specialist_request_signatures: list[str] = Field(default_factory=list)
    current_function_call: FunctionCall | None = None
    current_execution_result: ExecutionResult | None = None
    current_skeptic_result: SkepticResult | None = None

    stop: bool = False
    pdf_bytes: bytes | None = None
