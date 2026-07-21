from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.state import AgentState
from config.prompts import FOLLOWUP_PROMPT
from config.settings import NUM_FOLLOWUP_QUESTIONS


def followup_node(state: AgentState, llm) -> AgentState:
    """
    LangGraph Node: Follow-up Question Generator
    Generates 3 suggested follow-up questions after every non-casual answer.
    """
    # Skip follow-ups for casual chat
    if state.get("source") == "Chat":
        return {**state, "followups": []}

    question = state["question"]
    answer   = state["answer"]

    try:
        prompt = PromptTemplate(input_variables=["question", "answer"], template=FOLLOWUP_PROMPT)
        chain  = prompt | llm | StrOutputParser()
        result = chain.invoke({"question": question, "answer": answer})

        questions = []
        for line in result.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            # Strip numbering like "1." or "1)"
            if line and line[0].isdigit():
                line = line.split(".", 1)[-1].strip()
                line = line.split(")", 1)[-1].strip()
            if line:
                questions.append(line)

        followups = questions[:NUM_FOLLOWUP_QUESTIONS]
        print(f"[Followup Node] Generated {len(followups)} follow-up questions ✅")
        return {**state, "followups": followups}

    except Exception as e:
        print(f"[Followup Node] Error: {e}")
        return {**state, "followups": []}