import json

from app.core.models import ExecutionResult, SkepticResult, Verdict
from app.services.llm_client import structured


def audit_result(result: ExecutionResult) -> SkepticResult:
    if not result.success:
        short_error = (result.error or "execution error").splitlines()[0]
        return SkepticResult(
            verdict=Verdict.REJECT,
            reason=f"Execution failed: {short_error}",
        )

    payload = {
        "function_name": result.function_name,
        "statistics": result.statistics,
    }

    prompt = (
        "You are the Skeptic. Evaluate statistical evidence and decide ACCEPT or REJECT. "
        "Return ONLY JSON that matches this schema. No prose.\n"
        "Schema: {verdict: 'ACCEPT'|'REJECT', reason: string}.\n"
        "Use p_value < 0.05 as the default significance threshold when available.\n"
        f"Payload: {json.dumps(payload)}"
    )

    return structured(prompt, SkepticResult, agent_key="SKEPTIC")
