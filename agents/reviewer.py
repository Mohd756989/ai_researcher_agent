"""
Reviewer agent: critiques the drafted report and decides whether it's
approved or needs another pass.
"""
from llm_client import llm
from graph.state import AgentState
from langsmith import traceable

@traceable(name="reviewer_agent")
def reviewer_agent(state: AgentState) -> dict:
    report = state["report"]
    revision_count = state.get("revision_count", 0) + 1

    prompt = f"""
    Review this report.

    {report}

    Check for:
    - Missing sections
    - Weak conclusions
    - Unsupported claims

    Return only one word: APPROVED or REJECTED
    """

    response = llm.invoke(prompt)
    return {"review": response.content, "revision_count": revision_count}


def review_decision(state: AgentState) -> str:
    review = state["review"]
    revision_count = state.get("revision_count", 0)

    # Cap revisions so the graph can't loop forever
    if "APPROVED" in review.upper() or revision_count >= 3:
        return "approved"
    return "rejected"
