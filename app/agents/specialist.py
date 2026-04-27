import json

import pandas as pd

from app.core.models import FunctionCall, SpecialistCallProposal
from app.services.llm_client import structured
from app.services.rag import retrieve_context


ALLOWED_FUNCTIONS: dict[str, list[str]] = {
    "univariate": ["shapiro_wilk"],
    "bivariate": ["pearson_correlation", "spearman_correlation", "independent_t_test", "chi_square_independence"],
    "regression": ["linear_regression", "pearson_correlation", "spearman_correlation"],
}
ARG_KEYS_BY_FUNCTION: dict[str, list[str]] = {
    "pearson_correlation": ["x", "y"],
    "spearman_correlation": ["x", "y"],
    "chi_square_independence": ["x", "y"],
    "linear_regression": ["x", "y"],
    "independent_t_test": ["numeric", "group"],
    "shapiro_wilk": ["x"],
}
MAX_SPECIALIST_RETRIES = 3


def is_numeric(df: pd.DataFrame, col: str) -> bool:
    return col in df.columns and pd.api.types.is_numeric_dtype(df[col])


def is_categorical(df: pd.DataFrame, col: str) -> bool:
    return col in df.columns and not pd.api.types.is_numeric_dtype(df[col])


def build_args_key_rules(allowed: list[str]) -> str:
    lines: list[str] = []
    for fn in allowed:
        keys = ", ".join(ARG_KEYS_BY_FUNCTION[fn])
        if fn in {"pearson_correlation", "spearman_correlation"}:
            lines.append(f"- {fn}: args keys must be {{{keys}}}; both must be numeric columns.")
        elif fn == "linear_regression":
            lines.append("- linear_regression: args keys must be {x, y}; x is numeric predictor, y is numeric target.")
        elif fn == "independent_t_test":
            lines.append("- independent_t_test: args keys must be {numeric, group}; numeric must be numeric, group categorical.")
        elif fn == "chi_square_independence":
            lines.append("- chi_square_independence: args keys must be {x, y}; both must be categorical columns.")
        elif fn == "shapiro_wilk":
            lines.append("- shapiro_wilk: args keys must be {x}; x must be a numeric column.")
    return "\n".join(lines)


def to_function_call(proposal: SpecialistCallProposal, hypothesis: str) -> FunctionCall:
    args = proposal.args
    return FunctionCall(
        function_name=proposal.function_name,
        x=args.get("x"),
        y=args.get("y"),
        numeric=args.get("numeric"),
        group=args.get("group"),
        hypothesis=hypothesis,
    )


def valid_for_df(call: SpecialistCallProposal, df: pd.DataFrame, specialist_name: str) -> bool:
    allowed = ALLOWED_FUNCTIONS[specialist_name]
    if call.function_name not in allowed:
        return False

    args = call.args
    fn = call.function_name
    if fn in {"pearson_correlation", "spearman_correlation", "linear_regression"}:
        return is_numeric(df, args.get("x", "")) and is_numeric(df, args.get("y", ""))

    if fn == "independent_t_test":
        return is_numeric(df, args.get("numeric", "")) and is_categorical(df, args.get("group", ""))

    if fn == "chi_square_independence":
        return is_categorical(df, args.get("x", "")) and is_categorical(df, args.get("y", ""))

    if fn == "shapiro_wilk":
        return is_numeric(df, args.get("x", ""))

    return False


def invalid_reason(call: SpecialistCallProposal, specialist_name: str) -> str:
    allowed = ALLOWED_FUNCTIONS[specialist_name]
    if call.function_name not in allowed:
        return f"function_name must be one of: {', '.join(allowed)}"

    required = set(ARG_KEYS_BY_FUNCTION[call.function_name])
    provided = set(call.args.keys())
    if provided != required:
        return f"for {call.function_name}, args keys must be exactly: {', '.join(sorted(required))}"

    return "args values must use valid columns and satisfy numeric/categorical constraints"


def format_context(contexts: list[dict[str, object]]) -> str:
    if not contexts:
        return "No retrieved guidance."
    return "\n".join(
        f"{item['rank']}. {item['title']}: {item['content']}"
        for item in contexts
    )


def fallback_call(specialist_name: str, hypothesis: str, df: pd.DataFrame) -> FunctionCall:
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    categorical_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]

    if specialist_name == "regression" and len(numeric_cols) >= 2:
        return FunctionCall(
            function_name="linear_regression",
            x=numeric_cols[0],
            y=numeric_cols[1],
            hypothesis=hypothesis,
        )

    if specialist_name == "bivariate" and len(numeric_cols) >= 2:
        return FunctionCall(
            function_name="pearson_correlation",
            x=numeric_cols[0],
            y=numeric_cols[1],
            hypothesis=hypothesis,
        )

    if specialist_name == "bivariate" and len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
        return FunctionCall(
            function_name="independent_t_test",
            numeric=numeric_cols[0],
            group=categorical_cols[0],
            hypothesis=hypothesis,
        )

    if specialist_name == "bivariate" and len(categorical_cols) >= 2:
        return FunctionCall(
            function_name="chi_square_independence",
            x=categorical_cols[0],
            y=categorical_cols[1],
            hypothesis=hypothesis,
        )

    target = numeric_cols[0] if numeric_cols else str(df.columns[0])
    return FunctionCall(
        function_name="shapiro_wilk",
        x=target,
        hypothesis=hypothesis,
    )


def propose_specialist_call(specialist_name: str, hypothesis: str, df: pd.DataFrame) -> FunctionCall:
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    categorical_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    allowed = ALLOWED_FUNCTIONS[specialist_name]
    function_rules = build_args_key_rules(allowed)
    contexts = retrieve_context(
        hypothesis=hypothesis,
        k=3,
        enabled=True,
        allowed_functions=allowed,
    )

    base_prompt = (
        "You are a statistical specialist. Return ONLY JSON matching "
        "{function_name: string, args: object}. No prose.\n"
        f"Specialist: {specialist_name}\n"
        f"Allowed function_name values: {', '.join(allowed)}\n"
        f"Hypothesis to test: {hypothesis}\n"
        f"Numeric columns: {json.dumps(numeric_cols)}\n"
        f"Categorical columns: {json.dumps(categorical_cols)}\n"
        "Retrieved statistical guidance:\n"
        f"{format_context(contexts)}\n"
        "Choose one allowed function whose assumptions best match the hypothesis and available column types.\n"
        "args must contain exactly the required keys for that function and must use existing columns.\n"
        "Argument rules:\n"
        f"{function_rules}"
    )

    feedback = ""
    for _ in range(MAX_SPECIALIST_RETRIES):
        prompt = base_prompt
        if feedback:
            prompt += f"\nPrevious output was invalid: {feedback}. Correct it and return valid JSON only."

        try:
            proposal = structured(prompt, SpecialistCallProposal, agent_key=f"SPECIALIST_{specialist_name.upper()}")
        except Exception as exc:
            feedback = f"schema/parse error ({exc.__class__.__name__})"
            continue

        if valid_for_df(proposal, df, specialist_name):
            return to_function_call(proposal, hypothesis)

        feedback = invalid_reason(proposal, specialist_name)

    return fallback_call(specialist_name, hypothesis, df)
