from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.state import AgentState
from backend.web_search import web_search, format_web_results
from config.prompts import WEB_PROMPT
from config.settings import WEB_SEARCH_MAX_RESULTS


def web_node(state: AgentState, llm) -> AgentState:
    """
    LangGraph Node: Web Agent
    Searches DuckDuckGo and answers from web results.
    """
    question = state["question"]
    history  = state["history"]

    print(f"[Web Node] Searching web for: '{question}'")
    results = web_search(question, max_results=WEB_SEARCH_MAX_RESULTS)

    if not results:
        return {
            **state,
            "answer":  "I couldn't find any web results for this query. Please try rephrasing.",
            "source":  "Web",
            "details": [],
            "context": ""
        }

    context = format_web_results(results)
    details = [{"url": r["url"], "title": r["title"]} for r in results]

    prompt = PromptTemplate(input_variables=["history", "context", "question"], template=WEB_PROMPT)
    chain  = prompt | llm | StrOutputParser()
    answer = chain.invoke({"history": history, "context": context, "question": question})

    print("[Web Node] Answer generated from web ✅")
    return {
        **state,
        "context": context,
        "details": details,
        "answer":  answer,
        "source":  "Web"
    }