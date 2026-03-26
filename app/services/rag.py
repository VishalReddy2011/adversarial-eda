from typing import Any


def retrieve_context(hypothesis: str, k: int = 3, enabled: bool = False) -> list[dict[str, Any]]:
    if not enabled:
        return []
    return [{"title": "placeholder", "content": f"Context for: {hypothesis}", "rank": 1}][:k]
