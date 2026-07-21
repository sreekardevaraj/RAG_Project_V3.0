from langchain_groq import ChatGroq
from config.settings import GROQ_API_KEY, LLM_MODEL_NAME


def get_llm() -> ChatGroq:
    """Initialize and return the Groq LLM."""
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=LLM_MODEL_NAME
    )
    print(f"[LLM] Groq model loaded: {LLM_MODEL_NAME}")
    return llm
