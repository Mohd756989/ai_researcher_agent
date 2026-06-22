"""
Analyzer agent: synthesizes raw search results into key findings,
trends, opportunities, and risks.
"""
from researcher_agent.llm_client import llm
from researcher_agent.graph.state import AgentState

def _format_docs(docs: list[dict]) -> str:
    parts = []
    for d in docs:
        if isinstance(d, dict):
            title = d.get("title", "")
            content = d.get("content", "")
            url = d.get("url", "")
            parts.append(f"Source: {title} ({url})\n{content}")
        else:
            parts.append(str(d))
    return "\n\n".join(parts)


def analyzer_agent(state: AgentState) -> dict:
    docs = state["search_results"]
    context = _format_docs(docs)

    prompt = f"""
    Analyze the following research:

    {context}

    Extract:
    1. Key Findings
    2. Trends
    3. Opportunities
    4. Risks
    """

    response = llm.invoke(prompt)
    return {"analysis": response.content}
