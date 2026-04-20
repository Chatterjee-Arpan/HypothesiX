from langchain_openai import ChatOpenAI

from src.config import DEFAULT_TEMPERATURE, MODEL_ROUTING, OPENAI_GPT_KEY


def get_chat_model(route: str) -> ChatOpenAI:
    if not OPENAI_GPT_KEY:
        raise RuntimeError(
            "OPENAI_GPT_KEY is missing. Add it to your .env file before running HypothesiX."
        )
    if route not in MODEL_ROUTING:
        raise KeyError(f"Unknown model route: {route}")

    return ChatOpenAI(
        model=MODEL_ROUTING[route],
        temperature=DEFAULT_TEMPERATURE,
        api_key=OPENAI_GPT_KEY,
    )
