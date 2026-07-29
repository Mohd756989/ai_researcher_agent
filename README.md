# AI Research Agent

A multi-agent research pipeline built with **LangGraph** + **Groq** + **Tavily**, served via a **FastAPI** backend with a **Streamlit** UI on top.

## Architecture

```
┌─────────────┐      HTTP       ┌──────────────┐      invokes      ┌──────────────┐
│  Streamlit  │ ───────────────▶│   FastAPI    │ ─────────────────▶│   LangGraph  │
│     UI      │ ◀─────────────  │   backend    │ ◀───────────────  │   pipeline   │
└─────────────┘    poll status  └──────────────┘     result        └──────────────┘
```

- **FastAPI backend** — exposes the agent pipeline as a REST API, runs jobs in the background, tracks status, has request logging, CORS, and a global exception handler
- **Streamlit UI** — calls the API and polls for progress; if the API isn't running, it falls back to running the pipeline in-process so the app still works standalone

## Pipeline

```
planner → researcher → analyzer → writer → reviewer
              ↑                              |
              └────────── rejected ──────────┘
                                              |
                                          approved → END
```

- **Planner** — turns your topic into 5 targeted search queries
- **Researcher** — runs those queries via Tavily web search
- **Analyzer** — extracts key findings, trends, opportunities, risks
- **Writer** — drafts a professional report (exec summary, findings, recommendations, conclusion)
- **Reviewer** — critiques the report; if rejected, loops back to research (capped at 3 revisions to avoid infinite loops)

## Project structure

```
researcher_agent/
├── app.py                  # Streamlit UI (calls the API)
├── api_client.py           # HTTP client used by the UI
├── config.py                # env var loading
├── llm_client.py             # shared Groq LLM client
├── requirements.txt
├── .env.example
├── Dockerfile.api / Dockerfile.ui
├── docker-compose.yml
├── api/
│   ├── main.py               # FastAPI app + routes
│   ├── schemas.py            # Pydantic request/response models
│   ├── job_store.py          # in-memory async job tracking
│   └── runner.py             # runs the graph in a background thread
├── agents/
│   ├── planner.py
│   ├── researcher.py
│   ├── analyzer.py
│   ├── writer.py
│   └── reviewer.py
├── graph/
│   ├── state.py              # AgentState schema
│   └── workflow.py           # graph construction
└── tools/
    └── search.py              # Tavily search wrapper
```

## API reference

| Method | Endpoint              | Description                                              |
|--------|------------------------|-----------------------------------------------------------|
| GET    | `/health`              | Health check                                               |
| POST   | `/research`            | Start a research job. Returns `{job_id, status}`           |
| GET    | `/research/{job_id}`   | Poll for status/progress; includes `result` once completed |
| POST   | `/research/sync`       | Run the pipeline synchronously (blocks until done)         |

Interactive docs (Swagger UI) at **http://localhost:8000/docs** once the API is running.

Example:
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Cloud Computing Trends in 2026"}'
# -> {"job_id": "...", "status": "pending"}

curl http://localhost:8000/research/<job_id>
# -> {"status": "running", "current_step": "Researching the web", ...}
# poll again later ->
# -> {"status": "completed", "result": {"report": "...", ...}}
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your keys:
   ```bash
   cp .env.example .env
   ```
   ```
   GROQ_API_KEY=your_key_here
   TAVILY_API_KEY=your_key_here
   ```

   Get keys at https://console.groq.com and https://app.tavily.com

3. Run both services **from the parent directory** of `researcher_agent/` (so the package imports resolve):

   **Terminal 1 — API:**
   ```bash
   uvicorn researcher_agent.api.main:app --reload --port 8000
   ```

   **Terminal 2 — UI:**
   ```bash
   streamlit run researcher_agent/app.py
   ```

   The UI auto-detects the API at `http://localhost:8000` (override with the `RESEARCH_API_URL` env var). If the API isn't running, the UI falls back to running the pipeline locally.

### Run with Docker Compose

From inside `researcher_agent/`:
```bash
docker compose up --build
```
This builds and runs both the API (port 8000) and UI (port 8501), wired together automatically.

### Evaluate the agent

A lightweight evaluation harness is included under `evals/`.

```bash
python -m evals.runner --json
```

You can also run a single case:
```bash
python -m evals.runner --case cloud-trends
```

make sure the app completes the evals testing before going to production

## Notes on fixes from the original notebook

- Removed hardcoded API keys — now loaded from `.env` / environment variables only.
- Fixed the `search_web` bug where `.search()` was called twice (once on the client, once on the dict result).
- `analyzer_agent` now safely formats search results (the notebook crashed trying to `"\n".join()` a list of dicts).
- Added a `revision_count` cap so the reviewer→researcher loop can't run forever.
- Added a FastAPI backend with async job tracking, request logging, CORS, and a global error handler — so the agent logic is decoupled from the UI and can be consumed by anything (Streamlit, a future React frontend, curl, etc.).
- Streamlit UI now calls the API and polls for live progress, with a local-mode fallback, history of past runs, and a markdown download button.

