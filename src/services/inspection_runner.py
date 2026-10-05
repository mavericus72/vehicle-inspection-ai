from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict
from uuid import uuid4

from src.services.inspection_service import InspectionService


class InspectionRunner:
    """
    Manages asynchronous vehicle inspection jobs.

    Responsibilities:
        - Create inspection jobs.
        - Track job lifecycle.
        - Execute inspections in the background.
        - Store inspection results.
        - Store failures and errors.
        - Provide job status to the API layer.

    This class does NOT:
        - implement FastAPI routes.
        - perform vehicle inference directly.
        - contain the Phase 1 inspection pipeline.
        - import or depend on the API layer.
    """

    def __init__(
        self,
        inspection_service: InspectionService | None = None,
    ):
        """
        Initialize the inspection runner.

        Args:
            inspection_service:
                Optional InspectionService instance.

                If omitted, a new InspectionService is created.
        """

        self.inspection_service = (
            inspection_service
            if inspection_service is not None
            else InspectionService()
        )

        # --------------------------------------------------------------
        # In-memory job store
        #
        # This is appropriate for the current Phase 2 development
        # stage. Later, this can be replaced by Redis/database-backed
        # persistence without changing the API contract.
        # --------------------------------------------------------------

        self._jobs: Dict[
            str,
            Dict[str, Any],
        ] = {}

        self._lock = Lock()

    # ==================================================================
    # CREATE JOB
    # ==================================================================

    def create_job(
        self,
        video_path: str,
    ) -> str:
        """
        Create a new inspection job.

        New jobs always begin in the "queued" state.

        Args:
            video_path:
                Absolute or relative path to the inspection video.

        Returns:
            Newly generated job ID.
        """

        if not video_path:
            raise ValueError(
                "video_path is required."
            )

        job_id = str(
            uuid4()
        )

        timestamp = self._utc_now()

        job = {
            "job_id": job_id,
            "status": "queued",
            "video_path": str(video_path),
            "created_at": timestamp,
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None,
        }

        with self._lock:

            self._jobs[job_id] = job

        return job_id

    # ==================================================================
    # RUN JOB
    # ==================================================================

    def run_job(
        self,
        job_id: str,
    ) -> None:
        """
        Execute an inspection job.

        This method is intended to be called by a background worker.

        Lifecycle:

            queued
              ↓
            running
              ↓
            completed

        or:

            queued
              ↓
            running
              ↓
            failed
        """

        # --------------------------------------------------------------
        # Locate job and transition to RUNNING
        # --------------------------------------------------------------

        with self._lock:

            job = self._jobs.get(
                job_id
            )

            if job is None:
                raise KeyError(
                    f"Inspection job not found: {job_id}"
                )

            # Prevent accidental duplicate execution.
            if job["status"] != "queued":
                return

            job["status"] = "running"

            job["started_at"] = (
                self._utc_now()
            )

            video_path = job[
                "video_path"
            ]

        # --------------------------------------------------------------
        # Execute inspection
        # --------------------------------------------------------------

        try:

            result = (
                self.inspection_service.inspect(
                    video_path
                )
            )

            result_dict = (
                result.to_dict()
            )

            # ----------------------------------------------------------
            # Store successful or failed service result
            # ----------------------------------------------------------

            with self._lock:

                job = self._jobs.get(
                    job_id
                )

                if job is None:
                    return

                job["result"] = result_dict

                if result.success:

                    job["status"] = (
                        "completed"
                    )

                    job["error"] = None

                else:

                    job["status"] = (
                        "failed"
                    )

                    job["error"] = (
                        result.error
                    )

                job["completed_at"] = (
                    self._utc_now()
                )

        # --------------------------------------------------------------
        # Unexpected runner/service exception
        # --------------------------------------------------------------

        except Exception as exc:

            with self._lock:

                job = self._jobs.get(
                    job_id
                )

                if job is None:
                    return

                job["status"] = "failed"

                job["error"] = (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

                job["completed_at"] = (
                    self._utc_now()
                )

    # ==================================================================
    # GET JOB
    # ==================================================================

    def get_job(
        self,
        job_id: str,
    ) -> Dict[str, Any] | None:
        """
        Return the current state of an inspection job.

        Returns:
            A copy of the job dictionary, or None if the job does not
            exist.
        """

        with self._lock:

            job = self._jobs.get(
                job_id
            )

            if job is None:
                return None

            return dict(job)

    # ==================================================================
    # JOB EXISTS
    # ==================================================================

    def has_job(
        self,
        job_id: str,
    ) -> bool:
        """
        Check whether an inspection job exists.
        """

        with self._lock:

            return (
                job_id in self._jobs
            )

    # ==================================================================
    # UTC TIMESTAMP
    # ==================================================================

    @staticmethod
    def _utc_now() -> str:
        """
        Return the current UTC timestamp in ISO-8601 format.
        """

        return (
            datetime.now(
                timezone.utc
            ).isoformat()
        )
