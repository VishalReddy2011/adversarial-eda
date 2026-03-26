import json

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
from app.services.report_service import build_pdf_report


MAX_DUPLICATE_RETRIES = 3


def request_signature(specialist_name: str, hypothesis: str, function_call: FunctionCall) -> str:
    normalized_hypothesis = " ".join(hypothesis.lower().split())
    canonical_args = json.dumps(function_call.to_kwargs(), sort_keys=True, default=str)
    return f"{specialist_name}|{function_call.function_name}|{canonical_args}|{normalized_hypothesis}"


def run_analysis(dataframe, dataset_name: str, show_execution_order: bool = False) -> bytes:
    state = EDAState(
        dataset_name=dataset_name,
        raw_df=dataframe,
        show_execution_order=show_execution_order,
    )

    state.data_profile = profile_dataframe(state.raw_df)
    state.cleaning_plan = build_cleaning_plan(state.data_profile, state.raw_df)
    state.cleaned_df = apply_preprocessing(state.raw_df, state.cleaning_plan)

    while not state.stop:
        decision = next_step(
            df=state.cleaned_df,
            accepted_count=state.accepted_count,
            function_calls=state.function_calls,
            insight_ledger=state.insight_ledger,
        )
        state.current_hypothesis = decision.hypothesis
        state.current_specialist = decision.specialist_name
        state.stop = decision.stop

        if state.stop:
            break

        hypothesis = state.current_hypothesis
        specialist_name = state.current_specialist
        seen_signatures = set(state.specialist_request_signatures)
        state.current_function_call = None

        for attempt in range(MAX_DUPLICATE_RETRIES):
            function_call = propose_specialist_call(specialist_name, hypothesis, state.cleaned_df)
            signature = request_signature(specialist_name, hypothesis, function_call)

            if signature not in seen_signatures:
                state.current_hypothesis = hypothesis
                state.current_specialist = specialist_name
                state.current_function_call = function_call
                state.specialist_request_signatures.append(signature)
                break

            if attempt == MAX_DUPLICATE_RETRIES - 1:
                state.stop = True
                break

            retry_decision = next_step(
                df=state.cleaned_df,
                accepted_count=state.accepted_count,
                function_calls=state.function_calls,
                insight_ledger=state.insight_ledger,
            )
            if retry_decision.stop:
                state.stop = True
                break
            hypothesis = retry_decision.hypothesis
            specialist_name = retry_decision.specialist_name

        if state.stop or state.current_function_call is None:
            break

        state.current_execution_result = run_function_call(state.cleaned_df, state.current_function_call)
        state.current_skeptic_result = audit_result(state.current_execution_result)

        insight = Insight(
            hypothesis=state.current_function_call.hypothesis,
            function_name=state.current_function_call.function_name,
            result=state.current_execution_result,
            skeptic=state.current_skeptic_result,
            narrative="",
        )

        if state.current_skeptic_result.verdict == Verdict.ACCEPT:
            insight.narrative = to_narrative(insight)
        else:
            insight.narrative = state.current_skeptic_result.reason

        state.insight_ledger.append(insight)
        state.accepted_count += 1 if state.current_skeptic_result.verdict == Verdict.ACCEPT else 0
        state.function_calls += 1
        state.stop = state.accepted_count >= MAX_ACCEPTED or state.function_calls >= MAX_FUNCTION_CALLS

    state.pdf_bytes = build_pdf_report(state)
    return state.pdf_bytes
