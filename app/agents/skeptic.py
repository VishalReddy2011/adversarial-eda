import json
import math

from app.core.models import ExecutionResult, SkepticResult, Verdict
from app.services.llm_client import structured
from app.services.rag import retrieve_context


def format_context(contexts: list[dict[str, object]]) -> str:
    if not contexts:
        return "No retrieved guidance."
    return "\n".join(
        f"{item['rank']}. {item['title']}: {item['content']}"
        for item in contexts
    )


def deterministic_rejection(result: ExecutionResult) -> SkepticResult | None:
    note = result.statistics.get("note")
    if note:
        return SkepticResult(verdict=Verdict.REJECT, reason=str(note))

    p_value = result.statistics.get("p_value")
    if p_value is None or (isinstance(p_value, float) and math.isnan(p_value)):
        return SkepticResult(verdict=Verdict.REJECT, reason="No valid p_value was produced for this test.")

    return None


def audit_result(result: ExecutionResult) -> SkepticResult:
    if not result.success:
        short_error = (result.error or "execution error").splitlines()[0]
        return SkepticResult(
            verdict=Verdict.REJECT,
            reason=f"Execution failed: {short_error}",
        )

    rejection = deterministic_rejection(result)
    if rejection:
        return rejection

    payload = {
        "function_name": result.function_name,
        "statistics": result.statistics,
    }
    contexts = retrieve_context(
        hypothesis=result.function_name,
        k=1,
        enabled=True,
        allowed_functions=[result.function_name],
    )

    prompt = (
        "You are the Skeptic. Return ONLY JSON matching "
        "{verdict: 'ACCEPT'|'REJECT', reason: string}. No prose.\n"
        "Use p_value < 0.05 as the default threshold when available, but also consider "
        "sample size, effect size, and method assumptions.\n"
        "Retrieved method guidance:\n"
        f"{format_context(contexts)}\n"
        f"Payload: {json.dumps(payload)}"
    )

    return structured(prompt, SkepticResult, agent_key="SKEPTIC")
