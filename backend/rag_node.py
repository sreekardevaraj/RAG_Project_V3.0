from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.state import AgentState
from config.prompts import PDF_PROMPT
from config.settings import RELEVANCE_THRESHOLD


def rag_node(state: AgentState, vectorstore, llm) -> AgentState:
    """
    LangGraph Node: RAG Agent
    Searches FAISS vector DB and answers from PDF chunks.
    Sets rag_success=False if score is too low (triggers fallback to web).
    """
    question = state["question"]
    history  = state["history"]

    results = vectorstore.similarity_search_with_score(question, k=4)

    if not results:
        print("[RAG Node] No chunks found → rag_success=False")
        return {**state, "rag_success": False, "context": "", "details": []}

    top_doc, top_distance = results[0]
    top_score = 1 / (1 + top_distance)
    print(f"[RAG Node] Score: {top_score:.4f} (threshold: {RELEVANCE_THRESHOLD})")

    if top_score < RELEVANCE_THRESHOLD:
        print("[RAG Node] Score too low → rag_success=False")
        return {**state, "rag_success": False, "context": "", "details": []}

    # Build context
    chunks  = [doc for doc, _ in results]
    context = "\n\n".join(doc.page_content for doc in chunks)
    details = [doc.metadata for doc in chunks]

    # Generate answer
    prompt = PromptTemplate(input_variables=["history", "context", "question"], template=PDF_PROMPT)
    chain  = prompt | llm | StrOutputParser()
    answer = chain.invoke({"history": history, "context": context, "question": question})

    print("[RAG Node] Answer generated from PDF ✅")
    return {
        **state,
        "rag_success": True,
        "context":     context,
        "details":     details,
        "answer":      answer,
        "source":      "PDF"
    }