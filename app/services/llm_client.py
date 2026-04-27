import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


DEFAULT_MODEL = "gemini-3.1-pro-preview"
DEFAULT_TEMPERATURE = 0.2


def get_config() -> dict[str, str | float]:
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set")

    return {
        "api_key": api_key,
        "model": os.getenv("GOOGLE_MODEL", DEFAULT_MODEL).strip(),
        "temperature": float(os.getenv("GOOGLE_TEMPERATURE", str(DEFAULT_TEMPERATURE))),
    }


def create_llm() -> ChatGoogleGenerativeAI:
    cfg = get_config()
    return ChatGoogleGenerativeAI(
        model=str(cfg["model"]),
        temperature=float(cfg["temperature"]),
        google_api_key=str(cfg["api_key"]),
        thinking_level="minimal"
    )


def structured(prompt: str, schema_model, agent_key: str):
    _ = agent_key
    llm = create_llm()
    structured_llm = llm.with_structured_output(
        schema=schema_model.model_json_schema(),
        method="json_schema",
    )
    result = structured_llm.invoke(prompt)
    if isinstance(result, schema_model):
        return result
    return schema_model.model_validate(result)
