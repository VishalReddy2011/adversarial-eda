import json
from typing import Any, Literal, TypedDict

import pandas as pd
from langgraph.graph import END, START, StateGraph

from app.agents.cleaner import build_cleaning_plan
from app.agents.orchestrator import MAX_ACCEPTED, MAX_FUNCTION_CALLS, next_step
from app.agents.skeptic import audit_result
from app.agents.specialist import propose_specialist_call
from app.agents.translator import to_narrative
from app.core.models import FunctionCall, Insight, Verdict
from app.core.state import EDAState
from app.engine.execution_engine import run_function_call
from app.engine.preprocessing import apply_preprocessing
from app.services.profile_service import profile_dataframe
from app.services.report_insights import (
    build_data_quality_notes,
    build_executive_summary,
    build_recommended_actions,
)
from app.services.report_service import build_pdf_report


MAX_DUPLICATE_RETRIES = 3


class AnalysisState(TypedDict, total=False):
    dataset_name: str
    raw_df: pd.DataFrame
    cleaned_df: pd.DataFrame
    data_profile: dict[str, Any]
    cleaning_plan: Any
    show_execution_order: bool
    insight_ledger: list[Insight]
    accepted_count: int
    function_calls: int
    current_hypothesis: str
    current_specialist: str
    specialist_request_signatures: list[str]
    current_function_call: FunctionCall | None
    current_execution_result: Any
    current_skeptic_result: Any
    executive_summary: str
    recommended_actions: list[str]
    data_quality_notes: list[str]
    stop: bool
    pdf_bytes: bytes


def request_signature(specialist_name: str, hypothesis: str, function_call: FunctionCall) -> str:
    normalized_hypothesis = " ".join(hypothesis.lower().split())
    canonical_args = json.dumps(function_call.to_kwargs(), sort_keys=True, default=str)
    return f"{specialist_name}|{function_call.function_name}|{canonical_args}|{normalized_hypothesis}"


def _as_eda_state(state: AnalysisState) -> EDAState:
    return EDAState(
        dataset_name=state["dataset_name"],
        raw_df=state["raw_df"],
        cleaned_df=state.get("cleaned_df"),
        data_profile=state.get("data_profile", {}),
        cleaning_plan=state.get("cleaning_plan"),
        show_execution_order=state.get("show_execution_order", False),
        insight_ledger=state.get("insight_ledger", []),
        accepted_count=state.get("accepted_count", 0),
        function_calls=state.get("function_calls", 0),
        current_hypothesis=state.get("current_hypothesis", ""),
        current_specialist=state.get("current_specialist", ""),
        specialist_request_signatures=state.get("specialist_request_signatures", []),
        current_function_call=state.get("current_function_call"),
        current_execution_result=state.get("current_execution_result"),
        current_skeptic_result=state.get("current_skeptic_result"),
        executive_summary=state.get("executive_summary", ""),
        recommended_actions=state.get("recommended_actions", []),
        data_quality_notes=state.get("data_quality_notes", []),
        stop=state.get("stop", False),
        pdf_bytes=state.get("pdf_bytes"),
    )


def prepare_data(state: AnalysisState) -> dict[str, Any]:
    raw_df = state["raw_df"]
    cleaning_plan = build_cleaning_plan({}, raw_df)
    cleaned_df = apply_preprocessing(raw_df, cleaning_plan)
    return {
        "cleaning_plan": cleaning_plan,
        "cleaned_df": cleaned_df,
        "data_profile": profile_dataframe(cleaned_df),
    }


def orchestrate(state: AnalysisState) -> dict[str, Any]:
    decision = next_step(
        df=state["cleaned_df"],
        accepted_count=state.get("accepted_count", 0),
        function_calls=state.get("function_calls", 0),
        insight_ledger=state.get("insight_ledger", []),
        data_profile=state.get("data_profile", {}),
    )
    return {
        "current_hypothesis": decision.hypothesis,
        "current_specialist": decision.specialist_name,
        "stop": decision.stop,
        "current_function_call": None,
    }


