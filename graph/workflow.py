"""
Builds and compiles the multi-agent research LangGraph workflow:

  planner -> researcher -> analyzer -> writer -> reviewer
                ^                                   |
                |_________ rejected ________________|
                                                      |
                                                  approved -> END
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from researcher_agent.graph.state import AgentState
from researcher_agent.agents.planner import planner_agent
from researcher_agent.agents.researcher import researcher_agent
from researcher_agent.agents.analyzer import analyzer_agent
from researcher_agent.agents.writer import writer_agent
from researcher_agent.agents.reviewer import reviewer_agent, review_decision


def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("planner", planner_agent)
    builder.add_node("researcher", researcher_agent)
    builder.add_node("analyzer", analyzer_agent)
    builder.add_node("writer", writer_agent)
    builder.add_node("reviewer", reviewer_agent)

    builder.set_entry_point("planner")

    builder.add_edge("planner", "researcher")
    builder.add_edge("researcher", "analyzer")
    builder.add_edge("analyzer", "writer")
    builder.add_edge("writer", "reviewer")

    builder.add_conditional_edges(
        "reviewer",
        review_decision,
        {
            "approved": END,
            "rejected": "researcher",
        },
    )

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


graph = build_graph()
