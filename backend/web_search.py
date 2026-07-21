from ddgs import DDGS


def web_search(query: str, max_results: int = 5) -> list:
    """
    Search the web using DuckDuckGo and return top results.
    """
    results = []

    try:
        ddgs = DDGS()
        search_results = ddgs.text(query, max_results=max_results)
        for r in search_results:
            results.append({
                "title": r.get("title", ""),
                "url":   r.get("href", ""),
                "body":  r.get("body", "")
            })
        print(f"[WebSearch] Found {len(results)} results for: '{query}'")

    except Exception as e:
        print(f"[WebSearch] Error: {e}")

    return results


def format_web_results(results: list) -> str:
    """
    Format web search results into a single context string for the LLM.
    """
    if not results:
        return "No web results found."

    formatted = ""
    for i, r in enumerate(results, 1):
        formatted += f"[Result {i}] {r['title']}\n"
        formatted += f"Source: {r['url']}\n"
        formatted += f"{r['body']}\n\n"

    return formatted.strip()