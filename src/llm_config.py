import os

from crewai import LLM
from dotenv import load_dotenv

load_dotenv()


def get_model_name() -> str:
    return os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")


def get_local_llm() -> LLM:
    return LLM(
        model=f"ollama/{get_model_name()}",
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.5,
    )

