"""
Streamlit UI for the multi-agent research system.

By default this calls the FastAPI backend (researcher_agent/api/main.py).
If the API isn't reachable, it falls back to running the LangGraph
pipeline directly in-process, so the app still works standalone.

Run the API:
    uvicorn researcher_agent.api.main:app --reload --port 8000

Run the UI:
    streamlit run researcher_agent/app.py
"""
import streamlit as st
import os
import sys
import uuid

# Make sure the parent directory (which contains the `researcher_agent`
# package) is importable, regardless of which directory this script is
# launched from.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PARENT_DIR = os.path.dirname(_THIS_DIR)
if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)

import streamlit as st

from api_client import ResearchAPIClient

st.set_page_config(page_title="AI Research Agent", page_icon="🔎", layout="wide")

API_BASE_URL = os.getenv("RESEARCH_API_URL", "airesearcheragent-production.up.railway.app")
NODE_LABELS = {
    "planner": "🧭 Planning search queries",
    "researcher": "🌐 Researching the web",
    "analyzer": "🔬 Analyzing findings",
    "writer": "✍️ Writing report",
    "reviewer": "✅ Reviewing report",
}

# ---------- session state ----------
if "history" not in st.session_state:
    st.session_state.history = []  # list of {query, report, analysis, search_results}
if "api_client" not in st.session_state:
    st.session_state.api_client = ResearchAPIClient(API_BASE_URL)

api = st.session_state.api_client
api_available = api.health()

# ---------- sidebar ----------
with st.sidebar:
    st.title("🔎 Research Agent")
    st.caption("Planner → Researcher → Analyzer → Writer → Reviewer")
    st.divider()
    st.subheader("History")
    if not st.session_state.history:
        st.caption("No reports yet.")
    for i, item in enumerate(reversed(st.session_state.history)):
        if st.button(item["query"][:40] or "Untitled", key=f"hist_{i}"):
            st.session_state.selected = len(st.session_state.history) - 1 - i

# ---------- main ----------
st.title("AI Research Agent")
st.write("Enter a topic and the multi-agent pipeline will research, analyze, and write a report.")

query = st.text_area("Research topic", placeholder="e.g. Cloud Computing Trends in 2026", height=80)
col1, col2 = st.columns([1, 5])
with col1:
    run_clicked = st.button("Run Research", type="primary", use_container_width=True)

if run_clicked and query.strip():
    progress_box = st.status("Starting research pipeline...", expanded=True)
    final_result = None

    try:
        if api_available:
            job_id = api.start_job(query)

            def on_update(status):
                step = status.get("current_step")
                if step:
                    progress_box.write(step)

            status = api.poll_until_done(job_id, on_update=on_update)

            if status["status"] == "completed":
                final_result = status["result"]
                progress_box.update(label="Research complete ✅", state="complete")
            else:
                progress_box.update(label="Failed ❌", state="error")
                st.error(f"Pipeline error: {status.get('error')}")
        else:
            # Local in-process fallback (no API running)
            from graph.workflow import build_graph

            if "local_graph" not in st.session_state:
                st.session_state.local_graph = build_graph()

            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            final_state = {}
            for step in st.session_state.local_graph.stream({"query": query}, config=config):
                for node_name, node_output in step.items():
                    progress_box.write(NODE_LABELS.get(node_name, node_name))
                    final_state.update(node_output)
            progress_box.update(label="Research complete ✅", state="complete")
            final_result = {
                "query": query,
                "report": final_state.get("report"),
                "analysis": final_state.get("analysis"),
                "review": final_state.get("review"),
                "search_results": final_state.get("search_results", []),
            }
    except Exception as e:
        progress_box.update(label="Failed ❌", state="error")
        st.error(f"Pipeline error: {e}")

    if final_result and final_result.get("report"):
        st.session_state.history.append(final_result)
        st.session_state.selected = len(st.session_state.history) - 1

# ---------- render selected report ----------
selected_idx = st.session_state.get("selected")
if selected_idx is not None and 0 <= selected_idx < len(st.session_state.history):
    item = st.session_state.history[selected_idx]

    tab_report, tab_analysis, tab_sources = st.tabs(["📄 Report", "🔬 Analysis", "🌐 Sources"])

    with tab_report:
        st.subheader(f"Report: {item['query']}")
        st.markdown(item["report"] or "_No report generated._")
        st.download_button(
            "Download report (.md)",
            data=item["report"] or "",
            file_name="research_report.md",
            mime="text/markdown",
        )

    with tab_analysis:
        st.markdown(item["analysis"] or "_No analysis available._")

    with tab_sources:
        results = item["search_results"]
        if not results:
            st.caption("No sources recorded.")
        for r in results:
            if isinstance(r, dict):
                title = r.get("title", "Untitled")
                url = r.get("url", "")
                content = r.get("content", "") or ""
                st.markdown(f"**[{title}]({url})**")
                st.caption(content[:300] + ("..." if len(content) > 300 else ""))
                st.divider()