from backend.state import AgentState
from config.prompts import CASUAL_RESPONSES, DEFAULT_CASUAL


def casual_node(state: AgentState) -> AgentState:
    """
    LangGraph Node: Casual Chat
    Handles greetings and small talk without LLM call.
    """
    question = state["question"].lower().strip()
    answer   = CASUAL_RESPONSES.get(question, DEFAULT_CASUAL)

    print("[Casual Node] Direct casual response ✅")
    return {
        **state,
        "answer":  answer,
        "source":  "Chat",
        "details": [],
        "context": ""
    }