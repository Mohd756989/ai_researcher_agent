"""
Pydantic models for the API layer.
"""
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3, description="The research topic to investigate")


class ResearchJobResponse(BaseModel):
    job_id: str
    status: JobStatus


class SearchResultItem(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    content: Optional[str] = None


class ResearchResult(BaseModel):
    query: str
    report: Optional[str] = None
    analysis: Optional[str] = None
    review: Optional[str] = None
    search_results: List[SearchResultItem] = []


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    current_step: Optional[str] = None
    error: Optional[str] = None
    result: Optional[ResearchResult] = None
