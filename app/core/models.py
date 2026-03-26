from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class Verdict(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"


class FillStrategy(BaseModel):
    column: str
    method: str
    constant: Any | None = None


class TypeConversion(BaseModel):
    column: str
    target_dtype: str


class CleaningPlan(BaseModel):
    fill_missing: bool = False
    fill_strategy: list[FillStrategy] = Field(default_factory=list)
    remove_outliers: bool = False
    outlier_columns: list[str] = Field(default_factory=list)
    type_conversions: list[TypeConversion] = Field(default_factory=list)


class FunctionCall(BaseModel):
    function_name: str

    x: str | None = None
    y: str | None = None
    numeric: str | None = None
    group: str | None = None

    hypothesis: str

    @model_validator(mode="after")
    def validate_fields_for_function(self):
        fn = self.function_name
        if fn in {"pearson_correlation", "spearman_correlation", "chi_square_independence"}:
            if not self.x or not self.y:
                raise ValueError(f"{fn} requires x and y")
        elif fn == "independent_t_test":
            if not self.numeric or not self.group:
                raise ValueError("independent_t_test requires numeric and group")
        elif fn == "shapiro_wilk":
            if not self.x:
                raise ValueError("shapiro_wilk requires x")
        return self

    def to_kwargs(self) -> dict[str, str]:
        fn = self.function_name
        if fn in {"pearson_correlation", "spearman_correlation", "chi_square_independence"}:
            return {"x": str(self.x), "y": str(self.y)}
        if fn == "independent_t_test":
            return {"numeric": str(self.numeric), "group": str(self.group)}
        if fn == "shapiro_wilk":
            return {"x": str(self.x)}
        raise ValueError(f"Unsupported function_name: {fn}")


class SpecialistCallProposal(BaseModel):
    function_name: Literal[
        "pearson_correlation",
        "spearman_correlation",
        "independent_t_test",
        "chi_square_independence",
        "shapiro_wilk",
    ]
    args: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_args_for_function(self):
        required_by_fn: dict[str, set[str]] = {
            "pearson_correlation": {"x", "y"},
            "spearman_correlation": {"x", "y"},
            "chi_square_independence": {"x", "y"},
            "independent_t_test": {"numeric", "group"},
            "shapiro_wilk": {"x"},
        }

        required = required_by_fn[self.function_name]
        provided = set(self.args.keys())
        if provided != required:
            raise ValueError(
                f"{self.function_name} requires args keys {sorted(required)} and no others; got {sorted(provided)}"
            )

        for key, value in self.args.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"args['{key}'] must be a non-empty string")
        return self


class ExecutionResult(BaseModel):
    success: bool
    function_name: str
    statistics: dict[str, float | int | str | bool | None]
    metadata: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class SkepticResult(BaseModel):
    verdict: Verdict
    reason: str


class Insight(BaseModel):
    hypothesis: str
    function_name: str
    result: ExecutionResult
    skeptic: SkepticResult
    narrative: str


class OrchestratorDecision(BaseModel):
    hypothesis: str
    specialist_name: str
    stop: bool


class OrchestratorProposal(BaseModel):
    hypothesis: str
    specialist_name: str


class TranslatorOutput(BaseModel):
    narrative: str