def choose_specialist_call(state: AnalysisState) -> dict[str, Any]:
    hypothesis = state.get("current_hypothesis", "")
    specialist_name = state.get("current_specialist", "")
    seen_signatures = set(state.get("specialist_request_signatures", []))
    signatures = list(state.get("specialist_request_signatures", []))

    for _ in range(MAX_DUPLICATE_RETRIES):
        function_call = propose_specialist_call(specialist_name, hypothesis, state["cleaned_df"])
        signature = request_signature(specialist_name, hypothesis, function_call)
        if signature not in seen_signatures:
            signatures.append(signature)
            return {
                "current_hypothesis": hypothesis,
                "current_specialist": specialist_name,
                "current_function_call": function_call,
                "specialist_request_signatures": signatures,
                "stop": False,
            }

        retry_decision = next_step(
            df=state["cleaned_df"],
            accepted_count=state.get("accepted_count", 0),
            function_calls=state.get("function_calls", 0),
            insight_ledger=state.get("insight_ledger", []),
            data_profile=state.get("data_profile", {}),
        )
        if retry_decision.stop:
            return {"stop": True, "current_function_call": None}
        hypothesis = retry_decision.hypothesis
        specialist_name = retry_decision.specialist_name

    return {"stop": True, "current_function_call": None}


def execute_call(state: AnalysisState) -> dict[str, Any]:
    function_call = state.get("current_function_call")
    if function_call is None:
        return {"stop": True}
    return {"current_execution_result": run_function_call(state["cleaned_df"], function_call)}


def audit_call(state: AnalysisState) -> dict[str, Any]:
    return {"current_skeptic_result": audit_result(state["current_execution_result"])}


def translate_and_record(state: AnalysisState) -> dict[str, Any]:
    function_call = state["current_function_call"]
    skeptic_result = state["current_skeptic_result"]
    insight = Insight(
        hypothesis=function_call.hypothesis,
        function_name=function_call.function_name,
        result=state["current_execution_result"],
        skeptic=skeptic_result,
        narrative="",
    )

    if skeptic_result.verdict == Verdict.ACCEPT:
        insight.narrative = to_narrative(insight)
    else:
        insight.narrative = skeptic_result.reason

    insight_ledger = [*state.get("insight_ledger", []), insight]
    accepted_count = state.get("accepted_count", 0) + (1 if skeptic_result.verdict == Verdict.ACCEPT else 0)
    function_calls = state.get("function_calls", 0) + 1

    return {
        "insight_ledger": insight_ledger,
        "accepted_count": accepted_count,
        "function_calls": function_calls,
        "stop": accepted_count >= MAX_ACCEPTED or function_calls >= MAX_FUNCTION_CALLS,
    }


def enrich_report(state: AnalysisState) -> dict[str, Any]:
    data_profile = state.get("data_profile", {})
    insights = state.get("insight_ledger", [])
    return {
        "executive_summary": build_executive_summary(state["dataset_name"], data_profile, insights),
        "recommended_actions": build_recommended_actions(data_profile, insights),
        "data_quality_notes": build_data_quality_notes(data_profile),
    }


def render_report(state: AnalysisState) -> dict[str, Any]:
    return {"pdf_bytes": build_pdf_report(_as_eda_state(state))}


def route_after_orchestrator(state: AnalysisState) -> Literal["specialist", "enrich_report"]:
    return "enrich_report" if state.get("stop") else "specialist"


def route_after_specialist(state: AnalysisState) -> Literal["execute", "enrich_report"]:
    return "enrich_report" if state.get("stop") or state.get("current_function_call") is None else "execute"


def route_after_record(state: AnalysisState) -> Literal["orchestrator", "enrich_report"]:
    return "enrich_report" if state.get("stop") else "orchestrator"


def build_analysis_graph():
    graph = StateGraph(AnalysisState)
    graph.add_node("prepare_data", prepare_data)
    graph.add_node("orchestrator", orchestrate)
    graph.add_node("specialist", choose_specialist_call)
    graph.add_node("execute", execute_call)
    graph.add_node("skeptic", audit_call)
    graph.add_node("translator", translate_and_record)
    graph.add_node("enrich_report", enrich_report)
    graph.add_node("render_report", render_report)

    graph.add_edge(START, "prepare_data")
    graph.add_edge("prepare_data", "orchestrator")
    graph.add_conditional_edges(
        "orchestrator",
        route_after_orchestrator,
        {"specialist": "specialist", "enrich_report": "enrich_report"},
    )
    graph.add_conditional_edges(
        "specialist",
        route_after_specialist,
        {"execute": "execute", "enrich_report": "enrich_report"},
    )
    graph.add_edge("execute", "skeptic")
    graph.add_edge("skeptic", "translator")
    graph.add_conditional_edges(
        "translator",
        route_after_record,
        {"orchestrator": "orchestrator", "enrich_report": "enrich_report"},
    )
    graph.add_edge("enrich_report", "render_report")
    graph.add_edge("render_report", END)
    return graph.compile()


ANALYSIS_GRAPH = build_analysis_graph()
