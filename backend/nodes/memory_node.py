from backend.state import AgentState


def memory_node(state: AgentState, memory) -> AgentState:
    """
    LangGraph Node: Memory
    Saves the current question and answer to chat memory.
    """
    memory.add("user",      state["question"])
    memory.add("assistant", state["answer"])
    print("[Memory Node] Conversation saved ✅")
    return state