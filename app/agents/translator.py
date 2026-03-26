import json

from app.core.models import Insight, TranslatorOutput, Verdict
from app.services.llm_client import structured


def to_narrative(insight: Insight) -> str:
    if insight.skeptic.verdict != Verdict.ACCEPT:
        return ""

    payload = {
        "hypothesis": insight.hypothesis,
        "function_name": insight.function_name,
        "statistics": insight.result.statistics,
        "reason": insight.skeptic.reason,
    }

    prompt = (
        "Return ONLY a single JSON object with exactly one key: narrative. No prose.\n"
        "Output format example: {\"narrative\":\"...\"}.\n"
        "Write the narrative in at most two concise sentences.\n"
        f"Payload: {json.dumps(payload)}"
    )

    output = structured(prompt, TranslatorOutput, agent_key="TRANSLATOR")
    return output.narrative
