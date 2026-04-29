import json
from typing import Any

from app.core.models import ExecutiveSummaryOutput, Insight, RecommendedActionsOutput, Verdict
from app.services.llm_client import structured


QUALITY_ALERT_KEYWORDS = {
    "missing",
    "duplicate",
    "constant",
    "unique",
    "zeros",
    "infinite",
    "skewed",
    "imbalance",
    "cardinality",
    "unsupported",
}


def _column_names(data_profile: dict[str, Any]) -> list[str]:
    return [str(column.get("name")) for column in data_profile.get("columns", []) if column.get("name")]


def _accepted_payload(insights: list[Insight]) -> list[dict[str, Any]]:
    return [
        {
            "hypothesis": insight.hypothesis,
            "finding": insight.narrative,
            "function_name": insight.function_name,
            "statistics": insight.result.statistics,
        }
        for insight in insights
        if insight.skeptic.verdict == Verdict.ACCEPT
    ]


def build_executive_summary(dataset_name: str, data_profile: dict[str, Any], insights: list[Insight]) -> str:
    payload = {
        "dataset_name": dataset_name,
        "shape": data_profile.get("shape", {}),
        "columns": _column_names(data_profile),
        "column_types": data_profile.get("descriptive_statistics", {}).get("overview", {}).get("column_types", {}),
        "accepted_findings": _accepted_payload(insights),
    }
    prompt = (
        "Return ONLY JSON with exactly one key: summary.\n"
        "Write a brief end-user summary for the top of a statistical EDA report.\n"
        "Use 2 concise sentences. Explain what the dataset appears to describe and mention the strongest useful pattern if available.\n"
        "Do not mention p-values, model internals, agent names, or implementation details.\n"
        f"Payload: {json.dumps(payload, default=str)}"
    )
    return structured(prompt, ExecutiveSummaryOutput, agent_key="REPORT_SUMMARY").summary


def build_recommended_actions(data_profile: dict[str, Any], insights: list[Insight]) -> list[str]:
    payload = {
        "shape": data_profile.get("shape", {}),
        "columns": _column_names(data_profile),
        "alerts": data_profile.get("alerts", []),
        "accepted_findings": _accepted_payload(insights),
    }
    prompt = (
        "Return ONLY JSON with exactly one key: actions.\n"
        "actions must be a list of 3 to 5 short, practical next steps for a non-technical end user.\n"
        "Base the steps on the accepted findings and data profile. Avoid statistical jargon.\n"
        "Do not recommend collecting more data unless the profile suggests a quality or coverage issue.\n"
        f"Payload: {json.dumps(payload, default=str)}"
    )
    output = structured(prompt, RecommendedActionsOutput, agent_key="REPORT_ACTIONS")
    return [action.strip() for action in output.actions if action.strip()]


def build_data_quality_notes(data_profile: dict[str, Any]) -> list[str]:
    descriptive = data_profile.get("descriptive_statistics", {})
    overview = descriptive.get("overview", {})
    columns = descriptive.get("columns", [])
    notes: list[str] = []

    missing_rate = overview.get("missing_cells_percent")
    if isinstance(missing_rate, (float, int)):
        if missing_rate == 0:
            notes.append("No missing cells were detected in the profiled dataset.")
        elif missing_rate <= 0.05:
            notes.append(f"Missing data is low overall at {missing_rate:.1%} of cells.")
        else:
            notes.append(f"Missing data affects {missing_rate:.1%} of cells and may influence results.")

    duplicate_rate = overview.get("duplicate_rows_percent")
    if isinstance(duplicate_rate, (float, int)):
        if duplicate_rate == 0:
            notes.append("No duplicate rows were detected.")
        else:
            notes.append(f"Duplicate rows account for {duplicate_rate:.1%} of the dataset.")

    sparse_columns = [
        column.get("name")
        for column in columns
        if isinstance(column.get("missing_percent"), (float, int)) and column.get("missing_percent") > 0.2
    ]
    if sparse_columns:
        names = ", ".join(str(name).replace("_", " ") for name in sparse_columns[:5])
        notes.append(f"Columns with notable missingness: {names}.")

    low_variation_columns = [
        column.get("name")
        for column in columns
        if column.get("distinct") == 1
    ]
    if low_variation_columns:
        names = ", ".join(str(name).replace("_", " ") for name in low_variation_columns[:5])
        notes.append(f"Columns with only one observed value may not be useful for comparison: {names}.")

    quality_alerts = [
        str(alert).replace("_", " ")
        for alert in data_profile.get("alerts", [])
        if any(keyword in str(alert).lower() for keyword in QUALITY_ALERT_KEYWORDS)
    ]
    notes.extend(quality_alerts[:3])

    return notes[:6]
