import re
from pathlib import Path
from typing import Any


KNOWLEDGE_DIR = Path(__file__).resolve().parents[2] / "knowledge"


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9_]+", text.lower()) if len(token) > 2}


def _load_method_cards() -> dict[str, str]:
    cards: dict[str, str] = {}
    if KNOWLEDGE_DIR.exists():
        for path in KNOWLEDGE_DIR.glob("*.md"):
            content = path.read_text(encoding="utf-8").strip()
            if content:
                cards[path.stem] = content
    return cards


def retrieve_context(
    hypothesis: str,
    k: int = 3,
    enabled: bool = True,
    allowed_functions: list[str] | None = None,
) -> list[dict[str, Any]]:
    if not enabled:
        return []

    allowed = set(allowed_functions or [])
    query_tokens = _tokenize(hypothesis)
    scored: list[tuple[float, str, str]] = []

    for title, content in _load_method_cards().items():
        if allowed and title not in allowed:
            continue

        content_tokens = _tokenize(f"{title} {content}")
        overlap = len(query_tokens & content_tokens)
        score = float(overlap)

        if title in hypothesis.lower():
            score += 3.0
        if title in allowed:
            score += 1.0

        scored.append((score, title, content))

    scored.sort(key=lambda item: (-item[0], item[1]))
    return [
        {"title": title, "content": content, "rank": rank}
        for rank, (_, title, content) in enumerate(scored[:k], start=1)
    ]
