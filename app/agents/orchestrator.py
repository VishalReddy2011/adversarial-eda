import json

import pandas as pd

from app.core.models import OrchestratorDecision, OrchestratorProposal
from app.services.llm_client import structured


MAX_ACCEPTED = 3
MAX_FUNCTION_CALLS = 5
MAX_ORCHESTRATOR_RETRIES = 5
ALLOWED_SPECIALISTS = {"univariate", "bivariate", "regression"}
MAX_PROFILE_COLUMNS = 40
MAX_PROFILE_ALERTS = 6


def _valid_non_stop_proposal(proposal: OrchestratorProposal) -> bool:
    return bool(proposal.hypothesis.strip()) and proposal.specialist_name in ALLOWED_SPECIALISTS


def _invalid_reason(proposal: OrchestratorProposal) -> str | None:
    if not proposal.hypothesis.strip():
        return "hypothesis is empty"
    if proposal.specialist_name not in ALLOWED_SPECIALISTS:
        return "specialist_name must be one of: univariate, bivariate, regression"

    text = proposal.hypothesis.lower()
    relational_markers = ["correlat", "association", "relationship", "predict", "effect", "differs", "difference"]
    if proposal.specialist_name == "univariate" and any(marker in text for marker in relational_markers):
        return "univariate is only for single-variable distribution/normality hypotheses"

    return None


def _format_number(value) -> str:
    if value is None:
        return "unknown"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def _format_column_profile(column: dict) -> str:
    name = column.get("name", "unknown")
    col_type = column.get("type", "unknown")
    missing = column.get("missing", 0)
    distinct = column.get("distinct", "unknown")

    if col_type == "Numeric":
        parts = [
            f"{name} (numeric)",
            f"missing={missing}",
            f"distinct={distinct}",
            f"mean={_format_number(column.get('mean'))}",
            f"std={_format_number(column.get('std'))}",
            f"range={_format_number(column.get('min'))}..{_format_number(column.get('max'))}",
        ]
        skewness = column.get("skewness")
        if skewness is not None:
            parts.append(f"skew={_format_number(skewness)}")
        return "- " + "; ".join(parts)

    top_values = column.get("top_values", [])
    values = ", ".join(
        f"{item.get('value')}={item.get('count')}"
        for item in top_values[:5]
        if isinstance(item, dict)
    )
    suffix = f"; values: {values}" if values else ""
    return f"- {name} ({col_type}); missing={missing}; distinct={distinct}{suffix}"


def _profile_for_prompt(data_profile: dict | None, df: pd.DataFrame) -> str:
    if not data_profile:
        data_profile = {
            "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
            "numeric_columns": [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])],
            "categorical_columns": [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])],
            "columns": [],
            "alerts": [],
        }

    shape = data_profile.get("shape", {})
    table = data_profile.get("table", {})
    numeric_columns = data_profile.get("numeric_columns", [])
    categorical_columns = data_profile.get("categorical_columns", [])
    columns = data_profile.get("columns", [])[:MAX_PROFILE_COLUMNS]
    alerts = data_profile.get("alerts", [])[:MAX_PROFILE_ALERTS]

    lines = [
        f"Rows: {shape.get('rows', table.get('n', 'unknown'))}; columns: {shape.get('columns', table.get('n_var', 'unknown'))}",
        f"Missing cells: {_format_number(table.get('p_cells_missing', 0))}; duplicate rows: {_format_number(table.get('p_duplicates', 0))}",
        f"Numeric columns: {', '.join(numeric_columns) or 'None'}",
        f"Categorical/boolean columns: {', '.join(categorical_columns) or 'None'}",
        "Column summaries:",
    ]
    lines.extend(_format_column_profile(column) for column in columns)

    if alerts:
        lines.append("Profile hints:")
        lines.extend(f"- {alert}" for alert in alerts)

    return "\n".join(lines)


def next_step(
    df: pd.DataFrame,
    accepted_count: int,
    function_calls: int,
    insight_ledger,
    data_profile: dict | None = None,
) -> OrchestratorDecision:
    if accepted_count >= MAX_ACCEPTED or function_calls >= MAX_FUNCTION_CALLS:
        return OrchestratorDecision(hypothesis="", specialist_name="", stop=True)

    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    categorical_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    profile_summary = _profile_for_prompt(data_profile, df)

    ledger_summary = []
    for item in insight_ledger[-5:]:
        ledger_summary.append(
            {
                "hypothesis": item.hypothesis,
                "verdict": item.skeptic.verdict.value,
                "note": item.narrative or item.skeptic.reason,
            }
        )

    base_prompt = (
        "You are the Orchestrator for statistical EDA. Return ONLY JSON matching "
        "{hypothesis: string, specialist_name: string}. No prose.\n"
        "specialist_name must be one of: univariate, bivariate, regression.\n"
        "Selection rules:\n"
        "- univariate: one numeric column, usually a distribution or normality hypothesis.\n"
        "- bivariate: two-column association or group-difference hypothesis.\n"
        "- regression: one numeric predictor explaining or predicting one numeric target.\n"
        "Hypothesis rules:\n"
        "- Reference existing columns only.\n"
        "- Be specific and testable in one function call.\n"
        "- Avoid repeating hypotheses already in the ledger.\n"
        "- Do not output a stop field.\n"
        "Use the data profile to prioritize columns with enough non-missing data, meaningful variation, and sensible types.\n"
        f"Data profile:\n{profile_summary}\n"
        f"Numeric columns: {json.dumps(numeric_cols)}\n"
        f"Categorical columns: {json.dumps(categorical_cols)}\n"
        f"Recent ledger (most recent first): {json.dumps(list(reversed(ledger_summary)))}"
    )

    feedback = ""
    for _ in range(MAX_ORCHESTRATOR_RETRIES):
        prompt = base_prompt
        if feedback:
            prompt += f"\nPrevious output was invalid: {feedback}. Correct it and return valid JSON only."

        try:
            proposal = structured(prompt, OrchestratorProposal, agent_key="ORCHESTRATOR")
        except Exception as exc:
            feedback = f"schema/parse error ({exc.__class__.__name__})"
            continue

        if _valid_non_stop_proposal(proposal):
            reason = _invalid_reason(proposal)
            if reason is None:
                return OrchestratorDecision(
                    hypothesis=proposal.hypothesis.strip(),
                    specialist_name=proposal.specialist_name,
                    stop=False,
                )
            feedback = reason
            continue

        feedback = _invalid_reason(proposal) or "unknown validation error"

    return OrchestratorDecision(hypothesis="", specialist_name="", stop=True)
