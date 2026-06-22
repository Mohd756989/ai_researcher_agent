"""
Researcher agent: runs the planned search queries via Tavily and
collects the raw results.
"""
from researcher_agent.tools.search import search_web
from researcher_agent.graph.state import AgentState


def researcher_agent(state: AgentState) -> dict:
    queries = state["search_queries"]
    all_docs = []

    for q in queries:
        try:
            docs = search_web(q[:400])
            all_docs.extend(docs)
        except Exception as e:
            print(f"Search failed for query '{q}': {e}")

    return {"search_results": all_docs}
