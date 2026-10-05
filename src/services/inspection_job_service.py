from __future__ import annotations

import threading
import uuid
from concurrent.futures import (
    Future,
    ThreadPoolExecutor,
)
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from src.services.inspection_service import (
    InspectionService,
)


class InspectionJobService:
    """
    Asynchronous inspection job manager.

    Phase 2 implementation uses:
        - ThreadPoolExecutor
        - In-memory job storage
        - InspectionService for actual inference
        - Thread-safe job state management

    The inference pipeline itself remains unchanged.
    """

    def __init__(
        self,
        max_workers: int = 1,
    ):
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="inspection-worker",
        )

        self.jobs: Dict[
            str,
            Dict[str, Any],
        ] = {}

        self.lock = threading.Lock()

    # ==================================================================
    # CREATE JOB
    # ==================================================================

    def create_job(
        self,
        video_path: str,
    ) -> str:
        """
        Create and submit an asynchronous inspection job.

        Returns:
            Unique job ID.
        """

        job_id = str(
            uuid.uuid4()
        )

        created_at = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        # --------------------------------------------------------------
        # Register job BEFORE submitting it.
        # --------------------------------------------------------------

        with self.lock:

            self.jobs[job_id] = {
                "job_id": job_id,
                "status": "queued",
                "video_path": video_path,
                "created_at": created_at,
                "started_at": None,
                "completed_at": None,
                "result": None,
                "error": None,
            }

        # --------------------------------------------------------------
        # Submit background task.
        #
        # IMPORTANT:
        # The Future is assigned here.
        # We never reference `future` before this line.
        # --------------------------------------------------------------

        future = self.executor.submit(
            self._run_job,
            job_id,
            video_path,
        )

        # --------------------------------------------------------------
        # Store Future internally.
        # --------------------------------------------------------------

        with self.lock:

            job = self.jobs.get(
                job_id
            )

            if job is not None:
                job["future"] = future

        return job_id

    # ==================================================================
    # RUN JOB
    # ==================================================================

    def _run_job(
        self,
        job_id: str,
        video_path: str,
    ) -> None:
        """
        Execute the actual inspection in a worker thread.
        """

        started_at = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        # --------------------------------------------------------------
        # Mark job as running.
        # --------------------------------------------------------------

        with self.lock:

            job = self.jobs.get(
                job_id
            )

            if job is None:
                return

            job["status"] = "running"
            job["started_at"] = started_at

        try:

            # ----------------------------------------------------------
            # Use the existing Phase 2 service.
            # ----------------------------------------------------------

            service = InspectionService()

            result = service.inspect(
                video_path
            )

            completed_at = (
                datetime.now(
                    timezone.utc
                ).isoformat()
            )

            # ----------------------------------------------------------
            # Store successful/failed service result.
            # ----------------------------------------------------------

            with self.lock:

                job = self.jobs.get(
                    job_id
                )

                if job is None:
                    return

                job["status"] = (
                    "completed"
                    if result.success
                    else "failed"
                )

                job["completed_at"] = (
                    completed_at
                )

                job["result"] = (
                    result.to_dict()
                )

                if not result.success:

                    job["error"] = (
                        result.error
                    )

        except Exception as exc:

            completed_at = (
                datetime.now(
                    timezone.utc
                ).isoformat()
            )

            with self.lock:

                job = self.jobs.get(
                    job_id
                )

                if job is None:
                    return

                job["status"] = "failed"

                job["completed_at"] = (
                    completed_at
                )

                job["error"] = (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

    # ==================================================================
    # GET JOB
    # ==================================================================

    def get_job(
        self,
        job_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Return a JSON-safe representation of a job.

        The internal Future object is deliberately excluded.
        """

        with self.lock:

            job = self.jobs.get(
                job_id
            )

            if job is None:
                return None

            return {
                key: value
                for key, value in job.items()
                if key != "future"
            }

    # ==================================================================
    # SHUTDOWN
    # ==================================================================

    def shutdown(
        self,
    ) -> None:
        """
        Shut down the worker pool.
        """

        self.executor.shutdown(
            wait=False,
            cancel_futures=False,
        )
