from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.state import AgentState
from config.prompts import SUPERVISOR_PROMPT, CASUAL_RESPONSES


CASUAL_PHRASES = set(CASUAL_RESPONSES.keys())


def supervisor_node(state: AgentState, llm) -> AgentState:
    """
    LangGraph Node: Supervisor
    Reads the question and decides which agent node to route to.
    Updates state["agent"] with: RAG | WEB | ANALYST | CASUAL
    """
    question = state["question"]

    # Fast path — casual check without LLM call
    if question.lower().strip() in CASUAL_PHRASES:
        print("[Supervisor Node] → CASUAL")
        return {**state, "agent": "CASUAL"}

    # LLM-based classification
    prompt = PromptTemplate(input_variables=["question"], template=SUPERVISOR_PROMPT)
    chain  = prompt | llm | StrOutputParser()
    result = chain.invoke({"question": question}).strip().upper()

    valid = {"RAG", "WEB", "ANALYST", "CASUAL"}
    if result not in valid:
        print(f"[Supervisor Node] Unexpected '{result}' → defaulting to RAG")
        result = "RAG"

    print(f"[Supervisor Node] → {result}")
    return {**state, "agent": result}