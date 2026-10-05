from future import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict, Optional

@dataclass
class InspectionJob:
"""
Runtime state for an asynchronous vehicle inspection job.
"""

job_id: str

status: str = "queued"

created_at: datetime = field(
    default_factory=lambda: datetime.now(timezone.utc)
)

started_at: Optional[datetime] = None

completed_at: Optional[datetime] = None

result: Optional[Dict[str, Any]] = None

error: Optional[str] = None


class InspectionJobStore:
"""
Thread-safe in-memory inspection job store.

This is intentionally simple for the first asynchronous API
implementation. A persistent/shared job backend can replace this
later without changing the API contract.
"""

def __init__(self):
    self._jobs: Dict[str, InspectionJob] = {}
    self._lock = Lock()

def create(
    self,
    job_id: str,
) -> InspectionJob:

    job = InspectionJob(
        job_id=job_id
    )

    with self._lock:
        self._jobs[job_id] = job

    return job

def get(
    self,
    job_id: str,
) -> Optional[InspectionJob]:

    with self._lock:
        return self._jobs.get(job_id)

def update(
    self,
    job_id: str,
    **changes,
) -> Optional[InspectionJob]:

    with self._lock:

        job = self._jobs.get(job_id)

        if job is None:
            return None

        for key, value in changes.items():
            setattr(job, key, value)

        return job

def all(self) -> list[InspectionJob]:

    with self._lock:
        return list(self._jobs.values())


job_store = InspectionJobStore()