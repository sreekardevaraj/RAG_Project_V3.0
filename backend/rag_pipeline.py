from langgraph.graph import StateGraph, END
from functools import partial

from backend.state import AgentState
from backend.memory import ChatMemory
from backend.embeddings import get_embedding_model
from backend.vectorstore import create_vectorstore, load_vectorstore
from backend.loader import load_pdfs
from backend.splitter import split_documents
from backend.llm import get_llm

from backend.nodes.supervisor_node import supervisor_node
from backend.nodes.rag_node        import rag_node
from backend.nodes.web_node        import web_node
from backend.nodes.analyst_node    import analyst_node
from backend.nodes.casual_node     import casual_node
from backend.nodes.followup_node   import followup_node
from backend.nodes.memory_node     import memory_node

from config.settings import VECTOR_DB_DIR
import os


# ── Routing function ──────────────────────────────────────────────────
def route_after_supervisor(state: AgentState) -> str:
    """Conditional edge — routes to correct agent node after supervisor."""
    agent = state.get("agent", "RAG")
    routes = {
        "RAG":     "rag_node",
        "WEB":     "web_node",
        "ANALYST": "analyst_node",
        "CASUAL":  "casual_node"
    }
    return routes.get(agent, "rag_node")


def route_after_rag(state: AgentState) -> str:
    """Conditional edge — if RAG fails, fall back to web node."""
    if state.get("rag_success", False):
        return "followup_node"
    else:
        print("[Graph] RAG failed → falling back to web_node")
        return "web_node"


# ── Build LangGraph ───────────────────────────────────────────────────
def build_graph(vectorstore, llm, memory):
    """Build and compile the LangGraph StateGraph."""

    graph = StateGraph(AgentState)

    # ── Add Nodes ─────────────────────────────────────────────────────
    graph.add_node("supervisor_node", partial(supervisor_node, llm=llm))
    graph.add_node("rag_node",        partial(rag_node, vectorstore=vectorstore, llm=llm))
    graph.add_node("web_node",        partial(web_node, llm=llm))
    graph.add_node("analyst_node",    partial(analyst_node, vectorstore=vectorstore, llm=llm))
    graph.add_node("casual_node",     casual_node)
    graph.add_node("followup_node",   partial(followup_node, llm=llm))
    graph.add_node("memory_node",     partial(memory_node, memory=memory))

    # ── Entry Point ────────────────────────────────────────────────────
    graph.set_entry_point("supervisor_node")

    # ── Edges ──────────────────────────────────────────────────────────
    # Supervisor → conditional routing to agents
    graph.add_conditional_edges(
        "supervisor_node",
        route_after_supervisor,
        {
            "rag_node":      "rag_node",
            "web_node":      "web_node",
            "analyst_node":  "analyst_node",
            "casual_node":   "casual_node"
        }
    )

    # RAG → conditional (success → followup | fail → web)
    graph.add_conditional_edges(
        "rag_node",
        route_after_rag,
        {
            "followup_node": "followup_node",
            "web_node":      "web_node"
        }
    )

    # Web, Analyst → followup
    graph.add_edge("web_node",      "followup_node")
    graph.add_edge("analyst_node",  "followup_node")

    # Casual → memory (skip followup)
    graph.add_edge("casual_node",   "memory_node")

    # Followup → memory → END
    graph.add_edge("followup_node", "memory_node")
    graph.add_edge("memory_node",   END)

    return graph.compile()


# ── Public API ────────────────────────────────────────────────────────
def build_rag_pipeline(force_rebuild: bool = False) -> dict:
    """Build vectorstore, LLM, memory and compile LangGraph."""
    embedding_model = get_embedding_model()

    if os.path.exists(VECTOR_DB_DIR) and not force_rebuild:
        vectorstore = load_vectorstore(embedding_model)
    else:
        documents   = load_pdfs()
        chunks      = split_documents(documents)
        vectorstore = create_vectorstore(chunks, embedding_model)

    llm    = get_llm()
    memory = ChatMemory()
    graph  = build_graph(vectorstore, llm, memory)

    print("[LangGraph Pipeline] Compiled and Ready ✅")
    return {
        "graph":      graph,
        "vectorstore": vectorstore,
        "llm":        llm,
        "memory":     memory
    }


def ask_question(pipeline: dict, question: str) -> dict:
    """Run a question through the LangGraph pipeline."""
    graph  = pipeline["graph"]
    memory = pipeline["memory"]

    # Build initial state
    initial_state: AgentState = {
        "question":    question,
        "agent":       "",
        "context":     "",
        "details":     [],
        "answer":      "",
        "source":      "",
        "history":     memory.get_history_string(),
        "followups":   [],
        "rag_success": False
    }

    # Run the graph
    final_state = graph.invoke(initial_state)

    return {
        "answer":    final_state["answer"],
        "source":    final_state["source"],
        "details":   final_state["details"],
        "followups": final_state["followups"]
    }