from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.state import AgentState
from config.prompts import ANALYST_PROMPT


def analyst_node(state: AgentState, vectorstore, llm) -> AgentState:
    """
    LangGraph Node: Analyst Agent
    Retrieves broad document context and performs deep analysis.
    Handles: summarize, compare, report, quiz generation.
    """
    question = state["question"]
    history  = state["history"]

    print(f"[Analyst Node] Deep analysis for: '{question}'")

    # Get broad context — more chunks than RAG for full document coverage
    docs    = vectorstore.similarity_search(question, k=20)
    context = "\n\n".join(doc.page_content for doc in docs)

    if not context:
        return {
            **state,
            "answer":  "No document content found. Please upload and index a PDF first.",
            "source":  "Analyst",
            "details": [],
            "context": ""
        }

    prompt = PromptTemplate(input_variables=["history", "context", "question"], template=ANALYST_PROMPT)
    chain  = prompt | llm | StrOutputParser()
    answer = chain.invoke({"history": history, "context": context, "question": question})

    print("[Analyst Node] Analysis complete ✅")
    return {
        **state,
        "context": context,
        "details": [],
        "answer":  answer,
        "source":  "Analyst"
    }