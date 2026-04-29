import re
from pathlib import Path
from typing import Any, cast

import chromadb


KNOWLEDGE_DIR = Path(__file__).resolve().parents[2] / "knowledge"
CHROMA_DIR = KNOWLEDGE_DIR / "chroma_db"
COLLECTION_NAME = "statistical_eda_knowledge"


def _parse_front_matter(content: str) -> tuple[dict[str, str], str]:
    if not content.startswith("---"):
        return {}, content.strip()

    match = re.match(r"(?s)^---\s*\n(.*?)\n---\s*\n?(.*)$", content)
    if not match:
        return {}, content.strip()

    metadata: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.startswith((" ", "-")):
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata, match.group(2).strip()


def _knowledge_files() -> list[Path]:
    if not KNOWLEDGE_DIR.exists():
        return []
    return sorted(KNOWLEDGE_DIR.glob("*.md"))


def _load_documents() -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for path in _knowledge_files():
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue

        metadata, body = _parse_front_matter(content)
        doc_id = metadata.get("id") or path.stem
        function_name = metadata.get("function_name", doc_id)
        documents.append(
            {
                "id": doc_id,
                "text": f"{metadata.get('title', doc_id)}\n\n{body}",
                "metadata": {
                    "title": metadata.get("title", doc_id.replace("_", " ").title()),
                    "function_name": "" if function_name == "null" else function_name,
                    "specialist": "" if metadata.get("specialist") == "null" else metadata.get("specialist", ""),
                    "path": str(path.relative_to(KNOWLEDGE_DIR.parent)),
                    "mtime": str(path.stat().st_mtime),
                },
            }
        )
    return documents


def _source_signature() -> str:
    return "|".join(
        f"{path.name}:{path.stat().st_mtime}:{path.stat().st_size}"
        for path in _knowledge_files()
    )


def _collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    signature = _source_signature()
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"source_signature": signature},
    )

    current_signature = collection.metadata.get("source_signature") if collection.metadata else None
    if current_signature != signature or collection.count() == 0:
        documents = _load_documents()
        client.delete_collection(name=COLLECTION_NAME)
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={"source_signature": signature},
        )
        if documents:
            collection.add(
                ids=[document["id"] for document in documents],
                documents=[document["text"] for document in documents],
                metadatas=[document["metadata"] for document in documents],
            )

    return collection


def retrieve_context(
    hypothesis: str,
    k: int = 3,
    enabled: bool = True,
    allowed_functions: list[str] | None = None,
) -> list[dict[str, Any]]:
    if not enabled:
        return []

    collection = _collection()
    count = collection.count()
    if count == 0:
        return []

    where = None
    if allowed_functions:
        where = cast(Any, {"function_name": {"$in": allowed_functions}})

    result = collection.query(
        query_texts=[hypothesis],
        n_results=min(k, count),
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    ids = (result.get("ids") or [[]])[0]
    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]

    return [
        {
            "title": metadata.get("title", ""),
            "content": document,
            "rank": rank,
            "score": None if distance is None else round(1.0 - float(distance), 4),
            "path": metadata.get("path", ""),
            "document_id": document_id,
        }
        for rank, (document_id, document, metadata, distance) in enumerate(
            zip(ids, documents, metadatas, distances),
            start=1,
        )
        if metadata is not None and document is not None
    ]
