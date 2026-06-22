"""
Simple in-memory job store.

For a real production deployment you'd swap this for Redis / a database
so jobs survive restarts and work across multiple worker processes —
but this keeps the project dependency-free and easy to run.
"""
import threading
from datetime import datetime
from typing import Dict, Optional

from researcher_agent.api.schemas import JobStatus


class Job:
    def __init__(self, job_id: str, query: str):
        self.job_id = job_id
        self.query = query
        self.status = JobStatus.PENDING
        self.current_step: Optional[str] = None
        self.error: Optional[str] = None
        self.result: Optional[dict] = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class JobStore:
    def __init__(self):
        self._jobs: Dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self, job_id: str, query: str) -> Job:
        job = Job(job_id, query)
        with self._lock:
            self._jobs[job_id] = job
        return job

    def get(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)

    def update(self, job_id: str, **fields):
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            for k, v in fields.items():
                setattr(job, k, v)
            job.updated_at = datetime.utcnow()


job_store = JobStore()
