"""
Shared state schema passed between every node in the LangGraph workflow.
"""
from typing import TypedDict, List


class AgentState(TypedDict):
    query: str

    search_queries: List[str]
    search_results: List[dict]
    analysis: str

    report: str
    review: str

    revision_count: int
