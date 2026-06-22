"""
Planner agent: turns the user's research query into a set of concrete
web search queries.
"""
from researcher_agent.llm_client import llm
from researcher_agent.graph.state import AgentState


def planner_agent(state: AgentState) -> dict:
    query = state["query"]

    prompt = f"""
    Generate 5 concise web search queries for researching:

    {query}

    Return only the queries, one per line, with no numbering or extra text.
    """

    response = llm.invoke(prompt)
    queries = [line.strip("-*0123456789. ").strip()
               for line in response.content.split("\n") if line.strip()]

    return {"search_queries": queries}
