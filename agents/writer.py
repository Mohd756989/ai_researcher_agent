"""
Writer agent: drafts a professional report from the analysis.
"""
from llm_client import llm
from graph.state import AgentState
from langsmith import traceable

@traceable(name="writer_agent")
def writer_agent(state: AgentState) -> dict:
    query = state["query"]
    analysis = state["analysis"]

    prompt = f"""
    Create a professional report.

    Topic:
    {query}

    Analysis:
    {analysis}

    Include:
    - Executive Summary
    - Key Findings
    - Recommendations
    - Conclusion
    """

    response = llm.invoke(prompt)
    return {"report": response.content}
