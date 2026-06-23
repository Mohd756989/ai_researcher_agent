"""
Runs the research graph in a background thread and keeps the job store
updated with progress so the API can report status while it's running.
"""
import logging
import uuid

from graph.workflow import build_graph
from api.job_store import job_store
from api.schemas import JobStatus

logger = logging.getLogger("researcher_agent.runner")

_graph = build_graph()

NODE_LABELS = {
    "planner": "Planning search queries",
    "researcher": "Researching the web",
    "analyzer": "Analyzing findings",
    "writer": "Writing report",
    "reviewer": "Reviewing report",
}


def run_research_job(job_id: str, query: str):
    job_store.update(job_id, status=JobStatus.RUNNING, current_step="Starting")
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    final_state: dict = {}

    try:
        for step in _graph.stream({"query": query}, config=config):
            for node_name, node_output in step.items():
                job_store.update(
                    job_id,
                    current_step=NODE_LABELS.get(node_name, node_name),
                )
                final_state.update(node_output)

        result = {
            "query": query,
            "report": final_state.get("report"),
            "analysis": final_state.get("analysis"),
            "review": final_state.get("review"),
            "search_results": final_state.get("search_results", []),
        }
        job_store.update(
            job_id, status=JobStatus.COMPLETED, current_step="Done", result=result
        )
    except Exception as e:
        logger.exception("Research job %s failed", job_id)
        job_store.update(job_id, status=JobStatus.FAILED, error=str(e))
