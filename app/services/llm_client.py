import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()


DEFAULT_MODEL = "qwen3.5:2b"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_REASONING = False


def get_agent_config(agent_key: str) -> dict[str, object]:
    model = os.getenv(f"OLLAMA_{agent_key}_MODEL") or os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)
    temperature = float(
        os.getenv(f"OLLAMA_{agent_key}_TEMPERATURE")
        or os.getenv("OLLAMA_TEMPERATURE", str(DEFAULT_TEMPERATURE))
    )

    reasoning_raw = (
        os.getenv(f"OLLAMA_{agent_key}_REASONING")
        or os.getenv("OLLAMA_REASONING", str(DEFAULT_REASONING))
    ).strip().lower()
    reasoning = reasoning_raw in {"1", "true", "yes", "on"}

    return {
        "model": model,
        "temperature": temperature,
        "reasoning": reasoning,
    }


def create_llm(agent_key: str) -> ChatOllama:
    cfg = get_agent_config(agent_key)
    return ChatOllama(
        model=str(cfg["model"]),
        temperature=float(str(cfg["temperature"])),
        reasoning=bool(cfg["reasoning"]),
    )


def structured(prompt: str, schema_model, agent_key: str):
    llm = create_llm(agent_key)
    result = llm.with_structured_output(schema_model).invoke(prompt)
    if isinstance(result, schema_model):
        return result
    return schema_model.model_validate(result)
