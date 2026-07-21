from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.state import AgentState
from config.prompts import PDF_PROMPT


def rag_node(state: AgentState, vectorstore, llm) -> AgentState:
    """
    LangGraph Node: RAG Agent
    Retrieves relevant documents from the vectorstore and answers based on PDF context.
    """
    question = state["question"]
    history  = state["history"]

    print(f"[RAG Node] Searching documents for: '{question}'")

    # Retrieve relevant documents from vectorstore
    docs    = vectorstore.similarity_search(question, k=5)
    context = "\n\n".join(doc.page_content for doc in docs)

    if not context:
        return {
            **state,
            "answer":  "No relevant document content found. Please upload and index a PDF first.",
            "source":  "RAG",
            "details": [],
            "context": ""
        }

    prompt = PromptTemplate(input_variables=["history", "context", "question"], template=PDF_PROMPT)
    chain  = prompt | llm | StrOutputParser()
    answer = chain.invoke({"history": history, "context": context, "question": question})

    print("[RAG Node] Answer generated from PDF ✅")
    return {
        **state,
        "context": context,
        "details": [],
        "answer":  answer,
        "source":  "RAG"
    }
