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
        "Write for a non-technical reader in at most two concise sentences.\n"
        "Explain what the finding means in the dataset, using the column names naturally.\n"
        "Do not mention p-values, test names, statistics, sample size, or model diagnostics unless they are essential.\n"
        "Prefer practical language about direction, difference, strength, or pattern.\n"
        f"Payload: {json.dumps(payload)}"
    )

    output = structured(prompt, TranslatorOutput, agent_key="TRANSLATOR")
    return output.narrative
