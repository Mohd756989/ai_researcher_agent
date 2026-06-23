"""
Production-style FastAPI backend for the research agent.

Run with:
    uvicorn researcher_agent.api.main:app --reload --port 8000

Docs available at http://localhost:8000/docs
"""
import logging
import time
import uuid

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.schemas import (
    ResearchRequest,
    ResearchJobResponse,
    JobStatusResponse,
    JobStatus,
)
from researcher_agent.api.job_store import job_store
from researcher_agent.api.runner import run_research_job

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("researcher_agent.api")

app = FastAPI(
    title="AI Research Agent API",
    description="Multi-agent research pipeline (planner → researcher → analyzer → writer → reviewer) built with LangGraph.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in real production deployments
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- request logging / timing middleware ----------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    logger.info(
        "%s %s -> %s (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# ---------- error handling ----------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ---------- routes ----------
@app.get("/health", tags=["meta"])
def health_check():
    return {"status": "ok"}


@app.post("/research", response_model=ResearchJobResponse, tags=["research"])
def start_research(req: ResearchRequest, background_tasks: BackgroundTasks):
    """Kick off a research job asynchronously. Poll /research/{job_id} for status."""
    job_id = str(uuid.uuid4())
    job_store.create(job_id, req.query)
    background_tasks.add_task(run_research_job, job_id, req.query)
    return ResearchJobResponse(job_id=job_id, status=JobStatus.PENDING)


@app.get("/research/{job_id}", response_model=JobStatusResponse, tags=["research"])
def get_research_status(job_id: str):
    """Poll this to check job progress / fetch the final report."""
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        current_step=job.current_step,
        error=job.error,
        result=job.result,
    )


@app.post("/research/sync", response_model=JobStatusResponse, tags=["research"])
def run_research_sync(req: ResearchRequest):
    """Run the pipeline synchronously and return the final result directly.
    Convenient for quick testing, but blocks until the pipeline finishes."""
    job_id = str(uuid.uuid4())
    job_store.create(job_id, req.query)
    run_research_job(job_id, req.query)
    job = job_store.get(job_id)
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        current_step=job.current_step,
        error=job.error,
        result=job.result,
    )
